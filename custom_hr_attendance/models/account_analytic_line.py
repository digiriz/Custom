from odoo import models, fields, api
from datetime import timedelta, date

from odoo.exceptions import UserError

STATE = [
    ('draft', 'Draft'),
    ('awaiting_approval', 'Awaiting Approval'),
    ('approved', 'Approved'),
    ('declined', 'Declined')
]


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    timesheet_id = fields.Many2one(
        'daily.consulted.timesheet', string="Consultant Timesheet"
    )
    state = fields.Selection(selection=STATE,
                             default="draft",
                             string='Status', tracking=3)


    def action_awaiting_approval(self):
        for res in self:
            res.state = 'awaiting_approval'

    def action_approved(self):
        user_id = self.env.user
        for res in self:
            employee = res.employee_id.sudo() if res.employee_id else False
            parent = employee.parent_id.sudo() if employee and employee.parent_id else False
            manager_user = parent.user_id.sudo() if parent and parent.user_id else False
            if employee and parent and manager_user and manager_user.id == user_id.id:
                res.sudo().write({'state': 'approved'})
            else:
                manager_name = parent.name if parent else "Manager"
                raise UserError(f"Please get approval from {manager_name}")


    def action_declined(self):
        for res in self:
            res.state = 'declined'

    def action_draft(self):
        for res in self:
            res.state = 'draft'










