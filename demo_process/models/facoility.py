from odoo import models, fields

class FacilityMaster(models.Model):
    _name = 'facility.master'
    _description = 'Demo Station'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer("Sequence", default=10)