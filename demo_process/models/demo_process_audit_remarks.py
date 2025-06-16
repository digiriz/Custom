from odoo import models, fields

class DemoProcessUserRemarks(models.Model):
    _name = 'demo.process.user.remarks'
    _description = 'Demo Process User Remarks'

    name = fields.Char(string='Name', required=True)
