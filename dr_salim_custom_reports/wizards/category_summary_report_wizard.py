import datetime
import json
from collections import defaultdict

from odoo import models, fields, api


class CategorySummaryReportWizard(models.TransientModel):
    _name = "category.summary"
    _description = "Category Summary Report"

    customer = fields.Many2many('res.partner', string='Customer')
    city_ids = fields.Many2one('customer.city', string='Customer City')
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    orderbyamount = fields.Boolean(string="Amount")
    orderbyqty = fields.Boolean(string="Quantity", default="True")

    def action_category_summary_print_report(self):
        domain = []

        if self.customer:
            domain += [('partner_id', 'in', self.customer.ids)]
        if self.city_ids:
            domain += [('partner_id.cities.id', '=', self.city_ids.id)]
        if self.from_date:
            domain += [('move_id.invoice_date', '>=', self.from_date)]
        if self.to_date:
            domain += [('move_id.invoice_date', '<=', self.to_date)]

        orders = self.env['account.move.line'].search(domain)
        product_summary = {}

        for order in orders:
            # print('category name', order.product_id.categ_id.name)
            if order.journal_id.name == 'Customer Invoices':
                product_id = order.product_id.categ_id.id
                quantity = order.quantity if self.orderbyqty else order.price_subtotal
                gross_amount = order.quantity * order.price_unit
                total_discount = (order.quantity * order.price_unit) * order.discount / 100
                total_tax = 0  # You need to calculate tax here
                total_net_amount = order.price_subtotal

                if product_id in product_summary:
                    # If product already exists in summary, update its values
                    product_summary[product_id]['quantity'] += quantity
                    product_summary[product_id]['gross_amount'] += gross_amount
                    product_summary[product_id]['total_discount'] += total_discount
                    product_summary[product_id]['total_tax'] += total_tax
                    product_summary[product_id]['total_net_amount'] += total_net_amount
                else:
                    # Otherwise, add a new entry for the product
                    product_summary[product_id] = {
                        'product': order.product_id.categ_id.parent_id.name,
                        'product1': order.product_id.categ_id.name,
                        'quantity': quantity,
                        'gross_amount': gross_amount,
                        'total_discount': total_discount,
                        'total_tax': total_tax,
                        'total_net_amount': total_net_amount,
                    }

        # Convert product_summary dictionary to list of dictionaries
        customer_lines = list(product_summary.values())

        data = {
            'products': customer_lines,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }

        # Return report action
        return self.env.ref('dr_salim_custom_reports.action_category_summary_report').report_action(self, data=data)
