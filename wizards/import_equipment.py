import base64
import csv
import io
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class WizardImportEquipment(models.TransientModel):
    _name = 'wizard.import.equipment'
    _description = 'Wizard Importation Equipements CSV'

    file = fields.Binary(string='Fichier CSV', required=True)
    filename = fields.Char(string='Nom du fichier')
    report = fields.Html(string='Rapport d\'importation', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')

    def action_import(self):
        if not self.file:
            raise UserError(_("Veuillez sélectionner un fichier."))
            
        csv_data = base64.b64decode(self.file).decode('utf-8')
        lines = csv_data.splitlines()
        if not lines:
            raise UserError(_("Le fichier est vide."))
            
        reader = csv.DictReader(lines)
        created = 0
        ignored = 0
        errors = 0
        error_details = []
        
        for row in reader:
            try:
                name = row.get('name')
                serial = row.get('serial_number')
                if not name or not serial:
                    errors += 1
                    error_details.append(f"Ligne ignorée : nom ou numéro de série manquant ({row})")
                    continue
                    
                existing = self.env['it.equipment'].search([('serial_number', '=', serial)])
                if existing:
                    ignored += 1
                else:
                    self.env['it.equipment'].create({
                        'name': name,
                        'serial_number': serial,
                        'category': row.get('category', 'ordinateur'),
                        'purchase_value': float(row.get('purchase_value', 0) or 0),
                        'state': 'brouillon'
                    })
                    created += 1
            except Exception as e:
                errors += 1
                error_details.append(f"Erreur sur la ligne {row}: {str(e)}")

        report_html = f"<ul><li>Créés : {created}</li><li>Ignorés (doublons) : {ignored}</li><li>Erreurs : {errors}</li></ul>"
        if error_details:
            report_html += "<p>Détails des erreurs :</p><ul>"
            for err in error_details:
                report_html += f"<li>{err}</li>"
            report_html += "</ul>"
            
        self.write({'report': report_html, 'state': 'done'})
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.import.equipment',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
