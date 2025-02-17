from odoo import models, fields, api

class EmployeeTargetWizard(models.TransientModel):
    _name = 'employee.target.wizard'
    _description = 'Employee Target Wizard'

    employee_target_line_ids = fields.One2many('employee.target.line', 'employee_target_wizard_id',
                                              string="Employee Target Line")

    def action_generate_employee_target(self):
        # Loop through each line in the wizard

        for line in self.employee_target_line_ids:
            # Get the values for this line
            transaction_target = line.transaction_target
            invoice_target = line.invoice_target
            line_process_type = line.process_type
            line_from_date = line.from_date

            # Loop through each employee in the line's employee_ids
            for employee in line.employee_ids:
                # Create a new `employee.target` record for each employee with line values
                self.env['employee.target'].create({
                    'employee_id': employee.id,
                    'process_type': line_process_type,
                    'from_date': line_from_date,
                    'transaction_target': transaction_target,
                    'invoice_target': invoice_target,
                    'company_id': line.company_id.id,
                    'achievement_type': line.achievement_type,
                    'auditor_target': line.auditor_target,
                })

        views = [
            (self.env.ref('payment_posting.view_employee_target_tree').id, 'tree'),
            (self.env.ref('payment_posting.view_employee_target_form').id, 'form')
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Target',
            'res_model': 'employee.target',
            'view_mode': 'tree,form,search,pivot',
            'domain': [],
            'views': views,
        }



class EmployeeTargetLine(models.TransientModel):
    _name = 'employee.target.line'
    _description = 'Employee Target Line'

    process_type = fields.Selection(
        [('edm_process', 'EDM Process'),
         ('ecom_process', 'ECOM Process'),
         ('835_push', '835 Push'),
         ('pp_adjustments', 'PP ADJUSTMENTS'), ('pp_denials', 'PP DENIALS'),
         ('pp_corrections', 'PP CORRECTIONS'), ('pp_transfers', 'PP TRANSFERS'),
         ('pp_chk_research', 'PP CHK RESEARCH') ],
        string="Process Type", copy=False)
    from_date = fields.Date(string="From Date")
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')
    employee_target_wizard_id = fields.Many2one('employee.target.wizard', string='Employee Target Wizard', readonly=True,
                                          help='Utility field to express threshold currency')
    transaction_target = fields.Float(string="Transaction Target", currency_field='company_currency_id', tracking=True)
    invoice_target = fields.Float(string="Invoice Target", currency_field='company_currency_id', tracking=True)
    achievement_type = fields.Selection(selection=[('transaction_invoice','Transaction & Invoice'),('transaction','Transaction'),('invoice','Invoice'),('auditor','Auditor')],string='Achievement Type')
    auditor_target = fields.Float(string="Auditor Target")