# -*- coding: utf-8 -*-
{
    'name': "Leaders App",

    'summary': """
        APPLICATION DE GESTION DES PREPAS CONCOURS DE LEADERS COOPORATION""",

    'description': """
         APPLICATION DE GESTION DES PREPAS CONCOURS DE LEADERS COOPORATION Long description of module's purpose
    """,

    'author': "MT CONSULTING SARL",
    'website': "http://www.mtconsulting.cm",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mass_mailing_sms'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group_leaders.xml',

        'views/leaders_apprenant.xml',
        'views/leaders_config.xml',
        'views/leaders_employe.xml',
        'views/leaders_concours_blanc.xml',
        'views/leaders_payement.xml',
        'views/leaders_bilan_journalier.xml',
        'views/leaders_sms.xml',
        'views/leaders_presence_personel.xml',
        'views/res_users.xml',
        'reports/report_recu.xml',
        'reports/reports_definition.xml',


        #WIZARD
        'wizard/wizard_resultats_concours_blanc.xml',

         'menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
