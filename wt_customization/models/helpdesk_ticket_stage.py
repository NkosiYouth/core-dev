# -*- coding: utf-8 -*-

from odoo import api, fields, models, api


class HelpdeskTicketStage(models.Model):
    _inherit = "helpdesk.ticket.stage"


    @api.onchange('team_ids')
    def onchange_team_ids(self):
        if self.team_ids:
            project_ids = []
            for team in self.team_ids:
                project_id = self.env['project.project'].search([('name','=',team.name)],limit=1)
                if not project_id:
                    project_id = self.env['project.project'].create({
                        'name':team.name,
                        })
                    team.write({'default_project_id':project_id.id})
                project_ids.append(project_id.id)
            task_stage_id = self.env['project.task.type'].search([('name','=',self.name)],limit=1)
            vals = {
                'name':self.name,
                'project_ids':[(6,0, project_ids)]
                }
            if not task_stage_id:
                task_stage_id = self.env['project.task.type'].create(vals)
            else:
                task_stage_id.write(vals) 