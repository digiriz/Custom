from odoo import models, fields

class DemoProcessReprocessingStatus(models.Model):
    _name = 'demo.process.reprocessing.status'
    _description = 'DemoProcess Reprocessing Status'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)
