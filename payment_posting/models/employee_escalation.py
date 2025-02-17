from odoo import models, fields, api
from odoo.exceptions import AccessError
from lxml import etree

class EmployeeEscalation(models.Model):
    _name = 'employee.escalation'
    _description = 'Employee Escalation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', required=True, tracking=True)
    employee_public_id = fields.Many2one('hr.employee.public', string='Employees', required=False)  #Need to add compute functionality
    type = fields.Selection([('appreciation','Appreciation'),('escalation','Escalation')],string="Type", required=True)
    escalation_type_id = fields.Many2one('escalation.type', string='Escalation Type', required=True, tracking=True)
    description = fields.Text(string='Description', required=True)
    root_cause = fields.Text(string='Root Cause')
    incident_details = fields.Text(string='Incident Details')
    corrective_action_plan = fields.Text(string='Corrective Action Plan')
    employee_response = fields.Text(string='Employee Response')
    tl_comments = fields.Text(string='Team Lead Comments')
    manager_comments = fields.Text(string='Manager Comments')
    hr_comments = fields.Text(string='HR Comments')
