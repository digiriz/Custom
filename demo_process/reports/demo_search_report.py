from odoo import fields, models, _
from odoo.exceptions import UserError


class DemoSearchReport(models.TransientModel):
    _name = "demo.search.report"
    _description = "Demo Search Report"


    record_type = fields.Selection([('batch', 'Batch'), ('record', 'Record')], string="Batch / Record", required=False)
    batch_fields = fields.Selection([('facility','Facility'),('patient_no','Patient No'),('description','Description')],string="Batch Fields")
    record_fields = fields.Selection([('dos', 'DOs'),('facility','Facility')], string='Record Fields')
    record_details = fields.Text('Record Details', required=False)
    batch_details = fields.Text('Batch Details', required=False)
    type = fields.Selection([('ams', 'AMS'),('cama', 'CAMA'), ('pa', 'PA'),('wta', 'WTA'),('cama_charges', 'CAMA Charges'),('pa_charges', 'PA Charges')], string="Process Type", copy=False, required=True)


    def demo_search_report_action(self):
        """
                After clicking the view button, redirect to the report viview_employee_production_treeew with a domain filter
                on the 'payment.posting' model based on the provided batch numbers.
                """
        # Replace newlines with commas, then split the batch numbers by either comma or newline
        domain = [('type', '=', self.type)]
        if self.record_type == 'batch':
            input_detail_list = self.batch_details.replace('\n', ',').split(',') if self.batch_details else []
            input_detail_list_space = [batch.strip() for batch in input_detail_list if batch.strip()]
            if self.batch_fields == 'facility':
                facility_obj = self.env['facility.master'].search([('name','in',input_detail_list_space)])
                domain.append(('facility', 'in', facility_obj.ids))
            if self.batch_fields == 'patient_no':
                domain.append(('patient_no', 'in', input_detail_list_space))
            if self.batch_fields == 'description':
                domain.append(('description', 'in', input_detail_list_space))

            if self.type == 'ams':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_demo_process_ams_reporting")
            if self.type == 'cama':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_demo_process_cama_reporting")
            if self.type == 'pa':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_demo_process_pa_reporting")
            if self.type == 'wta':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_demo_process_wta_reporting")
            if self.type == 'cama_charges':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_demo_process_cama_charges_reporting")
            if self.type == 'pa_charges':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_demo_process_pa_charges_reporting")

        if self.record_type == 'record':
            input_detail_list = self.record_details.replace('\n', ',').split(',') if self.record_details else []
            input_detail_list_space = [batch.strip() for batch in input_detail_list if batch.strip()]
            if self.batch_fields == 'facility':
                facility_obj = self.env['facility.master'].search([('name','in',input_detail_list_space)])
                domain.append(('facility', 'in', facility_obj.ids))
            if self.batch_fields == 'dos':
                domain.append(('dos', 'in', input_detail_list_space))

            if self.type == 'ams':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_reporting_demo_process_ams_reporting")
            if self.type == 'cama':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_reporting_demo_process_cama_reporting")
            if self.type == 'pa':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_reporting_demo_process_pa_reporting")
            if self.type == 'wta':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_reporting_demo_process_wta_reporting")
            if self.type == 'cama_charges':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_reporting_demo_process_cama_charges_reporting")
            if self.type == 'pa_charges':
                action = self.env["ir.actions.act_window"]._for_xml_id("demo_process.action_reporting_demo_process_pa_charges_reporting")


        # Redirect to the action with the filtered domain
        action["domain"] = domain
        return action

