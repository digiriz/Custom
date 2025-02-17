# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    notified_users_id = fields.Many2one('res.users', string="Notified Users", related="company_id.notified_users_id", readonly=False)


