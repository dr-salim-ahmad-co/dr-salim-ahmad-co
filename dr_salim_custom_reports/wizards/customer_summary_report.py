from odoo import models, fields, api


class CustomerSummaryReportWizard(models.TransientModel):
    _name = "customer.summary"
    _description = "Customer Summary Report"

    customer = fields.Many2many('res.partner', string='Customer')
    city_ids = fields.Many2one('customer.city', string='Customer City')
    prod_cat_ids = fields.Many2one('product.category', string='Product Category')
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    orderbyamount = fields.Boolean(string="Amount")
    orderbyqty = fields.Boolean(string="Quantity" , default="True")

    display_name = fields.Char(compute='_compute_display_name', string='Display Name', store=True)

    @api.depends('customer', 'city_ids', 'from_date', 'to_date', 'orderbyamount', 'orderbyqty')
    def _compute_display_name(self):
        for record in self:
            record.display_name = 'Custom Summary Report'

    def action_customer_summary_print_report(self):
        domain = []

        # Construct domain based on filters
        if self.customer:
            domain += [('partner_id', 'in', self.customer.ids)]
        if self.city_ids:
            domain += [('partner_id.cities.id', '=', self.city_ids.id)]
        if self.prod_cat_ids:
            domain += [('invoice_line_ids.product_id.categ_id.id', '=', self.prod_cat_ids.id)]
        if self.from_date:
            domain += [('invoice_date', '>=', self.from_date)]
        if self.to_date:
            domain += [('invoice_date', '<=', self.to_date)]

        print('domain', domain)

        # Search for orders based on domain
        orders = self.env['account.move'].search(domain)
        print('orders', len(orders))

        # Initialize dictionary to store calculated values for each customer
        customer_totals = {}

        # Loop through each order and calculate totals for each customer
        for order in orders:
            customer = order.partner_id
            if customer not in customer_totals:
                # Initialize totals for the customer
                customer_totals[customer] = {
                    'total_quantity': 0,
                    'total_amount': 0,
                    'total_discount': 0,
                    'total_tax': 0,
                    'total_net_amount': 0,
                    'tax_nature': set(),  # Initialize as a set
                }

            # Calculate totals for the current order
            total_quantity = sum(
                line.quantity if self.orderbyqty else line.price_subtotal for line in order.invoice_line_ids)
            total_amount = order.amount_untaxed_signed
            total_discount = sum(line.discount for line in order.invoice_line_ids)
            total_tax = order.amount_tax_signed
            total_net_amount = order.amount_total_signed
            tax_nature = [tax.name for tax in order.invoice_line_ids.tax_ids]

            # Update customer totals
            customer_totals[customer]['total_quantity'] += total_quantity
            customer_totals[customer]['total_amount'] += total_amount
            customer_totals[customer]['total_discount'] += total_discount
            customer_totals[customer]['total_tax'] += total_tax
            customer_totals[customer]['total_net_amount'] += total_net_amount
            customer_totals[customer]['tax_nature'].update(tax_nature)  # Add tax nature to the set

        # Create a list of dictionaries to represent each customer with their calculated values
        customer_lines = []
        for customer, totals in customer_totals.items():
            # Convert set to string for tax nature
            tax_nature_str = ', '.join(totals['tax_nature'])

            customer_lines.append({
                'customer': customer.name,
                'total_quantity': totals['total_quantity'],
                'total_amount': totals['total_amount'],
                'total_discount': totals['total_discount'],
                'total_tax': totals['total_tax'],
                'total_net_amount': totals['total_net_amount'],
                'tax_nature': tax_nature_str,
            })

        data = {
            'customers': customer_lines,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }

        # Return report action
        return self.env.ref('dr_salim_custom_reports.action_customer_summary_report').report_action(self, data=data)


