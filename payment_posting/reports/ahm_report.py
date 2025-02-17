from odoo import fields, models, _
from odoo.exceptions import UserError


class AhmReport(models.TransientModel):
    _name = "ahm.report"
    _description = "AHM Report"

    batch_numbers = fields.Text('Input Details', required=True)
    type = fields.Selection([('edm_process', 'EDM Process'),('ecom_process', 'ECOM Process'),
                             ('835_push', '835 Push'),('etm', 'ETM'),], string="Process Type", copy=False, required=True)
    selection_field = fields.Selection([('batch','Batch'),('bar_batch','Bar Batch'),
                                        ('division','Division'),('check_eft_number', 'Check/EFT Number'),
                                        ('inv_enc','Inv Enc'),('id','ID'),],string='Select From')

    def ahm_report_action(self):
        """
                After clicking the view button, redirect to the report viview_employee_production_treeew with a domain filter
                on the 'payment.posting' model based on the provided batch numbers.
                """
        # Replace newlines with commas, then split the batch numbers by either comma or newline
        batch_numbers = self.batch_numbers.replace('\n', ',').split(',') if self.batch_numbers else []

        # Strip any leading/trailing whitespace and filter out empty strings
        batch_numbers = [batch.strip() for batch in batch_numbers if batch.strip()]
        domain = []
        res_model = ''
        if self.selection_field == 'batch':
            domain = [('type', '=', self.type), ('edm_batch', 'in', batch_numbers)]
        if self.selection_field == 'bar_batch':
            domain = [('type', '=', self.type), ('bar_batch', 'in', batch_numbers)]
        if self.selection_field == 'check_eft_number':
            domain = [('type', '=', self.type), '|',('check_s','in', batch_numbers), ('check_eft_number', 'in', batch_numbers)]
        if self.selection_field == 'inv_enc':
            domain = [('type', 'in', ['pp_adjustments', 'pp_denials',
                                     'pp_corrections','pp_transfers','pp_chk_research']),('inv_enc','in', batch_numbers)]
        if self.selection_field == 'id':
            domain = [('type', 'in', ['pp_adjustments', 'pp_denials',
                                      'pp_corrections', 'pp_transfers', 'pp_chk_research']),
                      ('etm_id', 'in', batch_numbers)]
        if self.selection_field == 'division':
            division_ids = []
            for division_name in batch_numbers:
                division_id = self.env['division.master'].search(['|',('division_code','=',division_name),('division_name','=',division_name)])
                division_ids.append(division_id.id)
            if not division_ids:
                raise UserError('No divisions are matched')
            domain = [('type', '=', self.type), ('division_id', 'in', division_ids)]
        if self.type == 'edm_process':
            views = [
                (self.env.ref('payment_posting.view_payment_posting_production_tree').id, 'tree'),
                (self.env.ref('payment_posting.view_payment_posting_production_form').id, 'form')
            ]
            res_model = 'payment.posting'
        if self.type == 'ecom_process':
            views = [
                (self.env.ref('payment_posting.view_payment_posting_production_ecom_tree').id, 'tree'),
                (self.env.ref('payment_posting.view_payment_posting_production_ecom_form').id, 'form')
            ]
            res_model = 'payment.posting'
        if self.type == '835_push':
            views = [
                (self.env.ref('payment_posting.view_payment_posting_production_835_push_tree').id, 'tree'),
                (self.env.ref('payment_posting.view_payment_posting_production_835_push_form').id, 'form')
            ]
            res_model = 'payment.posting'
        if self.type == 'etm':
            views = [
                (self.env.ref('payment_posting_etm.view_payment_posting_etm_pp_adjustments_reporting_tree').id, 'tree'),
                (self.env.ref('payment_posting_etm.view_payment_posting_etm_pp_adjustments_reporting_form').id, 'form')
            ]
            res_model = 'payment.posting.etm'

        # Redirect to the action with the filtered domain
        return {
            'type': 'ir.actions.act_window',
            'name': _(' '),
            'res_model': res_model,
            'view_mode': 'tree,form,search,pivot',
            'domain': domain,
            'views': views,
        }

