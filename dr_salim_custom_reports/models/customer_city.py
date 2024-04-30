import datetime

from odoo import models, fields, api


class CustomerCityModel(models.Model):
    _name = "customer.city"
    _description = "Customer City Model"

    name = fields.Char(string='Name')
