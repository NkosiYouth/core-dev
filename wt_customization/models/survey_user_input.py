# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    employee_id = fields.Many2one('hr.employee', "Employee")

    def save_lines(self, question, answer, comment=None):
        """ Save answers to questions, depending on question type.

            If an answer already exists for a question and user_input_id, it will be
            overwritten (or deleted for 'choice' questions) (to maintain data consistency).
        """
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])

        if question.question_type in ['char_box', 'text_box', 'numerical_box', 'date', 'datetime', 'user_id']:
            if question.question_type == 'user_id':
                answer = int(answer)
                self.employee_id = answer
            self._save_line_simple_answer(question, old_answers, answer)
            if question.save_as_email and answer:
                self.write({'email': answer})
            if question.save_as_nickname and answer:
                self.write({'nickname': answer})

        elif question.question_type in ['simple_choice', 'multiple_choice']:
            self._save_line_choice(question, old_answers, answer, comment)

        elif question.question_type == 'matrix':
            self._save_line_matrix(question, old_answers, answer, comment)

        elif question.question_type == 'upload_file':  # Added support for file uploads
            return self._save_line_file(question, old_answers, answer)

        else:
            raise AttributeError(f"{question.question_type}: This type of question has no saving function.")

    def _save_line_file(self, question, old_answers, answer):
        """ Save file uploads correctly. """
        if not isinstance(answer, list) or len(answer) < 2:
            raise ValueError("Invalid file upload answer format")

        vals = self._get_line_answer_file_upload_values(question, answer)
        if old_answers:
            old_answers.write(vals)
            return old_answers
        return self.env['survey.user_input.line'].create(vals)

    def _get_line_answer_file_upload_values(self, question, answer):
        """ Get values for creating/updating a user input line for a file upload. """
        file_data, file_names = answer

        if not isinstance(file_data, list) or not isinstance(file_names, list):
            raise ValueError("Expected list format for file data and filenames")

        attachment_ids = []
        for data, name in zip(file_data, file_names):
            attachment = self.env['ir.attachment'].create({
                'name': name,
                'type': 'binary',
                'datas': data,
            })
            attachment_ids.append(attachment.id)

        return {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': 'upload_file',
            'value_file_data_ids': [(6, 0, attachment_ids)],  # Many2many field fix
        }
