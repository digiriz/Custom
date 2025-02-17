from odoo import models, fields, api
from pytz import timezone
from odoo.addons.resource.models.utils import Intervals

class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Job Position', readonly=True, store=True)
    department_id = fields.Many2one('hr.department', 'Department', check_company=True, related='employee_id.department_id', store=True, readonly=True)
    manager_id = fields.Many2one('hr.employee', related='employee_id.parent_id', string='Manager', store=True, readonly=True)
    category_ids = fields.Many2many(related='employee_id.category_ids', string="Employee Tags", readonly=True, related_sudo=False)
    shortage_excess_hours = fields.Float(string='Excess / Shortage Hours', compute='_compute_shortage_excess_hours', store=True, readonly=True)

    @api.depends('check_in', 'check_out')
    def _compute_shortage_excess_hours(self):
        att_progress_values = dict()
        if self.employee_id:
            self.env['hr.attendance'].flush_model(['worked_hours'])
            self.env['hr.attendance.overtime'].flush_model(['duration'])
            self.env.cr.execute('''
                        WITH employee_time_zones AS (
                            SELECT employee.id AS employee_id,
                                   calendar.tz AS timezone
                              FROM hr_employee employee
                        INNER JOIN resource_calendar calendar
                                ON calendar.id = employee.resource_calendar_id
                        )
                        SELECT att.id AS att_id,
                               att.worked_hours AS att_wh,
                               ot.id AS ot_id,
                               ot.duration AS ot_d,
                               ot.date AS od,
                               att.check_in AS ad
                          FROM hr_attendance att
                    INNER JOIN employee_time_zones etz
                            ON att.employee_id = etz.employee_id
                    INNER JOIN hr_attendance_overtime ot
                            ON date_trunc('day',
                                          CAST(att.check_in
                                                   AT TIME ZONE 'utc'
                                                   AT TIME ZONE etz.timezone
                                          as date)) = date_trunc('day', ot.date)
                           AND att.employee_id = ot.employee_id
                           AND att.employee_id IN %s
                      ORDER BY att.check_in DESC
                    ''', (tuple(self.employee_id.ids),))
            a = self.env.cr.dictfetchall()
            grouped_dict = dict()
            for row in a:
                if row['ot_id'] and row['att_wh']:
                    if row['ot_id'] not in grouped_dict:
                        grouped_dict[row['ot_id']] = {'attendances': [(row['att_id'], row['att_wh'])],
                                                      'overtime_duration': row['ot_d']}
                    else:
                        grouped_dict[row['ot_id']]['attendances'].append((row['att_id'], row['att_wh']))

            for ot in grouped_dict:
                ot_bucket = grouped_dict[ot]['overtime_duration']
                for att in grouped_dict[ot]['attendances']:
                    if ot_bucket > 0:
                        sub_time = att[1] - ot_bucket
                        if sub_time < 0:
                            att_progress_values[att[0]] = 0
                            ot_bucket -= att[1]
                        else:
                            att_progress_values[att[0]] = float(((att[1] - ot_bucket) / att[1]) * 100)
                            ot_bucket = 0
                    else:
                        att_progress_values[att[0]] = 100
        for attendance in self:
            attendance.shortage_excess_hours = attendance.worked_hours - 8



