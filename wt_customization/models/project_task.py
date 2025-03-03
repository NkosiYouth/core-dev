# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)    

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    
    is_show_recent_so_q = fields.Boolean()


class ProjectTask(models.Model):
    _inherit = 'project.task'

    
        

    company_type = fields.Selection([("Partner","Partner"),("Host Site","Host Site")],string="Company Type",)
    female_ownership = fields.Float(string="Female Ownership(%)")
    add_learnings = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware of additional online learning that you can do to assist in achieving your plans?")
    attendance_register = fields.Binary(string="Register")
    attendance_register_id = fields.Many2one(string="Attendance Register",comodel_name="project.task")
    attendance_register_task_id = fields.Many2one(string="Attendance Register",comodel_name="project.task")
    attendance_report = fields.Boolean(string="Attendance Report Flag")
    attendance_status = fields.Selection([("Approved","Approved"),("Not Approved","Not Approved")],string="Attendance Status")
    attendance_week_end = fields.Date(string="Week End")
    attendance_week_start = fields.Date(string="Week Start")
    bee_level = fields.Selection([("BEE Level 1","BEE Level 1"),("BEE Level 2","BEE Level 2"),("BEE Level 3","BEE Level 3"),
                                  ("BEE Level 4","BEE Level 4"),("BEE Level 5","BEE Level 5"),("BEE Level 6","BEE Level 6"),
                                  ("BEE Level 7","BEE Level 7"),("BEE Level 8","BEE Level 8")],string="BEE Level")
    business_id = fields.Many2one(comodel_name="res.partner",string="Business")
    business_size = fields.Selection([("Small","Small"),("Medium","Medium"),("Large","Large")],string="Business Size")
    call_type = fields.Selection([("call_type_1","Call Type 1"),("call_type_2","Call Type 2")],string="Call Type")
    city = fields.Char(string="City")
    contract_yaw = fields.Selection([("Yes","Yes"),("No","No")],string="Do you know that you have to share your future employment contract with youth@WORK?")
    country_id = fields.Many2one(comodel_name="res.country",string="Country")
    cv = fields.Selection([("Yes","Yes"),("No","No")],string="Have you prepared your CV, updated it and included a reference letter from your current employer?")
    daily_attendance_status = fields.Selection([("Present","Present"),("Annual Leave","Annual Leave"),("Sick Leave","Sick Leave"),
                                                ("Study Leave","Study Leave"),("Maternity Leave","Maternity Leave"),("Half Day","Half Day"),("Unpaid Leave","Unpaid Leave"),('Family Responsibility Leave', 'Family Responsibility Leave'), ('Public Holiday', 'Public Holiday'), ('Off Day', 'Off Day'),
                                                ("Weekend","Weekend")],string="Daily Status Selection")
    daily_attendance_type = fields.Selection([("Weekly","Weekly"),("Session","Session")],string="Daily Attendance Type")
    daily_duties = fields.Text(string="Duties")
    daily_end_time = fields.Datetime(string="End Time")
    daily_leave_form = fields.Binary(string="Leave Form")
    daily_start_time = fields.Datetime(string="Start Time")
    daily_supervisor_id = fields.Many2one(comodel_name="hr.employee",string="Supervisor")
    daily_type = fields.Selection([("Session","Session"),("Weekly","Weekly")],string="Daily Attendance Type")
    date_closed = fields.Date(string="Date Closed")
    days_since_created = fields.Integer(string="Days since created")
    discussed_goals = fields.Selection([("Yes","Yes"),("No","No")],string="Has she/he discussed this with her supervisor and complete the monthly progress report?")
    duration = fields.Float(string="Duration")
    employee_id = fields.Many2one(comodel_name="hr.employee",string="Youth")
    end_date = fields.Date(string="End Date")
    engage_yesapp = fields.Selection([("When I have time","When I have time"),("Weekly","Weekly"),("Post the YES Program","Post the YES Program"),("Monthly","Monthly"),
                                      ("Daily","Daily")],string="How often will you engage on the YES Apps?")
    funder_id = fields.Many2one(comodel_name="res.partner",string="Funder")
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
    has_register_issues = fields.Boolean(string="Has Register Issues")
    have_new_cell_number = fields.Selection([("Yes","Yes"),("No","No")],string="Have you changed your cell phone number?")
    host_site_id = fields.Many2one(comodel_name="res.partner",string="Host Site")
    # host_site_name_id = fields.Many2one(comodel_name="res.partner",string="Name of Host Site")
    host_site_task_ids = fields.One2many(comodel_name="project.task", inverse_name="partner_task_id",string="Host Site Task")
    host_site_ticket_id = fields.Many2one(comodel_name="helpdesk.ticket",string="Host Site Ticket")
    youth_site_employee_id = fields.Many2one(comodel_name="hr.employee",string="Youth")
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
    matter_details = fields.Text(string="Matter Details")
    new_email = fields.Char(string="New email address")
    new_number = fields.Char(string="New number")
    nowork_nopay = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware of the no work no pay rule?")
    online_learning = fields.Selection([("Yes","Yes"),("No","No")],string="Are you committed to online learning?")
    partner_task_id = fields.Many2one(comodel_name="project.task",string="Partner Task")
    cohort_id = fields.Many2one(comodel_name="cohort.cohort",string="Cohort")
    cohorts_ids = fields.Many2many(comodel_name="cohort.cohort",string="Cohorts")
    site_visit_date = fields.Date(string="Host Site Visit Date")
    vacancies = fields.Integer(string="Vacancies")
    week = fields.Integer(string="Week", store=True)
    week_start = fields.Date(string="Week Start")
    week_end = fields.Date(string="Week End")
    register_doc = fields.Binary(string="Register")
    resignation_date = fields.Date(string="Resignation Date")
    reason_for_resignation = fields.Selection([("Better Job Opportunity","Better Job Opportunity"),("Family Reasons","Family Reasons"),("Personal Reasons","Personal Reasons"),
                                               ("Health Reasons","Health Reasons"),("Furthering Studies","Furthering Studies"),("Starting My Own Business","Starting My Own Business")],string="Reason for Resignation")
    resignation_letter = fields.Binary(string="Resignation Letter")
    street = fields.Char(string="Street Line 1")
    street2 = fields.Char(string="Street Line 2")
    state_id = fields.Many2one(comodel_name="res.country.state",string="State")
    zip = fields.Char(string="Zip")
    sector_id = fields.Many2one(comodel_name="res.partner.industry",string="Sector")
    start_date = fields.Date(string="Start Date")
    session_id = fields.Many2one(comodel_name="session.session",string="Session")
    session_link = fields.Html(string="Session Link")
    register_day = fields.Date(string="Date")
    register_day_summary = fields.Html(string="Register Summary")
    register_date = fields.Date(string="Register Date")
    rsa_id_number = fields.Char(string="RSA ID Number")
    register_issue_task_id = fields.Many2one(comodel_name="project.task",string="Register Issue Task")
    visit_type = fields.Selection([("Normal Host Site Visit","Normal Host Site Visit"),("Induction","Induction"),("Exit Session","Exit Session"),
                                   ("Cellphone Distribution","Cellphone Distribution"),("Questions for Supervisors","Questions for Supervisors"),
                                   ("Graduation Session","Graduation Session")],string="Type of Host Site Visit")
    type_of_visit = fields.Selection([("Yes Youth Alumni Visit","Yes Youth Alumni Visit"),("First Visit","First Visit"),("Follow Up","Follow Up"),
                                      ("Second Visit","Second Visit"),("None of the above","None of the above")],string="Type of Visit")
    plans_after_yes = fields.Text(string="What are your plans for after the YES programme?")
    registers_sent = fields.Selection([("Yes","Yes"),("No","No")],string="Have all registers been sent to the correct email address EVERY FRIDAY?")
    things_learnt_this_month = fields.Text(string="What are new things the youth has learned this month?")
    why_not_discussed_goals = fields.Char(string="If No - why not??")
    studying_what = fields.Text(string="What and where are you studying?")
    receive_whatsapp = fields.Selection([("Yes","Yes"),("No","No")],string="Are you receiving the Youth@Work WhatsApp messages?")
    saved_hotline_number = fields.Selection([("Yes","Yes"),("No","No")],string="If no - have you saved the Youth@Work Hotline 060 749 1927 onto your phone as a contact?")
    whatsapp_number = fields.Char(string="Please give us your ‘WhatsApp” number so we can save it to our system")
    remain_employed = fields.Selection([("Advance within current company","Advance within current company"),("Seek opportunities with a different company","Seek opportunities with a different company"),
                                        ("Pursue further education or training","Pursue further education or training"),("Self-employment","Self-employment")],string="How can you remain employed beyond the program?")
    yes_phone = fields.Selection([("To complete online learning modules","To complete online learning modules"),("To register on YESLife App weekly","To register on YESLife App weekly"),
                                  ("To give to other family members","To give to other family members")],string="Why are you getting a YES phone?")
    yes_supervisor_app = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that you are expected to download the YES Supervisor App and complete a survey once per quarter on the progress made by the youth?")
    yaw_registers = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that you need to send a signed attendance register to youth@WORK every Friday?")
    work_experience = fields.Selection([("Give daily tasks","Give daily tasks"),("Provide a clear job description","Provide a clear job description"),("Mentor and coach when necessary","Mentor and coach when necessary"),("Monitor the youth progress for growth and development","Monitor the youth progress for growth and development"),
                                        ("All of the above","All of the above")],string="How are you assisting the youth to gain a quality work experience?")
    rate_experience = fields.Selection([("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],string="How would you rate your work experience year on a scale of 1 -5 with 1 being bad, 5 being excellent?")
    prepared = fields.Selection([("Yes","Yes"),("No","No"),("Somewhat","Somewhat")],string="Has this program prepared you for future employment?")
    share_contract = fields.Selection([("Yes","Yes"),("No","No")],string="Are you aware that you are obligated to share your next employment contract with youth@WORK ?")
    youth_visit_task_ids = fields.One2many(comodel_name="project.task",inverse_name="site_visit_id",string="Youth Visit Tasks")
    site_visit_id = fields.Many2one(comodel_name="project.task",string="Site Visit")
    register_issue_task_ids = fields.One2many(comodel_name="project.task",inverse_name="register_task_id",string="Register Issue Tasks")
    register_task_id = fields.Many2one(comodel_name="project.task",string="Register Issue Taskk")
    weekly_tasks_ids = fields.One2many(comodel_name="project.task",inverse_name="attendance_register_id",string="Weekly Tasks")
    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")
    weekly_ticket_id = fields.Many2one('helpdesk.ticket')
    register_issue_ticket_id = fields.Many2one('helpdesk.ticket')
    weekly_ticket_register_id = fields.Many2one('helpdesk.ticket')
    register_issue_timesheet_ids = fields.One2many('account.analytic.line', 'registration_issue_task_id')
    daily_attendance_date = fields.Date()
    is_journey = fields.Boolean(related='project_id.journey', store=True)
    journey_session_id = fields.Many2one('journey.session', string="Session Name")
    session_type = fields.Selection(
         selection=[('online', 'Online'), ('in_person', 'In Person')],
         string="Session Type",
         help="Type of session: Online or In Person"
     )
    session_deadline = fields.Date('Session Deadline')
    office_id = fields.Many2one('office.office', "Office")

    is_ticket_timesheet_updated = fields.Boolean(string="Timesheet Updated", readonly=True, default=False)

    @api.onchange('stage_id')
    def update_issue_date(self):
        if self.project_id.id == 58:
            if self.stage_id.id == 728:
                self.issue_date_closed = datetime.now().date()
            else:
                self.issue_date_closed = False

    @api.onchange('partner_id', 'employee_id')
    def update_host_site_id(self):
        self.host_site_id = self.employee_id.host_site_id.id
        self.partner_id = self.host_site_id.parent_id.id

    def update_ticket_timesheet(self):
        """Update ticket timesheet from task timesheet without checking existing ticket timesheets"""
        project = self.env['project.project'].browse(66)
        if not project:
            return
        tasks = self.env['project.task'].search([('project_id', '=', project.id), ('is_ticket_timesheet_updated', '=', False)])
        for task in tasks:
            if task.ticket_id and task.timesheet_ids:
                task.ticket_id.timesheet_ids = [(6, 0, task.timesheet_ids.ids)]
                task.is_ticket_timesheet_updated = True
                self.env.cr.commit()
                _logger.info(f"--------------Updated Ticket {task.ticket_id.id} from Task {task.id}")

        _logger.info("***-----Timesheet update cron job completed.-------***")
