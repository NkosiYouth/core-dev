# -*- coding: utf-8 -*-
from odoo import models, fields

class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    answer_type = fields.Selection(selection_add=[('upload_file', 'File Upload')])

    value_file_data_ids = fields.Many2many(
        'ir.attachment', 
        string="Uploaded Files",
        help="Stores uploaded file attachments."
    )
