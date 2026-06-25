from odoo import api, fields, models

class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = 'Intervention de maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(string='Numéro d\'intervention', required=True, copy=False, readonly=True, default='Nouveau')
    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True)
    technician_id = fields.Many2one('res.users', string='Technicien', default=lambda self: self.env.user)
    
    date_start = fields.Datetime(string='Date de début', required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(string='Date de fin')
    duration = fields.Float(string='Durée (heures)', compute='_compute_duration', store=True)
    
    cost = fields.Monetary(string='Coût de l\'intervention')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)
    
    report = fields.Html(string='Rapport d\'intervention')
    
    state = fields.Selection([
        ('draft', 'Planifié'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé')
    ], string='Statut', default='draft', required=True)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                delta = record.date_end - record.date_start
                record.duration = delta.total_seconds() / 3600.0
            else:
                record.duration = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('it.intervention.seq') or 'Nouveau'
        return super().create(vals_list)
