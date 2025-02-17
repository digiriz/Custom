from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentPostingInvoice(models.Model):
    _name = 'payment.posting.invoice'

    invoice_no = fields.Char(string="Invoice Number")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id')
    payment_posting_id = fields.Many2one('payment.posting', string="Payment Posting")
