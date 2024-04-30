import datetime
import json
from collections import defaultdict

from odoo import models, fields, api


class SaleRegisterReportWizard(models.TransientModel):
    _name = "sale.register"
    _description = "Sale Register Report"

    customer = fields.Many2many('res.partner', string='Customer')
    city_ids = fields.Many2one('customer.city', string='Customer City')
    prod_cat_ids = fields.Many2one('product.category', string='Product Category')
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    show_sale_return = fields.Boolean(string="Show Sale Return")

    def action_sale_register_print_report(self):
        domain = []

        if self.customer:
            domain += [('partner_id', 'in', self.customer.ids)]
        if self.city_ids:
            domain += [('partner_id.cities.id', '=', self.city_ids.id)]
        if self.prod_cat_ids:
            domain += [('product_id.categ_id.id', '=', self.prod_cat_ids.id)]
        if self.from_date:
            domain += [('move_id.invoice_date', '>=', self.from_date)]
        if self.to_date:
            domain += [('move_id.invoice_date', '<=', self.to_date)]

        orders = self.env['account.move.line'].search(domain)
        product_summary = []

        for order in orders:
            # print('product name', order.product_id.name)
            if order.journal_id.name == 'Customer Invoices':
                product_summary.append({
                    'invoice_no': order.move_id.name,
                    'invoice_date': order.move_id.invoice_date,
                    'customer': order.partner_id.name,
                    'product_id': order.product_id.name,
                    'quantity': order.quantity,
                    'rate': order.price_unit,
                    'gross_amount': order.quantity * order.price_unit,
                    'total_discount': (order.quantity * order.price_unit) * order.discount / 100,
                    'total_tax': 0,  # You need to calculate tax here
                    'total_net_amount': order.price_subtotal,
                })

        data = {
            'products': product_summary,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }

        # Return report action
        return self.env.ref('dr_salim_custom_reports.action_sale_register_report').report_action(self, data=data)
