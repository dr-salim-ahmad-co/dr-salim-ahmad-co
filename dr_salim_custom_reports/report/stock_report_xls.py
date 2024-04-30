import datetime
from odoo import models


class StockReportXlsx(models.AbstractModel):
    _name = 'report.dr_salim_custom_reports.stock_report_xls'
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, products):
        print('data', data['stock'])
        sheet = workbook.add_worksheet('Stock')
        title = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_name': 'Georgia', 'font_size': 18})
        font_format = workbook.add_format({'font_name': 'Georgia', 'font_size': 11, 'bold': True, 'align': 'center', 'bg_color': '#fcba03'})
        bold = workbook.add_format({'bold': True, 'bg_color': '#fcba03', 'font_name': 'Georgia', 'font_size': 11})
        bg_color_format = workbook.add_format({'bg_color': '#fcba03'})

        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 20)

        col = 0
        row = 0

        row += 1
        sheet.merge_range(row, col, row + 1, col + 4, 'Stock Report', title)  # Merge range for the title
        row += 2
        # Merge cells for 'As On:' and date
        if isinstance(data['as_on'], datetime.date):
            as_on_text = 'As On: ' + data['as_on'].strftime('%d-%m-%Y')
        else:
            as_on_text = 'As On: ' + data['as_on']
        sheet.merge_range(row, col, row, col + 4, as_on_text, title)
        row += 1
        sheet.write(row, col, 'No', font_format)
        sheet.write(row, col + 1, 'Product', font_format)
        sheet.write(row, col + 2, 'Product Category', font_format)
        sheet.write(row, col + 3, 'Location', font_format)
        sheet.write(row, col + 4, 'Total Stock', font_format)
        serial_no = 1
        for rec in data['stock']:
            row += 1
            sheet.write(row, col, serial_no)
            serial_no += 1
            sheet.write(row, col + 1, rec['product_name'])
            sheet.write(row, col + 2, rec['category_name'])
            sheet.write(row, col + 3, rec['location'])
            sheet.write(row, col + 4, rec['total_stock'])

        row += 1

        sheet.merge_range(row, col, row, col + 3, 'Grand Total', bold)
        sheet.write(row, col + 4, sum(rec['total_stock'] for rec in data['stock']), bold)

