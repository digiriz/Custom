from odoo import models, fields

class LogInId(models.Model):
    _name = 'login.id'
    _description = 'Login ID'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)

