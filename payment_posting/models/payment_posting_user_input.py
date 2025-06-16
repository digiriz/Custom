from odoo import models, fields, api
from datetime import datetime

class PaymentPostingUserInput(models.Model):
    _name = 'payment.posting.user.input'
    _description = 'Payment Posting User Input'

    payment_posting_id = fields.Many2one('payment.posting', string="Payment Posting")
    check_number = fields.Char("Chk#")
    pg_number = fields.Char("PG#")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    check_amount = fields.Monetary(string="Check Amount", currency_field='company_currency_id', tracking=1)
    payer_name = fields.Char("Payer Name")