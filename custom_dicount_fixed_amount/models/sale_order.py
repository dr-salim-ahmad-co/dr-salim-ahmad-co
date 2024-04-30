from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderInheritDrSalim(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        for rec in self:

            if rec.partner_id.use_partner_credit_limit:
                if rec.partner_id.credit_limit < rec.amount_untaxed:
                    raise UserError(
                        _("Customer: '" + rec.partner_id.name + "' Limit Exceeded "))
                else:
                    super(SaleOrderInheritDrSalim, self).action_confirm()
            else:
                super(SaleOrderInheritDrSalim, self).action_confirm()


class SaleOrderLineInheritDrSalim(models.Model):
    _inherit = "sale.order.line"

    discount_fixed_amount = fields.Float(compute='_compute_disc_fixed_amt', string='Discount Fixed Amt', store=True, digits=(16, 4))

    @api.depends('price_reduce')
    def _compute_disc_fixed_amt(self):
        for rec in self:
            disc_amount = (rec.price_unit * rec.discount) / 100
            rec.discount_fixed_amount = round(disc_amount, 4)  # Explicit rounding to 4 decimal places
