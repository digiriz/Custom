from odoo import models, fields

class AuditStatus(models.Model):
    _name = 'audit.status'

    name = fields.Char(string="Audit Status")
    in_process = fields.Boolean('In Process')
    remarks_required = fields.Boolean('Remarks Required')
    completed_status = fields.Boolean('Completed Status')