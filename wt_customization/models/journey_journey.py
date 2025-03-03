# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common, Form


class Journey(models.Model):
    _name = "journey.journey"


    # name = fields.Char('Name')
    project_id = fields.Many2one('project.project', "Name")
    prev_youth_ids = fields.Many2many('hr.employee', 'hr_employee_journey_rel', 'journey_id', 'hr_employee_id')
    cohort_ids = fields.Many2many('cohort.cohort', string="Cohorts", help="Select cohorts to add their employees to the journey.")
    youth_ids = fields.Many2many('hr.employee', 'hr_employee_journey_rell', 'x_journey_id', 'hr_employee_id', string="Youth")
    session_ids = fields.One2many('project.task.type', 'journey_id')
    journey_task_ids = fields.Many2many('project.task')


    @api.onchange('cohort_ids')
    def _onchange_cohort_ids(self):
        """
        Dynamically add employees from the selected cohorts to the `youth_ids` field.
        This maintains the ability to add/remove youth manually in `youth_ids`.
        """
        if self.cohort_ids:
            cohort_employees = self.env['hr.employee'].search([('cohort_id', 'in', self.cohort_ids.ids)])
            existing_youth = self.youth_ids
            self.youth_ids = [(6, 0, (cohort_employees | existing_youth).ids)]
        else:
            self.youth_ids = False


    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for rec in vals:
            if rec.get('youth_ids'):
               rec.update({
                'prev_youth_ids':rec.get('youth_ids')
               }) 
        res.create_journey_tasks()
        return res

    def write(self, vals):
        if vals.get('youth_ids'):
            vals.update({
                'prev_youth_ids':[(6, 0, self.youth_ids.ids)]
                })
        res = super().write(vals)
        if not self._context.get('task_list'):
            self.create_journey_tasks()
        return res
    
    def unlink(self):
        for rec in self:
            rec.journey_task_ids.mapped('ticket_id').sudo().unlink()
            if rec.project_id:
                rec.journey_task_ids.sudo().unlink()
                if not rec.project_id.id in [54,55,56,58,57,62,63,64,65,66,67,68]:
                    rec.project_id.unlink()
        super().unlink()

    def create_journey_tasks(self):
        youth_on_journeys = self.search([('id', '!=', self.id)]).mapped('youth_ids')
        youth = self.youth_ids.filtered(lambda youth: youth in youth_on_journeys).mapped('name')
        if youth:
            raise UserError(_("The Following Youth are already on another journey: \n%s" % '\n'.join(youth)))
        journey_task_list = []
        if self.project_id:
            journey = self.env['project.project'].browse(self.project_id.id)
            journey.write({
                'journey': True
                })
            sessions = self.env['project.task.type'].search([('journey_id', '=', self.id)])
            for session in sessions:
                session.write({
                    'project_ids': [(6, 0, [journey.id])],
                    })
            prev_youth_ids = self.prev_youth_ids
            current_youth_ids = self.youth_ids
            new_youth_ids = current_youth_ids - prev_youth_ids
            removed_youth_ids = prev_youth_ids - current_youth_ids
            for youth in new_youth_ids:
                vals = {'employee_id': youth.id}
                
                vals.update({
                    'project_id': journey.id,
                    'name': youth.name + " " + journey.name  
                })
                
                set_task = self.env['project.task'].create(vals)
                set_task.write({
                    'session_link': set_task.stage_id.session_link,
                    'date_deadline': set_task.stage_id.session_deadline,
                })
                journey_task_list.append(set_task.id)

            for youth_id in removed_youth_ids:
                tasks_to_remove = self.env['project.task'].search([
                    ('project_id', '=', journey.id),
                    ('employee_id', '=', youth_id.id)])
                tasks_to_remove.unlink()
                
                host_site_tasks = self.env['project.task'].search([('partner_id', '=', youth_id.host_site_id.id), ('project_id', '=', 57)])
                host_site_tasks.sudo().unlink()
                
                youth_tasks = self.env['project.task'].search([('partner_id', '=', youth_id.host_site_id.id), ('project_id', '=', 68)])
                youth_tasks.sudo().unlink()
            for youth in self.youth_ids:
                if youth.host_site_id:
                    current_year = datetime.today().year
                    month = datetime.today().month
                    for quarter in range(4):
                        month += 3
                        if month > 12:
                            month -= 12
                            current_year += 1
                        first_day_quarter_month = datetime.strptime('01-%s-%s' % (month, current_year), '%d-%m-%Y').date()
                        next_month = first_day_quarter_month.replace(day=28) + timedelta(days=4)
                        last_day_quarter_month = next_month - timedelta(days=next_month.day)
                        host_site_visit = self.env['project.task'].search([('partner_id', '=', youth.host_site_id.id), ('project_id', '=', 57), ('date_deadline', '=', last_day_quarter_month)])
                        if not host_site_visit:
                            vals = {
                                'name': (youth.host_site_id.name or '') + '('+ last_day_quarter_month.strftime('%d-%m-%Y') + ')',
                                'kanban_state': 'normal',
                                'employee_id': youth.id,
                                'partner_id': youth.host_site_id.id,
                                'date_deadline': last_day_quarter_month,
                                'project_id': 57,
                            }
                            host_site_visit = self.env['project.task'].create(vals)
                            journey_task_list.append(host_site_visit.id)
                            self._cr.commit()
                        host_site_visit.update_host_site_id()
                        youth_site_visit = self.env['project.task'].search([('employee_id', '=', youth.id), ('project_id', '=', 68), ('date_deadline', '=', last_day_quarter_month)])
                        if not youth_site_visit:
                            youth_site_vals = {
                                'name': (youth.name or '') + '(' + last_day_quarter_month.strftime('%d-%m-%Y') + ')',
                                'kanban_state': 'normal',
                                'partner_id': youth.host_site_id.id,
                                'date_deadline': last_day_quarter_month,
                                # 'youth_site_employee_id': youth.id,
                                'employee_id': youth.id,
                                'project_id': 68,
                                'host_site_ticket_id': host_site_visit.ticket_id.id,
                                'site_visit_id': host_site_visit.id 
                            }
                            youth_site_visit = self.env['project.task'].create(youth_site_vals)
                            journey_task_list.append(youth_site_visit.id)
                        youth_site_visit.update_host_site_id()

            for youth in self.youth_ids:
                for session in self.session_ids:
                    session_task = self.env['project.task'].search([('employee_id', '=', youth.id), ('project_id', '=', 55), ('stage_id', '=', session.id)])
                    if not session_task:
                        vals = {'name': youth.name + '(' + session.name + ')',
                        'kanban_state': 'normal',
                        'employee_id': youth.id,
                        'partner_id': youth.related_contact_ids[0].id if youth.related_contact_ids else False,
                        'project_id': 55,
                        'date_deadline': session.session_deadline,
                        'cohorts_ids':self.cohort_ids.ids,
                        'journey_session_id':session.session_id.id,
                        'session_type':session.session_type,
                        'session_link':session.session_link,
                        'session_deadline':session.session_deadline
                        }
                        partner_ids_list = []
                        partner_ids_list.append(youth.related_contact_ids[0].id)
                        if youth.parent_id:
                            partner_ids_list.append(youth.parent_id.related_contact_ids[0].id)
                        rows = []
                        session_date = session.session_start.strftime("%m/%d/%Y")
                        session_time = session.session_start.strftime("%H:%M:%S")
                        calendar_event = self.env['calendar.event'].create({
                            'name': youth.name + '(' + session.name + ')',
                            'partner_ids': [(6, 0, partner_ids_list)],
                            'start': datetime.today(),
                            'stop': datetime.today(),
                            'duration':session.session_duration,
                            'description':""" Session Name : {name} <br/> Session Type : {type} <br/> Session Date : {date} <br/> session Time : {time} <br/> Session Link : <a href="{link}" target="_blank">{link}</a> <br/> Session Duration : {duration}""".format(name="".join(session.session_id.name), type="".join(session.session_type), date="".join(session_date), time="".join(session_time), link="".join(session.session_link), duration="".join(f"{session.session_duration:.2f}"))
                            })
                        self._cr.commit()
                        CalenderMail = self.env['mail.compose.message']
                        template_id = self.env['ir.model.data']._xmlid_to_res_id('calendar.calendar_template_meeting_update', raise_if_not_found=False)
                        composition_mode = self.env.context.get('composition_mode', 'comment')
                        mailwizard = CalenderMail.with_context( 
                            default_model='calendar.event',
                            default_res_id=calendar_event.id,
                            default_res_ids = calendar_event.ids,
                            default_use_template=bool(template_id),
                            default_template_id=template_id,
                            default_partner_ids=calendar_event.partner_ids.ids,
                            mail_tz=self.env.user.tz
                            )
                        mailwizard_form = Form(mailwizard).save()
                        mailwizard_form.action_send_mail()
                        session_task = self.env['project.task'].create(vals)
                        journey_task_list.append(session_task.id)
                    else:
                        session_task.write(vals)
            self.with_context(task_list=True).sudo().write({
                'journey_task_ids':[(6,0,journey_task_list)]
                })
