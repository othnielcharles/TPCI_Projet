from odoo import api, fields, models

class ItContract(models.Model):
    _name = 'it.contract'
    _description = 'Contrat Fournisseur'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Référence du contrat', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Fournisseur', required=True, tracking=True)
    start_date = fields.Date(string='Date de début', required=True, tracking=True)
    end_date = fields.Date(string='Date de fin', required=True, tracking=True)
    
    amount = fields.Monetary(string='Montant')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)
    
    equipment_ids = fields.Many2many('it.equipment', string='Équipements couverts')
    
    days_left = fields.Integer(string='Jours restants', compute='_compute_days_left', store=False)
    
    state = fields.Selection([
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('renewed', 'Renouvelé')
    ], string='Statut', compute='_compute_state', store=True)

    @api.depends('end_date')
    def _compute_days_left(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.end_date:
                delta = record.end_date - today
                record.days_left = delta.days
            else:
                record.days_left = 0

    @api.depends('end_date')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.state != 'renewed':
                if record.end_date and record.end_date < today:
                    record.state = 'expired'
                else:
                    record.state = 'active'
