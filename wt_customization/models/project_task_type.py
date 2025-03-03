# -*- coding: utf-8 -*-

from odoo import models,fields, api


class JourneySession(models.Model):
    _name = "journey.session"

    name = fields.Char("Session name")


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    journey_id = fields.Many2one('journey.journey')
    session_link = fields.Char('Session Link')
    session_deadline = fields.Datetime('Session Deadline')
    session_id = fields.Many2one('journey.session', string="Session name")
    session_type = fields.Selection(
         selection=[('online', 'Online'), ('in_person', 'In Person')],
         string="Session Type",
         required=True,
         help="Type of session: Online or In Person"
     )
    session_duration = fields.Float('Duration', compute="compute_session_duration")
    session_start = fields.Datetime('Session Start')

    @api.depends('session_deadline', 'session_start')
    def compute_session_duration(self):
        for rec in self:
            rec.session_duration = False
            if rec.session_start and rec.session_deadline:
                diff = rec.session_deadline - rec.session_start
                if diff.days:
                    rec.session_duration = diff.days * 86400 / 60 / 60
                else:
                    rec.session_duration = (rec.session_deadline - rec.session_start).seconds / 60 / 60


    @api.onchange('session_id')
    def onchange_session_name(self):
        if self.session_id:
            self.name = self.session_id.name
        else:
            self.name = False
    @api.onchange('project_ids')
    def onchange_project_ids(self):
        if self.project_ids:
            team_ids = []
            for project in self.project_ids:
                team_id = self.env['helpdesk.ticket.team'].search([('name','=',project.name)],limit=1)
                if not team_id:
                    team_id = self.env['helpdesk.ticket.team'].create({
                        'name':project.name,
                        'default_project_id':project.id
                        })
                team_ids.append(team_id.id)
            ticket_stage_id = self.env['helpdesk.ticket.stage'].search([('name','=',self.name)],limit=1)
            vals = {
                'name':self.name,
                'team_ids':[(6,0, team_ids)]
                }
            if not ticket_stage_id:
                ticket_stage_id = self.env['helpdesk.ticket.stage'].create(vals)
            else:
                ticket_stage_id.write(vals)



    