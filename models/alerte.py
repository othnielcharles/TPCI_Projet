from datetime import timedelta
from odoo import api, fields, models

class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = 'Alerte Système IT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Sujet', required=True)
    date = fields.Datetime(string='Date de l\'alerte', default=fields.Datetime.now, required=True)
    type = fields.Selection([
        ('warranty', 'Fin de garantie'),
        ('contract', 'Fin de contrat')
    ], string='Type', required=True)
    
    equipment_id = fields.Many2one('it.equipment', string='Équipement concerné')
    contract_id = fields.Many2one('it.contract', string='Contrat concerné')
    
    message = fields.Text(string='Message')
    is_read = fields.Boolean(string='Lue', default=False)

    @api.model
    def _cron_generate_alerts(self):
        """ Cron method to generate alerts for expiring warranties and contracts """
        today = fields.Date.context_today(self)
        threshold_date = today + timedelta(days=30)
        
        # Check warranties
        equipments = self.env['it.equipment'].search([
            ('warranty_date', '!=', False),
            ('warranty_date', '<=', threshold_date),
            ('warranty_date', '>=', today)
        ])
        
        for eq in equipments:
            existing = self.search([('type', '=', 'warranty'), ('equipment_id', '=', eq.id), ('is_read', '=', False)])
            if not existing:
                self.create({
                    'name': f'Garantie expirant bientôt : {eq.name}',
                    'type': 'warranty',
                    'equipment_id': eq.id,
                    'message': f'La garantie de l\'équipement {eq.reference} expire le {eq.warranty_date}.'
                })
                
        # Check contracts
        contracts = self.env['it.contract'].search([
            ('state', '=', 'active'),
            ('end_date', '<=', threshold_date),
            ('end_date', '>=', today)
        ])
        
        for contract in contracts:
            existing = self.search([('type', '=', 'contract'), ('contract_id', '=', contract.id), ('is_read', '=', False)])
            if not existing:
                self.create({
                    'name': f'Contrat expirant bientôt : {contract.name}',
                    'type': 'contract',
                    'contract_id': contract.id,
                    'message': f'Le contrat {contract.name} avec {contract.partner_id.name} expire le {contract.end_date}.'
                })
