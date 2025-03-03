# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_deadline = fields.Datetime()

    @api.model_create_multi
    def create(self, vals_list):
        rec = super(ProjectTask, self).create(vals_list)
        rec.generate_helpdesk_ticket()
        if rec.project_id.id == 66:
            rec.generate_weekly_timesheet()
        return rec

    def write(self, vals):

        week_start = self.week_start
        week_end = self.week_end
        res = super(ProjectTask, self).write(vals)
        self.generate_helpdesk_ticket()
        if not self._context.get('timesheet'):
            if not self.week_start or not self.week_end:
                self.timesheet_ids.unlink()
            if week_start and  self.project_id.id == 66 and (vals.get('week_start') or vals.get('week_end')):
                if self.week_start > week_start:
                    time_sheet = self.timesheet_ids.filtered(lambda x:x.date < self.week_start)
                    time_sheet.unlink()
            if week_end and self.project_id.id == 66 and (vals.get('week_start') or vals.get('week_end')):
                if self.week_end < week_end:
                    time_sheet = self.timesheet_ids.filtered(lambda x:x.date > self.week_end)
                    time_sheet.unlink()
            
            # temporary comment next line becuase task stage not change set default not submmited stage.
            # self.ticket_id.timesheet_ids = self.timesheet_ids

            if self.project_id.id == 58 and vals.get('stage_id'):
                if vals.get('stage_id') == 728 and self.employee_id:
                    self.employee_id.write({'category_ids': [(3, 19)]})

            # Register Issue task in done stage
            if self.project_id.id == 63 and vals.get('stage_id'):
                if vals.get('stage_id') == 794:
                    self.register_issue_timesheet_ids.write({'has_register_issues': False})
                    partner_task_id = self.search([('register_issue_task_id','=',self.id)],limit=1)
                    if partner_task_id:
                        partner_task_id.stage_id = 721
                        partner_task_id.ticket_id.has_approved = True
                else:
                    self.register_issue_timesheet_ids.write({'has_register_issues': True})

        return res

    def generate_helpdesk_ticket(self):
        today = datetime.today()
        week_start_date = today - timedelta(today.weekday())
        week_end_date = week_start_date + timedelta(6)
        if self.project_id.id == 65 and self.host_site_id:
            host_site_partner = self.host_site_id
            host_site_partner.write({'no_of_vaccancies': self.env['project.task'].search_count([('host_site_id', '=', self.host_site_id.id), ('project_id', '=', 65), ('stage_id', '!=', 739)])})
        if self.project_id.id in [66, 58, 62, 67, 65, 63, 64, 57, 54, 55]: 
            employee_id = self.employee_id
            if self.project_id.id == 66: #Weekly Register
                team_id = 76
            elif self.project_id.id == 56: #Daily Register
                team_id = 16
            elif self.project_id.id == 58: #HR Issue
                team_id = 79
                employee_id.write({'has_hr_issues': True, 'category_ids': [(6, 0, [19])]})
            elif self.project_id.id == 60: #Journey
                team_id = 11
            elif self.project_id.id == 68: #Youth Site Visits
                team_id = 17
            elif self.project_id.id == 62: #Partner & Host Site Recruitment
                team_id = 77
            elif self.project_id.id == 67 : #Youth Recruitment
                team_id = 71
            elif self.project_id.id == 65: #vacancies
                team_id = 78
            elif self.project_id.id == 63:  #Register issues
                team_id = 72
            elif self.project_id.id == 64:  #Resignations
                team_id = 70
            elif self.project_id.id == 57:  #Host Site Visits
                team_id = 75
            elif self.project_id.id == 54:  #Absorption
                team_id = 73
            elif self.project_id.id == 55:
                team_id = 74
            stage_ids = self.env['project.task.type'].search([('project_ids', '=', self.project_id.id)])
            stage = self.env['helpdesk.ticket.stage'].search([('name','=',self.stage_id.name)],limit=1)
            if not stage and self.stage_id.name:
                stage = self.env['helpdesk.ticket.stage'].create({
                    'name':self.stage_id.name
                    })
            vals = {'team_id': team_id,
                'company_type': self.company_type,
                'name': self.name,
                'register_date': self.register_date,
                'partner_youth_id': employee_id.id, 
                'partner_id': self.partner_id.id, 
                'description': self.description,
                'issue_type': self.issue_type,
                'issue_reporter_id': self.issue_reporter_id.id,
                'office_id':self.office_id.id,
                'issue_priority': self.issue_priority,
                'user_id': self.user_ids[0].id if self.user_ids else False,
                'my_activity_date_deadline': self.date_deadline,
                'issue_date_closed': self.issue_date_closed,
                'business_id': self.business_id.id,
                'visit_type': self.visit_type,
                'type_of_visit': self.type_of_visit,
                'plans_after_yes': self.plans_after_yes,
                'registers_sent': self.registers_sent,
                'things_learnt_this_month': self.things_learnt_this_month,
                'main_goals_for_month': self.main_goals_for_month,
                'discussed_goals': self.discussed_goals,
                'why_not_discussed_goals': self.why_not_discussed_goals,
                'is_studying': self.is_studying,
                'studying_what': self.studying_what,
                'receive_whatsapp': self.receive_whatsapp,
                'saved_hotline_number': self.saved_hotline_number,
                'whatsapp_number': self.whatsapp_number,
                'have_new_cell_number': self.have_new_cell_number,
                'new_number': self.new_number,
                'has_new_email': self.has_new_email,
                'new_email': self.new_email,
                'goals': self.goals,
                'add_learnings': self.add_learnings,
                'good_employee': self.good_employee,
                'joint_responsibility': self.joint_responsibility,
                'nowork_nopay': self.nowork_nopay,
                'future_employment': self.future_employment,
                'remain_employed': self.remain_employed,
                'future_absorption': self.future_absorption,
                'cv': self.cv,
                'contract_yaw': self.contract_yaw,
                'yes_phone': self.yes_phone,
                'online_learning': self.online_learning,
                'engage_yesapp': self.engage_yesapp,
                'mandatory_apps': self.mandatory_apps,
                'yes_supervisor_app': self.yes_supervisor_app,
                'yaw_registers': self.yaw_registers,
                'work_experience': self.work_experience,
                'rate_experience': self.rate_experience,
                'prepared': self.prepared,
                'share_contract': self.share_contract,
                'street': self.street,
                'street2': self.street2,
                'city': self.city,
                'state_id': self.state_id.id,
                'zip': self.zip,
                'country_id': self.country_id.id,
                'partner_email': self.email_from,
                'partner_phone': self.partner_phone,
                'cohorts_ids': [(6, 0, self.cohorts_ids.ids)] if self.cohorts_ids else [],
                'female_ownership': self.female_ownership,
                'business_size': self.business_size,
                'sector_id': self.sector_id.id,
                'register_doc': self.register_doc,
                'project_id': self.project_id.id,
                # 'stage_id':stage.id,
                'project_task_type_id': self.stage_id.id, 
                'project_task_stage_ids': [(6, 0, stage_ids.ids) ]if stage_ids else [],
                'youth_visit_task_ids': [(6, 0, self.youth_visit_task_ids.ids)] if self.youth_visit_task_ids else [],  # Ensure the youth tasks are also linked to the helpdesk ticket
                'resignation_date': self.resignation_date,
                'reason_for_resignation': self.reason_for_resignation,
                'resignation_letter': self.resignation_letter,
                'has_approved': self.has_approved,
                'has_declined': self.has_declined,
                'session_id': self.session_id.id,
                'session_link': self.session_link,
                'stage_id': False,
                'journey': self.is_journey,
                'week_start':self.week_start,
                'week_end':self.week_end

            }
            vals.update({
                'stage_id':stage.id
                })
            if self.project_id.id == 66:
                vals.update({
                    'name':"Week " + str(self.week) + '(' + week_start_date.date().strftime('%d-%m-%Y') + ' - ' + week_end_date.date().strftime('%d-%m-%Y') + ')',
                })
            if self.project_id.id == 62:
                if self.partner_task_id:
                    vals.update({'partner_ticket_id': self.partner_task_id.ticket_id.id, 'ticket_type': 'Host Site'})
                elif self.company_type != 'Host Site':
                    vals.update({'ticket_type': 'Partner'})
            
            ticket = self.ticket_id
            if not ticket:
                # try:
                if self.project_id.id == 65:
                    ticket = self.env['helpdesk.ticket'].create(vals)
                else:
                    ticket = self.env['helpdesk.ticket'].create(vals)
                # except Exception as error:
                #     raise UserError("%s" % error)
                self.write({'ticket_id': ticket.id})
            else:
                vals.pop('user_id', None)
                ticket.write(vals)

    @api.depends('employee_id')
    def compute_week(self):
        for rec in self:
            self.week = 0
            if rec.employee_id:
                contract = self.env['hr.contract'].search([('state','=','open'),('employee_id','=',rec.employee_id.id)])
                if contract:
                    start_date =  contract.date_start
                    difference_in_days = (datetime.today().date() - start_date).days
                    self.week = difference_in_days / 7


    @api.onchange('week_start','week_end')
    def generate_weekly_timesheet(self):
        if self.project_id.id == 66 and self.week_start and self.week_end:
            week_start = self.week_start
            week_end = self.week_end
            while week_start <= week_end:
                daily_attendance_status = False
                if week_start and week_start.strftime('%A') in ['Saturday', 'Sunday']:
                    daily_attendance_status = 'Weekend'
                time_sheet = self.env['account.analytic.line'].search([('project_id', '=', 66), ('task_id', '=', self._origin.id), ('date', '=', week_start)])
                vals = {
                    'date':week_start,
                    'task_id':self._origin.id,
                    'project_id': 66,
                    'daily_type': 'Weekly',
                    'company_id':self.company_id.id,
                    'daily_attendance_status':daily_attendance_status if daily_attendance_status else False,
                    'employee_id':self.employee_id.id
                }
                if not time_sheet:
                    time_sheet = self.env['account.analytic.line'].create(vals)
                else:
                    time_sheet.write(vals)
                week_start = week_start + timedelta(days=1)
            self.ticket_id.timesheet_ids = self.timesheet_ids

    def add_the_issued_timesheet_to_ticket(self):
        self.ticket_id.issue_timesheet_ids = self.register_issue_timesheet_ids


    def create_daily_task(self):
        for employee in self.env['hr.employee'].search([]):
            daily_task = self.env['project.task'].search([('employee_id', '=', employee.id), ('project_id', '=', 56), ('daily_attendance_date', '=', datetime.now().date())])
            if not daily_task:
                self.create({
                    'project_id': 56,
                    'name': "Week " + str(self.week) + '(' + week_start_date.date().strftime('%d-%m-%Y') + ' - ' + week_end_date.date().strftime('%d-%m-%Y') + ')',
                    'kanban_state': 'normal',
                    'company_id': employee.company_id.id,
                    'daily_start_time': datetime.now().date(),
                    'daily_end_time': datetime.now().date(),
                    'daily_attendance_date': datetime.now().date(),
                    'employee_id': employee.id,
                    # 'user_ids':
            })


    @api.model
    def create_weekly_register_task(self):
        today = datetime.today().date()
        current_week_start = today - timedelta(days=today.weekday())
        current_week_end = current_week_start + timedelta(days=6)

        for employee in self.env['hr.employee'].search([('user_roles_id.name', '=', 'Youth'), ('active', '=', True)]):
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', employee.id)], limit=1)

            if not contract:
                continue  # Skip employees without an active contract

            # Fetch all existing weekly registers for the employee
            weekly_registers = self.env['project.task'].search([
                ('employee_id', '=', employee.id),
                ('project_id', '=', 66)
            ], order="week_start asc", limit=1)
            if weekly_registers:
                # If weekly registers exist, get the first one's start date
                start_date = weekly_registers.week_start
            else:
                # If no previous weekly register, align contract date to Monday
                start_date = contract.date_start - timedelta(days=contract.date_start.weekday())

            # Calculate the week number
            difference_in_days = (current_week_start - start_date).days
            week_number = max(difference_in_days // 7, 0)  # Avoid negative week numbers
            week_number = week_number + 1
            # Check if the weekly task for the current week already exists
            weekly_task = self.env['project.task'].search([
                ('employee_id', '=', employee.id),
                ('project_id', '=', 66),
                ('week_start', '=', current_week_start)
            ], limit=1)

            task_name = f"Week {week_number} ({current_week_start.strftime('%d-%m-%Y')} - {current_week_end.strftime('%d-%m-%Y')})"

            vals = {
                'project_id': 66,
                'name': task_name,
                'kanban_state': 'normal',
                'company_id': employee.company_id.id,
                'week_start': current_week_start,
                'week_end': current_week_end,
                'employee_id': employee.id
            }

            if not weekly_task:
                weekly_task = self.env['project.task'].create(vals)
            else:
                weekly_task.write(vals)

            self._cr.commit()  # Commit changes in cron jobs
            _logger.info("-------------- Weekly Register Task Created/Updated ------ %s", weekly_task.name)
            weekly_task.generate_weekly_timesheet()



    @api.model
    def create_weekly_register_task_missing_task(self):
        """Automatically create weekly register tasks for missing weeks from contract start date to current week."""
        
        today = datetime.today().date()
        current_week_start = today - timedelta(today.weekday())

        employees = self.env['hr.employee'].search([
            ('user_roles_id.name', '=', 'Youth'),
            ('active', '=', True),
        ])

        for employee in employees:
            contract = self.env['hr.contract'].search([
                ('state', '=', 'open'),
                ('employee_id', '=', employee.id)
            ], limit=1)

            if not contract:
                continue  # Skip employees without an active contract

            # Get the first Monday after or on the contract start date
            start_date = contract.date_start
            start_week = start_date - timedelta(days=start_date.weekday())

            # Iterate over all weeks from contract start week to current week
            week_start_date = start_week
            while week_start_date <= current_week_start:
                week_end_date = week_start_date + timedelta(days=6)

                # Check if a task exists for this week
                weekly_task = self.env['project.task'].search([
                    ('employee_id', '=', employee.id),
                    ('project_id', '=', 66),
                    ('week_start', '=', week_start_date)
                ], limit=1)

                # Calculate the week number
                difference_in_days = (week_start_date - start_week).days
                week_number = difference_in_days // 7
                week_number = week_number + 1
                task_name = f"Week {week_number} ({week_start_date.strftime('%d-%m-%Y')} - {week_end_date.strftime('%d-%m-%Y')})"

                vals = {
                    'project_id': 66,
                    'name': task_name,
                    'kanban_state': 'normal',
                    'company_id': employee.company_id.id,
                    'week_start': week_start_date,
                    'week_end': week_end_date,
                    'employee_id': employee.id
                }

                if not weekly_task:
                    weekly_task = self.env['project.task'].create(vals)
                    self._cr.commit()  # Ensure database commit for cron stability

                # Call a function to generate the weekly timesheet (if applicable)
                # if hasattr(weekly_task, 'generate_weekly_timesheet'):
                weekly_task.generate_weekly_timesheet()

                # Move to next week
                week_start_date += timedelta(weeks=1)

    def create_weekly_register_task_temp(self):
        today = datetime.today()
        week_start_date = today - timedelta(today.weekday())
        week_end_date = week_start_date + timedelta(6)
        
        for employee in self.env['hr.employee'].search([('user_roles_id.name', '=', 'Youth'), ('active', '=', True), ('past_task_create','=',False)]):
            contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', employee.id)])
            if contract:
                start_date = contract.date_start
                current_week_number = (datetime.today().date() - start_date).days // 7
                for week_num in range(current_week_number + 1):
                    week_start = start_date - timedelta(days=start_date.weekday())
                    week_start = week_start + timedelta(week_num * 7)
                    week_end = week_start + timedelta(6)
                    if week_start > today.date():
                        break
                    weekly_task = self.env['project.task'].search([
                        ('employee_id', '=', employee.id),
                        ('project_id', '=', 66),
                        ('week_start', '=', week_start)
                    ])
                    if not weekly_task:
                        vals = {
                            'project_id': 66,
                            'name': "Week " + str(week_num + 1) + ' (' + week_start.strftime('%d-%m-%Y') + ' - ' + week_end.strftime('%d-%m-%Y') + ')',
                            'kanban_state': 'normal',
                            'week' : week_num + 1,
                            'company_id': employee.company_id.id,
                            'week_start': week_start,
                            'week_end': week_end,
                            'employee_id': employee.id
                        }
                        weekly_task = self.env['project.task'].create(vals)
                        _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s" % weekly_task)
                        self._cr.commit()
                    else:
                        _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>> update %s" % weekly_task)
                    weekly_task.generate_weekly_timesheet()
            employee.past_task_create = True
   
    # def filter_and_archive_employees(self):
    #     employees = self.env['hr.employee'].search([('user_roles_id', '=', 3)])
    #     for employee in employees:
    #         coach_record = self.env['hr.employee'].search([
    #             ('coach_id', '=', employee.id),
    #             ('user_roles_id', '=', 2)
    #          ])
    #         if coach_record:
    #             _logger.info(f"Employee ID: {employee.id} - Found Coach Record: {coach_record.id} (Active).")
    #             employee.write({'active': True})
    #         else:
    #             _logger.info(f"Employee ID: {employee.id} - No Coach Record found (Archived).")
    #             employee.write({'active': False})

    def filter_and_archive_employees(self):
        employees = self.env['hr.employee'].search([('user_roles_id', '=', 3)])
        for employee in employees:
            coach_records = self.env['hr.employee'].search([
                ('coach_id', '=', employee.id),
                ('user_roles_id', '=', 2),
                ('active', '=', True)
            ])
            if coach_records:
                for coach in coach_records:
                    #_logger.info(f"Employee ID: {employee.id} - Found Coach Record: {coach.id} (Active).")
                    employee.write({'active': True})
            else:
                #_logger.info(f"Employee ID: {employee.id} - No Coach Record found (Archived).")
                employee.write({'active': False})


    def update_ticket_name_as_task_name(self):
        tasks = self.env['project.task'].search([('project_id', '=', 66)])
        for task in tasks:
            if task.ticket_id.name != task.name and task.ticket_id:
                task.ticket_id.name = task.name
                self._cr.commit()
                _logger.info("!!!!!!!! ticket name changed: %s" % task.ticket_id.name)

    def filter_and_archive_contract_end_youths(self):
        seven_days_ago = datetime.today().date() - timedelta(days=7)
            
        employees = self.env['hr.employee'].search([
            ('user_roles_id', '=', 2),
            ('active', '=', True),
            ('contract_end_date', '<=', seven_days_ago)
        ])
            
        if employees:
            employees.write({'active': False})
    
    def update_contract_months_for_employees(self):
        contracts = self.env['hr.contract'].search([('state', '=', 'open')])
        date_today = fields.Date.today()

        if contracts:
            for contract in contracts:
                start_date = contract.date_start
                diff_years = date_today.year - start_date.year
                diff_months = date_today.month - start_date.month
                if date_today.day < start_date.day:
                    diff_months -= 1
                current_month = diff_years * 12 + diff_months + 1
                contract.write({
                    'month_into_program': current_month,
                })
                employee = self.env['hr.employee'].browse([contract.employee_id.id])
                if employee:
                    employee.write({
                        'x_contract_month': current_month,
                    })
                    #log(f"Contract {contract.id} start_date read as: {start_date}")
    
    # def follow_self(self):
    #     employees = self.env['hr.employee'].search([
    #         ('active', '=', True)
    #     ])
    #     mail_followers = self.env['mail.followers']

    #     for employee in employees:
    #         if employee.id:
    #             already_following = mail_followers.search([
    #                 ('res_model', '=', 'hr.employee'),
    #                 ('res_id', '=', employee.id),
    #                 ('partner_id', '=', employee.id)
    #             ], limit=1)

    #             if not already_following:
    #                 mail_followers.create({
    #                     'res_model': 'hr.employee',
    #                     'res_id': employee.id,
    #                     'partner_id': employee.id
    #                 })
   
    def follow_self(self):
        employees = self.env['hr.employee'].search([
            ('active', '=', True)
        ])
        mail_followers = self.env['mail.followers']
        partner_model = self.env['res.partner']

        for employee in employees:
            partner = partner_model.search([('youth_id', '=', employee.id)], limit=1)  # Get partner by youth_id

            if partner:
                already_following = mail_followers.search([
                    ('res_model', '=', 'hr.employee'),
                    ('res_id', '=', employee.id),
                    ('partner_id', '=', partner.id)
                ], limit=1)

                if not already_following:
                    mail_followers.create({
                        'res_model': 'hr.employee',
                        'res_id': employee.id,
                        'partner_id': partner.id
                    })

