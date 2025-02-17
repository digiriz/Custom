from odoo import models, fields, api

class SSStatus(models.Model):
    _name = 'ss.status'
    _description = 'SS Status'

    name = fields.Char(string='Name', required=True)