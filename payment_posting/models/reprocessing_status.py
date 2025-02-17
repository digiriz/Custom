from odoo import models, fields

class ReprocessingStatus(models.Model):
    _name = 'reprocessing.status'
    _description = 'Reprocessing Status'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)
