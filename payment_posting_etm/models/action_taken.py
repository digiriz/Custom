from odoo import models, fields, api, _

class ActionTaken(models.Model):
    _name = 'action.taken'

    name = fields.Char(string="Action Taken")