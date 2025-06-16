from odoo import models, fields


class DemoProcessNotes(models.Model):
    _name = 'demo.process.notes'
    _description = 'Demo Process Notes'
    # _rec_name = 'etm_id'
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _rec_name = 'date_image'

    demo_process_id = fields.Many2one('demo.process', ondelete='cascade')
    date_image = fields.Date('Date Image')
    imaging_type = fields.Char('Imaging Type')
    description = fields.Text('Description')
    date_entered = fields.Date('Date Entered')
    page_count = fields.Integer('Page Count')
    entered_by = fields.Char('Entered by')
    patient_no = fields.Char('Patient No')
    notes = fields.Text('Notes')
    reporting_remark = fields.Text('Reporting Remark')
    error_mark = fields.Boolean('Error Mark')
    demo_station_id = fields.Many2one('demo.station','Demo Station')
    type = fields.Selection(related="demo_process_id.type", store=True)
    dos = fields.Date(related="demo_process_id.dos", store=True)
    facility = fields.Many2one(related="demo_process_id.facility", store=True)
    received_date = fields.Date(related="demo_process_id.received_date", store=True)
    assigned_employee_id = fields.Many2one(related="demo_process_id.assigned_employee_id")
    assigned_to = fields.Many2one(related="demo_process_id.assigned_to", store=True)
    assigned_date = fields.Date(related="demo_process_id.assigned_date", store=True)
    select = fields.Boolean('Select', default=False)
    assigned_employee_id = fields.Many2one('hr.employee', 'Assigned To',
                                           domain=[("category_ids.name", 'in', ['Demo Process'])])

    assigned_date = fields.Date(string="Assigned Date", copy=False)


