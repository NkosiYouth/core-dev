# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
from datetime import datetime

import re
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    host_site_id = fields.Many2one('res.partner', string="Host Site", domain="[('youth_company_type', '=', 'Host Site')]")
    # partner_id = fields.Many2one('res.partner', string="Partner", domain="[('company_type', '=', 'Partner')]")
    partner_id = fields.Many2one('res.partner', string="Partner", related='host_site_id.parent_id')
    cohort_id = fields.Many2one('cohort.cohort')
    x_contract_month = fields.Integer('Month Into Programme')
    dashboard = fields.Html(compute='compute_dashboard')
    disabled = fields.Boolean()
    first_name = fields.Char()
    funder_id = fields.Many2one('res.partner', related="cohort_id.funder_id", store=True)
    has_hr_issues = fields.Boolean()
    host_id = fields.Many2one('res.partner')
    # host_site_id = fields.Many2one('res.partner')
    host_site_province_id = fields.Many2one('res.country.state', related="host_site_id.state_id", store=True)
    hr_issues_ids = fields.One2many('project.task', 'employee_id', string="HR Issues", domain=[('project_id', '=', 58)])
    jm_hr_basics = fields.Date('HR Basics - Employee Relations')
    jm_induction = fields.Date('Induction')
    journey_id = fields.Many2one('project.project', string='Journey')
    journey_ids = fields.One2many('project.task', 'employee_id', string='Journey Sessions', domain=[('is_journey', '=', True)])
    last_name = fields.Char()
    next_of_kin_ids = fields.Many2many('res.partner', string='Next of Kin')
    # partner_id = fields.Many2one('res.partner')
    payroll_type = fields.Selection([('ip', 'IP'),('Funder', 'Funder')], related="cohort_id.payroll_type", store=True)
    race = fields.Selection([('African', 'African'), ('Coloured', 'Coloured'), ('Indian', 'Indian'), ('Other', 'Other'), ('White', 'White')])
    register_ids = fields.One2many('project.task', 'employee_id', string='Weekly Registers', domain=[('project_id', '=', 66)])
    sector_id = fields.Many2one('res.partner.industry')
    session_task_ids = fields.One2many('project.task', 'employee_id', string='Session Tasks', domain=[('project_id', '=', 55)])
    site_visit_ids = fields.One2many('project.task', 'employee_id', string='Site Visits', domain=[('project_id', '=', 57)])
    title_id = fields.Many2one('res.partner.title')
    total_days_present = fields.Integer('Total Days Present')
    total_outstanding_registers = fields.Integer('Outstanding Registers', compute='compute_dashboard_value')
    total_register_tasks = fields.Integer('Total Register Tasks' , compute='compute_dashboard_value')
    user_roles_id = fields.Many2one('user.role', string='User Role')
    survey_ids = fields.One2many('survey.user_input', 'employee_id')
    contract_start_date = fields.Date(string="Contract Start Date", related="contract_id.date_start", store=True, readonly=True)
    contract_end_date = fields.Date(string="Contract End Date", related="contract_id.date_end", store=True, readonly=True)

    count_outstanding_registers = fields.Integer()
    count_hr_issues = fields.Integer(compute='compute_dashboard_value')
    count_annual_leave = fields.Float(compute='compute_dashboard_value')
    remaining_annual_leave = fields.Float(compute='compute_dashboard_value')
    count_sick_leave = fields.Float(compute='compute_dashboard_value')
    remaining_sick_leave = fields.Float(compute='compute_dashboard_value')
    count_unscheduled_visits = fields.Integer(compute='compute_dashboard_value')
    count_total_visits = fields.Integer(compute='compute_dashboard_value')
    count_maternity_leave = fields.Float(compute='compute_dashboard_value')
    remaining_maternity_leave = fields.Float(compute='compute_dashboard_value')
    count_family_responsibility_leave = fields.Float(compute='compute_dashboard_value')
    remaining_family_responsibility_leave = fields.Float(compute='compute_dashboard_value')
    count_discretionary_leave = fields.Float()
    id_number = fields.Char()
    absorption_indication = fields.Selection([('Permanent Employment', 'Permanent Employment'), ('Fixed Term Employment', 'Fixed Term Employment')])
    past_task_create = fields.Boolean()


    def _reset_host_site_id(self):
        employees = self.search([("host_site_id", "!=", False)])
        for employee in employees:
            host_site = employee.host_site_id
            _logger.info(">>>>>>>>>>>>host_site old>>>>>>>>>>>>>>>>> %s" % host_site.name)
            employee.host_site_id = False
            employee.host_site_id = host_site
            _logger.info(">>>>>>>>>>>>>>>>host_site new>>>>>>>>>>>>> %s" % employee.host_site_id.name)


    @api.depends()
    def compute_dashboard_value(self):
        for rec in self:
            rec.total_register_tasks = False
            rec.total_outstanding_registers = False
            rec.count_hr_issues = False
            rec.count_annual_leave = False
            rec.remaining_annual_leave = False
            rec.count_sick_leave = False
            rec.remaining_sick_leave = False
            rec.count_maternity_leave = False
            rec.remaining_maternity_leave = False
            rec.count_total_visits = False
            rec.count_family_responsibility_leave = False
            rec.remaining_family_responsibility_leave = False

            rec.total_register_tasks = self.env['project.task'].search_count([('project_id','=',63),('employee_id','=',self.id)])
            rec.total_outstanding_registers = self.env['project.task'].search_count(['&',('project_id','=',63),('employee_id','=',self.id),('stage_id','!=',794)])
            rec.count_hr_issues = self.env['project.task'].search_count(['&',('project_id','=',58),('employee_id','=',self.id),('stage_id','!=',728)])
            rec.count_total_visits = self.env['project.task'].search_count(['&',('project_id','=',68),('employee_id','=',self.id)])


            annual_leave_allocation_id = self.env['hr.leave.allocation'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',13),('state','=','validate')])
            annual_leave_ids = self.env['hr.leave'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',13),('state','=','validate')])
            annual_leave_count = sum(annual_leave_ids.mapped('number_of_days_display'))
            rec.count_annual_leave = sum(annual_leave_allocation_id.mapped('number_of_days_display'))
            rec.remaining_annual_leave = rec.count_annual_leave - annual_leave_count

            seak_leave_allocation_id = self.env['hr.leave.allocation'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',9),('state','=','validate')])
            annual_leave_ids = self.env['hr.leave'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',9),('state','=','validate')])
            annual_leave_count = sum(annual_leave_ids.mapped('number_of_days_display'))
            rec.count_sick_leave = sum(seak_leave_allocation_id.mapped('number_of_days_display'))
            rec.remaining_sick_leave = rec.count_sick_leave - annual_leave_count


            maternity_leave_allocation_id = self.env['hr.leave.allocation'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',12),('state','=','validate')])
            maternity_leave_ids = self.env['hr.leave'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',12),('state','=','validate')])
            maternity_leave_count = sum(maternity_leave_ids.mapped('number_of_days_display'))
            rec.count_maternity_leave = sum(maternity_leave_allocation_id.mapped('number_of_days_display'))
            rec.remaining_maternity_leave = rec.count_maternity_leave - maternity_leave_count

            family_responsibility_leave_allocation_id = self.env['hr.leave.allocation'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',14),('state','=','validate')])
            family_responsibility_leave_ids = self.env['hr.leave'].search(['&',('employee_id','=',self.id),('holiday_status_id','=',14),('state','=','validate')])
            family_responsibility_leave_count = sum(family_responsibility_leave_ids.mapped('number_of_days_display'))
            rec.count_family_responsibility_leave = sum(family_responsibility_leave_allocation_id.mapped('number_of_days_display'))
            rec.remaining_family_responsibility_leave = rec.count_family_responsibility_leave - family_responsibility_leave_count

    @api.onchange("job_title", "work_email", "work_phone", "user_roles_id")
    def update_employee_details(self):
        if self.hr_issues_ids:
            self.write({'has_hr_issues': True, 'category_ids': [(6, 0, [19])]})
        else:
            self.write({'has_hr_issues': False, 'category_ids': []})

        for contact in self.related_contact_ids:
            try:
                contact.write({
                'youth_contact_type':self.user_roles_id.name,
                'function':self.job_title,
                'phone':self.work_phone,
                })
            except Exception as error:
                raise UserError("%s" % error)



    def set_type(self):
        for rec in self.search([('user_roles_id','=',3)]):
            if rec.related_contact_ids:
                for res in rec.related_contact_ids:
                    res.youth_contact_type = rec.user_roles_id.name
                    _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>> %s" % res.youth_contact_type)

    def open_youth_visit_task(self):
        return {
            'name': "Youth visit",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'context': {'default_project_id': 68}
        }

    def open_hr_issue_task(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/hr-issues', 
            'target': 'self',
        }

    @api.depends()
    def compute_dashboard(self):
        for rec in self:
            rec.dashboard = False
            dashboard_html = """ """ 
            dashboard_html +="""
                    <div style="width:100%;display:block;">
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4790d0; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">{total_outstanding_registers}/{total_register_tasks}</div>
                        <div>Outstanding Registers</div> 
                    </div>
                    """.format(total_outstanding_registers=self.total_outstanding_registers, total_register_tasks=self.total_register_tasks)
            dashboard_html +="""
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4700d0; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">{count_hr_issues}</div>
                        <div>HR Issues </div>
                    </div>
                    """.format(count_hr_issues=self.count_hr_issues)
            dashboard_html +="""
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4770d0; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">{remaining_annual_leave}/{count_annual_leave}</div>
                        <div>Annual Leave</div>
                    </div>
                    """.format(remaining_annual_leave=self.remaining_annual_leave ,count_annual_leave=self.count_annual_leave)
            dashboard_html +="""
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4790da; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">{remaining_sick_leave}/{count_sick_leave}</div>
                        <div>Total Sick Leave </div>
                    </div>
                    """.format(remaining_sick_leave=self.remaining_sick_leave, count_sick_leave=self.count_sick_leave)
            dashboard_html +="""
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4790da; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">{count_total_visits}/{count_total_visits}</div>
                        <div>No. of Unscheduled Visits </div>
                    </div>
                    """.format(count_total_visits=self.count_total_visits)
            if self.gender == 'female':
                dashboard_html +="""
                        <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4790da; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                            <div style="font-size:40px;font-weight: bold;">{remaining_maternity_leave}/{count_maternity_leave}</div>
                            <div>Total Maternity Leave</div>
                        </div>
                        """.format(remaining_maternity_leave=self.remaining_maternity_leave, count_maternity_leave=self.count_maternity_leave)
            dashboard_html +="""
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4790da; color: #ffffff; margin-right: 4px; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">6/6</div>
                        <div>Total Discretionary Leave</div>
                    </div>
                    """
            dashboard_html +="""
                    <div style="width:24%;min-width: 100px; height: 95px; border: 1px solid #000000; text-align: center; background-color: #4790da; color: #ffffff; margin-bottom: 10px; display: inline-block;">
                        <div style="font-size:40px;font-weight: bold;">{remaining_family_responsibility_leave}/{count_family_responsibility_leave}</div>
                        <div>Total Family Responsibility Leave</div>
                    </div>
                </div> 
                """.format(remaining_family_responsibility_leave=self.remaining_family_responsibility_leave, count_family_responsibility_leave=self.count_family_responsibility_leave)
            rec.dashboard = dashboard_html
            
    # New write method
    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        # Check if 'active' field is being set to False (archiving the employee)
        if 'active' in vals and vals['active'] == False:
            for employee in self:
                # Check if the employee's user_roles_id is 'Youth'
                if employee.user_roles_id and employee.user_roles_id.name == 'Youth':
                    # Proceed with the logic
                    employee._check_cohort_conditions()
        return res

    # New _check_cohort_conditions method
    def _check_cohort_conditions(self):
        self.ensure_one()
        employee = self
        # Check if the employee is linked to a cohort
        if employee.cohort_id:
            # Get the employee's active contract
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'open')
            ], limit=1)
            # Use x_contract_month if month_into_program doesn't exist in hr.contract
            month_into_program = contract.month_into_program if hasattr(contract, 'month_into_program') else employee.x_contract_month
            if contract and month_into_program and month_into_program < 8:
                # Now, check cohort buffer and drop-off replacement target
                cohort = employee.cohort_id
                # Count number of inactive employees in the cohort who left before 8 months
                employees_in_cohort = self.env['hr.employee'].search([
                    ('cohort_id', '=', cohort.id),
                    ('user_roles_id', '=', employee.user_roles_id.id)
                ])
                inactive_before_month_8 = self.env['hr.employee'].search_count([
                    ('id', 'in', employees_in_cohort.ids),
                    ('active', '=', False),
                    ('x_contract_month', '<', 8)
                ])
                # Check if the cohort buffer has been reached
                if inactive_before_month_8 >= (cohort.cohort_buffer or 0):
                    # Display a notification
                    message = _(
                        "Cohort Buffer has been reached or exceeded for cohort '%s'. "
                        "No more replacements allowed."
                    ) % (cohort.name)
                    self.env.user.notify_info(message)
                # Check if the drop-off replacement target has been reached
                if inactive_before_month_8 >= (cohort.drop_off_replacement or 0):
                    message = _(
                        "Drop-off replacement target has been reached or exceeded for cohort '%s'. "
                        "Consider adding replacements."
                    ) % (cohort.name)
                    self.env.user.notify_info(message)


    def upate_weekly_register_name_seq(self):
        employees = self.env['hr.employee'].search([
            ('user_roles_id.name', '=', 'Youth'),
            ('active', '=', True)
        ])
        
        for employee in employees:
            weekly_registers = self.env['project.task'].search([
                ('employee_id', '=', employee.id),
                ('project_id', '=', 66)
            ])

            if not weekly_registers:
                continue  # Skip if no registers found

            # Extract and sort weekly registers by start date
            def get_start_date(register):
                try:
                    match = re.search(r"Week \d+ \((\d{2}-\d{2}-\d{4})", register.name)
                    if match:
                        return datetime.strptime(match.group(1), "%d-%m-%Y").date()
                except Exception:
                    return None  # Handle cases where name format is incorrect

            sorted_registers = sorted(
                [reg for reg in weekly_registers if get_start_date(reg)],
                key=get_start_date
            )

            if not sorted_registers:
                continue  # No valid registers

            start_date = get_start_date(sorted_registers[0])

            # Process each register
            for register in sorted_registers:
                try:
                    match = re.search(r"Week (\d+) \((\d{2}-\d{2}-\d{4}) - (\d{2}-\d{2}-\d{4})\)", register.name)
                    if not match:
                        continue  # Skip if format is incorrect
                    
                    existing_week_number = int(match.group(1))
                    first_date_str, second_date_str = match.group(2), match.group(3)

                    # Convert to date objects
                    week_start_date = datetime.strptime(first_date_str, "%d-%m-%Y").date()
                    week_end_date = datetime.strptime(second_date_str, "%d-%m-%Y").date()

                    # Calculate new week number
                    difference_in_days = (week_start_date - start_date).days
                    new_week_number = max(0, difference_in_days // 7) + 1  # Ensures week is not negative

                    # Skip update if week number is the same
                    if existing_week_number == new_week_number:
                        continue

                    # Update register name
                    new_name = f"Week {new_week_number} ({week_start_date.strftime('%d-%m-%Y')} - {week_end_date.strftime('%d-%m-%Y')})"
                    register.name = new_name

                    # Update related ticket name
                    if register.ticket_id:
                        register.ticket_id.name = new_name
                    
                    self._cr.commit()
                    _logger.info(f"Updated register name for {employee.name}: {new_name}")

                except Exception as e:
                    _logger.error(f"Error updating register {register.id}: {e}")
