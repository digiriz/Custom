from odoo import fields, models, api
from datetime import datetime, time, timedelta


class HrLeave(models.Model):
    _inherit= 'hr.leave'

    manager_employee_id = fields.Many2one(
        'hr.employee', string='Manager', index=True,related='employee_id.parent_id', store=True,
        tracking=True,)
    employee_department_id = fields.Many2one(
        'hr.department', store=True, string='Department', related='employee_id.department_id')
    leave_type = fields.Selection([('planned', 'Planned'), ('unplanned', 'Unplanned')], string="Leave Type", tracking=True)

    @api.model
    def send_daily_attendance_email(self):
        current_date = fields.Date.context_today(self)
        current_time = datetime.now().time()
        # Skip on Sundays
        if current_date.weekday() == 6:
            return

        employees = self.env['hr.employee'].search([('name','!=','Administrator')])

        # leave_records = self.env['hr.leave'].search([
        #     ('date_from', '<=', current_date),
        #     ('date_to', '>=', current_date),
        #     ('state', '=', 'validate')
        # ])
        # leave_employee_ids = leave_records.mapped('employee_id.id')
        absent_employees = []
        nine_am = time(9, 0, 0)
        for employee in employees:
            # if employee.id in leave_employee_ids:
            #     continue
            domain = [
                ('employee_id', '=', employee.id),
                ('check_in', '>=', datetime.combine(current_date, time.min)),
                ('check_in', '<=', datetime.combine(current_date, nine_am))
            ]
            attendance_today = self.env['hr.attendance'].search(domain, limit=1)

            if not attendance_today:
                absent_employees.append({
                    'name': employee.name,
                    'manager_name': employee.parent_id.name or 'N/A',
                    'tag': ', '.join(employee.category_ids.mapped('name')) or 'N/A',
                })

        if not absent_employees:
            return
        sno = 1
        email_content = """
            <p>Hello,</p>
            <p>The following employees have been marked as absent for not checking in by 9 AM:</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                        <th style="padding: 5px; text-align: left;">S. No</th>
                        <th style="padding: 5px; text-align: left;">Employee Name</th>
                        <th style="padding: 5px; text-align: left;">Manager Name</th>
                        <th style="padding: 5px; text-align: left;">Tag</th>
                    </tr>
                </thead>
                <tbody>
        """
        for absent in absent_employees:
            email_content += f"""
                <tr>
                    <td style="padding: 5px;">{sno}</td>
                    <td style="padding: 5px;">{absent['name']}</td>
                    <td style="padding: 5px;">{absent['manager_name']}</td>
                    <td style="padding: 5px;">{absent['tag']}</td>
                </tr>
            """
            sno+=1
        email_content += """
                </tbody>
            </table>
            <p>Regards,<br/>HR Department</p>
        """

        mail_values = {
            'subject': 'Daily Attendance Report',
            'body_html': email_content,
            'email_to': 'hr@idigimeta.com, info@idigimeta.com',
        }
        self.env['mail.mail'].create(mail_values).send()

    @api.model
    def send_weekly_timeoff_report(self):
        """Send Weekly Time-Off Report every Friday at 7 AM."""
        today = fields.Date.context_today(self)
        # if today.weekday() != 4:
        #     return

        last_friday = today - timedelta(days=7)
        last_thursday = today - timedelta(days=1)

        timeoff_records = self._get_timeoff_records(last_friday, last_thursday)

        self._send_timeoff_email(
            timeoff_records,
            f"Weekly Time-Off Report ({last_friday} to {last_thursday})",
            'Weekly Time-Off Report'
        )

    @api.model
    def send_monthly_timeoff_report(self):
        """Send Monthly Time-Off Report on the 26th at 7:30 AM."""
        today = fields.Date.context_today(self)
        # if today.day != 26:
        #     return

        first_day_of_current_month = today.replace(day=1)
        last_month_26th = first_day_of_current_month - timedelta(days=1)
        last_month_26th = last_month_26th.replace(day=26)
        this_month_25th = last_month_26th + timedelta(days=30)

        timeoff_records = self._get_timeoff_records(last_month_26th, this_month_25th)

        self._send_timeoff_email(
            timeoff_records,
            f"Monthly Time-Off Report ({last_month_26th} to {this_month_25th})",
            'Monthly Time-Off Report'
        )

    def _get_timeoff_records(self, start_date, end_date):
        """Fetch time-off records within the given date range."""
        timeoff_records = self.env['hr.leave'].search([
            ('date_from', '>=', start_date),
            ('date_to', '<=', end_date),
            ('state', '=', 'validate')
        ])
        data = []
        for record in timeoff_records:
            data.append({
                'date': record.date_from.date(),
                'employee_name': record.employee_id.name,
                'department': record.employee_id.department_id.name or 'N/A',
                'tag': ', '.join(record.employee_id.category_ids.mapped('name')) or 'N/A',
                'leave_type': record.holiday_status_id.name,
            })
        return data

    def _send_timeoff_email(self, timeoff_records, subject, report_name):
        """Send time-off email with the given data and subject."""
        if not timeoff_records:
            return

        email_content = f"""
                <p>Hello,</p>
                <p>{report_name}:</p>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <thead>
                        <tr>
                            <th style="padding: 5px; text-align: left;">Date</th>
                            <th style="padding: 5px; text-align: left;">Employee Name</th>
                            <th style="padding: 5px; text-align: left;">Department</th>
                            <th style="padding: 5px; text-align: left;">Tag</th>
                            <th style="padding: 5px; text-align: left;">Leave Type</th>
                        </tr>
                    </thead>
                    <tbody>
            """
        for record in timeoff_records:
            email_content += f"""
                    <tr>
                        <td style="padding: 5px;">{record['date']}</td>
                        <td style="padding: 5px;">{record['employee_name']}</td>
                        <td style="padding: 5px;">{record['department']}</td>
                        <td style="padding: 5px;">{record['tag']}</td>
                        <td style="padding: 5px;">{record['leave_type']}</td>
                    </tr>
                """
        email_content += """
                    </tbody>
                </table>
                <p>Regards,<br/>HR Department</p>
            """

        mail_values = {
            'subject': subject,
            'body_html': email_content,
            'email_to': 'hr@idigimeta.com, info@idigimeta.com',
        }
        self.env['mail.mail'].create(mail_values).send()