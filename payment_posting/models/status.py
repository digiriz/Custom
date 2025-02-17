from odoo import models, fields

class UserStatus(models.Model):
    _name = 'user.status'
    _description = 'EDM Status'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)
    in_process = fields.Boolean('In Process')
    remarks_required = fields.Boolean('Remarks Required')
    completed_status = fields.Boolean('Completed Status')
    is_hold_status = fields.Boolean('Is Hold Status')
    is_clarification_status = fields.Boolean('Is Clarification Status')
