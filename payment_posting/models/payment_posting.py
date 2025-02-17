from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import random
from datetime import datetime, date
from markupsafe import Markup

class PaymentPosting(models.Model):
    _name = 'payment.posting'
    _description = 'Payment Posting'
    _rec_name = 'edm_batch'
    _inherit = ["mail.activity.mixin", "mail.thread"]

    edm_batch = fields.Char(string='EDM Batch', tracking=1)
    status = fields.Char(string="Status")
    stage_id = fields.Many2one('user.status','User Status (Old)')
    images = fields.Char(string='Images')
    docs = fields.Char(string='Docs')
    def_doc_type = fields.Char(string='Def Doc Type')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id', tracking=1)
    descriptions = fields.Char(string='Descriptions')
    division_id = fields.Many2one('division.master', string="Division", tracking=1)
    deposit_date = fields.Date(string="Deposit Date", tracking=1)
    assigned_to = fields.Many2one('res.users','Assigned To', copy=False)
    assigned_date = fields.Date(string="Assigned Date", copy=False)
    bar_batch = fields.Char(string="Bar Batch#", copy=False)
    posted_amount = fields.Monetary(string="Posted Amount", currency_field='company_currency_id', copy=False)
    pending_amount = fields.Monetary(string="Pending Amount", currency_field='company_currency_id', compute="_compute_pending_amount", copy=False)
    transaction = fields.Integer(string="Transaction", copy=False)
    status_id = fields.Many2one('user.status', string="PStatus", tracking=1, default=lambda self: self._default_stage_id(), copy=False)
    remarks_id = fields.Many2one('user.remarks', string="Remarks", tracking=1, copy=False)
    posted_date = fields.Date(string="Posted Date", copy=False)
    posted_date_time = fields.Datetime(string="Posted Date Time", copy=False)
    clarification_sent_date = fields.Date(string="Clarification Sent Date", copy=False)
    clarification_received_date = fields.Date(string="Clarification Received Date", copy=False)
    batch_closed_date = fields.Date(string="Batch Closed Date", copy=False)
    tat = fields.Float("TAT", copy=False, compute="_compute_tat")
    auditor_user_id = fields.Many2one('res.users', string="Auditor Assigned To", copy=False)
    audited_date = fields.Date('Audited Assigned Date', copy=False)
    of_transactions = fields.Integer(string="No Of Invoices", copy=False)
    audit_id = fields.Many2one('audit.status', string="AStatus", tracking=1, default=lambda self: self._default_auditor_stage_id(), copy=False)
    auditor_status = fields.Selection(
        [("error", "Error"), ("no_error", "No Error")],
        string="Error Status", copy=False
    )
    c_audit_date = fields.Date(string="CAdudit Date", copy=False)
    error = fields.Selection([('error','Error'),('no_error','No Error')], copy=False)
    error_count = fields.Integer(string="Error Count", copy=False)
    incorrect = fields.Integer(string="Incorrect", copy=False)
    missed = fields.Integer(string="Missed", copy=False)
    navigation = fields.Integer(string="Navigation", copy=False)
    error_comments = fields.Text(string="Error Comments", copy=False)
    comments = fields.Text(string="Comments", copy=False)
    fixing_date = fields.Date(string="Fixing Date", copy=False)
    updated_bar_batch = fields.Char(string="Updated Bar Batch#", copy=False)
    error_status = fields.Selection(
        [("fixed", "Fixed"), ("un_fixed", "Un Fixed")],
        string="Fixed / Unfixed", copy=False
    )
    created = fields.Date('Created', tracking=1)
    last_edited_by = fields.Char('Last Edited By')
    reprocessing_id = fields.Many2one('reprocessing.status', 'RStatus', copy=False)
    id_duplicate = fields.Boolean('Is Duplicate', readonly=True, copy=False)
    recon_date = fields.Date(string="RECON Date")
    payment_posting_id = fields.Many2one('payment.posting', string="Reference", readonly=True, tracking=1, copy=False)
    duplicate_status_id = fields.Many2one('user.status','Duplicate Status', related="payment_posting_id.status_id", store=True, copy=False)
    payment_posting_invoice_ids = fields.One2many('payment.posting.invoice', 'payment_posting_id', string="Payment Invoice Items", copy=False)
    active = fields.Boolean(string='Active', default=True, copy=False)
    total_invoice_amount = fields.Monetary(string="Total Invoice Amount", compute="_compute_invoice_total_amount", currency_field='company_currency_id', copy=False)
    total_invoice_pending_amount = fields.Monetary(string="Pending Invoice Amount", compute="_compute_invoice_pending_amount", currency_field='company_currency_id', copy=False)
    ref_count = fields.Integer(string="Reference Count", compute="_compute_ref_count")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], string='Priority', compute="_compute_priority",store=True, index=True, default='0')
    priority_compute = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], string='Priority (Compute - Dont use)', compute="_compute_priority", index=True, default='0')
    tag_ids = fields.Many2many('custom.tags', string='Tags')
    type = fields.Selection([('edm_process', 'EDM Process'),('ecom_process', 'ECOM Process'),('835_push', '835 Push'),], string="Process Type", copy=False)
    ecom_type = fields.Char(string="Type")
    grp = fields.Char(string="GRP")
    run = fields.Char(string="RUN")
    init_s = fields.Char(string="Inits")
    bk_dep_dt = fields.Date(string="Bk Dep Dt")
    eob_s = fields.Char(string="EOBs")
    check_s = fields.Char(string="Check(s)", tracking=1)
    not_posted = fields.Integer(string="NotPosted")
    not_posted_amount = fields.Monetary(string="NotPosted$", currency_field='company_currency_id', tracking=1)
    offset_amount = fields.Monetary(string="Offset$", currency_field='company_currency_id', tracking=1)
    exchange = fields.Char(string="Exchange")
    check_eft_number = fields.Char(string="Check/EFT Number")
    load_date = fields.Date(string="Load Date")
    tax_id = fields.Char(string="Tax ID")
    offset = fields.Char(string="Offset")
    clm = fields.Char(string="CLM")
    pay_m = fields.Char(string="PayM")
    tx = fields.Char(string="Tx")
    remit_adv = fields.Char(string="Remit Adv#")
    payer_identity = fields.Char(string="Payer ID")
    payer_nm = fields.Char(string="Payer Number")
    pro_date = fields.Date(string="Proc Date")
    error_category_id = fields.Many2one('error.category', string='Error Category')
    current_status = fields.Char(string="Current Status", tracking=1)
    request = fields.Char(string="Request", tracking=1)
    approximate_invoice_count = fields.Integer(string="Approximate Invoice Count#", tracking=1)
    mail_date = fields.Date(string="Mail Date")
    query_status = fields.Char(string="Query Status")
    query_bar_batch = fields.Char(string="Query Bar Batch#")
    escalation_type_id = fields.Many2one('escalation.type', string='Escalation Type')
    clarification_details = fields.Char(string="Clarification Details")
    poster_login = fields.Char(string="Poster Login")
    query_assigned_date = fields.Date(string="Query ASSIGN DATE", copy=False)
    ss_status_id = fields.Many2one('ss.status', string="SS Status")
    q_status_id = fields.Many2one('q.status', string="Q Status")
    posted_date_ss = fields.Date(string="Posted Date(SS)", copy=False)
    response_date = fields.Date(string="Response Date", copy=False)
    closed_date = fields.Date(string="Query Closed Date", copy=False)
    gottlieb_comments = fields.Char(string="Gottlieb Comments")
    ahs_comments = fields.Char(string="AHS Comments")
    of_records = fields.Char(string="#of Record")
    remarks = fields.Char(string="Remarks")
    pg = fields.Char(string="PG#")
    production_timing_ids = fields.One2many('production.timing', 'payment_posting_id', string="Production Timing")
    total_work_hours = fields.Float(string="Work Hours")
    timer_start = fields.Boolean()
    auditor_invoice_count = fields.Integer('Auditor Invoice Count')
    client_audit_status = fields.Many2one('audit.status','CAdudit Status')
    client_error_count = fields.Integer('CError Count')
    client_remarks_id = fields.Many2one('user.remarks', string="CRemarks", tracking=1, copy=False)
    rebuttals = fields.Selection(selection=[('yes','Yes'),('no','No')],string='Rebuttals')
    employee_id = fields.Many2one('hr.employee', string='Employee', compute="_compute_employee", store=True)
    employee_parent_id = fields.Many2one('hr.employee', string='Employee Manager', compute="_compute_employee",
                                         store=True)
    category_ids = fields.Many2many(
        'hr.employee.category',
        string='Employee Tags', compute="_compute_employee", store=True
    )

    @api.depends('assigned_to')
    def _compute_employee(self):
        for rec in self:
            rec.employee_id = False
            rec.employee_parent_id = False
            rec.category_ids = False
            if rec.assigned_to:
                employee = self.env['hr.employee'].search([('user_id', '=', rec.assigned_to.id)], limit=1)
                if employee:
                    rec.employee_id = employee.id
                    rec.employee_parent_id = employee.parent_id.id
                    rec.category_ids = employee.category_ids

    # _sql_constraints = [
    #     ('edm_batch_uniq', 'unique (edm_batch)', 'Another EDM Batch with the same name already exists.!')
    # ]

    # @api.depends('production_timing_ids.duration')
    # def _compute_total_work_hours(self):
    #     """Compute the total work hours by summing up the duration of all related task records."""
    #     for task in self:
    #         total_hours = sum(task.production_timing_ids.mapped('duration'))
    #         task.total_work_hours = total_hours

    @api.constrains('posted_date')
    def _check_date_not_in_future(self):
        for record in self:
            if record.posted_date:
                date_field = fields.Date.from_string(record.posted_date)
                if date_field > datetime.today().date():
                    raise ValidationError("The date cannot be in the future!")

    @api.constrains('posted_date')
    def _check_posted_date_is_there_or_not(self):
        for record in self:
            if not record.posted_date and record.status_id.completed_status == True:
                raise ValidationError("Please add the posted date!")

    def _get_current_time_in_float(self):
        current_time = datetime.now()
        return current_time.hour + current_time.minute / 60.0

    def action_start_time(self):
        self.sudo().production_timing_ids = [(0, 0, {
            'production_start_time': datetime.now(),
            'production_end_time': False,
            'duration': 0.0,  # Duration will be updated later
            'payment_posting_id': self.id
        })]
        self.timer_start = True

    def action_stop_timing(self):
        last_timing = self.sudo().production_timing_ids[-1]
        if last_timing:
            last_timing.write({
                'production_end_time': datetime.now()
            })
        """Stop action to update total work hours."""
        for record in self:
            # Recalculate total hours from production_timing_ids
            total_hours = sum(record.production_timing_ids.mapped('duration'))
            record.total_work_hours = total_hours
        self.sudo().timer_start = False

    @api.depends('created', 'posted_date','status_id', 'posted_date_time')
    def _compute_tat(self):
        for record in self:
            if record.created:
                created_dt = datetime.combine(record.created, datetime.min.time())
                if record.posted_date or record.posted_date_time:
                    if isinstance(record.posted_date_time, datetime):
                        closed_dt = record.posted_date_time
                    elif isinstance(record.posted_date, date):
                        closed_dt = datetime.combine(record.posted_date, datetime.min.time())
                    else:
                        closed_dt = datetime.now()
                else:
                    closed_dt = datetime.now()

                time_difference = closed_dt - created_dt
                record.tat = time_difference.total_seconds() / 3600  # Convert seconds to hours
            else:
                record.tat = 0.0

    @api.onchange('auditor_status', 'error_count', 'error_comments', 'incorrect', 'missed', 'navigation')
    def _onchange_error_count(self):
        for record in self:
            if record.auditor_status == "error":
                if not record.error_count or not record.error_comments:
                    raise UserError(
                        "Please provide an error counts and error comments when auditor status is 'Error'.")
                if record.error_count > 0:
                    total_errors = record.incorrect + record.missed + record.navigation
                    if total_errors != record.error_count:
                        raise UserError(
                            "The sum of Incorrect, Missed, and Navigation must equal the Error Count."
                        )

    @api.depends('division_id.priority_date', 'status_id.completed_status')
    def _compute_priority(self):
        for record in self:
            if record.status_id and record.status_id.completed_status:
                record.priority = '0'
                record.priority_compute = '0'
                continue

            if record.division_id.priority_date:
                today = fields.Date.context_today(self)
                if record.division_id.priority_date == today:
                    record.priority = '1'
                    record.priority_compute = '1'
                else:
                    record.priority = '0'
                    record.priority_compute = '0'
            else:
                # 3. Default case if no priority_date
                record.priority = '0'
                record.priority_compute = '0'

    def _compute_ref_count(self):
        for rec in self:
            if rec.payment_posting_id:
                payment_posting_obj = self.env['payment.posting'].search([('edm_batch', '=', rec.edm_batch),'|',('active','=',False),('active','=',True)])
                rec.ref_count = len(payment_posting_obj)
            else:
                rec.ref_count = 0

    def action_view_reference_payment_posting(self):

        return {
            'name': _('Reference'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'payment.posting',
            'domain': [('edm_batch', '=', self.edm_batch),('type', '=', self.type),'|',('active','=',False),('active','=',True)],
            'views_id': False,
            'views': [(self.env.ref('payment_posting.view_payment_posting_production_tree').id or False, 'tree'),
                      (self.env.ref('payment_posting.view_payment_posting_production_form').id or False, 'form')],
        }

    @api.depends('payment_posting_invoice_ids.amount', 'amount')
    def _compute_invoice_pending_amount(self):
        total_invoice_amount = 0.0
        self.total_invoice_pending_amount = 0.0
        for rec in self.payment_posting_invoice_ids:
            total_invoice_amount += rec.amount
        self.total_invoice_pending_amount = self.amount - total_invoice_amount

    @api.depends('payment_posting_invoice_ids.amount')
    def _compute_invoice_total_amount(self):
        total_invoice_amount = 0.0
        self.total_invoice_amount = 0.0
        for rec in self.payment_posting_invoice_ids:
            total_invoice_amount += rec.amount
            self.total_invoice_amount = total_invoice_amount

    @api.depends('amount', 'posted_amount', 'not_posted_amount', 'offset_amount')
    def _compute_pending_amount(self):
        self.pending_amount = 0
        for rec in self:
            if rec.type == 'edm_process':
                rec.pending_amount = rec.amount - rec.posted_amount
            elif rec.type == 'ecom_process':
                rec.pending_amount = rec.posted_amount - (rec.not_posted_amount + rec.offset_amount)


    def _default_auditor_stage_id(self):
        return self.env['audit.status'].search([], limit=1)

    def _default_stage_id(self):
        return self.env['user.status'].search([], limit=1)

    def _add_manager_as_follower(self, record):
        """ Helper method to add the manager of the assigned employee, the assigned user,
        and a notified user from res.config.settings as followers """

        # Retrieve the assigned employee
        assigned_employee = self.env['hr.employee'].sudo().search([('user_id', '=', record.assigned_to.id)], limit=1)

        # Add manager as follower
        if assigned_employee and assigned_employee.parent_id:
            manager = assigned_employee.parent_id
            record.message_subscribe(partner_ids=[manager.user_id.partner_id.id])

        # Add the assigned user as a follower
        if record.assigned_to.partner_id:
            record.message_subscribe(partner_ids=[record.assigned_to.partner_id.id])

        # Retrieve the notified user from res.config.settings
        notified_user_id = self.env.company.notified_users_id
        if notified_user_id:
            notified_user = self.env['res.users'].browse(int(notified_user_id))
            if notified_user.partner_id:
                record.message_subscribe(partner_ids=[notified_user.partner_id.id])


    def _notify_followers_directly(self, record):
        """ Helper method to notify followers when q_status_id changes """
        message_body =f"The status has been changed to: {record.q_status_id.name}"
        message_body += Markup("<br/>") + f"The Comments Mentioned: {record.gottlieb_comments}"
        record.message_post(body=message_body, subtype_xmlid='mail.mt_comment')  # Posts a message to all followers

    def write(self, vals):
        today = fields.Date.context_today(self)
        user_id = self.env.user

        if 'posted_date' in vals:
            current_time = datetime.now().time()
            if isinstance(vals['posted_date'], str):
                posted_date = datetime.strptime(vals['posted_date'], "%Y-%m-%d").date()
            else:
                posted_date = vals['posted_date']  # If already a date object
            # Get the current time

            # Combine posted_date with current time
            vals['posted_date_time'] = datetime.combine(posted_date, current_time)
        if 'assigned_to' in vals:
            if not vals['assigned_to']:
                status_id = self.env['user.status'].search([('name', '=', 'Unassigned')], limit=1)
                vals['assigned_date'] = False
                if status_id:
                    vals['status_id'] = status_id.id
            else:
                status_id = self.env['user.status'].search([('name', '=', 'Yet to Start')], limit=1)
                vals['assigned_date'] = today
                if status_id:
                    vals['status_id'] = status_id.id
        if 'auditor_user_id' in vals:
            vals['audited_date'] = today
            audit_status_id = self.env['audit.status'].search([('name', '=', 'Yet to Start')], limit=1)
            if audit_status_id:
                vals['audit_id'] = audit_status_id.id
        if vals.get('auditor_status') == 'error' and not vals.get('reprocessing_id'):
            reprocessing_status = self.env['reprocessing.status'].search([], limit=1)
            if reprocessing_status:
                vals['reprocessing_id'] = reprocessing_status.id
        res = super(PaymentPosting, self).write(vals)

        if vals.get('status_id', False):
            completed_status = self.env['user.status'].search([('id','=',vals['status_id']),('completed_status','=', True)])
            remarks_required_status = self.env['user.status'].search([('id','=',vals['status_id']),('remarks_required','=', True)])
            for rec in self:
                if completed_status:
                    if rec.pending_amount != 0:
                        raise UserError('Still pending amount is there, please update posted amount')
                    if rec.bar_batch == '':
                        raise UserError('Please enter bar batch number')
                if remarks_required_status:
                    if not rec.remarks_id:
                        raise UserError('Please select remarks')

        if 'status_id' in vals:
            status_employee = self.env['user.status'].browse(vals['status_id'])
            if status_employee.is_hold_status or status_employee.is_clarification_status:
                for record in self:
                    self._add_manager_as_follower(record)

        if 'q_status_id' in vals:
            for record in self:
                self._notify_followers_directly(record)

        return res


    @api.onchange('status_id')
    def onchange_status_id(self):
        user_id = self.env.user
        today = fields.Date.context_today(self)

        for rec in self:
            in_process_status = self.env['user.status'].search(
                [('id', '=', rec.status_id.id), ('in_process', '=', True)])
            completed_status = self.env['user.status'].search(
                [('id', '=', rec.status_id.id), ('completed_status', '=', True)])
            remarks_required_status = self.env['user.status'].search(
                [('id', '=', rec.status_id.id), ('remarks_required', '=', True)])
            current_status =  self.env['user.status'].browse(rec.status_id.id)
            if in_process_status.id == current_status.id:
                existing_in_process = self.search(
                    [('assigned_to', '=', rec.assigned_to.id), ('status_id', '=', in_process_status.id)])
                if len(existing_in_process) > 0:
                    raise UserError('Please complete previous in process item assigned to you')
            if completed_status.id == current_status.id:
                if rec.pending_amount != 0:
                    raise UserError('Still pending amount is there, please update posted amount')
                if rec.transaction == 0:
                    raise UserError('Please add transaction')
                if rec.bar_batch == '' or not rec.bar_batch:
                    raise UserError('Please enter bar batch number')
                rec.posted_date = today
            else:
                rec.posted_date = False
                rec.posted_date_time = False
            if remarks_required_status:
                if not rec.remarks_id:
                    raise UserError('Please select remarks')

    @api.onchange('audit_id')
    def onchange_audit_id(self):
        for rec in self:
            completed_status = self.env['audit.status'].search(
                [('id', '=', rec.audit_id.id), ('completed_status', '=', True)])
            if completed_status:
                if rec.of_transactions == 0:
                    raise UserError('Please add no of transaction')
                if not rec.auditor_status:
                    raise UserError('Please select error status')

    @api.model
    def create(self, vals):
        if vals.get('auditor_status') == 'error' and not vals.get('reprocessing_id'):
            reprocessing_status = self.env['reprocessing.status'].search([], limit=1)
            if reprocessing_status:
                vals['reprocessing_id'] = reprocessing_status.id
        if vals.get('type') is None:
            raise UserError("Please add process type")
        if (('edm_batch' in vals and vals['edm_batch']) or ('check_eft_number' in vals and vals['check_eft_number']))  and vals['type']:
            if vals['type'] == '835_push':
                name_value = vals['check_eft_number']
                domain = [('check_eft_number', '=', name_value),('type','=', vals['type'])]
            else:
                name_value = vals['edm_batch']
                domain = [('edm_batch', '=', name_value), ('type', '=', vals['type'])]
            if name_value:
                other_record = self.env['payment.posting'].search(domain, limit=1)
                if other_record:
                    vals['payment_posting_id'] = other_record.id
                    vals['id_duplicate'] = True
                    other_record.write({'active': False})
        return super(PaymentPosting, self).create(vals)

    def unlink(self):
        for record in self:
            if record.id_duplicate and record.payment_posting_id:
                record.payment_posting_id.write({'active': True})
        return super(PaymentPosting, self).unlink()

    # def write(self, vals):
    #     # Automatically assign a default reprocessing.status record if auditor_status is 'error'
    #     if vals.get('auditor_status') == 'error' and not vals.get('reprocessing_id'):
    #         reprocessing_status = self.env['reprocessing.status'].search([], limit=1)
    #         if reprocessing_status:
    #             vals['reprocessing_id'] = reprocessing_status.id
    #
    #     return super(PaymentPosting, self).write(vals)





