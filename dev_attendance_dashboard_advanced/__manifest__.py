# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Attendance Dashboard Advanced | Employee Attendance Calendar',
    'version': '17.0.1.2',
    'sequence': 1,
    'category': 'Human Resources',
    'description':
        """
        Employee Attendance Monthly Dashboard Odoo App, designed to revolutionize your attendance management. This intuitive app provides a comprehensive attendance dashboard where you can see employees with their job designations and day-wise attendance on one screen. The app displays check-in and check-out times along with the total hours worked each day. If an employee is on leave, it is clearly shown. For weekends, the app manages days off based on the employee’s work schedule, and global holidays are also accounted for. If an employee does not have leave, weekend, attendance, or a holiday marked, they are displayed as absent for that day.

The app features a flexible calendar that allows you to switch between months and years effortlessly. On the left side of the screen, you’ll find a summary of monthly attendance, making attendance summary management straightforward. A unique feature is the ability to click on any holiday, leave, or attendance record to view detailed information. Filters for company, employee, month, and year make it easy to customize the data displayed to suit your needs.

Additionally, the app provides a leave summary for the current month, which can be adjusted using the provided filters. This summary includes the employee’s name, leave dates, and the reason for leave. A view button allows you to see detailed information about specific leave records. The Employee Attendance Monthly Dashboard Odoo App ensures efficient and straightforward attendance management, enhancing your organization’s productivity.
        
        Attendance Dashboard Attendance Management Attendance Monthly Summary Attendance Report Attendance onscreen Leave Summary Employee Leave Screen Advanced Dashboard Monthwise Employee Attendance Report Excel PDF

    """,
    'summary': 'Attendance Dashboard Employee Attendance Calendar Attendance Management Attendance Monthly Summary Attendance Report Attendance onscreen Leave Summary Employee Leave Screen Advanced Dashboard Monthwise Employee Attendance Report Excel PDF',
    'depends': ['hr_attendance','hr_holidays'],
    'data': [
        'security/security.xml',
        'views/dashboard.xml',
        
        # 'views/hr_employee.xml',
    ],
    'assets': {
       'web.assets_backend': [
           'dev_attendance_dashboard_advanced/static/src/css/dashboard_new.css',
           'dev_attendance_dashboard_advanced/static/src/js/attendanceDashboard.js',
           'dev_attendance_dashboard_advanced/static/src/xml/attendance_dashboard.xml'
       ],
    },
	'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':32.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
