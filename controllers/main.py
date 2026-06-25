import io
from odoo import http
from odoo.http import request

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None

class ItParcExportController(http.Controller):
    
    @http.route('/it_parc/export_excel', type='http', auth='user')
    def export_excel(self, export_type=None, **kwargs):
        if not xlsxwriter:
            return request.make_response(
                "La librairie xlsxwriter n'est pas installée sur le serveur Python.",
                headers=[('Content-Type', 'text/plain')]
            )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'border': 1})
        normal_format = workbook.add_format({'border': 1})
        warning_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'border': 1})
        critical_format = workbook.add_format({'bg_color': '#FF0000', 'font_color': '#FFFFFF', 'border': 1, 'bold': True})

        filename = "export.xlsx"

        if export_type == 'inventory':
            filename = "Inventaire_Complet.xlsx"
            sheet = workbook.add_worksheet('Inventaire')
            headers = ['Référence', 'Nom', 'Numéro de série', 'Catégorie', 'Date d\'achat', 'Valeur', 'État', 'Employé']
            for col, h in enumerate(headers):
                sheet.write(0, col, h, header_format)
                
            equipments = request.env['it.equipment'].search([])
            for row, eq in enumerate(equipments, 1):
                sheet.write(row, 0, eq.reference or '', normal_format)
                sheet.write(row, 1, eq.name or '', normal_format)
                sheet.write(row, 2, eq.serial_number or '', normal_format)
                sheet.write(row, 3, eq.category or '', normal_format)
                if eq.purchase_date:
                    sheet.write(row, 4, eq.purchase_date, date_format)
                else:
                    sheet.write(row, 4, '', normal_format)
                sheet.write(row, 5, eq.purchase_value or 0.0, currency_format)
                state_label = dict(eq._fields['state'].selection).get(eq.state, '')
                sheet.write(row, 6, state_label, normal_format)
                sheet.write(row, 7, eq.current_employee_id.name if eq.current_employee_id else '', normal_format)

        elif export_type == 'maintenance':
            filename = "Synthese_Couts_Maintenance.xlsx"
            sheet = workbook.add_worksheet('Synthèse Coûts')
            headers = ['Équipement', 'Mois', 'Nombre d\'interventions', 'Durée Totale (h)', 'Coût Total']
            for col, h in enumerate(headers):
                sheet.write(0, col, h, header_format)
                
            interventions = request.env['it.intervention'].search([])
            
            # Agrégation par équipement et par mois
            summary = {}
            for inv in interventions:
                if not inv.date_start:
                    continue
                month = inv.date_start.strftime('%Y-%m')
                eq_name = inv.equipment_id.name or 'Inconnu'
                key = (eq_name, month)
                if key not in summary:
                    summary[key] = {'count': 0, 'duration': 0.0, 'cost': 0.0}
                summary[key]['count'] += 1
                summary[key]['duration'] += (inv.duration or 0.0)
                summary[key]['cost'] += (inv.cost or 0.0)
                
            row = 1
            for (eq_name, month), data in sorted(summary.items()):
                sheet.write(row, 0, eq_name, normal_format)
                sheet.write(row, 1, month, normal_format)
                sheet.write(row, 2, data['count'], normal_format)
                sheet.write(row, 3, data['duration'], normal_format)
                sheet.write(row, 4, data['cost'], currency_format)
                row += 1

        elif export_type == 'contracts':
            filename = "Contrats_Expirant_60j.xlsx"
            sheet = workbook.add_worksheet('Contrats')
            headers = ['Référence', 'Fournisseur', 'Date Fin', 'Jours Restants', 'Statut']
            for col, h in enumerate(headers):
                sheet.write(0, col, h, header_format)
                
            contracts = request.env['it.contract'].search([('state', '=', 'active')])
            row = 1
            for contract in contracts:
                if contract.days_left <= 60:
                    fmt = normal_format
                    if contract.days_left <= 15:
                        fmt = critical_format
                    elif contract.days_left <= 30:
                        fmt = warning_format
                        
                    sheet.write(row, 0, contract.name or '', fmt)
                    sheet.write(row, 1, contract.partner_id.name or '', fmt)
                    if contract.end_date:
                        sheet.write(row, 2, contract.end_date, date_format)
                    else:
                        sheet.write(row, 2, '', normal_format)
                    sheet.write(row, 3, contract.days_left or 0, fmt)
                    state_label = dict(contract._fields['state'].selection).get(contract.state, '')
                    sheet.write(row, 4, state_label, fmt)
                    row += 1

        workbook.close()
        output.seek(0)
        
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', f'attachment; filename={filename}')
            ]
        )
