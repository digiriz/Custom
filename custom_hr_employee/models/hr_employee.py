from odoo import models, fields, api
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)

class HrEmployeePublic(models.Model):
    _inherit= 'hr.employee.public'

    emp_id = fields.Char('EMP ID')
    vendra_id = fields.Char('Ventra ID')
    athena_id = fields.Char('Athena ID')
    allow_multi_process = fields.Boolean("Allow Multi Process")


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    emp_id = fields.Char('EMP ID')
    vendra_id = fields.Char('Ventra ID')
    athena_id = fields.Char('Athena ID')
    allow_multi_process = fields.Boolean("Allow Multi Process")

    def _get_week_range(self):
        today = fields.Date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week

    def calculate_daily_shortages(self):
        employees = self.env['hr.employee'].search([('user_id','!=',False)])
        today = fields.Date.today()

        daily_shortages = []
        for employee in employees:
            _logger.info(employee.name)
            today_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('shortage_excess_hours','<',0),
                ('check_in', '>=', today),
                ('check_in', '<', today + timedelta(days=1))
            ], limit=1)
            if today_attendance:
                daily_shortages.append((employee, round(today_attendance.shortage_excess_hours,2), today_attendance.check_in, today_attendance.check_out))

        return daily_shortages

    def calculate_weekly_shortages(self):
        employees = self.env['hr.employee'].search([])
        start_of_week, end_of_week = self._get_week_range()

        weekly_shortages = []
        for employee in employees:
            weekly_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('shortage_excess_hours', '<', 0),
                ('check_in', '>=', start_of_week),
                ('check_in', '<', end_of_week + timedelta(days=1))
            ])
            weekly_duration = sum(record.worked_hours for record in weekly_attendance)

            weekly_duration = round(weekly_duration, 2)

            expected_weekly_hours = 8 * 5
            if weekly_duration < expected_weekly_hours:
                shortage = round(expected_weekly_hours - weekly_duration, 2)
                weekly_shortages.append((employee, shortage))

        return weekly_shortages

    def notify_shortages(self, shortages, frequency):
        if not shortages:
            return

        manager_shortages = {}
        hr_shortages = ""

        for employee, shortage, checkin, checkout in shortages:
            hr_shortages += (
                "<tr>"
                f"<td>{employee.name}</td>"
                f"<td>{checkin}</td>"
                f"<td>{checkout}</td>"
                f"<td>{shortage}</td>"
                "</tr>"
            )

            if employee.work_email:
                self.env['mail.mail'].create({
                    'subject': f"{frequency.capitalize()} - Attendance Shortage Notification User",
                    'body_html': (
                        f"<p>Dear {employee.name},</p>"
                        "<p>You have an attendance shortage, please check the details below.</p>"
                        "<table border='1' cellspacing='0' cellpadding='5'>"
                        "<tr>"
                        "<th>Check In</th>"
                        "<th>Check Out</th>"
                        "<th>Shortage</th>"
                        "</tr>"
                        "<tr>"
                        f"<td>{checkin}</td>"
                        f"<td>{checkout}</td>"
                        f"<td>{shortage}</td>"
                        "</tr>"
                        "</table>"
                    ),
                    'email_to': employee.work_email,
                }).send()

            manager = employee.parent_id
            if manager:
                if manager.id not in manager_shortages:
                    manager_shortages[manager.id] = {
                        'manager': manager,
                        'employees': []
                    }
                manager_shortages[manager.id]['employees'].append(
                    "<tr>"
                    f"<td>{employee.name}</td>"
                    f"<td>{checkin}</td>"
                    f"<td>{checkout}</td>"
                    f"<td>{shortage}</td>"
                    "</tr>"
                )

        for manager_data in manager_shortages.values():
            manager = manager_data['manager']
            employee_list = (
                "<table border='1' cellspacing='0' cellpadding='5'>"
                "<tr>"
                "<th>Employee</th>"
                "<th>Checkin</th>"
                "<th>Checkout</th>"
                "<th>Shortage</th>"
                "</tr>"
            )
            for manager_data_employees in manager_data['employees']:
                employee_list += manager_data_employees
            employee_list += "</table>"

            if manager.work_email:
                self.env['mail.mail'].create({
                    'subject': f"{frequency.capitalize()} - Attendance Shortages Notification - Team",
                    'body_html': (
                        f"<p>Dear {manager.name},</p>"
                        "<p>The following team members have attendance shortages, please check the details below.</p>"
                        f"{employee_list}"
                    ),
                    'email_to': manager.work_email,
                }).send()

        hr_emails = ['rizwan.s@idigimeta.com']

        if hr_emails:
            hr_shortages_content = (
                "<table border='1' cellspacing='0' cellpadding='5'>"
                "<tr>"
                "<th>Employee</th>"
                "<th>Checkin</th>"
                "<th>Checkout</th>"
                "<th>Shortage</th>"
                "</tr>"
                f"{hr_shortages}"
                "</table>"
            )
            self.env['mail.mail'].create({
                'subject': f"{frequency.capitalize()} - Attendance Shortages Notification - All",
                'body_html': (
                    f"<p>Hi sir,</p>"
                    "<p>The following employees have attendance shortages, please check the details below.</p>"
                    f"{hr_shortages_content}"
                ),
                'email_to': ','.join(hr_emails),
            }).send()

    @api.model
    def attendance_shortage_cron_daily(self):
        daily_shortages = self.calculate_daily_shortages()
        if daily_shortages:
            self.notify_shortages(daily_shortages, 'daily')
        self.send_attendance_shortages_completion_email()

    @api.model
    def attendance_shortage_cron_weekly(self):
        print("Something")
        # weekly_shortages = self.calculate_weekly_shortages()
        # if weekly_shortages:
        #     self.notify_shortages(weekly_shortages, 'weekly')

    def send_attendance_shortages_completion_email(self):
        email_subject = "Daily Attendance Shortage Report"
        email_body = f"""
        Dear User,

       The attendance shortage emails successfully sent.

        """
        recipient_email = "rizwan.s@idigimeta.com"
        company = self.env.user.company_id
        sender_email = company.email or 'no-reply@example.com'

        # Create and send the email
        mail_values = {
            'subject': email_subject,
            'body_html': email_body,
            'email_to': recipient_email,
            'email_from': sender_email,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

        _logger.info(f"Email sent successfully to {recipient_email} regarding attendance shortages.")




