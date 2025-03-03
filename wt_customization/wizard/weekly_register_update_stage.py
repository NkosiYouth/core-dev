from odoo import models, fields, api
import base64
import io
import pandas as pd
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class ImportWeeklyRegister(models.TransientModel):
    _name = 'update.weekly.register'
    _description = 'Import Weekly Register'

    file = fields.Binary(string="Upload File", required=True)
    file_name = fields.Char(string="File Name")

    def action_import(self):
        """Process the uploaded XLSX file and update related project.task records"""
        self.ensure_one()

        if not self.file:
            return

        # Decode and read the file
        file_data = base64.b64decode(self.file)
        xlsx_file = io.BytesIO(file_data)

        try:
            df = pd.read_excel(xlsx_file, dtype=str)  # Read as string to avoid numeric conversion issues
        except Exception as e:
            _logger.error("Error reading Excel file: %s", e)
            return

        # Print out columns for debugging
        _logger.debug("Columns in the uploaded file: %s", df.columns)

        # Strip any leading/trailing spaces from column names
        df.columns = df.columns.str.strip()

        # Ensure required columns exist
        required_columns = ['Youth/Identification No', 'Stage', 'Week Start', 'Week End']
        if not all(col in df.columns for col in required_columns):
            _logger.error("Missing required columns in the file")
            return

        self._update_weekly_register(df)

    def _update_weekly_register(self, df):
        """Update related project.task records based on the XLSX data"""
        Employee = self.env['hr.employee'].sudo()
        ProjectTask = self.env['project.task'].sudo()  # Tasks are stored here

        for _, row in df.iterrows():
            identification_no = row['Youth/Identification No']
            stage_name = row['Stage']
            # Extract and log the date values
            week_start_str = str(row['Week Start']) if not pd.isna(row['Week Start']) else ''
            week_end_str = str(row['Week End']) if not pd.isna(row['Week End']) else ''

            week_start_str = week_start_str.split(' ')[0] if ' ' in week_start_str else week_start_str
            week_end_str = week_end_str.split(' ')[0] if ' ' in week_end_str else week_end_str



            # Find employee by Identification No
            employee = Employee.search([('identification_id', '=', identification_no)], limit=1)
            if not employee:
                _logger.warning("Employee not found for ID: %s", identification_no)
                continue

            # Find project.task using week_start and week_end instead of title
            task = ProjectTask.search([
                ('id', 'in', employee.register_ids.ids),
                ('week_start', '=', week_start_str),
                
            ], limit=1)

            if not task:
                _logger.warning("No task found for employee %s in the week %s - %s", employee.name, week_start_str, week_end_str)
                continue

            # Find the stage
            stage = self.env['project.task.type'].search([('name', '=', stage_name)], limit=1)


            if not stage:
                _logger.warning("Stage '%s' not found", stage_name)
                continue
            
            if task and stage.id != task.stage_id.id:
                task.sudo().with_context(bypass_stage=True).write({'stage_id': stage.id})
                self._cr.commit()
                _logger.info("********- Updated task: %s to stage: %s", task.name, task.stage_id.name)
