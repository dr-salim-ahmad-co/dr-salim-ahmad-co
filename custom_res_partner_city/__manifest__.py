{
    'name': 'Custom Res Partner City',
    'version': '16.0',
    'category': 'Sales',
    'summary': """Dr salim odoo16 Custom Res Partner City""",
    'description': """ Dr salim odoo16 Custom Res Partner City""",
    'author': 'Paz Technologies',
    'company': 'Paz Technologies',
    'maintainer': 'Paz Technologies',
    'website': "",
    'depends': ['base', 'base_setup', 'account', 'sale', 'product', 'stock', 'dr_salim_custom_reports'],
    'data': [
        'views/res_partner.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
