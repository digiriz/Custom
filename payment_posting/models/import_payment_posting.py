from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ImportPaymentPosting(models.Model):
    _name = 'import.payment.posting'
    _description = 'Import Payment Posting'
    _rec_name = 'edm_batch'
    _inherit = ["mail.activity.mixin", "mail.thread"]


    edm_batch = fields.Char(string='EDM Batch', required=True)
    status = fields.Char(string="Status")
    stage_id = fields.Many2one('user.status', 'User Status (Old)')
    images = fields.Char(string='Images')
    docs = fields.Char(string='Docs')
    def_doc_type = fields.Char(string='Def Doc Type')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id')
    descriptions = fields.Char(string='Descriptions')
    division_id = fields.Many2one('division.master', string="Division", tracking=1)
    deposit_date = fields.Date(string="Deposit Date")
    created = fields.Date('Created')
    import_status = fields.Selection([('not_imported', 'Not Imported'), ('imported', 'Imported')], default='imported', string="Import Status")
    last_edited_by = fields.Char('Last Edited By')
    tag_ids = fields.Many2many('custom.tags', string='Tags')
    payment_posting_status_id = fields.Many2one('user.status', string="PStatus", tracking=1, copy=False)
    type = fields.Selection([('edm_process', 'EDM Process'),('ecom_process', 'ECOM Process'),('835_push', '835 Push'),], string="Process Type", copy=False)
    grp = fields.Char(string="GRP")
    run = fields.Char(string="RUN")
    ecom_type = fields.Char(string="Type")
    init_s = fields.Char(string="Inits")
    bk_dep_dt = fields.Date(string="Bk Dep Dt")
    eob_s = fields.Char(string="EOBs")
    check_s = fields.Char(string="Check(s)", tracking=1)
    not_posted = fields.Integer(string="NotPosted")
    not_posted_amount = fields.Monetary(string="NotPosted$", currency_field='company_currency_id', tracking=1)
    offset_amount = fields.Monetary(string="Offset$", currency_field='company_currency_id', tracking=1)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], string='Priority', compute="_compute_priority", store=True, index=True, default='0')

    @api.depends('division_id.priority_date')
    def _compute_priority(self):
        for record in self:
            if record.division_id.priority_date:
                today = fields.Date.context_today(self)
                days_difference = (record.division_id.priority_date - today).days
                if days_difference <= 2:
                    record.priority = '1'
                else:
                    record.priority = '0'
            else:
                record.priority = '0'

    @api.model
    def create(self, vals):
        res = super(ImportPaymentPosting, self).create(vals)
        if 'edm_batch' in vals:
            edm_batch = vals.get('edm_batch')
            type = vals.get('type')

            if type is None:
                raise UserError("Please add process type")
            payment_posting_record = self.env['payment.posting'].search([('edm_batch', '=', edm_batch),('type','=',type)], limit=1)
            if payment_posting_record:
                res.import_status = 'not_imported'
                res.payment_posting_status_id = payment_posting_record.status_id.id
            else:
                res.create_payment_posting()
        else:
            raise UserError("Please add edm batch")
        return res

    def action_move_to_allocation(self):
        for record in self:
            record.create_payment_posting()

    def create_payment_posting(self):
        context = self.env.context
        if context.get('edm_payment_posting'):
            payment_posting_obj = self.env['payment.posting']
            payment_posting_obj.create({
                'edm_batch': self.edm_batch,
                'type': self.type,
                'status': self.status,
                'images': self.images,
                'docs': self.docs,
                'def_doc_type': self.def_doc_type,
                'created': self.created,
                'last_edited_by': self.last_edited_by,
                'amount': self.amount,
                'descriptions': self.descriptions,
                'division_id': self.division_id.id,
                'deposit_date': self.deposit_date,
            })

            self.import_status = 'imported'
        elif context.get('ecom_payment_posting'):
            payment_posting_obj = self.env['payment.posting']
            payment_posting_obj.create({
                'grp': self.grp,
                'division_id': self.division_id.id,
                'run': self.run,
                'type': self.type,
                'edm_batch': self.edm_batch,
                'status': self.status,
                'init_s': self.init_s,
                'bk_dep_dt': self.bk_dep_dt,
                'ecom_type': self.ecom_type,
                'created': self.created,
                'descriptions': self.descriptions,
                'eob_s': self.eob_s,
                'check_s': self.check_s,
                'not_posted': self.not_posted,
                'not_posted_amount': self.not_posted_amount,
                'offset_amount': self.offset_amount,
            })

            self.import_status = 'imported'



