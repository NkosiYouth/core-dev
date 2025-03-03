# -*- coding: utf-8 -*-

from odoo import models, fields 

class RegisterTicket(models.Model):
    _name = 'register.tickets'

    ticket_id = fields.Many2one('helpdesk.ticket')
    employee_id = fields.Many2one('hr.employee', string='Youth')
    register_day_summary = fields.Html('Register Summary')
    task_id = fields.Many2one('project.task')
    ticket_id = fields.Many2one('helpdesk.ticket')
    weekly_registers_id = fields.Many2one('project.task', string='Weekly Registers')


    def open_popup(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ticket',
            'view_mode': 'form',
            'res_model': 'helpdesk.ticket',
            'res_id':self.weekly_registers_id.ticket_id.id,
            'target':'new'
        }
