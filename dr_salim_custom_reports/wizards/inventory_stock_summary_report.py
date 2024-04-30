import datetime
import json
from collections import defaultdict

from odoo import models, fields, api


class StockSummaryReportWizard(models.TransientModel):
    _name = "ms.report.stocksum"
    _description = "Stock Summary Report"

    products_ids = fields.Many2many('product.product', string='Products')
    categ_ids = fields.Many2many('product.category', string='Categories')
    location_ids = fields.Many2many('stock.location', string='Locations')

    def action_stock_summary_report_print(self):
        domain = []

        # Construct domain based on filters
        if self.products_ids:
            domain.append(('product_id', 'in', self.products_ids.ids))
        if self.categ_ids:
            domain.append(('product_id.categ_id', 'in', self.categ_ids.ids))
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))

        # print('domain', domain)

        # Search for orders based on domain
        orders = self.env['stock.quant'].search(domain)
        # print('orders', orders)

        stock_list = []
        for order in orders:
            # print(order.quantity)

            vals = {
                'name': order.product_id.name,
                'category': order.product_categ_id.parent_id.parent_id.name,
                'location': order.location_id.location_id.name,
                'total_stock': order.quantity,
            }
            stock_list.append(vals)
        data = {
            'stock': stock_list,
            'as_on': datetime.date.today()
        }

        # print('data', data)
        return self.env.ref('dr_salim_custom_reports.stock_summary_report_xlsx').report_action(self, data=data)
