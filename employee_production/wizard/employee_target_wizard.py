from odoo import models, fields, api

class EmployeeTargetWizard(models.TransientModel):
    _name = 'employee.target.wizard'
    _description = 'Employee Target Wizard'

    employee_target_line_ids = fields.One2many('employee.target.line', 'employee_target_wizard_id',
                                              string="Employee Target Line")

    def action_generate_employee_target(self):
        # Loop through each line in the wizard
        for line in self.employee_target_line_ids:
            if line.process_type:  # If process_type exists, process it separately
                for employee in line.employee_ids:
                    self.env['employee.target'].create({
                        'employee_id': employee.id,
                        'process_type': line.process_type,
                        'from_date': line.from_date,
                        'transaction_target': line.transaction_target,
                        'invoice_target': line.invoice_target,
                        'company_id': line.company_id.id,
                        'achievement_type': line.achievement_type,
                        'auditor_target': line.auditor_target,
                    })
                domain = [('process_type', 'in', ['edm_process', 'ecom_process', '835_push',
        'pp_adjustments', 'pp_denials', 'pp_corrections', 'pp_transfers', 'pp_chk_research'])]

            if line.demo_process_type:  # If demo_process_type exists, process it separately
                for employee in line.employee_ids:
                    self.env['employee.target'].create({
                        'employee_id': employee.id,
                        'process_type': line.demo_process_type,  # Use demo_process_type instead
                        'from_date': line.from_date,
                        'transaction_target': line.transaction_target,
                        'invoice_target': line.invoice_target,
                        'company_id': line.company_id.id,
                        'achievement_type': line.achievement_type,
                        'auditor_target': line.auditor_target,
                    })
                domain = [('process_type', 'in', ['ams', 'cama', 'pa', 'wta', 'cama_charges', 'pa_charges'])]

        views = [
            (self.env.ref('payment_posting.view_employee_target_tree').id, 'tree'),
            (self.env.ref('payment_posting.view_employee_target_form').id, 'form')
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employee Target',
            'res_model': 'employee.target',
            'view_mode': 'tree,form,search,pivot',
            'domain': domain,
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
         ('pp_chk_research', 'PP CHK RESEARCH')
         ],
        string="Process Type", copy=False)
    demo_process_type = fields.Selection(
        [
         ('ams', 'AMS'), ('cama', 'CAMA'),
         ('pa', 'PA'), ('wta', 'WTA'),
         ('cama_charges', 'CAMA Charges'),
         ('pa_charges', 'PA Charges')
         ],
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