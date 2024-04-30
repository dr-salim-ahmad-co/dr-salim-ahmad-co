import datetime

from odoo import models, fields, api
from collections import defaultdict


class RegionalOutstandingReportWizard(models.TransientModel):
    _name = "regional.outstanding"
    _description = "Regional Outstanding Report"

    city_ids = fields.Many2many('customer.city', string='Customer City')
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")

    def action_regional_print_report(self):
        domain = []
        domain1 = []
        domain2 = []
        city_names = self.city_ids
        if self.city_ids:
            domain += [('partner_id.cities.id', 'in', city_names.ids)]
            domain1 += [('partner_id.cities.id', 'in', city_names.ids)]
            domain2 += [('partner_id.cities.id', 'in', city_names.ids)]
        from_date = self.from_date
        if from_date:
            domain += [('invoice_date', '>=', from_date)]
            domain1 += [('date', '>=', from_date)]
            domain2 += [('move_id.invoice_date', '>=', from_date)]

        to_date = self.to_date
        if to_date:
            domain += [('invoice_date', '<=', to_date)]
            domain1 += [('date', '<=', to_date)]
            domain2 += [('move_id.invoice_date', '<=', to_date)]

        # Use the search method to retrieve a record set
        orders = self.env['account.move'].search(domain)
        # print('order', len(orders))
        city_total_due = defaultdict(float)
        city_invoices_totals = defaultdict(float)
        refund_total_amount_invoices = defaultdict(float)
        total_invoice_payments = defaultdict(float)
        shipping_charges = defaultdict(float)
        insurance_charges = defaultdict(float)
        courier_charges = defaultdict(float)
        orderss = []
        # Calculate total amounts per city for total due and invoices totals
        for order in orders:
            if order.journal_id.name == 'Customer Invoices' and order.state == 'posted':
                city_name = order.partner_id.cities.name
                total_amount = order.amount_residual_signed
                city_total_due[city_name] += total_amount
                total_amount_invoices = order.amount_total_signed
                city_invoices_totals[city_name] += total_amount_invoices

        for order in orders.filtered(lambda r: r.move_type == 'out_refund'):
            city_name = order.partner_id.cities.name  # Update city_name within the loop
            total_refund = order.amount_total_signed
            refund_total_amount_invoices[city_name] += total_refund

        for move in orders:
            city_name = move.partner_id.cities.name
            payment_widget = move.invoice_payments_widget
            if payment_widget and payment_widget.get('content'):
                # print('payment widget', payment_widget.get('content'), 'payment widget2', payment_widget)
                for payment in payment_widget['content']:
                    payment_amount = payment['amount']
                    # print('payment amount', payment_amount)
                    total_invoice_payments[city_name] += payment_amount
                    # print('payment amount', total_invoice_payments[city_name])

        invoice_lines = self.env['account.move.line'].search(domain2)
        for line in invoice_lines:
            city_name = line.partner_id.cities.name
            if line.product_id.name == 'Shipping Charges':
                shipping_amount = line.price_subtotal
                shipping_charges[city_name] += shipping_amount
            elif line.product_id.name == 'Insurance Charges':
                insurance_amount = line.price_subtotal
                insurance_charges[city_name] += insurance_amount
            # elif line.account_id.name == 'Courier Charges' and line.journal_id.name == 'Miscellaneous Operations':
            #     print('journal_id', line.journal_id.name)
            #     courier = line.credit
            #     courier_charges[city_name] += courier
            # else:
            #     print('nothing matched.')

        journal_entries = self.env['account.move.line'].search(domain1)
        for line in journal_entries:
            city_name = line.partner_id.cities.name
            if line.journal_id.name == 'Miscellaneous Operations':
                courier = line.credit
                courier_charges[city_name] += courier

        print('shipping', courier_charges[city_name])
        # print('insurance', insurance_charges[city_name])
        orders_list = []
        for city_name, total_amount in city_total_due.items():
            total_balance = city_total_due[city_name] + city_invoices_totals[city_name] + refund_total_amount_invoices[
                city_name] - total_invoice_payments[city_name] + shipping_charges[city_name] + insurance_charges[city_name] + courier_charges[city_name]
            orders_list.append({
                'city': city_name,
                'total_due': city_total_due[city_name],
                'city_invoices_totals': city_invoices_totals[city_name],
                'refund_total_amount_invoices': refund_total_amount_invoices[city_name],
                'total_invoice_payments': total_invoice_payments[city_name],
                'total_balance': total_balance,
                'shipping_charges': shipping_charges[city_name],
                'insurance_charges': insurance_charges[city_name],
                'courier_charges': courier_charges[city_name],
            })

        # print('orders_list', orders_list)

        data = {
            'orders': orders_list,
            'from_date': from_date,
            'to_date': to_date,
        }

        return self.env.ref('dr_salim_custom_reports.action_regional_outstanding_report').report_action(self, data=data)
