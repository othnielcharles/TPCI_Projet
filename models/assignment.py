from odoo import api, fields, models

class ItAssignment(models.Model):
    _name = 'it.assignment'
    _description = 'Affectation d\'équipement'
    _order = 'start_date desc'

    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True)
    department_id = fields.Many2one('hr.department', string='Département', related='employee_id.department_id', store=True)
    
    start_date = fields.Date(string='Date d\'affectation', default=fields.Date.context_today, required=True)
    end_date = fields.Date(string='Date de retour')
    reason = fields.Char(string='Motif de réaffectation/retour')
    is_active = fields.Boolean(string='Actif', compute='_compute_is_active', store=True)

    @api.depends('end_date')
    def _compute_is_active(self):
        for record in self:
            record.is_active = not bool(record.end_date)
