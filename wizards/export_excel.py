from odoo import models, fields, api

class WizardExportExcel(models.TransientModel):
    _name = 'wizard.export.excel'
    _description = 'Assistant d\'Export Excel'

    export_type = fields.Selection([
        ('inventory', 'Inventaire complet'),
        ('maintenance', 'Synthèse des coûts de maintenance'),
        ('contracts', 'Contrats expirant (60 jours)')
    ], string='Type d\'export', required=True, default='inventory')

    def action_export(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/it_parc/export_excel?export_type={self.export_type}',
            'target': 'new',
        }
