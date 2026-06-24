from odoo import api, fields, models, _

class ItEquipment(models.Model):
    _name = 'it.equipment'
    _description = 'Equipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nom de l\'équipement', required=True, tracking=True)
    reference = fields.Char(string='Référence', required=True, copy=False, readonly=True, default=lambda self: _('Nouveau'))
    serial_number = fields.Char(string='Numéro de série', tracking=True)
    category = fields.Selection([
        ('ordinateur', 'Ordinateur'),
        ('serveur', 'Serveur'),
        ('imprimante', 'Imprimante'),
        ('reseau', 'Équipement Réseau'),
        ('telephone', 'Téléphone IP'),
        ('autre', 'Autre')
    ], string='Catégorie', required=True, default='ordinateur', tracking=True)
    
    purchase_date = fields.Date(string='Date d\'achat')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)
    purchase_value = fields.Monetary(string='Valeur d\'achat')
    warranty_date = fields.Date(string='Date de fin de garantie', tracking=True)
    
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('affecte', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retire', 'Retiré')
    ], string='État', default='brouillon', tracking=True, required=True)

    assignment_ids = fields.One2many('it.assignment', 'equipment_id', string='Historique des affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipment_id', string='Historique des interventions')
    current_employee_id = fields.Many2one('hr.employee', string='Employé Actuel', compute='_compute_current_assignment', store=True)
    current_department_id = fields.Many2one('hr.department', string='Département Actuel', compute='_compute_current_assignment', store=True)

    @api.depends('assignment_ids', 'assignment_ids.is_active')
    def _compute_current_assignment(self):
        for record in self:
            active_assignment = record.assignment_ids.filtered(lambda a: a.is_active)
            if active_assignment:
                latest = active_assignment.sorted(key=lambda a: a.start_date, reverse=True)[0]
                record.current_employee_id = latest.employee_id
                record.current_department_id = latest.department_id
            else:
                record.current_employee_id = False
                record.current_department_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('Nouveau')) == _('Nouveau'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('it.equipment.seq') or _('Nouveau')
        return super().create(vals_list)

    def action_affecter(self):
        self.state = 'affecte'

    def action_maintenance(self):
        self.state = 'maintenance'

    def action_retirer(self):
        self.state = 'retire'

    def action_brouillon(self):
        self.state = 'brouillon'
