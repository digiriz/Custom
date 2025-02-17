from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit= 'hr.employee'

    production_lines = fields.One2many('employee.production','employee_id','Production - Target')
    target_lines = fields.One2many('employee.target','employee_id','Target')
    esclation_lines = fields.One2many('employee.escalation','employee_id','Target')


class HrEmployeePublic(models.Model):
    _inherit= 'hr.employee.public'

    target_lines = fields.One2many('employee.target','employee_public_id','Target')
    esclation_lines = fields.One2many('employee.escalation', 'employee_public_id', 'Target')
