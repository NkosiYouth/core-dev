from odoo import models, fields, api

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    completed_host_site_ids = fields.Many2many("project.task", 'x_hr_expense_project_task_rel', 'hr_expense_id', 'project_task_id')
    # domain="[('project_id', '=', 57), ('stage_id', '=', 112)]"
 
    @api.depends('completed_host_site_ids')
    def set_validate_task(self):
        completed_host_sites = []
        if self.host_site_ids:
            try:    
                for youth in self.host_site_ids:
                    host_site_task = model.env['project.task'].search([('project_id', '=', 57), ('partner_id', '=', youth.id)])
                    is_completed = all(task.stage_id.id == 705 for task in host_site_task)
                    if is_completed:
                        completed_host_sites += host_site_task.ids
                    if sorted(self.completed_host_site_ids.ids) != sorted(completed_host_sites):
                     raise UserError('Need to select the all the completed task of the selected host sites')
            except Exception as error:
                raise UserError("%s" % error)