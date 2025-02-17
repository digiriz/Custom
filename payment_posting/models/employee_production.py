from odoo import models, fields, api

class EmployeeProduction(models.Model):
    _name = 'employee.production'
    _description = 'Employee Production'
    _order = "id desc"
    _rec_name = 'employee_id'

    process_type = fields.Selection(
        [('edm_process', 'EDM Process'), ('ecom_process', 'ECOM Process'), ('835_push', '835 Push'),
         ('pp_adjustments', 'PP ADJUSTMENTS'), ('pp_denials', 'PP DENIALS'),
         ('pp_corrections', 'PP CORRECTIONS'), ('pp_transfers', 'PP TRANSFERS'),
         ('pp_chk_research', 'PP CHK RESEARCH')
         ],
        string="Process Type", copy=False, readonly=True)
    from_date = fields.Date(string="From Date", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employees', required=True, readonly=True)

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    transaction_target = fields.Float(string="Transaction Target", currency_field='company_currency_id', tracking=True, readonly=True)
    transaction_achieved = fields.Float(string="Transaction Achieved", currency_field='company_currency_id', tracking=True, readonly=True)
    invoice_achieved = fields.Float(string="Invoice Achieved", currency_field='company_currency_id', tracking=True, readonly=True)
    invoice_target = fields.Float(string="Invoice Target", currency_field='company_currency_id', tracking=True, readonly=True)
    total_work_hours = fields.Float('Total Work Hours')
    # achieved_amount = fields.Monetary(string="Achieved Amount", currency_field='company_currency_id' ,tracking=True, readonly=True)
    auditor_target = fields.Float(string="Auditor Target")
    auditor_achieved = fields.Float(string="Auditor Achieved")
    original_transaction_target = fields.Float(string="Original Transaction Target",
                                               currency_field='company_currency_id', tracking=True)
    original_invoice_target = fields.Float(string="Original Invoice Target", currency_field='company_currency_id',
                                           tracking=True)
    original_auditor_target = fields.Float(string="Original Auditor Target")

    achievement_percentage = fields.Float(
        string="Achievement (%)", readonly=True, group_operator="avg", compute="_compute_achievement_percentage", store=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(EmployeeProduction, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        # If 'achievement_percentage' is in the fields, calculate the custom average
        if 'achievement_percentage' in fields:
            for group in result:
                group_domain = domain.copy()

                for gb in (groupby if isinstance(groupby, list) else [groupby]):
                    if gb in group:
                        group_value = group[gb]
                        if isinstance(group_value, tuple):
                            group_value = group_value[0]  # Extract ID from (ID, 'Name')

                        # Handle date grouping manually
                        if gb.endswith(":day"):
                            date_field = gb.split(":")[0]  # Extract 'from_date' from 'from_date:day'
                            group_domain.append((date_field, '=', group_value))
                        else:
                            group_domain.append((gb, '=', group_value))

                # Search for records in the current group
                records = self.search(group_domain)

                # Calculate the custom average
                division_count = 0
                invoice_target = sum(record.invoice_target for record in records)
                transaction_target = sum(record.transaction_target for record in records)
                auditor_target = sum(record.auditor_target for record in records)


                invoice_achieved = sum(record.invoice_achieved for record in records)
                transaction_achieved = sum(record.transaction_achieved for record in records)
                auditor_achieved = sum(record.auditor_achieved for record in records)

                achievement_total = 0
                target_total = 0
                if invoice_target > 0 and invoice_achieved > 0:
                    achievement_total += invoice_achieved
                    target_total += invoice_target
                if transaction_target > 0 and transaction_achieved > 0:
                    achievement_total += transaction_achieved
                    target_total += transaction_target
                if auditor_target > 0 and auditor_achieved > 0:
                    achievement_total += auditor_achieved
                    target_total += auditor_target



                # Avoid division by zero
                if target_total > 0:
                    achievement_percentage = achievement_total / target_total * 100
                else:
                    achievement_percentage = 0

                # Assign the calculated value to the group
                group['achievement_percentage'] = achievement_percentage

        return result

    @api.depends('invoice_achieved','auditor_achieved','transaction_achieved')
    def _compute_achievement_percentage(self):
        for rec in self:
            target_total = 0
            target_achieved = 0
            if rec.invoice_target > 0 and rec.invoice_achieved > 0:
                target_total+=rec.invoice_target
                target_achieved+=rec.invoice_achieved
            if rec.transaction_target > 0 and rec.transaction_achieved > 0:
                target_total+=rec.transaction_target
                target_achieved+=rec.transaction_achieved
            if rec.auditor_target > 0 and rec.auditor_achieved > 0:
                target_total+=rec.auditor_target
                target_achieved+=rec.auditor_achieved
            if target_total > 0:
                achievement_percentage = target_achieved / target_total * 100
            else:
                achievement_percentage = 0
            rec.achievement_percentage = achievement_percentage
