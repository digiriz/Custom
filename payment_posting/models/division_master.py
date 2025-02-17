from odoo import models, fields, api

class DivisionMaster(models.Model):
    _name = 'division.master'
    _description = 'Division Master'
    _rec_name = 'complete_name'

    division_code = fields.Char('Division Code')
    division_name = fields.Char('Division Name')
    priority_date = fields.Date('Internal Priority Date')
    client_priority_date = fields.Date('Client Priority Date')
    complete_name = fields.Char(
        'Complete Name',
        compute='_compute_complete_name',
        recursive=True,
        store=True,
    )

    @api.depends('division_code', 'division_name')
    def _compute_complete_name(self):
        for rec in self:
            if rec.division_code and rec.division_name:
                rec.complete_name = '%s - %s' % (rec.division_code, rec.division_name)
            else:
                rec.complete_name = rec.division_code or rec.division_name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        domain = ['|', ('division_code', operator, name), ('division_name', operator, name)] + args

        return self.search(domain, limit=limit).name_get()

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = record.division_code
    #         if record.division_name:
    #             name = f"{record.division_code} - {record.division_name}"
    #         result.append((record.id, name))
    #     return result

