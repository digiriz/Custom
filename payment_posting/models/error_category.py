from odoo import models, fields

class ErrorCategory(models.Model):
    _name = 'error.category'
    _description = 'Error Category'

    name = fields.Char(string='Name', required=True)
