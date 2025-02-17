{
    'name': 'Custom HR Employee',
    'version': '17.0.0.1',
    'summary': 'A custom module for Odoo 17',
    'description': 'Custom HR Attendance',
    'author': 'Digimeta',
    'website': 'https://www.digimeta.dev/',
    'category': 'Custom',
    'depends': ['base', 'mail', 'hr', 'hr_holidays'],
    'data': [
        'views/hr_employee.xml',
        'views/hr_leave_view.xml',
        'cron/employee_attendance_shortage_cron.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}