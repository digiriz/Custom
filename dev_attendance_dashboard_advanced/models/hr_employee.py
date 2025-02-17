# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api, _

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    allowed_companies = fields.Many2many('res.company', string="Allowed Companies", compute='_compute_companies', store=True)

    def _compute_companies(self):
        print("============================================",jjjj)
        # for record in self:
        #     record.allowed_companies = self._context.get('allowed_company_ids')
        #     print(record.allowed_companies)
    
    
        
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: