from odoo import models, fields, api

class EscalationType(models.Model):
    _name = 'escalation.type'
    _description = 'Escalation Type'

    name = fields.Char(string='Name', required=True)