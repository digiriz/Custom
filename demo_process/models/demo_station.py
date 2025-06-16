from odoo import models, fields

class DemoStation(models.Model):
    _name = 'demo.station'
    _description = 'Demo Station'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)
