# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_type = fields.Selection(selection_add=[('user_id', 'User ID')])
    survey_type = fields.Selection(
        selection=[
            ("youth_survey", "Youth Survey"),
            ("supervisor_survey", "Supervisor Survey"),
            ("y@w_employee_survey", "Y@W Employee Survey"),
            ("all_users_survey", "All Users Survey")
        ],string="Survey Type")

    def validate_question(self, answer, comment=None):
        if self.question_type == 'user_id':
            if self.constr_mandatory and not answer:
                return {self.id: _('This question requires an answer.')}
            else:
                return {}
        else:
            return super(SurveyQuestion, self).validate_question(answer, comment=comment)


    
