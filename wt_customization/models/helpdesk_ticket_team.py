# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HelpdeskTeam(models.Model):

    _inherit = "helpdesk.ticket.team"

    assign_method = fields.Selection([("off","Off"),("round_robin","Round Robin"),("fewest_records","Fewest Records")], string="Assign Method", default="off")
    assign_online_users = fields.Boolean()
    assign_limit = fields.Integer('Assign Limit' , default=1)
    assign_user_domain = fields.Char()
    ex_assigen_user_ids = fields.Many2many('res.users', 'ex_user_rel', 'ex_user_id', 'user_id')
    stage_ids = fields.Many2many('helpdesk.ticket.stage', string="Stages")
    sla_response = fields.Float('Response SLA')
    sla_resolve = fields.Float('Resolve SLA')


    # @api.model_create_multi
    # def create(self,vals_list):
    #     res = super().create(vals_list)
    #     vals = {
    #         'name':res.name,
    #     }
    #     if not self._context.get('with_project'):
    #         project_id = self.env['project.project'].search([('name','=',res.name)],limit=1)
    #         if not project_id:
    #             project_id = self.env['project.project'].with_context(with_team=True).create(vals)
    #         res.write({'default_project_id':project_id.id})
    #         for stage in res.stage_ids:
    #             task_stage_id = self.env['project.task.type'].search([('name','=',stage.name)],limit=1)
    #             stage_vals = {
    #                 'name':stage.name,
    #                 'project_ids':[(6, 0, project_id.ids)]
    #             }
    #             if not task_stage_id:
    #                 task_stage_id = self.env['project.task.type'].create(stage_vals)
    #             else:
    #                 task_stage_id.write(stage_vals)
    #     return res

    def write(self,vals):
        res = super().write(vals)
        project_id = self.default_project_id
        if project_id:
            task_stage_ids = self.env['project.task.type']
            for stage in self.stage_ids:
                task_stage_id = self.env['project.task.type'].search([('name','=',stage.name)],limit=1)
                stage_vals = {
                    'name':stage.name or "Test",
                    'project_ids':[(6, 0, project_id.ids)]
                }
                if not task_stage_id:
                    task_stage_id = self.env['project.task.type'].create(stage_vals)
                else:
                    task_stage_id.write(stage_vals)
                task_stage_ids += task_stage_id
            if not self._context.get('with_project'):
                project_id.with_context(with_team=True).write({
                    'type_ids':[(6, 0, task_stage_ids.ids)]
                    })
        return res
