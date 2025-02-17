# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
import datetime
from datetime import timedelta
from odoo import http
from odoo.http import request
import math, calendar
import pytz


class AttendanceDashboard(http.Controller):
  
    @http.route('/employee/attendance', auth='public', type='json')
    def employee_attendance(self, **kw):
        user_tz = request.env.user.tz or pytz.utc  # Get user's timezone or default to UTC
        local = pytz.timezone(user_tz)
        employee_domain = []
        month_domain = datetime.date.today().month
        year_domain = datetime.date.today().year
        department_domain = []
        domains = self.roomDashboardFilterApply(kw)

        if domains:
            if domains['employee_domain']:
                employee_domain = domains['employee_domain']

            if domains['department_domain']:
                department_domain = domains['department_domain']

            if domains['month_domain']:
                month_domain = domains['month_domain']

            if domains['year_domain']:
                year_domain = domains['year_domain']

        response = [[]]
        employee_ids = request.env['hr.employee'].search(employee_domain + department_domain)

        days = calendar.monthrange(year_domain, month_domain)[1]

        for employee in employee_ids:
            emp_dict = {}
            att_dict = {}
            all_leaves = []
            all_present = []
            all_holidays = []
            leave = 0
            absent = 0
            present = 0
            weekoff = 0
            t_holiday = 0
            emp_dict['id'] = employee.id

            if employee.image_1920 and len(employee.image_1920) > 1000:
                emp_dict['img'] = employee.image_1920
            else:
                emp_dict['img'] = None
            emp_dict['name'] = employee.name
            emp_dict['job'] = employee.job_id.name

            for day in range(1,days+1):
                check_in = datetime.datetime(year_domain, month_domain, day, 00, 00, 1)
                check_out = datetime.datetime(year_domain, month_domain, day, 23, 59, 59)
                employee_work_schedule = employee.resource_calendar_id.attendance_ids
                workingdays = list(set([int(schedule.dayofweek) for schedule in employee_work_schedule]))

                public_holiday_ids = employee.resource_calendar_id.global_leave_ids   

                if check_in.weekday() not in workingdays:
                    att_dict[day] = {'status':'W'}
                    weekoff+=1

                else:
                    leave_ids = request.env['hr.leave'].search([('employee_id', 'in', [employee.id]), ('request_date_from', '<=', check_in.date()), ('request_date_to', '>=', check_out.date()),('state', 'in', ['validate'])])
                    
                    if leave_ids:
                        all_leaves.append(leave_ids.id)
                        att_dict[day] = {'status':'l', 'ids': leave_ids.id}
                        leave+=1
                    else:
                        attendance_ids = request.env['hr.attendance'].search([('employee_id', 'in', [employee.id]), ('check_in', '>=', check_in), ('check_out', '<=', check_out)], order='id asc') 
                        if attendance_ids:
                            for att in attendance_ids.ids:
                                all_present.append(att)
                            total_hours = sum(att.worked_hours for att in attendance_ids)
                            td = timedelta(hours=total_hours)
                            hours, remainder = divmod(td.total_seconds(), 3600)
                            minutes = remainder // 60
                            att_dict[day] = {'status':'p', 'hours': '{:02}:{:02}'.format(int(hours), int(minutes)),'ids': attendance_ids.ids}
                            present+=1
                        else:
                            att_dict[day] = {'status':'absent'}
                            absent+=1

                    for holiday in public_holiday_ids:
                        from_date = holiday.date_from.astimezone(local).date()
                        to_date = holiday.date_to.astimezone(local).date()

                        if from_date <= check_in.date() and to_date >= check_out.date():
                            if att_dict[day]['status'] == 'l':
                                leave-=1
                            att_dict[day] = {'status':'holiday', 'ids':holiday.id}
                            all_holidays.append(holiday.id)
                            t_holiday += 1

            emp_dict['attendance'] = att_dict
            if all_leaves:
                emp_dict['all_leave'] = list(set(all_leaves))
            if all_present:
                emp_dict['all_present'] = all_present
            if all_holidays:
                emp_dict['all_holidays'] = all_holidays
            emp_dict['summary'] = {'w':weekoff, 'l':leave, 'p':present, 'a':absent-t_holiday, 'h':t_holiday}
            response[0].append(emp_dict)
        response.append({'days':days})
        return response
    '''        
        [{'id': 6, 
          'name': 'Abigail Peterson', 
          'img' : 'img',
          'leave_ids' : [leave ids],
          'all_leave' : [all leave]
          'job_id': (3, 'Consultant'),
          'attendance':{
              1 : 'Absent'
              2 : 8.36}
        }, {days:}]
          '''
    
    @http.route('/employee/leave', auth='public', type='json')
    def get_leave_detail(self, **kw):
        domains = self.roomDashboardFilterApply(kw)
        employee_domain = []
        month_domain = datetime.datetime.today().month
        year_domain = datetime.datetime.today().year
        department_domain = []
        if domains:
            if domains['employee_domain']:
                employee_domain =  [('employee_id', 'in', domains['employee_domain'][0][2])]  

            if domains['month_domain']:
                month_domain = domains['month_domain']

            if domains['year_domain']:
                year_domain = domains['year_domain']
            
            if domains['department_domain']:
                department_domain = domains['department_domain']


        leave_details = request.env['hr.leave'].search_read(employee_domain + [('state', 'in', ['validate'])],['employee_id', 'holiday_status_id', 'request_date_from', 'request_date_to', 'number_of_days_display', 'name'], order='request_date_from asc')
        new_leave_details = []
        for leave in leave_details:
            if leave['request_date_from'].month == month_domain and leave['request_date_from'].year == year_domain:
                if department_domain:
                    employee = request.env['hr.employee'].browse(leave['employee_id'][0])
                    if employee.department_id.id in department_domain[0][2]:
                        new_leave_details.append(leave)
                else:
                        new_leave_details.append(leave)

        return new_leave_details
    
    @http.route('/render_attendance_dashboard_filter', auth='public', type='json')
    def renderAttendanceDashboardFilter(self):
        employee_ids = request.env['hr.employee'].search_read([], ['id', 'name'])
        department_ids = request.env['hr.department'].search_read([], ['id', 'name'])
        return [employee_ids, department_ids]
    

    @http.route('/attn/user_detail', auth='public', type='json')
    def hotel_user_detail(self):
        user_name = request.env.user.name
        user_img = request.env.user.image_1920

        if user_img and len(user_img) > 1000:
            final_user_img = request.env.user.image_1920
        else:
            final_user_img = None

        return {
            'user_img': final_user_img,
            'user_name': user_name
        }

    @http.route('/attendance_dashboard_filter_apply', auth='public', type='json')
    def roomDashboardFilterApply(self, kw):
        if kw:
            request = kw['request']
        else:
            request = {}
        employee_domain = []
        department_domain = []
        month_domain = None
        year_domain = None

        if request:
            if request['employee']:
                employee_id = request['employee']
                if not employee_id == "all":
                    employee_id = int(employee_id)
                    employee_domain = [('id', 'in', [employee_id])]

            if request['department']:
                department_id = request['department']
                if not department_id == "all":
                    department_id = int(department_id)
                    department_domain = [('department_id', 'in', [department_id])]

            if request['month']:
                month = int(request['month'])
                month_domain = month+1

            if request['year']:
                year = int(request['year'])
                year_domain = year

        # result = self.employee_attendance(employee_domain=employee_domain, month_domain=month_domain, year_domain=year_domain)
        return {'employee_domain':employee_domain, 'department_domain':department_domain, 'month_domain': month_domain, 'year_domain': year_domain}
    

    
    
