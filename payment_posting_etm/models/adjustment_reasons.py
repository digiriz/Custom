from odoo import models, fields, api, _

class PaymentPostingETM(models.Model):
    _name = 'adjustment.reasons'

    name = fields.Char(string="Reason")