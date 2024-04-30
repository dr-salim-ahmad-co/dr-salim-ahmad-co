{
    'name': 'Custom Discount Fixed Amount',
    'version': '16.0',
    'category': 'Sales',
    'summary': """Dr salim odoo16 sales Fixed Discounted Amount""",
    'description': """ Dr salim odoo16 sales Fixed Discounted Amount""",
    'author': 'Paz Technologies',
    'company': 'Paz Technologies',
    'maintainer': 'Paz Technologies',
    'website': "",
    'depends': ['base', 'base_setup', 'account', 'sale', 'product', 'stock'],
    'data': [
        'views/sale_order.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
