from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentPostingETMInvoice(models.Model):
    _name = 'payment.posting.etm.invoice'
    _description = "Payment posting ETM Invoices"

    invoice_no = fields.Char(string="Invoice Number", required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id')
    payment_posting_etm_id = fields.Many2one('payment.posting.etm', string="Payment Posting ETM")
    inv_enc = fields.Char("Inv Enc", required=True)
    mrn = fields.Char(string="MRN#", required=True)
    dos = fields.Date(string="DOS", required=True)
    etm_id = fields.Char("Id", required=True)
    invoice_availability = fields.Boolean(string="Invoice Availability",
                                          compute="_compute_invoice_availability", store=True)

    @api.depends("etm_id")
    def _compute_invoice_availability(self):
        """Check if etm_id exists in payment.posting.etm and set invoice_availability"""
        for rec in self:
            rec.invoice_availability = False
            if rec.etm_id:
                existing_etm_ids = self.env["payment.posting.etm"].search([('etm_id','=',rec.etm_id)])
                if existing_etm_ids:
                    rec.invoice_availability = True


    def action_view_related_etm(self):
        """Redirect to the related payment.posting.etm record"""
        payment_postings = self.env['payment.posting.etm'].search([('etm_id','=',self.etm_id)], limit=1)
        return {
            "type": "ir.actions.act_window",
            "name": "Related ETM",
            "res_model": "payment.posting.etm",
            "view_mode": "form",
            "res_id": payment_postings.id,
            "target": "current",
        }


