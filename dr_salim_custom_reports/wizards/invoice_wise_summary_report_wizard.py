import datetime
import json
from collections import defaultdict

from odoo import models, fields, api


class InvoiceWiseSummaryReportWizard(models.TransientModel):
    _name = "invoice.wise.summary"
    _description = "Invoice Wise Summary Report"

    customer = fields.Many2many('res.partner', string='Customer')
    city_ids = fields.Many2one('customer.city', string='Customer City')
    prod_cat_ids = fields.Many2one('product.category', string='Product Category')
    fiscal_position = fields.Many2one('account.fiscal.position', string='Fiscal Position')
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    orderbyamount = fields.Boolean(string="Amount")
    orderbyqty = fields.Boolean(string="Quantity", default="True")

    def action_invoice_wise_summary_print_report(self):
        domain = []

        if self.customer:
            domain += [('partner_id', 'in', self.customer.ids)]
        if self.city_ids:
            domain += [('partner_id.cities.id', '=', self.city_ids.id)]
        if self.prod_cat_ids:
            domain += [('product_id.categ_id.id', '=', self.prod_cat_ids.id)]
        if self.fiscal_position:
            domain += [('partner_id.property_account_position_id.id', '=', self.fiscal_position.id)]
        if self.from_date:
            domain += [('move_id.invoice_date', '>=', self.from_date)]
        if self.to_date:
            domain += [('move_id.invoice_date', '<=', self.to_date)]

        orders = self.env['account.move.line'].search(domain)
        invoice_summary = defaultdict(lambda: {'mrp': 0, 'gross_amount': 0, 'discount': 0})

        for order in orders:
            if order.journal_id.name == 'Customer Invoices':
                invoice_key = (order.move_id.name, order.move_id.invoice_date, order.partner_id.name, order.partner_id.x_cnic, order.partner_id.property_account_position_id.name)
                invoice_summary[invoice_key]['mrp'] += order.quantity * order.price_unit
                invoice_summary[invoice_key]['gross_amount'] += order.price_subtotal
                invoice_summary[invoice_key]['discount'] += (order.quantity * order.price_unit) * order.discount / 100

        product_summary = [{
            'invoice_no': invoice[0],
            'invoice_date': invoice[1],
            'customer': invoice[2],
            'cnic': invoice[3],
            'fiscal': invoice[4],
            'mrp': summary['mrp'],
            'gross_amount': summary['gross_amount'],
            'total_discount': summary['discount'],  # You need to calculate discount here
            'total_tax': 0,  # You need to calculate tax here
        } for invoice, summary in invoice_summary.items()]

        data = {
            'products': product_summary,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }

        # # Return report action
        return self.env.ref('dr_salim_custom_reports.action_invoice_wise_summary_report').report_action(self, data=data)
