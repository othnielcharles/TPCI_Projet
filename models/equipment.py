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
            if vals.get('reference', 'Nouveau') == 'Nouveau':
                vals['reference'] = self.env['ir.sequence'].next_by_code('it.equipment.seq') or 'Nouveau'
        return super().create(vals_list)

    @api.model
    def get_statistics(self):
        equipments = self.search([])
        interventions = self.env['it.intervention'].search([])
        contracts = self.env['it.contract'].search([('state', '=', 'active')])

        total_equipments = len(equipments)
        in_maintenance = len(equipments.filtered(lambda e: e.state == 'maintenance'))
        active_contracts = len(contracts)
        total_maintenance_cost = sum(interventions.mapped('cost'))

        categories = {}
        for eq in equipments:
            cat = eq.category or 'Autre'
            categories[cat] = categories.get(cat, 0) + 1

        return {
            'total_equipments': total_equipments,
            'in_maintenance': in_maintenance,
            'active_contracts': active_contracts,
            'total_maintenance_cost': total_maintenance_cost,
            'chart_data': {
                'labels': list(categories.keys()),
                'values': list(categories.values())
            }
        }

    def action_affecter(self):
        self.state = 'affecte'

    def action_maintenance(self):
        self.state = 'maintenance'

    def action_retirer(self):
        self.state = 'retire'

    def action_brouillon(self):
        self.state = 'brouillon'
