# -*- coding: utf-8 -*-

from odoo import models, fields ,api

class ProjectProject(models.Model):
    _inherit = 'project.project'


    journey = fields.Boolean('Is Journey?')


    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super().create(vals_list)
    #     vals = {
    #     'name':res.name,
    #     'default_project_id':res.id
    #     }
    #     if not self._context.get('with_team'):
    #         team_id = self.env['helpdesk.ticket.team'].with_context(with_project=True).create(vals)
    #         for stage in res.type_ids:
    #             ticket_stage_id = self.env['helpdesk.ticket.stage'].search([('name','=',stage.name)],limit=1)
    #             vals = {
    #                 'name':stage.name,
    #                 'team_ids':[(6, 0, team_id.ids)]
    #             }
    #             if not ticket_stage_id:
    #                 ticket_stage_id = self.env['helpdesk.ticket.stage'].create(vals)
    #             else:
    #                 ticket_stage_id.write(vals)
    #     return res

    def write(self,vals):
        res = super().write(vals)
        team_id = self.env['helpdesk.ticket.team'].search([('default_project_id','=',self.id)],limit=1)

        if team_id:
            ticket_stage_ids = self.env['helpdesk.ticket.stage']
            for stage in self.type_ids:
                ticket_stage_id = self.env['helpdesk.ticket.stage'].search([('name','=',stage.name)],limit=1)
                vals = {
                    'name':stage.name,
                    'team_ids':[(6, 0, team_id.ids)]
                }
                if not ticket_stage_id:
                    ticket_stage_id = self.env['helpdesk.ticket.stage'].create(vals)
                else:
                    ticket_stage_id.write(vals)
                ticket_stage_ids += ticket_stage_id
            if not self._context.get('with_team'):
                team_id.with_context(with_project=True).write({
                    'stage_ids':[(6, 0, ticket_stage_ids.ids)]
                    })
        return res




    