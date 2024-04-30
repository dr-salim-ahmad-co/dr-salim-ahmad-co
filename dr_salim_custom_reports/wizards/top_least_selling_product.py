import datetime
import json
from collections import defaultdict

from odoo import models, fields, api
from datetime import datetime, timedelta


class TopLeastProductReportWizard(models.TransientModel):
    _name = "top.selling"
    _description = "Top/Least Product Selling Report"

    customer = fields.Many2many('res.partner', string='Customer')
    city_ids = fields.Many2one('customer.city', string='Customer City')
    prod_cat_ids = fields.Many2one('product.category', string='Product Category')
    fiscal_position = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    period = fields.Char(string="Products Range")
    least_selling_product = fields.Boolean(string="Least Selling Product")
    date = fields.Selection([
        ('days', 'Last 10 Days'),
        ('curr_month', 'Current Month'),
        ('last_month', 'Last Month'),
        ('curr_year', 'Current Year'),
        ('last_year', 'Last Year'),
        ('select_period', 'Select Period'),
    ], string="Top Selling Product Of", default="days")

    def action_top_least_selling_product_print_report(self):
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

        today = fields.Date.today()
        if self.date == 'days':
            date_10_days_ago = today - timedelta(days=9)
            domain += [('move_id.invoice_date', '>=', date_10_days_ago), ('move_id.invoice_date', '<=', today)]
        elif self.date == 'curr_month':
            first_day_of_month = today.replace(day=1)
            domain += [('move_id.invoice_date', '>=', first_day_of_month), ('move_id.invoice_date', '<=', today)]
        elif self.date == 'last_month':
            first_day_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_of_last_month = first_day_of_last_month.replace(day=1) - timedelta(days=1)
            domain += [('move_id.invoice_date', '>=', first_day_of_last_month),
                       ('move_id.invoice_date', '<=', last_day_of_last_month)]
        elif self.date == 'curr_year':
            first_day_of_year = today.replace(month=1, day=1)
            domain += [('move_id.invoice_date', '>=', first_day_of_year), ('move_id.invoice_date', '<=', today)]
        elif self.date == 'last_year':
            first_day_of_last_year = today.replace(year=today.year - 1, month=1, day=1)
            last_day_of_last_year = first_day_of_last_year.replace(year=first_day_of_last_year.year + 1, month=1,
                                                                   day=1) - timedelta(days=1)
            domain += [('move_id.invoice_date', '>=', first_day_of_last_year),
                       ('move_id.invoice_date', '<=', last_day_of_last_year)]
        elif self.date == 'select_period':
            # Handle selection of custom period if needed
            pass

        orders = self.env['account.move.line'].search(domain)
        product_summary = {}

        for order in orders:
            if order.journal_id.name == 'Customer Invoices':
                product_id = order.product_id.id
                quantity = order.quantity

                if product_id in product_summary:
                    # If product already exists in summary, update its values
                    product_summary[product_id]['quantity'] += quantity
                else:
                    # Otherwise, add a new entry for the product
                    product_summary[product_id] = {
                        'product': order.product_id.name,
                        'quantity': quantity,
                        'uom': 'Units',
                    }

        # Convert product_summary dictionary to list of dictionaries
        customer_lines = list(product_summary.values())

        customer_lines.sort(key=lambda x: x['quantity'], reverse=not self.least_selling_product)

        data = {
            'products': customer_lines,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'least_selling': self.least_selling_product,
        }
        #
        # # Return report action
        return self.env.ref('dr_salim_custom_reports.action_top_least_selling_product_report').report_action(self, data=data)
