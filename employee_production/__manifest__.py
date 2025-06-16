{
    'name': 'Employee Production',
    'version': '17.0.0.1',
    'summary': 'Employee Production',
    'description': 'IDMT - EDM Process',
    'author': 'Digimeta',
    'website': 'https://www.digimeta.dev/',
    'category': 'Custom',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/employee_target_wizard_view.xml',
        'wizard/demo_process_employee_target_wizard_view.xml'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}