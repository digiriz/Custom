from odoo import models, fields

class UserRemarks(models.Model):
    _name = 'user.remarks'
    _description = 'User Remarks'

    name = fields.Char(string='Name', required=True)
