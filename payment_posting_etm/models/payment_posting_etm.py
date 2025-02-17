from odoo import models, fields, api, _
from datetime import datetime, date

from odoo.exceptions import UserError
from markupsafe import Markup

class PaymentPostingETM(models.Model):
    _name = 'payment.posting.etm'
    _description = 'Payment Posting ETM'
    _rec_name = 'etm_id'
    _inherit = ["mail.activity.mixin", "mail.thread"]

    type = fields.Selection([('pp_adjustments', 'PP ADJUSTMENTS'), ('pp_denials', 'PP DENIALS'),
                                     ('pp_corrections', 'PP CORRECTIONS'), ('pp_transfers', 'PP TRANSFERS'),
                                     ('pp_chk_research', 'PP CHK RESEARCH')], string="Task Role")
    processed_date = fields.Date(string="Processed Date")
    last_activity_date = fields.Date(string="Last Activity Date")
    last_updated_date = fields.Date(string="Last Updated Date")
    id_duplicate = fields.Boolean('Is Duplicate', readonly=True, copy=False)
    updated_date = fields.Date(string="Updated Date")
    last_updated_user = fields.Char("Last Updated User")
    payment_posting_etm_id = fields.Many2one('payment.posting.etm', string="Reference", readonly=True, tracking=1, copy=False)
    division_id = fields.Many2one('division.master', string="Division", tracking=1)
    ind = fields.Char(string="Ind")
    task = fields.Char("Task")
    v_age = fields.Integer(string="View Age")
    category = fields.Char("Category")
    inv_enc = fields.Char("Inv Enc")
    inv_balance = fields.Monetary("Inv Balance", currency_field='company_currency_id')
    totchag = fields.Monetary("TotChg", currency_field='company_currency_id')
    mrn = fields.Char(string="MRN#")
    invoice_no = fields.Char(string="Invoice#")
    dos = fields.Date(string="DOS")
    fsc = fields.Char(string="FSC")
    inscomp = fields.Char("InsComp")
    assigned_employee_id = fields.Many2one('hr.employee', 'Assigned To', copy=False, domain=[("category_ids.name",'in',['ETM'])] )
    assigned_to = fields.Many2one('res.users', 'Assigned To - User', copy=False, related="assigned_employee_id.user_id", store=True)
    assigned_date = fields.Date(string="Assigned Date", copy=False)
    cpt = fields.Char(string="CPT")
    batch_no = fields.Char(string="Batch#")
    ar_comments = fields.Char(string="AR Comments")
    user_id = fields.Many2one('res.users', 'User Name (Not Used)', copy=False)
    status_id = fields.Many2one('user.status', string="PStatus", tracking=1, copy=False, default=lambda self: self._default_stage_id())
    no_of_invoice = fields.Integer(string="# of Invoice")
    remarks = fields.Char(string="Remarks")
    auditor_user_id = fields.Many2one('res.users', string="Auditor Assigned To", copy=False)
    audited_date = fields.Date('Audited Assigned Date', copy=False)
    no_of_transactions = fields.Integer(string="# Of Transaction", copy=False)
    audit_id = fields.Many2one('audit.status', string="AStatus", tracking=1, copy=False)
    auditor_status = fields.Selection(
        [("error", "Error"), ("no_error", "No Error")],
        string="Error Status", copy=False
    )
    c_audit_date = fields.Date(string="C Audit Date", copy=False)
    error = fields.Selection([('error', 'Error'), ('no_error', 'No Error')], copy=False)
    error_count = fields.Integer(string="Error Count", copy=False)
    incorrect = fields.Integer(string="Incorrect", copy=False)
    missed = fields.Integer(string="Missed", copy=False)
    navigation = fields.Integer(string="Navigation", copy=False)
    error_comments = fields.Text(string="Error Comments", copy=False)
    error_category_id = fields.Many2one('error.category', string='Error Category')
    comments = fields.Text(string="Comments", copy=False)
    fixing_date = fields.Date(string="Fixing Date", copy=False)
    deposit_date = fields.Date(string="Deposit Date ", copy=False)
    updated_bar_batch = fields.Char(string="Updated Bar Batch#", copy=False)
    reprocessing_id = fields.Many2one('reprocessing.status', 'RStatus', copy=False)
    check = fields.Char(string="Check(s)", tracking=1)
    check_date = fields.Date(string="Check Date", tracking=1)
    icn_no_tcn_no = fields.Char(string="Icn#/Tcn#")
    denial_code = fields.Char(string="Denial Code")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    paid_amount = fields.Monetary(string="Paid Amount", currency_field='company_currency_id', tracking=1)
    check_amount = fields.Monetary(string="Check Amount", currency_field='company_currency_id', tracking=1)
    unm_amount = fields.Monetary(string="UNM Amount", currency_field='company_currency_id', tracking=1)
    adjustment_reasons_id = fields.Many2one('adjustment.reasons', 'Reasons', copy=False)
    action_taken_id = fields.Many2one('action.taken', 'Action Taken', copy=False)
    auditor_invoice_count = fields.Integer('Auditor Invoice Count')
    error_status = fields.Selection(
        [("fixed", "Fixed"), ("un_fixed", "Un Fixed")],
        string="Fixed / Unfixed", copy=False
    )
    client_audit_status = fields.Many2one('audit.status','CAdudit Status')
    client_error_count = fields.Integer('CError Count')
    client_remarks_id = fields.Many2one('user.remarks', string="CRemarks", tracking=1, copy=False)
    rebuttals = fields.Selection(selection=[('yes','Yes'),('no','No')],string='Rebuttals')
    production_timing_ids = fields.One2many('production.timing.etm', 'payment_posting_etm_id', string="Production Timing")
    timer_start = fields.Boolean()
    athena_id = fields.Char("User name",compute="_compute_athena_id", store=True)
    payer = fields.Char("Payer")
    note_type = fields.Char("Note Type")
    notes = fields.Text("Notes")
    posted_date = fields.Date("Posted Date")
    etm_id = fields.Char("Id")
    received_date = fields.Date("Received Date")
    action_needed = fields.Char("Action Needed")
    action_comments = fields.Char("Action Comments")
    etm_type = fields.Char("Type")
    bar_batch = fields.Char("Bar Batch")
    clarification_response = fields.Char("Clarification Response")
    esclation_category = fields.Char("Esclation Category")
    issue_raised_date = fields.Date('Issue Raised Date')
    issue_closed_date = fields.Date('Issue Closed Date')
    active = fields.Boolean("Active", default=True)
    total_work_hours = fields.Float(string="Work Hours")
    remarks_id = fields.Many2one('user.remarks', string="Remarks", tracking=1, copy=False)
    q_status_id = fields.Many2one('q.status', string="Q Status")
    employee_parent_id = fields.Many2one('hr.employee', string='Employee Manager', compute="_compute_employee",
                                         store=True)
    category_ids = fields.Many2many(
        'hr.employee.category',
        string='Tags', compute="_compute_employee", store=True
    )
    payment_posting_etm_invoice_ids = fields.One2many('payment.posting.etm.invoice', 'payment_posting_etm_id',
                                                  string="Payment Invoice Items", copy=False)
    total_invoice_amount = fields.Monetary(string="Total Invoice Amount", compute="_compute_invoice_pending_amount",
                                           currency_field='company_currency_id', copy=False)
    total_invoice_pending_amount = fields.Monetary(string="Pending Invoice Amount",
                                                   compute="_compute_invoice_pending_amount",
                                                   currency_field='company_currency_id', copy=False)
    amount = fields.Monetary(string="Amount", currency_field='company_currency_id', tracking=1)
    manually_create = fields.Boolean(string="Manually Created", default=False)

    @api.depends('payment_posting_etm_invoice_ids.amount', 'amount')
    def _compute_invoice_pending_amount(self):
        for rec in self:
            total_invoice_amount = 0.0
            rec.total_invoice_pending_amount = 0.0
            for line in rec.payment_posting_etm_invoice_ids:
                total_invoice_amount += line.amount
            rec.total_invoice_amount = total_invoice_amount
            rec.total_invoice_pending_amount = rec.amount - total_invoice_amount


    @api.depends('assigned_employee_id')
    def _compute_employee(self):
        for rec in self:
            rec.employee_parent_id = False
            rec.category_ids = False
            if rec.assigned_to:
                employee = self.env['hr.employee'].search([('user_id', '=', rec.assigned_to.id)], limit=1)
                if employee:
                    rec.employee_parent_id = employee.parent_id.id
                    rec.category_ids = employee.category_ids

    def _default_stage_id(self):
        return self.env['user.status'].search([], limit=1)



    @api.depends('assigned_employee_id')
    def _compute_athena_id(self):
        for rec in self:
            athena_val = False
            if rec.assigned_employee_id:                
                athena_val = rec.assigned_employee_id.athena_id
            rec.athena_id = athena_val

    def search_invoice(self):
        self.ensure_one()
        if self.type == 'pp_chk_research':
            action = self.env["ir.actions.actions"]._for_xml_id("payment_posting_etm.action_payment_posting_etm_pp_chk_research_allocation")
        else:
            # need to update for other views
            action = self.env["ir.actions.actions"]._for_xml_id(
                "payment_posting_etm.action_payment_posting_etm_pp_chk_research_allocation")
        division_id = self.division_id

        context_vals = {
            'default_check': self.check,
            'default_type': self.type,
            'default_ind': self.ind,
            'default_fsc': self.fsc,
            'default_inscomp': self.inscomp,
            'default_v_age': self.v_age,
            'default_task': self.task,
            'default_category': self.category,
            'default_inv_balance': self.inv_balance,
            'default_totchag': self.totchag,
            'default_received_date': self.received_date,
            'default_assigned_employee_id': self.assigned_employee_id.id,
            'default_assigned_date': self.assigned_date,
            'default_manually_create': True,
        }
        assigned_employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])

        if assigned_employee_id:
            context_vals.update({
                'default_assigned_employee_id': assigned_employee_id.id
            })
        if division_id:
            context_vals.update({
                'default_division_id': division_id.id
            })
        action['context'] = context_vals
        # action['domain'] = [('check','=',self.check)]
        return action


    def action_start_time(self):
        self.sudo().production_timing_ids = [(0, 0, {
            'production_start_time': datetime.now(),
            'production_end_time': False,
            'duration': 0.0,  # Duration will be updated later
            'payment_posting_etm_id': self.id
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

    def _add_manager_as_follower(self, record):
        """ Helper method to add the manager of the assigned employee, the assigned user,
        and a notified user from res.config.settings as followers """
        # Retrieve the assigned employee
        assigned_employee = record.sudo().assigned_employee_id
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
        if 'assigned_employee_id' in vals:
            if not vals['assigned_employee_id']:
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
        res = super(PaymentPostingETM, self).write(vals)
        if vals.get('status_id', False):
            completed_status = self.env['user.status'].search([('id','=',vals['status_id']),('completed_status','=', True)])
            remarks_required_status = self.env['user.status'].search([('id','=',vals['status_id']),('remarks_required','=', True)])
            for rec in self:
                if completed_status:
                    # if rec.pending_amount != 0:
                    #     raise UserError('Still pending amount is there, please update posted amount')
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
                    [('assigned_employee_id', '=', rec.assigned_employee_id.id), ('status_id', '=', in_process_status.id)])
                if len(existing_in_process) > 0:
                    raise UserError('Please complete previous in process item assigned to you')
            if completed_status.id == current_status.id:
                if rec.no_of_transactions == 0:
                    raise UserError('Please add transaction')
                if rec.bar_batch == '' or not rec.bar_batch:
                    raise UserError('Please enter bar batch number')
                rec.posted_date = today
            else:
                rec.posted_date = False
            if remarks_required_status:
                if not rec.remarks_id:
                    raise UserError('Please select remarks')


    @api.onchange('audit_id')
    def onchange_audit_id(self):
        for rec in self:
            completed_status = self.env['audit.status'].search(
                [('id', '=', rec.audit_id.id), ('completed_status', '=', True)])
            if completed_status:
                if rec.no_of_transactions == 0:
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
        if ('etm_id' in vals and vals['etm_id']):
            if vals['etm_id']:
                name_value = vals['etm_id']
                domain = [('etm_id', '=', name_value)]
                if name_value:
                    other_record = self.env['payment.posting.etm'].search(domain, limit=1)
                    if other_record:
                        vals['payment_posting_etm_id'] = other_record.id
                        vals['id_duplicate'] = True
                        other_record.write({'active': False})
        return super(PaymentPostingETM, self).create(vals)

    def action_create_invoice(self):
        """Create invoice records in payment.posting.etm.invoice for records where invoice_availability is False"""
        invoices_to_create = self.payment_posting_etm_invoice_ids.filtered(lambda inv: not inv.invoice_availability)

        for invoice in invoices_to_create:
            self.env["payment.posting.etm"].create({
                "payment_posting_etm_id": self.id,
                "inv_enc": invoice.invoice_no,
                "mrn": invoice.mrn,
                "dos": invoice.dos,
                "etm_id": invoice.etm_id,
                "amount": invoice.amount,
                "check": self.check,
                "type": self.type,
                "ind": self.ind,
                "fsc": self.fsc,
                "inscomp": self.inscomp,
                "division_id": self.division_id.id,
                "v_age": self.v_age,
                "task": self.task,
                "category": self.category,
                "inv_balance": self.inv_balance,
                "totchag": self.totchag,
                "received_date": self.received_date,
                "assigned_employee_id": self.assigned_employee_id.id,
                "assigned_date": self.assigned_date,
                "manually_create": True,
            })
            invoice.invoice_availability = True






