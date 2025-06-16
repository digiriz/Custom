from odoo import models, fields

class EhmProcessType(models.Model):
    _name = 'ehm.process.type'
    _description = 'Util. Type'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)