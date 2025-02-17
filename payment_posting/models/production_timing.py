from odoo import models, fields, api
from datetime import datetime

class ProductionTiming(models.Model):
    _name = 'production.timing'
    _description = 'Production Timing'

    production_start_time = fields.Datetime(string="Start Time")
    production_end_time = fields.Datetime(string="End Time")
    duration = fields.Float(string="Work Hours", compute="_compute_total_time")
    payment_posting_id = fields.Many2one('payment.posting', string="Payment Posting")
    payment_posting_etm_id = fields.Many2one('payment.posting.etm', string="Payment Posting ETM")


    @api.depends('production_start_time', 'production_end_time')
    def _compute_total_time(self):
        for record in self:
            if record.production_start_time and record.production_end_time:
                # Calculate the duration as the difference in hours
                duration = record.production_end_time - record.production_start_time
                duration_in_hours = duration.total_seconds() / 3600  # Convert seconds to hours
                record.duration = duration_in_hours
            else:
                record.duration = 0.0


