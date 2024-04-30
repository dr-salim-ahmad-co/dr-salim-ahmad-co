import datetime
import json
from collections import defaultdict
from datetime import timedelta, datetime, time
from odoo import models, fields, api


class SaleSummaryReportWizard(models.TransientModel):
    _name = "sale.summary"
    _description = "Sale Summary Report"

    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")

    def action_sae_summary_print_report(self):
        domain = []
        from_date = self.from_date
        to_date = self.to_date

        if from_date and to_date:
            from_date_dt = datetime.combine(from_date, time.min)

            to_date_dt = datetime.combine(to_date, time.max)

            domain += [('date_order', '>=', from_date_dt.date()), ('date_order', '<=', to_date_dt.date())]

        orders = self.env['sale.order'].search(domain)

        orders_by_date = defaultdict(int)
        amount_by_date = defaultdict(float)
        orders_list = []

        for order in orders:
            if order.type_name == 'Sales Order' and order.state == 'sale':
                order_date = order.date_order.date()
                orders_by_date[order_date] += 1
                amount_by_date[order_date] += order.amount_total

        date_range = [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]

        for date in date_range:
            vals = {
                'date': date,
                'total_orders': orders_by_date.get(date, 0),
                'total_amount': amount_by_date.get(date, 0.0),
            }
            orders_list.append(vals)

        data = {
            'orders': orders_list,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }

        return self.env.ref('dr_salim_custom_reports.action_sale_report_report').report_action(self, data=data)
