from odoo import api, fields, models
from dateutil.relativedelta import relativedelta

class WizardRenewContract(models.TransientModel):
    _name = 'wizard.renew.contract'
    _description = 'Wizard de Renouvellement de Contrat'

    contract_id = fields.Many2one('it.contract', string='Contrat', required=True)
    new_end_date = fields.Date(string='Nouvelle date de fin', required=True)
    amount = fields.Monetary(string='Nouveau montant')
    currency_id = fields.Many2one('res.currency', string='Devise', related='contract_id.currency_id')

    @api.model
    def default_get(self, fields):
        res = super(WizardRenewContract, self).default_get(fields)
        if self.env.context.get('active_id'):
            contract = self.env['it.contract'].browse(self.env.context.get('active_id'))
            res['contract_id'] = contract.id
            if contract.end_date:
                res['new_end_date'] = contract.end_date + relativedelta(years=1)
        return res

    def action_renew(self):
        # Marquer l'ancien comme renouvelé
        self.contract_id.state = 'renewed'
        
        # Créer le nouveau contrat
        new_contract = self.contract_id.copy({
            'name': f"{self.contract_id.name} (Renouvelé)",
            'start_date': fields.Date.context_today(self),
            'end_date': self.new_end_date,
            'amount': self.amount,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'it.contract',
            'res_id': new_contract.id,
            'view_mode': 'form',
            'target': 'current',
        }
