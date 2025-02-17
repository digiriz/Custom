{
    'name': 'Custom HR Attendance',
    'version': '17.0.0.1',
    'summary': 'A custom module for Odoo 17',
    'description': 'Custom HR Attendance',
    'author': 'Digimeta',
    'website': 'https://www.digimeta.dev/',
    'category': 'Custom',
    'depends': ['base', 'mail', 'hr_attendance', 'hr_timesheet','analytic', 'payment_posting', 'payment_posting_etm'],
    'data': [
        'security/ir.model.access.csv',
        'security/access_groups.xml',
        'views/hr_attendance.xml',
        'views/daily_consulted_timesheet_view.xml',
        'views/account_analytic_line.xml',
        'cron/daily_consultant_timesheet_cron_view.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}