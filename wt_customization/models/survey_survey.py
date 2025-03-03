# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _


class Survey(models.Model):
    _inherit = 'survey.survey'


    youth_user_id = fields.Many2one('hr.employee', string="User")
    journey_id  = fields.Many2one('journey.journey')
    cohort_id = fields.Many2one('cohort.cohort')
    host_site_id = fields.Many2one(comodel_name="res.partner",string="Host Site")
    partner_id = fields.Many2one('res.partner')


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    value_user_id = fields.Many2one('hr.employee')
    answer_type = fields.Selection(selection_add=[('user_id', 'User ID')])
    

    @api.depends('answer_type')
    def _compute_display_name(self):
        for line in self:
            if line.answer_type == 'user_id':
                line.display_name = line.value_user_id.name or ''
        super(SurveyUserInputLine, self)._compute_display_name()