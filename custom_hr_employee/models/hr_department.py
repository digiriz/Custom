from odoo import fields, models, api


class HrDepartment(models.Model):
    _inherit= 'hr.department'
    _rec_name = 'name'


