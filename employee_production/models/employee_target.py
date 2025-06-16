from datetime import date, timedelta

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class EmployeeTarget(models.Model):
    _name = 'employee.target'
    _description = 'Employee Target'
    _order = "id desc"
    _rec_name = 'employee_id'

    process_type = fields.Selection(
        [('edm_process', 'EDM Process'), ('ecom_process', 'ECOM Process'), ('835_push', '835 Push'),
         ('pp_adjustments', 'PP ADJUSTMENTS'), ('pp_denials', 'PP DENIALS'),
         ('pp_corrections', 'PP CORRECTIONS'), ('pp_transfers', 'PP TRANSFERS'),
         ('pp_chk_research', 'PP CHK RESEARCH'), ('ams', 'AMS'), ('cama', 'CAMA'),
         ('pa', 'PA'), ('wta', 'WTA'),
         ('cama_charges', 'CAMA Charges'),
         ('pa_charges', 'PA Charges')],
        string="Process Type", copy=False)
    from_date = fields.Date(string="From Date")
    employee_id = fields.Many2one('hr.employee', string='Employees', required=True)
    employee_public_id = fields.Many2one('hr.employee.public', string='Employees',
                                         required=True)  # Need to add compute functionality
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',
                                          related='company_id.currency_id', readonly=True,
                                          help='Utility field to express threshold currency')

    transaction_target = fields.Float(string="Transaction Target", currency_field='company_currency_id', tracking=True)
    invoice_target = fields.Float(string="Invoice Target", currency_field='company_currency_id', tracking=True)
    achievement_type = fields.Selection(
        selection=[('transaction_invoice', 'Transaction & Invoice'), ('transaction', 'Transaction'),
                   ('invoice', 'Invoice'), ('auditor', 'Auditor')], string='Achievement Type')

    auditor_target = fields.Float(string="Auditor Target")

    def update_work_hours(self, target_date, employee, project_task_dict, process_type):
        if not process_type:
            project_working_hours = self.env['payment.posting']._read_group(
                [('posted_date', '=', target_date), ('assigned_to', '=', employee.user_id.id)],
                ['assigned_to', 'type'],
                ['total_work_hours:sum']
            )
        else:
            project_working_hours = self.env['payment.posting']._read_group(
                [('posted_date', '=', target_date), ('assigned_to', '=', employee.user_id.id),
                 ('type', 'in', process_type)],
                ['assigned_to', 'type'],
                ['total_work_hours:sum']
            )

        for working_hour in project_working_hours:
            work_type = working_hour[1]
            total_hours = working_hour[2]

            project_task = project_task_dict.get(work_type)
            if not project_task:
                continue

            existing_timesheet = project_task.timesheet_ids.filtered(
                lambda t: t.employee_id.id == employee.id and t.date == target_date
            )

            if existing_timesheet:
                existing_timesheet.sudo().write({'unit_amount': total_hours})
            else:
                task_vals = {
                    'employee_id': employee.id,
                    'unit_amount': total_hours,
                    'date': target_date,
                    'task_id': project_task.id,
                    'name': project_task.name,
                    'state': 'approved'
                }
                project_task.timesheet_ids.create(task_vals)

    def action_generate_employee_timesheet(self, from_date=False, to_date=False, type=False, name=False):
        project_task_dict = {}
        task_name_map = {
            'edm_process': 'EDM',
            'ecom_process': 'ECOM',
            '835_push': '835Push',
            'pp_adjustments': 'PP Adjustments',
            'pp_denials': 'PP Denials',
            'pp_corrections': 'PP Corrections',
            'pp_transfers': 'PP Transfer',
            'pp_chk_research': 'PP Chk Research',
        }

        employees = self.env['hr.employee'].search([('user_id', '!=', False)]) if not name else self.env[
            'hr.employee'].search([('name', '=', name)])
        employees_dict = {emp.user_id.id: emp for emp in employees}

        project = self.env['project.project'].search([('name', '=', 'Production')], limit=1)
        if not project:
            return

        for key, task_name in task_name_map.items():
            task = self.env['project.task'].search([('name', '=', task_name), ('project_id', '=', project.id)], limit=1)
            if task:
                project_task_dict[key] = task

        yesterday = date.today() - timedelta(days=1)
        from_date = fields.Date.from_string(from_date) if from_date else yesterday
        to_date = fields.Date.from_string(to_date) if to_date else yesterday

        while from_date <= to_date:
            domain = [('posted_date', '=', from_date)]
            if type:
                domain.append(('type', 'in', type))
            if name:
                employee = self.env['hr.employee'].search([('name', '=', name)], limit=1)
                if employee:
                    domain.append(('assigned_to', '=', employee.user_id.id))

            work_hours = self.env['payment.posting']._read_group(domain, ['assigned_to', 'type'],
                                                                 ['total_work_hours:sum'])
            etm_work_hours = self.env['payment.posting.etm']._read_group(domain, ['assigned_to', 'type'],
                                                                         ['total_work_hours:sum'])

            for work_hour in work_hours + etm_work_hours:
                user_id, work_type, total_hours = work_hour[0], work_hour[1], work_hour[2]
                project_task = project_task_dict.get(work_type)
                employee = employees_dict.get(user_id.id)
                if not project_task or not employee:
                    continue

                existing_timesheet = project_task.timesheet_ids.filtered(
                    lambda t: t.employee_id.id == employee.id and t.date == from_date)
                if existing_timesheet:
                    existing_timesheet.sudo().write({'unit_amount': total_hours})
                else:
                    project_task.timesheet_ids.create({
                        'employee_id': employee.id,
                        'unit_amount': total_hours,
                        'date': from_date,
                        'task_id': project_task.id,
                        'name': project_task.name,
                        'state': 'approved'
                    })

            from_date += timedelta(days=1)
                # stop

    # def action_generate_employee_timesheet(self, from_date=False, to_date=False, type=False, name=False):
    #     process_type = type
    #     employee_name = name
    #     yesterday_date = date.today() - timedelta(days=1)
    #     from_date = fields.Date.from_string(from_date) if from_date else yesterday_date
    #     to_date = fields.Date.from_string(to_date) if to_date else yesterday_date
    #
    #     project_task_dict = {}
    #     task_name_map = {
    #         'edm_process': 'EDM',
    #         'ecom_process': 'ECOM',
    #         '835_push': '835Push',
    #     }
    #
    #     project = self.env['project.project'].search([('name', '=', 'Production')])
    #     if not project:
    #         return  # Exit early if the project is not found
    #
    #     for task_key, task_name in task_name_map.items():
    #         project_task = self.env['project.task'].search([('name', '=', task_name), ('project_id', '=', project.id)],
    #                                                        limit=1)
    #         if project_task:
    #             project_task_dict[task_key] = project_task
    #
    #     yesterday_date = date.today() - timedelta(days=1)  # Keep it as a date object
    #     if not from_date:
    #         from_date = yesterday_date
    #     else:
    #         from_date = fields.Date.from_string(from_date)  # Convert to date object
    #     if not to_date:
    #         to_date = yesterday_date
    #     else:
    #         to_date = fields.Date.from_string(to_date)  # Convert to date object
    #     while from_date <= to_date:
    #
    #         target_date = from_date
    #         _logger.info(target_date)
    #         # Get completed targets
    #         if not employee_name:
    #             all_employees = self.env['hr.employee'].search([('user_id', '!=', False)])
    #         else:
    #             all_employees = self.env['hr.employee'].search([('name', '=', employee_name)])
    #         # all_employees = self.env['hr.employee'].browse(1229)
    #         for employee in all_employees:
    #             _logger.info(employee.name)
    #             self.update_work_hours(target_date, employee, project_task_dict, process_type)
    #         from_date += timedelta(days=1)
    #     self.send_employee_timesheets_completion_email()

    def action_generate_employee_production(self, from_date=False, to_date=False, type=False, name=False):
        yesterday_date = date.today() - timedelta(days=1)
        from_date = fields.Date.from_string(from_date) if from_date else yesterday_date
        to_date = fields.Date.from_string(to_date) if to_date else yesterday_date
        yesterday_date = date.today() - timedelta(days=1)  # Keep it as a date object
        if not from_date:
            from_date = yesterday_date
        else:
            from_date = fields.Date.from_string(from_date)  # Convert to date object
        if not to_date:
            to_date = yesterday_date
        else:
            to_date = fields.Date.from_string(to_date)  # Convert to date object
        while from_date <= to_date:
            target_date = from_date
            _logger.info(target_date)

            # Initialize the domain with the posted_date condition
            domain = [('posted_date', '=', target_date)]
            auditor_domain = [('audited_date', '=', target_date)]

            # Check if 'type' is provided
            if type:
                domain.append(('type', 'in', type))
                auditor_domain.append(('type', 'in', type))

            HrEmployee = self.env['hr.employee']
            # Check if 'name' is provided
            if name:
                # Search for the employee object based on the name
                employee_obj = HrEmployee.search([('name', '=', name)],
                                                 limit=1)  # Added limit to return a single record
                if employee_obj:
                    # Append conditions to the domain for assigned_to or auditor_user_id
                    domain.append(('assigned_to', '=', employee_obj.user_id.id))
                    auditor_domain.append(('auditor_user_id', '=', employee_obj.user_id.id))

            payment_posting_transactions = self.env['payment.posting'].search(domain)
            # Initialize a dictionary to store the results
            values = {}

            for payment_posting_transaction in payment_posting_transactions:
                assigned_to_id = payment_posting_transaction.assigned_to.id
                transaction_type = payment_posting_transaction.type

                # Ensure the structure exists for the assigned_to_id
                if assigned_to_id not in values:
                    values[assigned_to_id] = {}

                # Ensure the structure exists for the type
                if transaction_type not in values[assigned_to_id]:
                    values[assigned_to_id][transaction_type] = {'of_transactions': 0, 'auditor_invoice_count': 0,
                                                                'transaction': 0, 'total_work_hours': 0}

                # Add the of_transactions value
                values[assigned_to_id][transaction_type][
                    'of_transactions'] += payment_posting_transaction.of_transactions
                values[assigned_to_id][transaction_type][
                    'transaction'] += payment_posting_transaction.transaction
                values[assigned_to_id][transaction_type][
                    'total_work_hours'] += payment_posting_transaction.total_work_hours

            payment_posting_auditor_transactions = self.env['payment.posting'].search(auditor_domain)

            for payment_posting_auditor_transaction in payment_posting_auditor_transactions:
                auditor_user_id = payment_posting_auditor_transaction.auditor_user_id.id
                transaction_type = payment_posting_auditor_transaction.type

                # Ensure the structure exists for the assigned_to_id
                if auditor_user_id not in values:
                    values[auditor_user_id] = {}

                # Ensure the structure exists for the type
                if transaction_type not in values[auditor_user_id]:
                    values[auditor_user_id][transaction_type] = {'of_transactions': 0, 'auditor_invoice_count': 0,
                                                                 'transaction': 0, 'total_work_hours': 0}

                values[auditor_user_id][transaction_type][
                    'auditor_invoice_count'] += payment_posting_auditor_transaction.auditor_invoice_count

            for key, value in values.items():
                process_count = 0
                # Looping through the inner dictionary
                for inner_key, inner_value in value.items():
                    # Looping through the innermost dictionary
                    production_count = inner_value['of_transactions'] + inner_value['transaction']
                    auditor_count = inner_value['auditor_invoice_count']
                    if production_count > 0:
                        process_count += 1
                    if auditor_count > 0:
                        process_count += 1
                if process_count > 0:
                    _logger.info(key)
                    _logger.info("key")
                    employee = HrEmployee.search([('user_id', '=', key)])
                    if employee:
                        division_count = 0
                        for inner_key, inner_value in value.items():
                            target_set = self.search(
                                [('employee_id', '=', employee.id), ('from_date', '<=', target_date),
                                 ('process_type', '=', inner_key), ('achievement_type', '!=', 'auditor')], limit=1)
                            if target_set:
                                transaction_target = 0
                                invoice_target = 0
                                transaction_achieved = 0
                                invoice_achieved = 0
                                total_work_hours = inner_value['total_work_hours']
                                original_invoice_target = target_set.invoice_target
                                original_transaction_target = target_set.transaction_target
                                if target_set.invoice_target:
                                    invoice_achieved = inner_value['of_transactions']
                                    if employee.allow_multi_process:
                                        invoice_target = target_set.invoice_target / process_count
                                    else:
                                        invoice_target = target_set.invoice_target
                                if target_set.transaction_target > 0:
                                    transaction_achieved = inner_value['transaction']
                                    if employee.allow_multi_process:
                                        transaction_target = target_set.transaction_target / process_count
                                    else:
                                        transaction_target = target_set.transaction_target

                                production_vals = {
                                    'employee_id': target_set.employee_id.id,
                                    'process_type': inner_key,
                                    'from_date': target_date,
                                    'original_invoice_target': original_invoice_target,
                                    'invoice_target': invoice_target,
                                    'invoice_achieved': invoice_achieved,
                                    'original_transaction_target': original_transaction_target,
                                    'transaction_target': transaction_target,
                                    'transaction_achieved': transaction_achieved,
                                    'total_work_hours': total_work_hours,
                                    'company_id': target_set.company_id.id,
                                }
                                employee_production = self.env['employee.production'].search(
                                    [('employee_id', '=', target_set.employee_id.id), ('process_type', '=', inner_key),
                                     ('from_date', '=', target_date)])
                                if not employee_production:
                                    self.env['employee.production'].sudo().create(production_vals)
                                else:
                                    employee_production.sudo().write(production_vals)

                            target_set = self.search(
                                [('employee_id', '=', employee.id), ('from_date', '<=', target_date),
                                 ('process_type', '=', inner_key), ('achievement_type', '=', 'auditor')], limit=1)
                            if target_set:
                                total_work_hours = inner_value['total_work_hours']
                                auditor_invoice_count = 0
                                auditor_target = 0
                                original_auditor_target = target_set.auditor_target
                                if original_auditor_target > 0:
                                    auditor_invoice_count = inner_value['auditor_invoice_count']
                                    if employee.allow_multi_process:
                                        auditor_target = target_set.auditor_target / process_count
                                    else:
                                        auditor_target = target_set.auditor_target
                                production_vals = {
                                    'employee_id': target_set.employee_id.id,
                                    'process_type': inner_key,
                                    'from_date': target_date,
                                    'original_auditor_target': original_auditor_target,
                                    'auditor_target': auditor_target,
                                    'total_work_hours': total_work_hours,
                                    'auditor_achieved': auditor_invoice_count,
                                    'company_id': target_set.company_id.id,
                                }
                                employee_production = self.env['employee.production'].search(
                                    [('employee_id', '=', target_set.employee_id.id), ('process_type', '=', inner_key),
                                     ('from_date', '=', target_date)])
                                if not employee_production:
                                    self.env['employee.production'].sudo().create(production_vals)
                                else:
                                    employee_production.sudo().write(production_vals)

            payment_posting_etm_transactions = self.env['payment.posting.etm'].search(domain)
            payment_posting_etm_auditor_transactions = self.env['payment.posting.etm'].search(auditor_domain)
            # Initialize a dictionary to store the results
            values = {}

            for payment_posting_etm_transaction in payment_posting_etm_transactions:
                assigned_to_id = payment_posting_etm_transaction.assigned_to.id
                transaction_type = payment_posting_etm_transaction.type

                # Ensure the structure exists for the assigned_to_id
                if assigned_to_id not in values:
                    values[assigned_to_id] = {}

                # Ensure the structure exists for the type
                if transaction_type not in values[assigned_to_id]:
                    values[assigned_to_id][transaction_type] = {'no_of_transactions': 0, 'auditor_invoice_count': 0,
                                                                'total_work_hours': 0}

                # Add the of_transactions value
                values[assigned_to_id][transaction_type][
                    'no_of_transactions'] += payment_posting_etm_transaction.no_of_transactions
                values[assigned_to_id][transaction_type][
                    'total_work_hours'] += payment_posting_etm_transaction.total_work_hours

            for payment_posting_etm_auditor_transaction in payment_posting_etm_auditor_transactions:
                auditor_user_id = payment_posting_etm_auditor_transaction.auditor_user_id.id
                transaction_type = payment_posting_etm_transaction.type

                # Ensure the structure exists for the assigned_to_id
                if auditor_user_id not in values:
                    values[auditor_user_id] = {}

                # Ensure the structure exists for the type
                if transaction_type not in values[auditor_user_id]:
                    values[auditor_user_id][transaction_type] = {'no_of_transactions': 0, 'auditor_invoice_count': 0,
                                                                 'total_work_hours': 0}

                # Add the of_transactions value
                values[auditor_user_id][transaction_type][
                    'auditor_invoice_count'] += payment_posting_etm_transaction.auditor_invoice_count
                values[assigned_to_id][transaction_type][
                    'total_work_hours'] += payment_posting_etm_transaction.total_work_hours

            for key, value in values.items():
                process_count = 0
                # Looping through the inner dictionary
                for inner_key, inner_value in value.items():
                    # Looping through the innermost dictionary
                    production_count = inner_value['no_of_transactions']
                    auditor_count = inner_value['auditor_invoice_count']
                    if production_count > 0:
                        process_count += 1
                    if auditor_count > 0:
                        process_count += 1
                if process_count > 0:
                    employee = HrEmployee.search([('user_id', '=', key)])
                    if employee:
                        for inner_key, inner_value in value.items():
                            target_set = self.search(
                                [('employee_id', '=', employee.id), ('from_date', '<=', target_date),
                                 ('process_type', '=', inner_key), ('achievement_type', '!=', 'auditor')], limit=1)
                            if target_set:
                                transaction_target = 0
                                transaction_achieved = 0
                                total_work_hours = inner_value['total_work_hours']

                                original_transaction_target = target_set.transaction_target
                                if original_transaction_target:
                                    transaction_achieved = inner_value['no_of_transactions']
                                    if employee.allow_multi_process:
                                        transaction_target = target_set.transaction_target / process_count
                                    else:
                                        transaction_target = target_set.transaction_target

                                production_vals = {
                                    'employee_id': target_set.employee_id.id,
                                    'process_type': inner_key,
                                    'from_date': target_date,
                                    'original_transaction_target': original_transaction_target,
                                    'transaction_target': transaction_target,
                                    'transaction_achieved': transaction_achieved,
                                    'total_work_hours': total_work_hours,
                                    'company_id': target_set.company_id.id,
                                }
                                employee_production = self.env['employee.production'].search(
                                    [('employee_id', '=', target_set.employee_id.id), ('process_type', '=', inner_key),
                                     ('from_date', '=', target_date)])
                                if not employee_production:
                                    self.env['employee.production'].sudo().create(production_vals)
                                else:
                                    employee_production.sudo().write(production_vals)

                            target_set = self.search(
                                [('employee_id', '=', employee.id), ('from_date', '<=', target_date),
                                 ('process_type', '=', inner_key), ('achievement_type', '=', 'auditor')], limit=1)
                            if target_set:

                                total_work_hours = inner_value['total_work_hours']
                                auditor_invoice_count = 0
                                auditor_target = 0
                                original_auditor_target = target_set.auditor_target
                                if original_auditor_target > 0:
                                    auditor_invoice_count = inner_value['auditor_invoice_count']
                                    if employee.allow_multi_process:
                                        auditor_target = target_set.auditor_target / process_count
                                    else:
                                        auditor_target = target_set.auditor_target
                                production_vals = {
                                    'employee_id': target_set.employee_id.id,
                                    'process_type': inner_key,
                                    'from_date': target_date,
                                    'original_auditor_target': original_auditor_target,
                                    'auditor_target': auditor_target,
                                    'total_work_hours': total_work_hours,
                                    'auditor_achieved': auditor_invoice_count,
                                    'company_id': target_set.company_id.id,
                                }
                                employee_production = self.env['employee.production'].search(
                                    [('employee_id', '=', target_set.employee_id.id), ('process_type', '=', inner_key),
                                     ('from_date', '=', target_date)])
                                if not employee_production:
                                    self.env['employee.production'].sudo().create(production_vals)
                                else:
                                    employee_production.sudo().write(production_vals)
                            # first complete above
                            # stop
            # Get data from demo.process model
            print(domain)
            demo_process_transactions = self.env['demo.process'].search(domain)

            # Initialize a dictionary to store the results
            values = {}

            for demo_process in demo_process_transactions:
                assigned_to_id = demo_process.assigned_to.id
                transaction_type = demo_process.type

                if assigned_to_id not in values:
                    values[assigned_to_id] = {}

                if transaction_type not in values[assigned_to_id]:
                    values[assigned_to_id][transaction_type] = {
                        'final_count': 0,  # Changed from no_of_transactions
                        'total_work_hours': 0  # Changed from total_work_hours
                    }
                print(demo_process.final_count, 'final_count')
                print(demo_process.total_work_hours, 'total_work_hours')
                # Update values from demo.process
                values[assigned_to_id][transaction_type]['final_count'] += demo_process.final_count
                values[assigned_to_id][transaction_type]['total_work_hours'] += demo_process.total_work_hours

            for key, value in values.items():
                process_count = 0

                for inner_key, inner_value in value.items():
                    production_count = inner_value['final_count']
                    print(production_count, 'production_count')
                    if production_count > 0:
                        process_count += 1

                if process_count > 0:
                    employee = self.env['hr.employee'].search([('user_id', '=', key)], limit=1)
                    print(employee.name, 'employee')
                    if employee:
                        for inner_key, inner_value in value.items():
                            print(target_date, 'target_date')
                            print(inner_key, 'inner_key')
                            target_set = self.search([
                                ('employee_id', '=', employee.id),
                                ('from_date', '<=', target_date),
                                ('process_type', '=', inner_key),
                                ('achievement_type', '!=', 'auditor')
                            ], limit=1)
                            print(target_set, 'target_set')

                            if target_set:
                                print(process_count, 'process_count 2')
                                transaction_target = target_set.transaction_target
                                if employee.allow_multi_process:
                                    print(process_count, 'process_count')
                                    transaction_target /= process_count

                                production_vals = {
                                    'employee_id': employee.id,
                                    'process_type': inner_key,
                                    'from_date': target_date,
                                    'original_transaction_target': target_set.transaction_target,
                                    'transaction_target': transaction_target,
                                    'transaction_achieved': inner_value['final_count'],
                                    # Changed from no_of_transactions
                                    'total_work_hours': inner_value['total_work_hours'],  # Changed from total_work_hours
                                    'company_id': target_set.company_id.id,
                                }
                                print(production_vals, 'production_vals')
                                employee_production = self.env['employee.production'].search([
                                    ('employee_id', '=', employee.id),
                                    ('process_type', '=', inner_key),
                                    ('from_date', '=', target_date)
                                ])
                                if not employee_production:
                                    res = self.env['employee.production'].sudo().create(production_vals)
                                    print(res, 'res')
                                else:
                                    employee_production.sudo().write(production_vals)

            from_date += timedelta(days=1)

        self.send_employee_production_completion_email()

    # def action_generate_employee_production(self, from_date=False, to_date=False, type=False, name=False):
    #     project = self.env['project.project'].search([('name', '=', 'Production')])
    #     if not project:
    #         return  # Exit early if the project is not found
    #     task_name_map = {
    #         'edm_process': 'EDM',
    #         'ecom_process': 'ECOM',
    #         '835_push': '835Push',
    #     }
    #     project_task_dict = {}
    #     for task_key, task_name in task_name_map.items():
    #         project_task = self.env['project.task'].search([('name', '=', task_name), ('project_id', '=', project.id)],
    #                                                        limit=1)
    #         if project_task:
    #             project_task_dict[task_key] = project_task
    #     if not type:
    #         types = ['edm_process','ecom_process','835_push','pp_adjustments','pp_denials','pp_corrections','pp_transfers','pp_chk_research']
    #     else:
    #         types = type
    #     yesterday_date = date.today() - timedelta(days=1)
    #     from_date = fields.Date.from_string(from_date) if from_date else yesterday_date
    #     to_date = fields.Date.from_string(to_date) if to_date else yesterday_date
    #     yesterday_date = date.today() - timedelta(days=1)  # Keep it as a date object
    #     print(from_date,"from_date")
    #     print(to_date,"to_date")
    #     if not from_date:
    #         from_date = yesterday_date
    #     else:
    #         from_date = fields.Date.from_string(from_date)  # Convert to date object
    #     if not to_date:
    #         to_date = yesterday_date
    #     else:
    #         to_date = fields.Date.from_string(to_date)  # Convert to date object
    #     employee_name = name
    #
    #     if not employee_name:
    #         all_employees = self.env['hr.employee'].search([('user_id', '!=', False)])
    #     else:
    #         all_employees = self.env['hr.employee'].search([('name', '=', employee_name)])
    #         # all_employees = self.env['hr.employee'].browse(1229)
    #     print(all_employees)
    #     original_from_date = from_date
    #     original_to_date = to_date
    #     for employee in all_employees:
    #         yesterday_date = date.today() - timedelta(days=1)
    #         from_date = fields.Date.from_string(original_from_date) if original_from_date else yesterday_date
    #         to_date = fields.Date.from_string(original_to_date) if original_to_date else yesterday_date
    #         while from_date <= to_date:
    #             target_date = from_date
    #             print(target_date,'target_date')
    #             _logger.info(target_date)
    #             for type_item in types:
    #                 # Get completed targets
    #
    #                 _logger.info(employee.name)
    #                 _logger.info(target_date)
    #                 target_set = self.search([('employee_id', '=', employee.id), ('from_date', '<=', target_date),
    #                                           ('process_type', '=', type_item)], limit=1)
    #                 if target_set and target_set.process_type == 'edm_process' or target_set.process_type == 'ecom_process' or target_set.process_type == '835_push':
    #                     # For Production users
    #                     payment_posting_transactions = self.env['payment.posting']._read_group(
    #                         [('posted_date', '=', target_date), ('assigned_to', '=', employee.user_id.id),('type','=',type_item)],
    #                         ['assigned_to', 'type'],
    #                         ['of_transactions:sum', 'transaction:sum', 'total_work_hours:sum']
    #                     )
    #                     number_of_items_per_day = self.env['payment.posting']._read_group(
    #                         [('posted_date', '=', target_date), ('assigned_to', '=', employee.user_id.id)],
    #                         ['assigned_to', 'type'],
    #                         ['of_transactions:sum', 'transaction:sum', 'total_work_hours:sum']
    #                     )
    #                     number_of_items_per_day_audit = self.env['payment.posting']._read_group(
    #                         [('audited_date', '=', target_date), ('auditor_user_id', '=', employee.user_id.id)],
    #                         ['auditor_user_id', 'type'],
    #                         ['auditor_invoice_count:sum']
    #                     )
    #                     number_of_items = len(number_of_items_per_day) + len(number_of_items_per_day_audit)
    #                     for payment_posting_transaction in payment_posting_transactions:
    #                         if payment_posting_transaction and (
    #                                 payment_posting_transaction[2] > 0 or payment_posting_transaction[3] > 0):
    #                             type = payment_posting_transaction[1]
    #                             invoice_achieved = payment_posting_transaction[2]
    #                             transaction_achieved = payment_posting_transaction[3]
    #                             total_work_hours = payment_posting_transaction[4]
    #                             original_invoice_target = target_set.invoice_target
    #                             original_transaction_target = target_set.transaction_target
    #                             if employee.allow_multi_process:
    #                                 invoice_target = target_set.invoice_target / number_of_items
    #                                 transaction_target = target_set.transaction_target / number_of_items
    #                             else:
    #                                 invoice_target = target_set.invoice_target
    #                                 transaction_target = target_set.transaction_target
    #
    #                             if target_set.achievement_type == 'transaction':
    #                                 achievement_percentage = (transaction_achieved / transaction_target) * 100
    #                             elif target_set.achievement_type == 'invoice':
    #                                 achievement_percentage = (invoice_achieved / invoice_target) * 100
    #                             elif target_set.achievement_type == 'auditor':
    #                                 achievement_percentage = 0
    #                             else:
    #                                 total_target = transaction_target + invoice_target
    #                                 total_achieved = invoice_achieved + transaction_achieved
    #                                 achievement_percentage = (total_achieved / total_target) * 100
    #
    #                             production_vals = {
    #                                 'employee_id': target_set.employee_id.id,
    #                                 'process_type': type_item,
    #                                 'from_date': target_date,
    #                                 'original_invoice_target': original_invoice_target,
    #                                 'invoice_target': invoice_target,
    #                                 'auditor_target': target_set.auditor_target,
    #                                 'invoice_achieved': invoice_achieved,
    #                                 'original_transaction_target': original_transaction_target,
    #                                 'transaction_target': transaction_target,
    #                                 'transaction_achieved': transaction_achieved,
    #                                 'total_work_hours': total_work_hours,
    #                                 'achievement_percentage': achievement_percentage,
    #                                 'company_id': target_set.company_id.id,
    #                             }
    #                             employee_production = self.env['employee.production'].search(
    #                                 [('employee_id', '=', target_set.employee_id.id), ('process_type', '=', type_item),
    #                                  ('from_date', '=', target_date)])
    #                             if not employee_production:
    #                                 self.env['employee.production'].sudo().create(production_vals)
    #                             else:
    #                                 employee_production.sudo().write(production_vals)
    #
    #                     payment_posting_transactions_auditor = self.env['payment.posting']._read_group(
    #                         [('audited_date', '=', target_date), ('auditor_user_id', '=', employee.user_id.id),('type','=',type_item)],
    #                         ['auditor_user_id', 'type'],
    #                         ['auditor_invoice_count:sum']
    #                     )
    #
    #                     for payment_posting_transaction_auditor in payment_posting_transactions_auditor:
    #                         if payment_posting_transaction_auditor and payment_posting_transaction_auditor[2] and (
    #                                 payment_posting_transaction_auditor[2] > 0):
    #                             type = payment_posting_transaction_auditor[1]
    #                             auditor_achieved = payment_posting_transaction_auditor[2]
    #                             original_auditor_target = target_set.auditor_target
    #                             if employee.allow_multi_process:
    #                                 auditor_target = target_set.auditor_target / number_of_items
    #                             else:
    #                                 auditor_target = target_set.auditor_target
    #
    #                             if target_set.achievement_type == 'auditor':
    #                                 achievement_percentage = (auditor_achieved / auditor_target) * 100
    #                                 production_vals = {
    #                                     'employee_id': target_set.employee_id.id,
    #                                     'process_type': type,
    #                                     'from_date': target_date,
    #                                     'original_auditor_target': original_auditor_target,
    #                                     'auditor_target': auditor_target,
    #                                     'auditor_achieved': auditor_achieved,
    #                                     'achievement_percentage': achievement_percentage,
    #                                     'company_id': target_set.company_id.id,
    #                                 }
    #                                 employee_production = self.env['employee.production'].search(
    #                                     [('employee_id', '=', target_set.employee_id.id),
    #                                      ('process_type', '=', type), ('from_date', '=', target_date)])
    #                                 if not employee_production:
    #                                     self.env['employee.production'].sudo().create(production_vals)
    #                                 else:
    #                                     employee_production.sudo().write(production_vals)
    #
    #                 if target_set and target_set.process_type == 'pp_adjustments' or target_set.process_type == 'pp_denials' or target_set.process_type == 'pp_corrections' or target_set.process_type == 'pp_transfers' or target_set.process_type == 'pp_chk_research':
    #                     # For Production users
    #                     payment_posting_transactions = self.env['payment.posting.etm']._read_group(
    #                         [('posted_date', '=', target_date), ('assigned_to', '=', employee.user_id.id), ('type','=',type_item)],
    #                         ['assigned_to', 'type'],
    #                         ['no_of_transactions:sum', 'total_work_hours:sum']
    #                     )
    #                     number_of_items_per_day = self.env['payment.posting.etm']._read_group(
    #                         [('posted_date', '=', target_date), ('assigned_to', '=', employee.user_id.id)],
    #                         ['assigned_to', 'type'],
    #                         ['no_of_transactions:sum', 'total_work_hours:sum']
    #                     )
    #                     number_of_items_per_day_audit = self.env['payment.posting.etm']._read_group(
    #                         [('audited_date', '=', target_date), ('auditor_user_id', '=', employee.user_id.id)],
    #                         ['auditor_user_id', 'type'],
    #                         ['auditor_invoice_count:sum']
    #                     )
    #                     number_of_items = len(number_of_items_per_day) + len(number_of_items_per_day_audit)
    #                     for payment_posting_transaction in payment_posting_transactions:
    #                         if payment_posting_transaction and (payment_posting_transaction[2] > 0):
    #                             type = payment_posting_transaction[1]
    #                             transaction_achieved = payment_posting_transaction[2]
    #                             total_work_hours = payment_posting_transaction[3]
    #                             original_transaction_target = target_set.transaction_target
    #                             if employee.allow_multi_process:
    #                                 transaction_target = target_set.transaction_target / number_of_items
    #                             else:
    #                                 transaction_target = target_set.transaction_target
    #                             if target_set.achievement_type == 'transaction':
    #                                 achievement_percentage = (transaction_achieved / transaction_target) * 100
    #                             elif target_set.achievement_type == 'auditor':
    #                                 achievement_percentage = 0
    #                             else:
    #                                 total_target = transaction_target
    #                                 total_achieved = transaction_achieved
    #                                 achievement_percentage = (total_achieved / total_target) * 100
    #
    #                             production_vals = {
    #                                 'employee_id': target_set.employee_id.id,
    #                                 'process_type': type_item,
    #                                 'from_date': target_date,
    #                                 'auditor_target': target_set.auditor_target,
    #                                 'original_transaction_target': original_transaction_target,
    #                                 'transaction_target': transaction_target,
    #                                 'transaction_achieved': transaction_achieved,
    #                                 'total_work_hours': total_work_hours,
    #                                 'achievement_percentage': achievement_percentage,
    #                                 'company_id': target_set.company_id.id,
    #                             }
    #                             employee_production = self.env['employee.production'].search(
    #                                 [('employee_id', '=', target_set.employee_id.id), ('process_type', '=', type_item),
    #                                  ('from_date', '=', target_date)])
    #                             if not employee_production:
    #                                 self.env['employee.production'].sudo().create(production_vals)
    #                             else:
    #                                 employee_production.sudo().write(production_vals)
    #
    #                     payment_posting_transactions_auditor = self.env['payment.posting.etm']._read_group(
    #                         [('audited_date', '=', target_date), ('auditor_user_id', '=', employee.user_id.id),('type','=',type_item)],
    #                         ['auditor_user_id', 'type'],
    #                         ['auditor_invoice_count:sum']
    #                     )
    #
    #
    #                     for payment_posting_transaction_auditor in payment_posting_transactions_auditor:
    #                         if payment_posting_transaction_auditor and payment_posting_transaction_auditor[2] and (
    #                                 payment_posting_transaction_auditor[2] > 0):
    #                             type = payment_posting_transaction_auditor[1]
    #                             auditor_achieved = payment_posting_transaction_auditor[2]
    #                             original_auditor_target = target_set.auditor_target
    #                             if employee.allow_multi_process:
    #                                 auditor_target = target_set.auditor_target / number_of_items
    #                             else:
    #                                 auditor_target = target_set.auditor_target
    #
    #                             if target_set.achievement_type == 'auditor':
    #                                 achievement_percentage = (auditor_achieved / auditor_target) * 100
    #                                 production_vals = {
    #                                     'employee_id': target_set.employee_id.id,
    #                                     'process_type': type,
    #                                     'from_date': target_date,
    #                                     'original_auditor_target': original_auditor_target,
    #                                     'auditor_target': auditor_target,
    #                                     'auditor_achieved': auditor_achieved,
    #                                     'achievement_percentage': achievement_percentage,
    #                                     'company_id': target_set.company_id.id,
    #                                 }
    #                                 employee_production = self.env['employee.production'].search(
    #                                     [('employee_id', '=', target_set.employee_id.id),
    #                                      ('process_type', '=', type), ('from_date', '=', target_date)])
    #                                 if not employee_production:
    #                                     self.env['employee.production'].sudo().create(production_vals)
    #                                 else:
    #                                     employee_production.sudo().write(production_vals)
    #             from_date += timedelta(days=1)
    #     self.send_employee_production_completion_email()

    def send_employee_production_completion_email(self):
        # Define email details
        email_subject = "Employee Production Generated"
        email_body = f"""
        Dear User,

        The employee production records have been successfully generated

        """
        recipient_email = "rizwan.s@idigimeta.com"
        company = self.env.user.company_id
        sender_email = company.email or 'no-reply@example.com'

        # Create and send the email
        mail_values = {
            'subject': email_subject,
            'body_html': email_body,
            'email_to': recipient_email,
            'email_from': sender_email,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

        _logger.info(f"Email sent successfully to {recipient_email} regarding production generation.")

    def send_employee_timesheets_completion_email(self):
        email_subject = "Employee Timesheets Processed"
        email_body = f"""
        Dear User,

        The employee timesheets have been successfully processed

        """
        recipient_email = "rizwan.s@idigimeta.com"
        company = self.env.user.company_id
        sender_email = company.email or 'no-reply@example.com'

        # Create and send the email
        mail_values = {
            'subject': email_subject,
            'body_html': email_body,
            'email_to': recipient_email,
            'email_from': sender_email,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()

        _logger.info(f"Email sent successfully to {recipient_email} regarding employee timesheets.")
