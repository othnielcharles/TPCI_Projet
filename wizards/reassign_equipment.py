from odoo import api, fields, models

class WizardReassignEquipment(models.TransientModel):
    _name = 'wizard.reassign.equipment'
    _description = 'Wizard de Réaffectation'

    equipment_id = fields.Many2one('it.equipment', string='Équipement', required=True)
    new_employee_id = fields.Many2one('hr.employee', string='Nouvel Employé', required=True)
    reason = fields.Char(string='Motif de réaffectation', required=True)

    @api.model
    def default_get(self, fields):
        res = super(WizardReassignEquipment, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['equipment_id'] = self.env.context.get('active_id')
        return res

    def action_reassign(self):
        # Clôturer l'affectation actuelle
        active_assignments = self.env['it.assignment'].search([
            ('equipment_id', '=', self.equipment_id.id),
            ('end_date', '=', False)
        ])
        today = fields.Date.context_today(self)
        for assignment in active_assignments:
            assignment.end_date = today
            assignment.reason = self.reason

        # Créer la nouvelle affectation
        self.env['it.assignment'].create({
            'equipment_id': self.equipment_id.id,
            'employee_id': self.new_employee_id.id,
            'start_date': today,
            'reason': self.reason
        })
        
        self.equipment_id.state = 'affecte'
