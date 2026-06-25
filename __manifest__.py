{
    'name': 'Gestion de parc informatique - it_parc',
    'version': '18.0.1.0.0',
    'summary': 'Module de gestion du parc informatique interne pour TECHPARK CI',
    'description': """
        Module Odoo 18 personnalisé pour la gestion du parc informatique de TECHPARK CI.
        Fonctionnalités :
        - Inventaire des équipements
        - Affectations (employés et départements)
        - Interventions et maintenance
        - Gestion des contrats fournisseurs et alertes
        - Rapports PDF et exports Excel
        - Tableau de bord OWL
    """,
    'category': 'IT Management',
    'author': 'TECHPARK CI',
    'website': 'https://www.techpark.ci',
    'license': 'AGPL-3',
    'depends': [
        'base', 'hr', 'stock', 'purchase', 'account', 'maintenance', 'mail', 'contacts', 'web'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/it_equipment_sequence.xml',
        'data/it_cron.xml',
        'views/equipment_views.xml',
        'views/assignment_views.xml',
        'views/intervention_views.xml',
        'views/contract_views.xml',
        'views/alerte_views.xml',
        'wizards/import_equipment_views.xml',
        'wizards/reassign_equipment_views.xml',
        'wizards/renew_contract_views.xml',
        'views/menus.xml',
        # 'views/menus.xml',
        # 'data/it_parc_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'it_parc/static/src/js/dashboard.js',
            # 'it_parc/static/src/xml/dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
