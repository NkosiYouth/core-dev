# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from datetime import datetime, timedelta
from dateutil import tz
import pytz
from pytz import timezone, utc
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    company_type = fields.Selection([("Partner","Partner"),("Host Site","Host Site")],string="Company Type",)
    add_learnings = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Are you aware of additional online learning that you can do to assist in achieving your plans?")
    body = fields.Html('Message Body')
    business_id = fields.Many2one('res.partner')
    business_size = fields.Selection([('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')], string='Business Size')
    city = fields.Char()
    cohorts_ids = fields.Many2many('cohort.cohort', string='Cohorts')
    contract_yaw = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Do you know that you have to share your future employment contract with youth@WORK?")
    country_id = fields.Many2one('res.country')
    cv = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Have you prepared your CV, updated it and included a reference letter from your current employer?')
    daily_attendance_date = fields.Date()
    daily_attendance_status = fields.Selection([('Present', 'Present'), ('Annual Leave', 'Annual Leave'), ('Sick Leave', 'Sick Leave'), ('Study Leave', 'Study Leave'), ('Maternity Leave', 'Maternity Leave'), ('Half Day', 'Half Day'), ('Unpaid Leave', 'Unpaid Leave'), ('Family Responsibility Leave', 'Family Responsibility Leave'), ('Public Holiday', 'Public Holiday'), ('Off Day', 'Off Day')])    
    daily_duties = fields.Text(string="Duties")
    daily_end_time = fields.Datetime(string="End Time")
    daily_start_time = fields.Datetime(string="Start Time")
    daily_supervisor_id = fields.Many2one(comodel_name="hr.employee",string="Supervisor")
    daily_task_ids = fields.One2many('project.task', 'weekly_ticket_id', string='Attendance Registers')
    daily_type = fields.Selection([("Session","Session"),("Weekly","Weekly")],string="Daily Attendance Type")
    date_reported = fields.Date('Date on which the matter was reported')
    discussed_goals = fields.Selection([("Yes","Yes"), ("No","No")], string="Has she/he discussed this with her supervisor and complete the monthly progress report?")
    employee_ids = fields.Many2many('hr.employee', string='Youth')
    engage_yesapp = fields.Selection([("When I have time", "When I have time"), ("Weekly", "Weekly"), ("Post the YES Program", "Post the YES Program"), ("Monthly", "Monthly"), 
        ("Daily","Daily")], string="How often will you engage on the YES Apps?")
    female_ownership = fields.Float(string="Female Ownership(%)")

    future_absorption = fields.Selection([("Yes","Yes"),("No","No")],string="Have you discussed future employment with your current employer?")
    future_employment = fields.Selection([("I increased my qualifications, gained valuable workplace experience","I increased my qualifications, gained valuable workplace experience"),
                                          ("Created a network for future employment","Created a network for future employment"),("Saved money","Saved money"),
                                          ("Created healthy habits","Created healthy habits"),("All of the above","All of the above")],string="How has this program helped towards future employment?")
    goals = fields.Selection([("Permanent job at current host site","Permanent job at current host site"),("Start my own business","Start my own business"),("Study","Study"),
                              ("Look for work at another employer","Look for work at another employer"),("Have no plans yet","Have no plans yet")],string="""
                             What are your goals beyond the youth employment program?""")
    good_employee = fields.Selection([("Be punctual","Be punctual"),("Always inform my supervisor ahead of time if I will be late","Always inform my supervisor ahead of time if I will be late"),("Apply for leave well ahead of time","Apply for leave well ahead of time"),
                                      ("Communicate well","Communicate well"),("All of the above","All of the above")],string="How do you plan to be a good employee and follow our employment guidelines?")
    has_approved = fields.Boolean(string="Has Approved")
    has_declined = fields.Boolean(string="Has Declined")
    has_new_email = fields.Selection([("Yes","Yes"),("No","No")],string="Have you changed your email address?")
    have_new_cell_number = fields.Selection([("Yes","Yes"),("No","No")],string="Have you changed your cell phone number?")
    host_site_id = fields.Many2one(related='partner_youth_id.host_site_id', comodel_name="res.partner", string="Host Site")
    is_studying = fields.Selection([("Yes","Yes"),("No","No")],string="Are you studying anything? UNISA or Alison online?")
    issue_date_closed = fields.Date(string="Date Closed")
    issue_priority = fields.Selection([("Low","Low"),("Medium","Medium"),("High","High")],string="Priority")
    issue_reporter_id = fields.Many2one(comodel_name="res.users",string="Issue Reporter")
    issue_type = fields.Selection([("Absenteeism","Absenteeism"),("Late Coming","Late Coming"),("Unauthorised Leave","Unauthorised Leave"),
                                   ("Absconscion","Absconscion"),("Excessive and/or abuse of sick leave","Excessive and/or abuse of sick leave"),("Dishonesty / fraudulent behaviour","Dishonesty / fraudulent behaviour"),
                                   ("Theft","Theft"),("Negligence","Negligence"),("Insubordination","Insubordination"),("Bringing company name into disrepute","Bringing company name into disrepute"),("Dereliction of duty","Dereliction of duty"),("Abusive behaviour and/or harassment","Abusive behaviour and/or harassment"),
                                   ("Under the influence of alcohol and/or controlled substances","Under the influence of alcohol and/or controlled substances"),("Breach of company policy & procedures","Breach of company policy & procedures"),("General misconduct","General misconduct")],string="Issue Type")
    joint_responsibility = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that it is your joint responsibility to ensure that your signed and stamped register is emailed to youth@WORK every Friday morning?")
    main_goals_for_month = fields.Text(string="What are the youths main goals for the month?")
    mandatory_apps = fields.Selection([("Yes","Yes"),("No","No"),("Not Sure","Not Sure")],string="Is it mandatory to engage on the Apps.")
    matter_priority = fields.Selection([('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], string='Priority of the matter')
    new_email = fields.Char(string="New email address")
    new_number = fields.Char(string="New number")
    nowork_nopay = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware of the no work no pay rule?")
    online_learning = fields.Selection([("Yes","Yes"),("No","No")],string="Are you committed to online learning?")
    partner_id = fields.Many2one('res.partner', related='host_site_id.parent_id', string="Partner")
    partner_youth_id = fields.Many2one('hr.employee', string='Youth', help='This is the Youth that is linked to the Contact')
    plans_after_yes = fields.Text(string="What are your plans for after the YES programme?")
    prepared = fields.Selection([("Yes","Yes"),("No","No"),("Somewhat","Somewhat")],string="Has this program prepared you for future employment?")
    project_task_stage_ids = fields.Many2many('project.task.type', string='stages')
    project_task_type_id = fields.Many2one('project.task.type', string="Stage")
    rate_experience = fields.Selection([("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],string="How would you rate your work experience year on a scale of 1 -5 with 1 being bad, 5 being excellent?")
    reason_for_resignation = fields.Selection([("Better Job Opportunity","Better Job Opportunity"),("Family Reasons","Family Reasons"),("Personal Reasons","Personal Reasons"),
                                               ("Health Reasons","Health Reasons"),("Furthering Studies","Furthering Studies"),("Starting My Own Business","Starting My Own Business")],string="Reason for Resignation")
    receive_whatsapp = fields.Selection([("Yes","Yes"),("No","No")],string="Are you receiving the Youth@Work WhatsApp messages?")
    register_date = fields.Date(string="Register Date")
    register_doc = fields.Binary(string="Register")
    register_ids = fields.One2many('register.tickets', 'ticket_id')
    register_issue_task_ids = fields.One2many('project.task', 'register_issue_ticket_id', string='Register Issue tasks')
    registers_sent = fields.Selection([("Yes","Yes"),("No","No")],string="Have all registers been sent to the correct email address EVERY FRIDAY?")
    remain_employed = fields.Selection([("Advance within current company","Advance within current company"),("Seek opportunities with a different company","Seek opportunities with a different company"),
                                        ("Pursue further education or training","Pursue further education or training"),("Self-employment","Self-employment")],string="How can you remain employed beyond the program?")
    resignation_date = fields.Date()
    resignation_letter = fields.Binary()
    saved_hotline_number = fields.Selection([("Yes","Yes"),("No","No")],string="If no - have you saved the Youth@Work Hotline 060 749 1927 onto your phone as a contact?")
    sector_id = fields.Many2one(comodel_name="res.partner.industry",string="Sector")
    share_contract = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that you are obligated to share your next employment contract with youth@WORK ?")
    state_id = fields.Many2one(comodel_name="res.country.state",string="State")
    street = fields.Char(string="Street Line 1")
    street2 = fields.Char(string="Street Line 2")
    studying_what = fields.Text(string="What and where are you studying?")
    task_ids = fields.One2many('project.task', 'ticket_id')
    things_learnt_this_month = fields.Text(string="What are new things the youth has learned this month?")
    ticket_type = fields.Selection([('Partner', 'Partner'), ('Host Site', 'Host Site')])
    type_of_visit = fields.Selection([("Yes Youth Alumni Visit","Yes Youth Alumni Visit"),("First Visit","First Visit"),("Follow Up","Follow Up"),
                                      ("Second Visit","Second Visit"),("None of the above","None of the above")],string="Type of Visit")
    visit_type = fields.Selection([("Normal Host Site Visit","Normal Host Site Visit"),("Induction","Induction"),("Exit Session","Exit Session"),
                                   ("Cellphone Distribution","Cellphone Distribution"),("Questions for Supervisors","Questions for Supervisors"),
                                   ("Graduation Session","Graduation Session")],string="Type of Host Site Visit")


    weekly_register_issue_task_ids = fields.One2many('project.task', 'weekly_ticket_register_id', string="Register Issues")
    whatsapp_number = fields.Char(string="Please give us your ‘WhatsApp” number so we can save it to our system")
    why_not_discussed_goals = fields.Char(string="If No - why not??")
    work_experience = fields.Selection([("Give daily tasks","Give daily tasks"),("Provide a clear job description","Provide a clear job description"),("Mentor and coach when necessary","Mentor and coach when necessary"),("Monitor the youth progress for growth and development","Monitor the youth progress for growth and development"),
                                        ("All of the above","All of the above")],string="How are you assisting the youth to gain a quality work experience?")
    yaw_registers = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that you need to send a signed attendance register to youth@WORK every Friday?")
    yes_phone = fields.Selection([("To complete online learning modules","To complete online learning modules"),("To register on YESLife App weekly","To register on YESLife App weekly"),
                                  ("To give to other family members","To give to other family members")],string="Why are you getting a YES phone?")
    yes_supervisor_app = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that you are expected to download the YES Supervisor App and complete a survey once per quarter on the progress made by the youth?")
    youth_issue = fields.Text('Youth Issue / Challenge')
    youth_visit_task_ids = fields.One2many('project.task', 'host_site_ticket_id', string='Youth Visit Tasks')
    partner_phone = fields.Char('Phone')
    host_site_ticket_ids = fields.One2many('helpdesk.ticket', 'partner_ticket_id')
    partner_ticket_id = fields.Many2one('helpdesk.ticket')
    zip = fields.Char(string="Zip")
    timesheet_ids = fields.One2many('account.analytic.line', 'ticket_id')
    issue_timesheet_ids = fields.One2many('account.analytic.line', 'issue_ticket_id')
    session_id = fields.Many2one(comodel_name="session.session",string="Session")
    session_link = fields.Html(string="Session Link")
    team_stage_ids = fields.Many2many('helpdesk.ticket.stage', related="team_id.stage_ids", string="Team Stages")
    journey = fields.Boolean()
    sla_response_state = fields.Selection([('in_sla','In SLA'),('due_soon','Due Soon'),('out_sla','Out of SLA')], default='in_sla', compute='compute_sla_response_state', string="Response SLA")
    sla_resolve_state = fields.Selection([('in_sla','In SLA'),('due_soon','Due Soon'),('out_sla','Out of SLA')], default='in_sla', compute='compute_sla_state', string="Resolve SLA")
    response_date = fields.Datetime('Response Date', compute="compute_response_date")
    resolve_date = fields.Datetime('Resolve Date', compute="compute_response_date")
    closed_date = fields.Datetime(compute="compute_response_date")
    time_to_assign = fields.Float()
    time_to_response = fields.Float(compute="compute_time")
    time_to_resolve = fields.Float(compute="compute_time")
    sla_response_time_left = fields.Integer(compute="compute_countdown_seconds")
    sla_response_time_left_char  = fields.Char(compute="compute_countdown_seconds")
    sla_response_date = fields.Datetime(compute="compute_sla_response_date", store=True)
    sla_resolve_date = fields.Datetime(compute="compute_sla_resolve_date", store=True)
    week_start = fields.Date(string="Week Start")
    week_end = fields.Date(string="Week End")
    office_id = fields.Many2one('office.office', "Office")

    dummy_datetime = fields.Datetime()
    timer_pause = fields.Datetime("Timer Last Pause")

    cohort_id = fields.Many2one(
        comodel_name="cohort.cohort",
        related="partner_youth_id.cohort_id",
        string="Cohort",
        store=True
    )

    youth_name = fields.Char(
        related="partner_youth_id.name",
        string="Youth Name",
        store=True
    )

    cohort_name = fields.Char(
        related="partner_youth_id.cohort_id.name",
        string="Cohort Name",
        store=True
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get('has_approved') or vals.get('has_declined'):
            self.generate_register_issue_ticket()
        return res

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        stage_id = self.env['project.task.type'].search([('name','=',self.stage_id.name)],limit=1)
        task_id = self.env['project.task'].search([('ticket_id','=',self.id)],limit=1)
        task_id.write({'stage_id':stage_id.id})

    def prepare_working_hours_dictionary(self, attendance_ids):
        working_hours = {}
        for rec in attendance_ids:

            minutes = int((rec.hour_from - int(rec.hour_from)) * 60)
            hours = int(rec.hour_from)
            hour_from = f"{hours}:{minutes}"

            minutes = int((rec.hour_to - int(rec.hour_to)) * 60)
            hours = int(rec.hour_to)
            hour_to = f"{hours}:{minutes}"

            if int(rec.dayofweek) not in working_hours:
                working_hours[int(rec.dayofweek)] = [(hour_from, hour_to)]
            else:
                working_hours[int(rec.dayofweek)].append((hour_from, hour_to))
        return working_hours

    def find_starting_day(self, datetime, working_hours):
        while True:
            starting_day = working_hours.get(datetime.weekday())
            if not starting_day:
                datetime += timedelta(days=1)
            else:
                break
        return datetime, starting_day

    def find_starting_time(self, datetime, working_hours):
        weekday = datetime.weekday()
        datetime, starting_day = self.find_starting_day(datetime, working_hours)
        if datetime.time() <= datetime.strptime(starting_day[0][0], "%H:%M").time():
            return datetime, starting_day[0][0]
        elif datetime.time() >= datetime.strptime(starting_day[-1][1], "%H:%M").time():
            datetime += timedelta(days=1)
            datetime, starting_day = self.find_starting_day(datetime, working_hours)
            return datetime, starting_day[0][0]
        else:
            last_hour = None
            for rec in starting_day:
                if last_hour and rec[0] != last_hour:
                    if datetime.time() >= datetime.strptime(last_hour, "%H:%M").time() and datetime.time() <= datetime.strptime(rec[0], "%H:%M").time():
                        return datetime, rec[0]
                if datetime.time() >= datetime.strptime(rec[0], "%H:%M").time() and datetime.time() <= datetime.strptime(rec[1], "%H:%M").time():
                    return datetime, datetime.time().strftime("%H:%M")
                last_hour = rec[1]

    @api.depends('user_id')
    def compute_sla_resolve_date(self):
        for rec in self:
            rec.sla_resolve_date = False
            # if rec.dummy_datetime:
            if rec.user_id and rec.team_id.sla_resolve :
                user_pytz = pytz.timezone(rec.user_id.tz)
                # starting_date = rec.dummy_datetime.astimezone(user_pytz)
                starting_date = datetime.now().astimezone(user_pytz)
                employee = rec.env['hr.employee'].search([('user_id', '=', rec.user_id.id)])
                attendance_ids = employee.resource_calendar_id.attendance_ids
                if attendance_ids:
                    sla_response_minute = int((rec.team_id.sla_resolve - int(rec.team_id.sla_resolve)) * 60)
                    sla_response_hours = int(rec.team_id.sla_resolve)
                    # sla_response = datetime.strptime(f"{sla_response_hours}:{sla_response_minute}", "%H:%M").time()
                    sla_response = timedelta(hours=sla_response_hours, minutes=sla_response_minute)
                    working_hours = self.prepare_working_hours_dictionary(attendance_ids)
                    starting_date, starting_time = rec.find_starting_time(starting_date, working_hours)
                    # calculated_time = datetime.strptime(str(starting_date.date()) + ' 0:0', '%Y-%m-%d %H:%M')
                    calculated_time = timedelta(hours=0, minutes=0)
                    if attendance_ids and sla_response:
                        while True:
                            for working_hour in working_hours.get(starting_date.weekday()) or []:
                                if starting_time:
                                    # if datetime.strptime(starting_time, "%H:%M").time() >= datetime.strptime(working_hour[0], "%H:%M").time() and datetime.strptime(starting_time, "%H:%M").time() <= datetime.strptime(working_hour[1], "%H:%M").time():
                                    if timedelta(hours=int(starting_time.split(':')[0]), minutes=int(starting_time.split(':')[1])) >= timedelta(hours=int(working_hour[0].split(':')[0]), minutes=int(working_hour[0].split(':')[1])) and timedelta(hours=int(starting_time.split(':')[0]), minutes=int(starting_time.split(':')[1])) <= timedelta(hours=int(working_hour[1].split(':')[0]), minutes=int(working_hour[1].split(':')[1])):
                                        tt = starting_time
                                    else:
                                        continue
                                else:
                                    tt = working_hour[0]
                                hour_from = datetime.strptime(str(starting_date.date()) + ' ' + tt, '%Y-%m-%d %H:%M')
                                hour_to = datetime.strptime(str(starting_date.date()) + ' ' + working_hour[1], '%Y-%m-%d %H:%M')
                                difference = hour_to - hour_from
                                hours = difference.seconds // 3600
                                minutes = (difference.seconds // 60) % 60
                                # calculated_hour_minute = calculated_time + timedelta(hours=hours, minutes=minutes)
                                calculated_hour_minute = calculated_time + timedelta(hours=hours, minutes=minutes)
                                
                                # if calculated_hour_minute.time() >= sla_response:
                                if calculated_hour_minute >= sla_response:
                                    # calculated_time = datetime.strptime(str(starting_date.date()) + ' ' + f"{sla_response.hour}:{sla_response.minute}", '%Y-%m-%d %H:%M') - timedelta(hours=calculated_time.hour, minutes=calculated_time.minute)
                                    # calculated_time = sla_response - timedelta(hours=calculated_time.hour, minutes=calculated_time.minute)
                                    calculated_time = sla_response - calculated_time
                                    # sla_response_date_utc = hour_from + timedelta(hours=calculated_time.hour, minutes=calculated_time.minute)
                                    sla_response_date_utc = hour_from + calculated_time
                                    
                                    sla_response_date_local = utc.localize(sla_response_date_utc).astimezone(timezone(self.env.user.tz or 'UTC')).replace(tzinfo=None)
                                    if  sla_response_date_local > sla_response_date_utc:
                                        time_diff = sla_response_date_local - sla_response_date_utc
                                        hours = time_diff.seconds // 3600
                                        minutes = (time_diff.seconds // 60) % 60
                                        rec.sla_resolve_date = sla_response_date_utc - timedelta(hours=hours, minutes=minutes)
                                    else:
                                        time_diff = sla_response_date_utc - sla_response_date_local
                                        hours = time_diff.seconds // 3600
                                        minutes = (time_diff.seconds // 60) % 60
                                        rec.sla_resolve_date = sla_response_date_utc + timedelta(hours=hours, minutes=minutes)
                                    break
                                else:
                                    calculated_time = calculated_hour_minute
                                starting_time = 0

                            if rec.sla_resolve_date:
                                break
                            starting_date += timedelta(days=1)
                            # calculated_time = datetime.strptime(str(starting_date.date()) + ' ' + f"{calculated_time.hour}:{calculated_time.minute}", '%Y-%m-%d %H:%M')

    @api.depends('user_id')
    def compute_sla_response_date(self):
        for rec in self:
            rec.sla_response_date = False
            # if rec.dummy_datetime:
            if rec.user_id and rec.team_id.sla_response :
                user_pytz = pytz.timezone(rec.user_id.tz)
                # starting_date = rec.dummy_datetime.astimezone(user_pytz)
                starting_date = datetime.now().astimezone(user_pytz)
                employee = rec.env['hr.employee'].search([('user_id', '=', rec.user_id.id)])
                attendance_ids = employee.resource_calendar_id.attendance_ids
                if attendance_ids:
                    sla_response_minute = int((rec.team_id.sla_response - int(rec.team_id.sla_response)) * 60)
                    sla_response_hours = int(rec.team_id.sla_response)
                    # sla_response = datetime.strptime(f"{sla_response_hours}:{sla_response_minute}", "%H:%M").time()
                    sla_response = timedelta(hours=sla_response_hours, minutes=sla_response_minute)
                    working_hours = self.prepare_working_hours_dictionary(attendance_ids)
                    starting_date, starting_time = rec.find_starting_time(starting_date, working_hours)
                    # calculated_time = datetime.strptime(str(starting_date.date()) + ' 0:0', '%Y-%m-%d %H:%M')
                    calculated_time = timedelta(hours=0, minutes=0)
                    if attendance_ids and sla_response:
                        while True:
                            for working_hour in working_hours.get(starting_date.weekday()) or []:
                                if starting_time:
                                    # if datetime.strptime(starting_time, "%H:%M").time() >= datetime.strptime(working_hour[0], "%H:%M").time() and datetime.strptime(starting_time, "%H:%M").time() <= datetime.strptime(working_hour[1], "%H:%M").time():
                                    if timedelta(hours=int(starting_time.split(':')[0]), minutes=int(starting_time.split(':')[1])) >= timedelta(hours=int(working_hour[0].split(':')[0]), minutes=int(working_hour[0].split(':')[1])) and timedelta(hours=int(starting_time.split(':')[0]), minutes=int(starting_time.split(':')[1])) <= timedelta(hours=int(working_hour[1].split(':')[0]), minutes=int(working_hour[1].split(':')[1])):
                                        tt = starting_time
                                    else:
                                        continue
                                else:
                                    tt = working_hour[0]
                                hour_from = datetime.strptime(str(starting_date.date()) + ' ' + tt, '%Y-%m-%d %H:%M')
                                hour_to = datetime.strptime(str(starting_date.date()) + ' ' + working_hour[1], '%Y-%m-%d %H:%M')
                                difference = hour_to - hour_from
                                hours = difference.seconds // 3600
                                minutes = (difference.seconds // 60) % 60
                                # calculated_hour_minute = calculated_time + timedelta(hours=hours, minutes=minutes)
                                calculated_hour_minute = calculated_time + timedelta(hours=hours, minutes=minutes)
                                
                                # if calculated_hour_minute.time() >= sla_response:
                                if calculated_hour_minute >= sla_response:
                                    # calculated_time = datetime.strptime(str(starting_date.date()) + ' ' + f"{sla_response.hour}:{sla_response.minute}", '%Y-%m-%d %H:%M') - timedelta(hours=calculated_time.hour, minutes=calculated_time.minute)
                                    # calculated_time = sla_response - timedelta(hours=calculated_time.hour, minutes=calculated_time.minute)
                                    calculated_time = sla_response - calculated_time
                                    # sla_response_date_utc = hour_from + timedelta(hours=calculated_time.hour, minutes=calculated_time.minute)
                                    sla_response_date_utc = hour_from + calculated_time
                                    
                                    sla_response_date_local = utc.localize(sla_response_date_utc).astimezone(timezone(self.env.user.tz or 'UTC')).replace(tzinfo=None)
                                    if  sla_response_date_local > sla_response_date_utc:
                                        time_diff = sla_response_date_local - sla_response_date_utc
                                        hours = time_diff.seconds // 3600
                                        minutes = (time_diff.seconds // 60) % 60
                                        rec.sla_response_date = sla_response_date_utc - timedelta(hours=hours, minutes=minutes)
                                    else:
                                        time_diff = sla_response_date_utc - sla_response_date_local
                                        hours = time_diff.seconds // 3600
                                        minutes = (time_diff.seconds // 60) % 60
                                        rec.sla_response_date = sla_response_date_utc + timedelta(hours=hours, minutes=minutes)
                                    break
                                else:
                                    calculated_time = calculated_hour_minute
                                starting_time = 0

                            if rec.sla_response_date:
                                break
                            starting_date += timedelta(days=1)
                            # calculated_time = datetime.strptime(str(starting_date.date()) + ' ' + f"{calculated_time.hour}:{calculated_time.minute}", '%Y-%m-%d %H:%M')

    @api.depends('sla_response_date')
    def compute_countdown_seconds(self):
        for record in self:
            record.sla_response_time_left = False
            record.sla_response_time_left_char = "No deadline"
            if record.sla_response_date:
                current_datetime = fields.Datetime.now()
                time_difference = record.sla_response_date - current_datetime
                days, remainder = divmod(time_difference.total_seconds(), 86400)  # 86400 seconds in a day
                hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
                minutes, seconds = divmod(remainder, 60)  # 60 seconds in a minute
                if not int(days) == 0:
                    record.sla_response_time_left_char = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
                else:
                    record.sla_response_time_left_char = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    @api.depends('closed_date', 'response_date')
    def compute_time(self):
        for rec in self:
            rec.time_to_response = False
            rec.time_to_resolve = False
            if rec.response_date and rec.assigned_date:
                response_diff = datetime.now() - rec.assigned_date
                response_hours = response_diff.total_seconds() / 3600
                rec.time_to_response = response_hours
            if rec.closed_date and rec.assigned_date:
                resolve_diff = datetime.now() - rec.assigned_date
                resolve_hours = resolve_diff.total_seconds() / 3600
                rec.time_to_resolve = resolve_hours

    @api.depends('message_ids', 'stage_id')
    def compute_response_date(self):
        for rec in self:
            rec.response_date = False
            rec.resolve_date = False
            rec.closed_date = False

            if len(rec.message_ids) > 1:
                rec.response_date = fields.Datetime.now()
            if rec.stage_id.closed:
                rec.closed_date = fields.Datetime.now()

    @api.depends()
    def compute_sla_response_state(self):
        for rec in self:
            rec.sla_response_state = False
            response_diff_hours = 0
            if rec.assigned_date and isinstance(rec.assigned_date, datetime) and rec.response_date and isinstance(rec.response_date, datetime):
                diff_time = rec.response_date - rec.assigned_date
                response_diff_hours = diff_time.total_seconds() / 3600
                if response_diff_hours < rec.team_id.sla_response:
                    rec.sla_response_state = 'in_sla'
            if rec.assigned_date and isinstance(rec.assigned_date, datetime) or rec.response_date:
                if isinstance(rec.assigned_date, datetime):
                    response_diff = datetime.now() - rec.assigned_date
                    response_hours = response_diff.total_seconds() / 3600
                    diff_hours = abs(rec.team_id.sla_response - response_hours)
                    if diff_hours <= 1 and not rec.response_date:
                        rec.sla_response_state = 'due_soon'
                    elif response_diff_hours > rec.team_id.sla_response:
                        rec.sla_response_state = 'out_sla'
                    else:
                        rec.sla_response_state = 'in_sla'

    @api.depends()
    def compute_sla_state(self):
        for rec in self:
            rec.sla_resolve_state = False
            resolve_diff_hours = 0
            if rec.assigned_date and rec.closed_date:
                diff_time = rec.closed_date  - rec.assigned_date
                resolve_diff_hours = diff_time.total_seconds() / 3600
                if resolve_diff_hours < rec.team_id.sla_resolve:
                    rec.sla_resolve_state = 'in_sla'
            if rec.closed_date or rec.assigned_date:
                resolve_diff = datetime.now() - rec.assigned_date
                resolve_hours = resolve_diff.total_seconds() / 3600
                diff_hours = rec.team_id.sla_resolve - resolve_hours    
                if diff_hours <= 1 and not rec.closed_date:
                    rec.sla_resolve_state = 'due_soon'
                elif resolve_diff_hours > rec.team_id.sla_resolve:
                    rec.sla_resolve_state = 'out_sla'
                else:
                    rec.sla_resolve_state = 'in_sla'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        confirmed_users = res.team_id.user_ids.filtered(lambda x:x.state == 'active' and x.share == False)
        # confirmed_users = self.env['res.users'].search([('state','=','active'),('share', '=', False)])
        if res.team_id.assign_method == 'round_robin' and confirmed_users and len(res.team_id.user_ids) > 1:
            user_count = 1
            if len(confirmed_users) > 1:
                user_count = len(confirmed_users) -1
            if res.team_id.assign_online_users:
                user_count = len(confirmed_users.filtered(lambda x:x.hr_presence_state == 'present'))
                if user_count > 1:
                    user_count = user_count -1 
            previous_tickets = self.search([('team_id','=',res.team_id.id),('id','!=',res.id)],limit=user_count)
            if previous_tickets:
                avilable_users = confirmed_users - previous_tickets[0].user_id
                if res.team_id.assign_online_users:
                    avilable_users = confirmed_users.filtered(lambda x:x.hr_presence_state == 'present')
                if len(avilable_users) > 1:
                    previous_users = previous_tickets.mapped('user_id')
                    can_asigen_users = avilable_users - previous_users
                else:
                    can_asigen_users = avilable_users
                if can_asigen_users:
                    res.user_id = can_asigen_users[0].id
            else:
                if res.team_id.assign_online_users:
                    for user in confirmed_users:
                        if user.employee_id and user.employee_id.hr_presence_state == 'present':
                            res.user_id = user.id
                            break
                else:
                    res.user_id = confirmed_users[0]
        else:
            if res.team_id.assign_method == 'fewest_records' and confirmed_users and len(res.team_id.user_ids) > 1:
                previous_tickets = self.search([('team_id','=',res.team_id.id),('id','!=',res.id)])
                if previous_tickets:
                    ticket_count_per_users = []
                    users = confirmed_users
                    if res.team_id.assign_online_users:
                        users = confirmed_users.filtered(lambda x:x.hr_presence_state == 'present')
                    for user in users:
                        count_dic = {}
                        ticket_count = len(previous_tickets.filtered(lambda x:x.user_id.id == user.id))
                        count_dic[user.id] = ticket_count
                        ticket_count_per_users.append(count_dic)
                    min_key = []
                    min_value = float('inf')
                    for item in ticket_count_per_users:
                        for key, value in item.items():
                            if value < min_value:
                                min_value = value
                                min_key = [key]
                            elif value == min_value:
                                min_key.append(key)
                    for rec in min_key:
                        if len(confirmed_users.filtered(lambda x:x.hr_presence_state == 'present')) > 1:
                            if previous_tickets[0].user_id.id != rec:
                                res.user_id = rec
                                break
                        else:
                            res.user_id = rec
                            break
                else:
                    if res.team_id.assign_online_users:
                        for user in confirmed_users:
                            if user.employee_id and user.employee_id.hr_presence_state == 'present':
                                res.user_id = user.id
                                break
                    else:
                        res.user_id = confirmed_users[0]

        return res

    @api.onchange('stage_id')
    def generate_res_partner(self):
        if self.team_id.id == 77 and self.stage_id.id in [52, 43]:
            task = self.env['project.task'].search([('ticket_id', '=', self._origin.id)])

            if task:
                host_partner_contact = self.env['res.partner'].search([('host_partner_ticket_id', '=', self._origin.id)])
                host_partner_contact_vals = {
                    'name': task.name,
                    'youth_company_type': task.company_type,
                    'host_partner_ticket_id': self._origin.id,
                    'street': task.street,
                    'street2': task.street2,
                    'city': task.city,
                    'state_id': task.state_id.id,
                    'country_id': task.country_id.id,
                    'zip': task.zip,
                    'bee_level': task.bee_level,
                    'business_size': task.business_size,
                    'sector_id': task.sector_id.id,
                    'email': task.email_from
                }
                if not host_partner_contact:
                    context = self._context.copy()
                    context.pop('default_team_id', None)
                    rec = self.env['res.partner'].with_context(context).create(host_partner_contact_vals)
                else:
                    host_partner_contact.write(host_partner_contact_vals)
        if self.team_id.id == 76 and self.has_approved and self.stage_id.id == 51:
            task_id = self.env['project.task'].search([('ticket_id','=',self._origin.id)],limit=1)
            leave_timesheets = task_id.timesheet_ids.filtered(lambda x:x.daily_attendance_status not in ['Present', 'Weekend'])
            for rec in leave_timesheets:
                if rec.daily_leave_form:
                    leave = self.env['hr.leave'].search([('timesheet_id','=',rec.id)])
                    try:
                        leave.action_approve()
                    except Exception as error:
                        raise UserError("%s" % error)

    @api.onchange('stage_id')
    def generate_project_task(self):
        # Ensure that the method only runs on an existing ticket
        if self._origin:
            # Search for the related task using the original ticket id
            task = self.env['project.task'].search([('ticket_id', '=', self._origin.id)])
            stage = self.env['project.task.type'].search([('name','=',self.stage_id.name)],limit=1)
            if not stage:
                stage = self.env['project.task.type'].create({
                    "name":self.state_id.name
                    })
            if task:
                task.ensure_one()
                vals = {
                    'company_type': self.company_type,
                    'resignation_date': self.resignation_date,
                    'session_id': self.session_id.id,
                    'session_link': self.session_link,
                    'has_approved': self.has_approved,
                    'has_declined': self.has_declined,
                    'stage_id': stage.id,
                    'visit_type': self.visit_type,
                    'register_date': self.register_date,
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
                    'issue_date_closed': self.issue_date_closed,
                }
                task.write(vals)
                if self.project_id.id == 66 and self.stage_id.id == 721:
                    task.register_issue_timesheet_ids.write({'has_register_issues': False})
                else:
                    task.register_issue_timesheet_ids.write({'has_register_issues': True})
            else:
                pass
        else:
            pass

    @api.onchange('has_approved', 'has_declined')
    def generate_register_issue_ticket(self):
        weekly_task = self.env['project.task'].search([('ticket_id', '=', self._origin.id)])
        if self.project_id.id == 66 and (self.has_approved or self.has_declined) and not weekly_task.register_issue_task_id:
            timesheet_with_issues = False
            vals = {}
            if self.has_approved:
                timesheet_with_issues = self.timesheet_ids.filtered(lambda sub_task: sub_task.daily_attendance_status and sub_task.daily_attendance_status not in ['Present', 'Weekend'])
                vals.update({'has_approved': True})
            elif self.has_declined:
                timesheet_with_issues = self.timesheet_ids
                vals.update({'has_declined': True})
            if timesheet_with_issues:
                vals.update({
                    'name': (weekly_task.employee_id.name or '')  + '(' + weekly_task.week_start.strftime('%d-%m-%Y') + ' ' + weekly_task.week_end.strftime('%d-%m-%Y') + ')',
                    'employee_id': weekly_task.employee_id.id,
                    'project_id': 63,
                    'company_id': self.company_id.id})
                registration_issue_task = self.env['project.task'].create(vals)
                if registration_issue_task:
                    for time_sheet in timesheet_with_issues:
                        time_sheet._origin.with_context(test=True).write({'registration_issue_task_id': registration_issue_task.id, 'has_register_issues': True})
                    registration_issue_task.with_context(test=True).add_the_issued_timesheet_to_ticket()
                    weekly_task.with_context(test=True).write({'register_issue_task_id': registration_issue_task.id, 'stage_id': 706})
            else:
                self.write({'stage_id':51})
                
    def delete_ticket_kwaZulu_natal(self):
        current_year = datetime.now().year

        # Search for tickets with team_id = 64 and created in January
        tickets = self.env['helpdesk.ticket'].search([
            ('team_id', '=', 64),
            ('create_date', '>=', f'{current_year}-01-01 00:00:00'),
            ('create_date', '<', f'{current_year}-02-01 00:00:00')
        ])
        tickets.unlink()
