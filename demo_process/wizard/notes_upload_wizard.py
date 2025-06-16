import io
import base64
from odoo import models, fields
from odoo.exceptions import UserError
import pandas as pd


class NotesUploadWizard(models.TransientModel):
    _name = 'notes.upload.wizard'
    _description = 'Notes Upload Wizard'

    file_data = fields.Binary("Upload File", required=True)
    file_name = fields.Char("File Name")

    def action_read_file(self):
        """ Reads uploaded Excel (.xlsx) or ODS (.ods) files and creates records in Odoo """
        active_id = self.env.context.get('active_id')
        if not self.file_data or not self.file_name:
            raise UserError("Please upload a valid file.")

        file_content = io.BytesIO(base64.b64decode(self.file_data))
        file_extension = self.file_name.split('.')[-1].lower()
        records_created = 0
        rows = []

        try:
            # Read file using pandas
            engine = "odf" if file_extension == "ods" else None
            df = pd.read_excel(file_content, engine=engine, dtype=str)

            # Convert date columns to string format if applicable
            for col in df.select_dtypes(include=['datetime64', 'datetime']):
                df[col] = df[col].dt.strftime('%Y-%m-%d')

            # Fill NaN values and extract first 13 columns
            rows = df.fillna('').iloc[:, :13].values.tolist()

        except Exception as e:
            raise UserError(f"Error reading file: {str(e)}")

        records_created = 0
        for row in rows:
            location = row[12]
            demo_station_obj = self.env['demo.station'].search([('name', '=', location)], limit=1)
            if not demo_station_obj:
                raise UserError(f"Demo station - {location} - Not available")

            note_vals = {
                'demo_process_id': active_id,
                'date_image': row[0],
                'imaging_type': row[1],
                'description': row[2],
                'date_entered': row[3],
                'page_count': row[4],
                'entered_by': row[7],
                'patient_no': row[10],
                'notes': row[11],
                'demo_station_id': demo_station_obj.id
            }

            self.env['demo.process.notes'].create(note_vals)
            records_created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Imported Successfully',
                'message': f"{records_created} Notes Created",
                'type': 'success',
                'sticky': False,
            }
        }



