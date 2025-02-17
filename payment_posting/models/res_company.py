# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ResCompany(models.Model):
    _inherit = "res.company"

    notified_users_id = fields.Many2one('res.users',string="Notified Users")


