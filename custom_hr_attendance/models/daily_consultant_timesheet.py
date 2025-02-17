from odoo import models, fields, api
from datetime import timedelta, date
import logging
_logger = logging.getLogger(__name__)

STATE = [
    ('draft', 'Draft'),
    ('awaiting_approval', 'Awaiting Approval'),
    ('approved', 'Approved'),
    ('declined', 'Declined')
]

class DailyConsultantTimesheet(models.Model):
    _name = 'daily.consulted.timesheet'
    _description = "Daily Consolidated Timesheet"
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _rec_name = 'employee_id'

    date = fields.Date(string="Date", tracking=1)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )
    attendance_hours = fields.Float(string="Attendance Hours", tracking=1, compute="_compute_hours", store=True)
    worked_hours = fields.Float(string="Worked Hours", tracking=1, compute="_compute_hours", store=True)
    shortage_hours = fields.Float(string="Shortage Hours", tracking=1, compute="_compute_hours", store=True)
    analytic_line_ids = fields.Many2many(
        'account.analytic.line',
        string='Analytic Lines', compute='_compute_timesheet_line_ids',)

    @api.depends('date','employee_id')
    def _compute_timesheet_line_ids(self):
        for rec in self:
            if rec.date and rec.employee_id:
                domain = [
                    ('date', '=', rec.date),
                    ('employee_id', '=', rec.employee_id.id)
                ]
                account_analytic_ids = self.env['account.analytic.line'].search(domain)
                rec.analytic_line_ids = account_analytic_ids
            else:
                rec.analytic_line_ids  = False

    @api.depends('date', 'employee_id','analytic_line_ids')
    def _compute_hours(self):
        for rec in self:
            """Update analytic_line_ids, attendance_hours, and worked_hours based on the selected date and employee."""
            if rec.date and rec.employee_id:
                account_analytic = self.env['account.analytic.line'].search([
                    ('date', '=', rec.date),
                    ('employee_id', '=', rec.employee_id.id),
                    ('state','=','approved')
                ])

                total_worked_hours = sum(line.unit_amount for line in account_analytic)
                rec.worked_hours = total_worked_hours

                attendances = rec.env['hr.attendance'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('check_in', '>=', rec.date),
                    ('check_in', '<', rec.date + timedelta(days=1))
                ])

                total_attendance_hours = 0
                for attendance in attendances:
                    if attendance.check_in and attendance.check_out:
                        total_attendance_hours += attendance.worked_hours

                rec.attendance_hours = total_attendance_hours

                rec.shortage_hours = total_attendance_hours - total_worked_hours
            else:
                rec.attendance_hours = 0
                rec.shortage_hours = 0
                rec.worked_hours = 0


    @api.model
    def _cron_update_attendance_and_hours(self, from_date=False, to_date=False, employee_name=False):

        if not employee_name:
            all_employees = self.env['hr.employee'].search([('user_id', '!=', False)])
        else:
            all_employees = self.env['hr.employee'].search([('name', '=', employee_name)])
        all_employees_dict = {}
        for all_employee in all_employees:
            all_employees_dict[all_employee.user_id.id] = all_employee

        yesterday_date = date.today() - timedelta(days=1)  # Keep it as a date object
        from_date = fields.Date.from_string(from_date) if from_date else yesterday_date
        to_date = fields.Date.from_string(to_date) if to_date else yesterday_date

        if not from_date:
            from_date = yesterday_date
        else:
            from_date = fields.Date.from_string(from_date)  # Convert to date object
        if not to_date:
            to_date = yesterday_date
        else:
            to_date = fields.Date.from_string(to_date)  # Convert to date object
        while from_date <= to_date:
            target_date = from_date
            domain = [('date', '=', target_date)]
            HrEmployee = self.env['hr.employee']
            # Check if 'name' is provided
            if employee_name:
                # Search for the employee object based on the name
                employee_obj = HrEmployee.search([('name', '=', employee_name)],
                                                 limit=1)  # Added limit to return a single record
                if employee_obj:
                    # Append conditions to the domain for assigned_to or auditor_user_id
                    #     domain.append('|')  # Use '|' to create an OR condition
                    domain.append(('employee_id', '=', employee_obj.id))
                    # domain.append(('auditor_user_id', '=', employee_obj.user_id.id))
            print(domain)
            timesheet_hours = self.env['account.analytic.line']._read_group(
                domain,
                ['employee_id', 'date:day'],
                ['unit_amount:sum']
            )
            for timesheet_hour in timesheet_hours:
                employee = timesheet_hour[0]
                attendance_date = timesheet_hour[1]

                attendance_hours = timesheet_hour[2]
                existing_timesheet = self.search([('date','=',attendance_date),('employee_id','=',employee.id)])
                if existing_timesheet:
                    existing_timesheet.sudo().write({'attendance_hours': attendance_hours})
                else:
                    task_vals = {
                        'employee_id': employee.id,
                        'attendance_hours': attendance_hours,
                        'date': target_date,
                    }
                    self.create(task_vals)
            from_date += timedelta(days=1)


    # @api.model
    # def _cron_update_attendance_and_hours(self, from_date=False, to_date=False, employee_name=False):
    #     """Cron method to run every day at 7 AM and create daily consulted timesheets for yesterday's date."""
    #     if employee_name:
    #         employee_ids = self.env['hr.employee'].search([('name','=',employee_name)])
    #     else:
    #         employee_ids = self.env['hr.employee'].search([])
    #     _logger.info(employee_ids)
    #     for employee in employee_ids:
    #         _logger.info(employee.name)
    #         yesterday_date = date.today() - timedelta(days=1)  # Keep it as a date object
    #         if not from_date:
    #             from_date = yesterday_date
    #         else:
    #             from_date = fields.Date.from_string(from_date)  # Convert to date object
    #         if not to_date:
    #             to_date = yesterday_date
    #         else:
    #             to_date = fields.Date.from_string(to_date)  # Convert to date object
    #         print(from_date)
    #         print(to_date)
    #         target_date = from_date
    #         while target_date <= to_date:
    #             _logger.info(target_date)
    #             # stop
    #             account_analytic = self.env['account.analytic.line'].search([
    #                 ('date', '=', target_date),
    #                 ('employee_id', '=', employee.id),
    #                 ('state','=','approved')
    #             ])
    #             print(account_analytic)
    #
    #             attendances = self.env['hr.attendance'].search([
    #                 ('employee_id', '=', employee.id),
    #                 ('check_in', '>=', target_date),
    #                 ('check_in', '<', target_date + timedelta(days=1))
    #             ])
    #
    #             if not account_analytic and not attendances:
    #                 target_date += timedelta(days=1)
    #                 continue
    #             if account_analytic:
    #                 total_worked_hours = sum(line.unit_amount for line in account_analytic)
    #             else:
    #                 total_worked_hours = 0
    #
    #             total_attendance_hours = 0
    #             for attendance in attendances:
    #                 if attendance.check_in and attendance.check_out:
    #                     total_attendance_hours += attendance.worked_hours
    #
    #             shortage_hours = total_attendance_hours - total_worked_hours
    #             existing_record = self.env['daily.consulted.timesheet'].search([('employee_id','=',employee.id),('date','=',target_date)])
    #             consolidated_vals = {
    #                 'employee_id': employee.id,
    #                 'date': target_date,
    #                 'worked_hours': total_worked_hours,
    #                 'attendance_hours': total_attendance_hours,
    #                 'shortage_hours': shortage_hours,
    #             }
    #             if existing_record:
    #                 existing_record.write(consolidated_vals)
    #             else:
    #                 self.env['daily.consulted.timesheet'].create(consolidated_vals)
    #             target_date += timedelta(days=1)


    def add_timesheet(self):
        return {
            'name': "Add Timesheet",
            'view_mode': 'form',
            'res_model': 'account.analytic.line',
            'views': [(self.env.ref('custom_hr_attendance.view_form_account_analytic_line').id, "form")],
            # 'view_id': self.env.ref('view_form_account_analytic_line').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_date': self.date,
            },
            'target': 'new',
        }







