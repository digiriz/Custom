from odoo import models, fields, api

class QStatus(models.Model):
    _name = 'q.status'
    _description = 'Q Status'

    name = fields.Char(string='Name', required=True)
    is_open_status = fields.Boolean(string="Is Open status")