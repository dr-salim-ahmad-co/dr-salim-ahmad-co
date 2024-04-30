import datetime
import json
from collections import defaultdict

from odoo import models, fields, api


class StockReportWizard(models.TransientModel):
    _name = "ms.stock.report"
    _description = "Stock Report"

    products_ids = fields.Many2many('product.product', string='Products')
    categ_ids = fields.Many2many('product.category', string='Categories')
    location_ids = fields.Many2many('stock.location', string='Locations')

    def action_stock_report_print(self):
        domain = []

        # Construct domain based on filters
        if self.products_ids:
            domain.append(('product_id', 'in', self.products_ids.ids))
        if self.categ_ids:
            domain.append(('product_id.categ_id', 'in', self.categ_ids.ids))
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))

        # Search for orders based on domain
        orders = self.env['stock.quant'].search(domain)

        # Create a defaultdict to store combined data for each location
        stock_dict = defaultdict(lambda: {'total_stock': 0, 'product_data': {}})

        for order in orders:
            location_name = order.location_id.complete_name
            product_name = order.product_id.name
            category_name = order.product_id.categ_id.parent_id.parent_id.name

            stock_dict[location_name]['total_stock'] += order.quantity
            product_data = stock_dict[location_name]['product_data'].setdefault((product_name, category_name), 0)
            stock_dict[location_name]['product_data'][(product_name, category_name)] = product_data + order.quantity

        # Convert the defaultdict to a list of dictionaries
        stock_list = []
        for location, data in stock_dict.items():
            for (product_name, category_name), total_quantity in data['product_data'].items():
                stock_list.append({
                    'location': location,
                    'product_name': product_name,
                    'category_name': category_name,
                    'total_stock': total_quantity
                })

        # Prepare data for the report
        data = {
            'stock': stock_list,
            'as_on': datetime.date.today()
        }

        return self.env.ref('dr_salim_custom_reports.stock_report_xlsx').report_action(self, data=data)
