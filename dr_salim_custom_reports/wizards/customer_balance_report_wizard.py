import datetime
import json

from odoo import models, fields, api
from collections import defaultdict


class CustomerBalanceReportWizard(models.TransientModel):
    _name = "customer.balance"
    _description = "Customer Balance Report"

    city_ids = fields.Many2many('customer.city', string='Customer City')
    ason_date = fields.Date(string="As On")

    def action_customer_balance_print_report(self):
        domain = []
        city_names = self.city_ids
        if self.city_ids:
            domain += [('partner_id.cities.id', 'in', city_names.ids)]
        ason_date = self.ason_date
        if ason_date:
            domain += [('invoice_date', '=', ason_date)]
        # print('domain', domain)

        # Use the search method to retrieve a record set
        orders = self.env['account.move'].search(domain)
        # print('orders', len(orders))

        # Create a dictionary to store aggregated data
        customer_data = defaultdict(lambda: {
            'balance': 0,
            'advance': 0,
            'contact': None,
            'city': None,
            'address': None,
            'country': None,
            'last_sale_date': None,
            'last_sale_amount': 0,
            'last_payment_date': None,
            'total_payment': 0,
            'invoices': [],  # Initialize invoices key
        })

        for order in orders:
            customer = order.partner_id.name

            # Update contact, city, address (if not already set)
            if not customer_data[customer]['contact']:
                customer_data[customer]['contact'] = order.partner_id.phone or order.partner_id.mobile
            if not customer_data[customer]['city']:
                customer_data[customer]['city'] = order.partner_id.cities.name
            if not customer_data[customer]['address']:
                customer_data[customer]['address'] = order.partner_id.street
            if not customer_data[customer]['country']:
                customer_data[customer]['country'] = order.partner_id.country_id.name

            # Update last sale date
            if not customer_data[customer]['last_sale_date'] or order.invoice_date > customer_data[customer][
                'last_sale_date']:
                customer_data[customer]['last_sale_date'] = order.invoice_date
            customer_data[customer]['last_sale_amount'] += order.amount_untaxed_signed

            # Calculate balance and advance (only once per customer)
            total_due = order.partner_id.total_due
            if total_due >= 0:
                customer_data[customer]['balance'] = total_due
            else:
                customer_data[customer]['advance'] = abs(total_due)

            # Fetch payments for each invoice
            # payments = []
            payment_widget = order.invoice_payments_widget
            if payment_widget and payment_widget.get('content'):
                for payment in payment_widget['content']:
                    # print('payment', payment['amount'])
                    payment_date = fields.Date.from_string(payment.get('date'))
                    payment_amount = payment.get('amount')
                    # print('chat gpt payment', payment_amount)
                    if payment_date and payment_amount:
                        customer_data[customer]['last_payment_date'] = payment_date
                        customer_data[customer]['total_payment'] += payment_amount

        orders_list = [{'customer': customer, **data} for customer, data in customer_data.items()]
        # print('order', orders_list)

        data = {
            'orders': orders_list,
            'ason_date': ason_date,
        }

        return self.env.ref('dr_salim_custom_reports.action_customer_balance_rep').report_action(self, data=data)
