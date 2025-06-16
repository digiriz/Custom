from odoo import models, fields, api
from datetime import datetime, date

from odoo.exceptions import UserError, ValidationError


class DemoProcess(models.Model):
    _name = 'demo.process'
    _description = 'Demo Process'
    # _rec_name = 'etm_id'
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _rec_name = 'dos'

    received_date = fields.Date(string="Received Date")
    type = fields.Selection([('ams', 'AMS'), ('cama', 'CAMA'),
                             ('pa', 'PA'), ('wta', 'WTA'),
                             ('cama_charges', 'CAMA Charges'),
                             ('pa_charges', 'PA Charges'),
                             ('avala', 'AVALA')], string="Process Name")
    scan_date = fields.Date(string="Scan Date")
    dos = fields.Date(string="DOS", required=True)
    demo_station = fields.Many2one('demo.station', string="Demo Station")
    facility = fields.Many2one('facility.master', string="Facility", required=True)
    updated_facility = fields.Char(string="Updated Facility")
    demo_count = fields.Integer(string="Demo Count")
    assigned_employee_id = fields.Many2one('hr.employee', 'Assigned To',
                                           domain=[("category_ids.name", 'in', ['Demo Process'])])
    assigned_to = fields.Many2one('res.users', 'Assigned to User', copy=False, related="assigned_employee_id.user_id",
                                  store=True)
    assigned_date = fields.Date(string="Assigned Date", copy=False)
    login_id = fields.Many2one('login.id', string="Login ID(Not used)")
    final_count = fields.Integer(string="Final Count", store=True)
    demo_download = fields.Integer(string="Demo Download")
    manual = fields.Integer(string="Manual")
    facesheet_missing = fields.Integer(string="Facesheet Missing")
    self_pay = fields.Integer(string="Self Pay")
    ins_missing = fields.Integer(string="Ins Missing")
    chk_elig_nt_avail = fields.Integer(string="Chk Elig Nt Avail")
    others = fields.Integer(string="Others")
    demo_process_pstatus = fields.Many2one('demo.process.user.status', tracking=1,
                                           default=lambda self: self._default_stage_id(), copy=False, string="Pstatus")
    comments = fields.Text(string="Comments")
    eligibility_report = fields.Integer(string="Eligibility Report")
    auditor_user_id = fields.Many2one('res.users', string="Auditor Assigned To", copy=False)
    audited_date = fields.Date('Audited Assigned Date', copy=False)
    error = fields.Selection([('error', 'Error'), ('no_error', 'No Error')], copy=False)
    error_count = fields.Integer(string="Error Count", copy=False)
    incorrect = fields.Integer(string="Incorrect", copy=False)
    missed = fields.Integer(string="Missed", copy=False)
    navigation = fields.Integer(string="Navigation", copy=False)
    error_comments = fields.Text(string="Error Comments", copy=False)
    error_category_id = fields.Many2one('demo.process.error.category', string='Error Category')
    fixing_date = fields.Date(string="Fixing Date", copy=False)
    updated_bar_batch = fields.Char(string="Updated Bar Batch#", copy=False)
    reprocessing_id = fields.Many2one('demo.process.reprocessing.status', 'RStatus', copy=False)
    auditor_status = fields.Selection(
        [("error", "Error"), ("no_error", "No Error")],
        string="Error Status", copy=False
    )
    demo_process_note_lines = fields.One2many('demo.process.notes', 'demo_process_id', 'Notes', auto_join=True)
    active = fields.Boolean("Active", default=True)
    timer_start = fields.Boolean()
    production_timing_ids = fields.One2many('demo.process.production.timing', 'demo_process_id',
                                            string="Production Timing")
    total_work_hours = fields.Float(string="Work Hours")
    posted_date = fields.Date(string="Posted Date", copy=False)
    client_audit_status = fields.Many2one('demo.process.audit.status', 'CAdudit Status')
    client_error_count = fields.Integer('CError Count')
    client_remarks_id = fields.Many2one('demo.process.user.remarks', string="CRemarks", tracking=1, copy=False)
    c_audit_date = fields.Date(string="C Audit Date", copy=False)
    rebuttals = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string='Rebuttals')
    athena_id = fields.Char("Login Id", compute="_compute_athena_id", store=True)

    @api.onchange('demo_process_note_lines')
    def _onchange_notes_lines(self):
        for rec in self:
            rec.final_count = len(rec.demo_process_note_lines)

    @api.depends('assigned_employee_id')
    def _compute_athena_id(self):
        for record in self:
            rec = record.sudo()
            athena_val = False
            if rec.assigned_employee_id:
                athena_val = rec.assigned_employee_id.athena_id
            rec.athena_id = athena_val

    @api.constrains('posted_date', 'demo_process_pstatus', 'demo_download', 'manual', 'facesheet_missing', 'self_pay',
                    'ins_missing', 'chk_elig_nt_avail', 'others', 'eligibility_report')
    def _check_complete_constrains(self):
        for record in self:
            if record.posted_date:
                date_field = fields.Date.from_string(record.posted_date)
                if date_field > datetime.today().date():
                    raise ValidationError("The date cannot be in the future!")
            if not record.posted_date and record.demo_process_pstatus.completed_status:
                raise ValidationError("Please add the posted date!")
            if record.demo_process_pstatus.completed_status:
                final_count = record.final_count
                calculate_final_count = record.demo_download + record.manual
                # Hidden this warning for now
                # if final_count != calculate_final_count:
                #     raise ValidationError("Final count is not matching.")
                # Hidden this warning for now
                # others_counts = record.facesheet_missing + record.self_pay + record.ins_missing + record.chk_elig_nt_avail + record.others + record.eligibility_report
                # if final_count != others_counts:
                #     raise ValidationError("Final count is not matching with eligibility report and other items.")

    def _default_stage_id(self):
        return self.env['demo.process.user.status'].search([], limit=1)

    def write(self, vals):
        today = fields.Date.context_today(self)
        if 'assigned_employee_id' in vals:
            if not vals['assigned_employee_id']:
                status_id = self.env['demo.process.user.status'].search([('name', '=', 'Unassigned')], limit=1)
                vals['assigned_date'] = False
                if status_id:
                    vals['demo_process_pstatus'] = status_id.id
            else:
                status_id = self.env['demo.process.user.status'].search([('name', '=', 'Yet to Start')], limit=1)
                vals['assigned_date'] = today
                if status_id:
                    vals['demo_process_pstatus'] = status_id.id
        if vals.get('demo_process_pstatus', False):
            remarks_required_status = self.env['user.status'].search(
                [('id', '=', vals['demo_process_pstatus']), ('remarks_required', '=', True)])
            print(remarks_required_status)
            for rec in self:
                print(rec.comments)
                if remarks_required_status:
                    if not rec.comments:
                        raise UserError('Please select remarks')
        res = super(DemoProcess, self).write(vals)
        return res

    @api.onchange('demo_process_pstatus')
    def onchange_status_id(self):
        user_id = self.env.user
        today = fields.Date.context_today(self)

        for rec in self:
            # in_process_status = self.env['demo.process.user.status'].search(
            #     [('id', '=', rec.demo_process_pstatus.id), ('in_process', '=', True)])
            current_status = self.env['demo.process.user.status'].browse(rec.demo_process_pstatus.id)
            completed_status = self.env['demo.process.user.status'].search(
                [('id', '=', rec.demo_process_pstatus.id), ('completed_status', '=', True)])
            remarks_required_status = self.env['demo.process.user.status'].search(
                [('id', '=', rec.demo_process_pstatus.id), ('remarks_required', '=', True)])
            # if in_process_status.id == current_status.id:
            #     existing_in_process = self.search(
            #         [('assigned_employee_id', '=', rec.assigned_employee_id.id), ('demo_process_pstatus', '=', in_process_status.id)])
            #     if len(existing_in_process) > 0:
            #         raise UserError('Please complete previous in process item assigned to you')
            if completed_status.id == current_status.id:
                rec.posted_date = today
            else:
                rec.posted_date = False
            if remarks_required_status:
                if not rec.comments:
                    raise UserError('Please enter comments')

    def action_open_notes_upload_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Notes File',
            'res_model': 'notes.upload.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_start_time(self):
        self.sudo().production_timing_ids = [(0, 0, {
            'production_start_time': datetime.now(),
            'production_end_time': False,
            'duration': 0.0,  # Duration will be updated later
            'demo_process_id': self.id
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

    def deselect_all(self):
        for item in self.demo_process_note_lines:
            item.select = False

    def select_all(self):
        for item in self.demo_process_note_lines:
            item.select = True

    def delete_records(self):
        records = self.demo_process_note_lines.filtered(lambda notes: notes.select)
        records.unlink()
