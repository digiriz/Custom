from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id', groups=False,
        string='Tags')
