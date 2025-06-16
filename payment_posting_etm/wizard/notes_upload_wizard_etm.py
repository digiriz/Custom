import base64
import io
from odoo import models, fields, _
from odoo.exceptions import UserError
import pandas as pd
import datetime



class NotesUploadWizardETM(models.TransientModel):
    _name = 'notes.upload.wizard.etm'
    _description = 'Notes Upload Wizard'

    file_data = fields.Binary("Upload File", required=True)
    file_name = fields.Char("File Name")

    def action_read_file(self):
        """ Reads uploaded Excel (.xlsx) or ODS (.ods) files and creates records in Odoo """
        active_id = self.env.context.get('active_id')
        if not self.file_data or not self.file_name:
            return

        file_content = io.BytesIO(base64.b64decode(self.file_data))
        file_extension = self.file_name.split('.')[-1].lower()

        try:
            # Read file using pandas
            engine = "odf" if file_extension == "ods" else None
            df = pd.read_excel(file_content, engine=engine)

            # Convert datetime fields to string format (YYYY-MM-DD)
            for col in df.select_dtypes(include=['datetime64', 'datetime']):
                df[col] = df[col].dt.strftime('%Y-%m-%d')

            # Fill NaN values and extract required columns
            rows = df.fillna('').iloc[:, :5].values.tolist()

        except Exception as e:
            raise UserError(f"Error reading file: {str(e)}")

        records_created = 0
        excel_start_date = datetime.datetime(1899, 12, 30)

        for row in rows:
            # Access values directly using indices
            note_vals = {
                'payment_posting_etm_id': active_id,
                'invoice_no': row[0],
                'mrn': row[1],
                'dos': row[2] if row[2] else False,  # Set False if empty
                'etm_id': row[3],
                'amount': row[4]
            }

            # Convert Excel serial date if necessary
            # if isinstance(note_vals['dos'], float):
            #     note_vals['dos'] = (excel_start_date + datetime.timedelta(days=note_vals['dos'])).strftime('%Y-%m-%d')
            self.env['payment.posting.etm.invoice'].create(note_vals)
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


