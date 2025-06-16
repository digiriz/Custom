from odoo import models, fields

class DemoProcessErrorCategory(models.Model):
    _name = 'demo.process.error.category'
    _description = 'DemoProcess Error Category'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)
