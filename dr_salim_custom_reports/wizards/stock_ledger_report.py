import datetime
import json
from collections import defaultdict

from odoo import models, fields, api


class StockLedgerReportWizard(models.TransientModel):
    _name = "report.stockledger"
    _description = "Stock Ledger Report"

    products_ids = fields.Many2many('product.product', string='Products')
    location_ids = fields.Many2one('stock.location', string='Locations', domain="[('location_id', '=', 1)]")
    from_date = fields.Date(string="From", default=fields.Date.today())
    to_date = fields.Date(string="To", default=fields.Date.today())

    display_name = fields.Char(compute='_compute_display_name', string='Display Name', store=True)

    @api.depends('location_ids', 'products_ids', 'from_date', 'to_date')
    def _compute_display_name(self):
        for record in self:
            record.display_name = 'Stock Ledger Report'

    def action_stock_ledger_report_print(self):
        # your report generation logic here
        pass

        # # Construct domain based on filters
        # if self.products_ids:
        #     domain.append(('product_id', 'in', self.products_ids.ids))
        # if self.categ_ids:
        #     domain.append(('product_id.categ_id', 'in', self.categ_ids.ids))
        # if self.location_ids:
        #     domain.append(('location_id', 'in', self.location_ids.ids))
        #
        # # print('domain', domain)
        #
        # # Search for orders based on domain
        # orders = self.env['stock.quant'].search(domain)
        # # print('orders', orders)
        #
        # stock_list = []
        # for order in orders:
        #     # print(order.quantity)
        #
        #     vals = {
        #         'name': order.product_id.name,
        #         'category': order.product_categ_id.parent_id.parent_id.name,
        #         'location': order.location_id.location_id.name,
        #         'total_stock': order.quantity,
        #     }
        #     stock_list.append(vals)
        # data = {
        #     'stock': stock_list,
        #     'as_on': datetime.date.today()
        # }
        #
        # # print('data', data)
        # return self.env.ref('dr_salim_custom_reports.stock_summary_report_xlsx').report_action(self, data=data)
