{
    'name': 'Employee Escalation',
    'version': '17.0.0.1',
    'summary': 'Employee Escalation',
    'description': 'IDMT - EDM Process',
    'author': 'Digimeta',
    'website': 'https://www.digimeta.dev/',
    'category': 'Custom',
    'depends': ['base', 'mail', 'hr','custom_hr_employee'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}