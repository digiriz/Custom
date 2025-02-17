from odoo import models, fields

class CustomTags(models.Model):
    _name = 'custom.tags'
    _description = 'Tags'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)