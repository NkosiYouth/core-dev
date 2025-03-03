# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from dateutil import tz
import re
import pytz
import logging
_logger = logging.getLogger(__name__)

from pytz import timezone, utc


class WtCustomizationApi(http.Controller):

    @http.route("/api/ReadRegister", methods=['POST'], type='json', auth='public', csrf=False)
    def get_weeklyregister_timesheet(self, **kwargs):
        phone = kwargs.get('phone')
        if not phone:
            return {"WasSuccessful": False, "message": "Phone number is required"}

        # Sanitize the phone number
        sanitized_phone = re.sub(r'\D', '', phone)
        _logger.info('Received phone number: %s', sanitized_phone)

        # Search for the contact based on phone number
        contact = request.env['res.partner'].sudo().search([
            '|', 
            ('phone', 'ilike', sanitized_phone),
            ('mobile', 'ilike', sanitized_phone),
        ], limit=1)

        _logger.info('Contact found: %s', contact)

        if not contact:
            return {"WasSuccessful": False, "message": "Contact with given phone does not exist!"}

        # Get the linked employee record via 'youth_id'
        employee = request.env['hr.employee'].sudo().search([('active','in',[True, False])]).filtered(lambda employee: employee.related_contact_ids and contact in employee.related_contact_ids)
        if not employee:
            return {"WasSuccessful": False, "message": "Contact is not linked to an employee record"}

        _logger.info('Employee found: %s', employee)
        if employee:
            user_role = employee[0].user_roles_id
            if not user_role:
                return {"WasSuccessful": False, "message": "Employee does not have a user role assigned"}

        user_role_name = user_role.name
        _logger.info('User role: %s', user_role_name)

        # Prepare the response data
        response = {"WasSuccessful": True, "user_role": user_role_name}

        if user_role_name == 'Youth':
            # For 'Youth', retrieve their own tasks
            # user = employee.user_id
            # if not user:
            #     return {"WasSuccessful": False, "message": "Employee does not have a linked user"}

            task_domain = [
                ('employee_id', '=', employee.id),
                ('project_id', '=', 66),
                ('stage_id', '!=', 721),  # Exclude tasks in stage 721
            ]
            tasks = request.env['project.task'].sudo().search(task_domain)

            list_task = []
            if tasks:
                for task in tasks:
                    time_sheets = []
                    for time_sheet in task.timesheet_ids:
                        time_sheet_dic = {
                            'duties': time_sheet.name or ' ',
                            'date': time_sheet.date,
                            'start_time': time_sheet.daily_start_time,
                            'end_time': time_sheet.daily_end_time,
                            'attendance_status': time_sheet.daily_attendance_status or ' ',
                            'duration': time_sheet.unit_amount,
                        }
                        time_sheets.append(time_sheet_dic)
                    task_detail = {
                        "task_id": task.id,
                        "task_name": task.name,
                        "task_stage_id": task.stage_id.id,
                        "stage_name": task.stage_id.name or ' ',
                        "timesheets": time_sheets,
                        "has_approved": task.has_approved,
                        "has_declined": task.has_declined,
                        "user_role": user_role_name,
                    }
                    list_task.append(task_detail)
                if list_task:
                    response['tasks'] = list_task
                    return response
                else:
                    return {
                        "WasSuccessful": False,
                        "message": "There are no tasks that have not been submitted",
                        "user_role": user_role_name
                    }
            else:
                return {
                    "WasSuccessful": False,
                    "message": "The given user does not have tasks!",
                    "user_role": user_role_name
                }

        elif user_role_name == 'Supervisor':
            # For 'Supervisor', retrieve tasks pending approval for all supervised 'Youths'
            subordinates = employee.child_ids.filtered(lambda e: e.user_roles_id.name == 'Youth')
            _logger.info('Supervisor %s has %d subordinates', employee.name, len(subordinates))

            if not subordinates:
                return {
                    "WasSuccessful": False,
                    "   ": "Supervisor has no subordinates",
                    "user_role": user_role_name
                }

            subordinates_tasks = []
            for subordinate in subordinates:
                # subordinate_user = subordinate.user_id
                # if not subordinate_user:
                #     _logger.info('Subordinate %s has no linked user', subordinate.name)
                    # continue  # Skip if subordinate has no linked user

                # Retrieve the contact linked via 'youth_id' in res.partner
                subordinate_contact = request.env['res.partner'].sudo().search([('youth_id', '=', subordinate.id)], limit=1)

                # Retrieve tasks in "Approval Needed" stage (stage ID = 644)
                task_domain = [
                    ('employee_id', '=', subordinate.id),
                    ('project_id', '=', 66),
                    ('stage_id', '=', 644),  # Only tasks needing approval
                ]
                tasks = request.env['project.task'].sudo().search(task_domain)
                youth_tasks = []
                if tasks:
                    for task in tasks:
                        time_sheets = []
                        for time_sheet in task.timesheet_ids:
                            time_sheet_dic = {
                                'duties': time_sheet.name or ' ',
                                'date': time_sheet.date,
                                'start_time': time_sheet.daily_start_time,
                                'end_time': time_sheet.daily_end_time,
                                'attendance_status': time_sheet.daily_attendance_status or ' ',
                                'duration': time_sheet.unit_amount,
                            }
                            time_sheets.append(time_sheet_dic)
                        task_detail = {
                            "task_id": task.id,
                            "task_name": task.name,
                            "task_stage_id": task.stage_id.id,
                            "stage_name": task.stage_id.name or ' ',
                            "timesheets": time_sheets,
                            "has_approved": task.has_approved,
                            "has_declined": task.has_declined,
                            "user_role": subordinate.user_roles_id.name,
                        }
                        youth_tasks.append(task_detail)
                if youth_tasks:
                    subordinate_info = {
                        'youth_name': subordinate.name,
                        'youth_user_role': subordinate.user_roles_id.name,
                        'contact_id': subordinate_contact.id if subordinate_contact else False,
                        'contact_name': subordinate_contact.name if subordinate_contact else '',
                        'tasks': youth_tasks
                    }
                    subordinates_tasks.append(subordinate_info)

            if subordinates_tasks:
                response['subordinates_tasks'] = subordinates_tasks
                return response
            else:
                return {
                    "WasSuccessful": False,
                    "message": "No tasks pending approval for subordinates",
                    "user_role": user_role_name
                }
        else:
            return {
                "WasSuccessful": False,
                "message": "User role not recognized",
                "user_role": user_role_name
            }

    @http.route("/api/WriteRegister", type='json', methods=['POST'], auth='public', csrf=False)
    def update_timesheet(self, **kwargs):
        phone = kwargs.get('phone')
        task_id = kwargs.get('task_id')
        timesheets_data = kwargs.get('timesheets')

        if not task_id:
            return {"WasSuccessful": False, "message": "Task ID is required."}

        if not timesheets_data:
            return {"WasSuccessful": False, "message": "No timesheets data provided."}

        # Validate Task
        task = request.env['project.task'].sudo().search([('id', '=', task_id), ('project_id', '=', 66)])
        if not task:
            return {"WasSuccessful": False, "message": "Task with given ID does not exist!"}


                    
        sanitized_phone = re.sub(r'\D', '', phone)

        contact = request.env['res.partner'].sudo().search([
            '|', 
            ('phone', 'ilike', sanitized_phone),
            ('mobile', 'ilike', sanitized_phone),
        ], limit=1)

        employee  = request.env['hr.employee'].search([('active','in',[True, False])]).filtered(lambda employee: employee.related_contact_ids and contact in employee.related_contact_ids)
        if not employee:
            return {"WasSuccessful": False, "message": "Contact is not linked to an employee record"}

        user_role = employee.user_roles_id
        if not user_role:
            return {"WasSuccessful": False, "message": "Employee does not have a user role assigned"}

        user_role_name = user_role.name
        if user_role_name != 'Youth':
            return {"WasSuccessful": False, "message": "Only Youth can Edit Register"}

        if user_role_name == 'Youth':
            results = []
            for rec in timesheets_data:
                try:
                    # Parse date
                    date_str = rec.get('date')
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    # Get attendance status
                    daily_attendance_status = rec.get('daily_attendance_status')

                    # Build timesheet_vals with name and attendance status
                    timesheet_vals = {
                        'name': rec.get('duties'),
                        'daily_attendance_status': daily_attendance_status,
                    }

                    if daily_attendance_status == 'Present':
                        # Parse start and end times
                        start_time_str = rec.get('daily_start_time')
                        end_time_str = rec.get('daily_end_time')

                        if not start_time_str or not end_time_str:
                            return {
                                "WasSuccessful": False,
                                "message": f"Start time and end time are required for date {date_str} when attendance status is 'Present'."
                            }

                        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
                        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()

                        # Combine date and time
                        daily_start_time = datetime.combine(date, start_time)
                        daily_end_time = datetime.combine(date, end_time)

                        # Update timesheet_vals with start and end times
                        timesheet_vals.update({
                            'daily_start_time': daily_start_time,
                            'daily_end_time': daily_end_time,
                        })
                    else:
                        # If attendance status is not 'Present', ensure times are not required
                        pass  # No need to include daily_start_time and daily_end_time

                    # Search for existing timesheet
                    timesheet = request.env['account.analytic.line'].sudo().search([
                        ('task_id', '=', task.id),
                        ('date', '=', date)
                    ], limit=1)
                    if timesheet:
                        timesheet.sudo().write(timesheet_vals)
                        results.append({"date": date_str, "status": "updated"})
                    else:
                        # Get employee
                        employee = task.user_ids.mapped('employee_id')
                        if not employee:
                            return {
                                "WasSuccessful": False,
                                "message": "Assignee has no employees for creating timesheets."
                            }

                        # Create new timesheet
                        timesheet_vals.update({
                            'task_id': task.id,
                            'project_id': 66,
                            'date': date,
                            'employee_id': employee[0].id,
                        })
                        request.env['account.analytic.line'].sudo().create(timesheet_vals)
                        results.append({"date": date_str, "status": "created"})
                except Exception as e:
                    _logger.error('Error processing timesheet for date %s: %s', date_str, str(e))
                    return {"WasSuccessful": False, "message": f"Error processing timesheet for date {date_str}: {str(e)}"}


        return {
            "WasSuccessful": True,
            "message": "Timesheets processed successfully.",
            "details": results
        }
        
    @http.route("/api/ApproveRegister", methods=['POST'], type='json', auth='public', csrf=False)
    def approve_register(self, **kwargs):
        phone = kwargs.get('phone')
        approvals = kwargs.get('approvals')

        if not phone:
            return {"WasSuccessful": False, "message": "Phone number is required."}
        if not approvals:
            return {"WasSuccessful": False, "message": "No approvals provided."}

        # Sanitize phone number
        sanitized_phone = re.sub(r'\D', '', phone)
        _logger.info('Received phone number: %s', sanitized_phone)

        # Search for the supervisor contact
        contact = request.env['res.partner'].sudo().search([
            '|',
            ('phone', 'ilike', sanitized_phone),
            ('mobile', 'ilike', sanitized_phone),
        ], limit=1)

        if not contact:
            return {"WasSuccessful": False, "message": "Supervisor with given phone does not exist!"}

        # Get the linked employee
        supervisor_employee = request.env['hr.employee'].sudo().search([('active','in',[True, False])]).filtered(lambda employee: employee.related_contact_ids and contact in employee.related_contact_ids)
        if not supervisor_employee:
            return {"WasSuccessful": False, "message": "Contact is not linked to an employee record"}

        # Verify supervisor role
        user_role = supervisor_employee.user_roles_id
        if not user_role or user_role.name != 'Supervisor':
            return {"WasSuccessful": False, "message": "User is not a supervisor"}

        # Get subordinates (youths)
        subordinates = supervisor_employee.child_ids.filtered(lambda e: e.user_roles_id.name == 'Youth')

        if not subordinates:
            return {"WasSuccessful": False, "message": "Supervisor has no subordinates"}

        # subordinate_user_ids = subordinates.mapped('user_id').ids

        # Process each approval
        results = []
        for approval in approvals:
            task_id = approval.get('task_id')
            action = approval.get('action')

            if not task_id or action not in ['approve', 'decline']:
                results.append({
                    'task_id': task_id,
                    'status': 'failed',
                    'message': 'Invalid task_id or action'
                })
                continue

            # Search for the task
            task = request.env['project.task'].sudo().search([
                ('id', '=', task_id),
                ('project_id', '=', 66),
                ('stage_id', '=', 644),
            ], limit=1)

            if not task:
                results.append({
                    'task_id': task_id,
                    'status': 'failed',
                    'message': 'Task not found or not in approval stage'
                })
                continue
            else:
                if action == 'approve':
                    task.ticket_id.sudo().write({
                        'has_approved': True,
                        'has_declined': False,
                    })
                    task.ticket_id.onchange_stage_id()
                    results.append({
                        'task_id': task_id,
                        'status': 'approved'
                    })
                elif action == 'decline':
                    task.ticket_id.sudo().write({
                        'has_approved': False,
                        'has_declined': True,
                        # Optionally change the stage
                    })
                    task.ticket_id.onchange_stage_id()
                    results.append({
                        'task_id': task_id,
                        'status': 'declined'
                    })

        return {
            "WasSuccessful": True,
            "message": "Approvals processed",
            "results": results
        }    


    @http.route("/api/RegisterIssue", methods=['GET'], type='json', auth='public', csrf=False)
    def get_register_issue(self, **kwargs):
        user = request.env['res.users'].sudo().search([('phone', '=', kwargs.get('phone'))])
        if not user:
            return {"WasSuccessful": False, "message": "User with given phone does not exists !"}
        else:
            task_domain = [('user_ids', '=',user.id ), ('project_id', '=', 63)]
            if user.employee_id:
                if user.employee_id.user_roles_id.id == 2:
                    task_domain = [('project_id', '=', 63)]
                tasks = request.env['project.task'].sudo().search(task_domain)
                list_task = []
                if tasks:
                    for task in tasks:
                        time_sheets = []
                        task_detail = {
                        "task_name":task.name or ' ',
                        "task_stage_id":task.stage_id.id,
                        "stage_name":task.stage_id.name or ' ',
                        "register_isseus":time_sheets
                        }
                        list_task.append(task_detail)
                        for time_sheet in task.register_issue_timesheet_ids:
                            time_sheet_dic = {
                                'duties':time_sheet.name or ' ',
                                'date':time_sheet.date,
                                'start_time':time_sheet.daily_start_time,
                                'end_time':time_sheet.daily_end_time,
                                'attendance_status':time_sheet.daily_attendance_status or ' ',
                                'has_register_issue':time_sheet.has_register_issues,
                                'duration':time_sheet.unit_amount,
                                }
                            time_sheets.append(time_sheet_dic)
                    response = {"WasSuccessful": True,}
                    response['tasks'] = list_task
                    return response
                else:
                    return {"WasSuccessful": False, "message": "The given user does not have a task !!"}
            else:
                return {"WasSuccessful": False, "message": "The given user does not have a employees !!"}

    @http.route("/api/WriteRegisterIssue", type='json', methods=['POST'],auth='public', csrf=False)
    def create_update_register_issue(self, **kwargs):
        task_id = request.env['project.task'].sudo().search([('id','=',kwargs.get('task_id')),('project_id','=',63)])
        if not task_id:
            return {"WasSuccessful": False, "message": "Task with given ID does not exists !"}
        else:
            for rec in kwargs.get('register_issues'):
                date = datetime.strptime(rec.get('date'),'%Y-%m-%d').date()
                register_issue_id = request.env['account.analytic.line'].sudo().search([('registration_issue_task_id.id','=',kwargs.get('task_id')),('date','=',date)])
                if register_issue_id:
                    register_issue_date = register_issue_id.date.strftime('%Y-%m-%d')
                    if register_issue_id.daily_start_time:
                        daily_start_time = datetime.strptime(register_issue_id.daily_start_time.strftime('%m/%d/%Y %H:%M:%S'), '%m/%d/%Y %H:%M:%S')
                    else:
                        daily_start_time = datetime.strptime(register_issue_id.date.strftime('%m/%d/%Y %H:%M:%S'), '%m/%d/%Y %H:%M:%S')
                    if register_issue_id.daily_end_time:
                        daily_end_time = datetime.strptime(register_issue_id.daily_end_time.strftime('%m/%d/%Y %H:%M:%S'), '%m/%d/%Y %H:%M:%S')
                    else:
                        daily_end_time = datetime.strptime(register_issue_id.date.strftime('%m/%d/%Y %H:%M:%S'), '%m/%d/%Y %H:%M:%S')

                    start_hours = rec.get('daily_start_time').split(":")[0]
                    start_minute = rec.get('daily_start_time').split(":")[1]
                    start_second = rec.get('daily_start_time').split(":")[2]
                    end_hours = rec.get('daily_end_time').split(":")[0]
                    end_minute = rec.get('daily_end_time').split(":")[1]
                    end_second = rec.get('daily_end_time').split(":")[2]
                    start_time = daily_start_time.replace(hour=int(start_hours), minute=int(start_minute), second=int(start_second))
                    end_time = daily_end_time.replace(hour=int(end_hours), minute=int(end_minute), second=int(end_second))
                    register_issue_id.sudo().write({
                        'daily_attendance_status':rec.get('daily_attendance_status'),
                        'name':rec.get('dutes'),
                        'has_register_issues':rec.get('has_register_issues'),
                        'daily_start_time':start_time,
                        'daily_end_time':end_time
                        })
                    return {"WasSuccessful": True, "message": "Timesheet hasbeen updated!"}
                else:
                    timesheet_date = date
                    start_hours = rec.get('daily_start_time').split(":")[0]
                    start_minute = rec.get('daily_start_time').split(":")[1]
                    start_second = rec.get('daily_start_time').split(":")[2]
                    end_hours = rec.get('daily_end_time').split(":")[0]
                    end_minute = rec.get('daily_end_time').split(":")[1]
                    end_second = rec.get('daily_end_time').split(":")[2]
                    daily_start_time = datetime.strptime(timesheet_date.strftime('%m/%d/%Y %H:%M:%S'), '%m/%d/%Y %H:%M:%S')
                    daily_end_time = datetime.strptime(timesheet_date.strftime('%m/%d/%Y %H:%M:%S'), '%m/%d/%Y %H:%M:%S')
                    start_time = daily_start_time.replace(hour=int(start_hours), minute=int(start_minute), second=int(start_second))
                    end_time = daily_end_time.replace(hour=int(end_hours), minute=int(end_minute), second=int(end_second))  
                    employee_id = task_id.sudo().user_ids.mapped('employee_id')
                    if employee_id:
                        register_issue_id = request.env['account.analytic.line'].sudo().create({
                            'registration_issue_task_id':kwargs.get('task_id'),
                            'project_id':63,
                            'date':date,
                            'employee_id':employee_id[0].id,
                            'daily_attendance_status':rec.get('daily_attendance_status'),
                            'name':rec.get('dutes'),
                            'has_register_issues':True,
                            'daily_start_time':start_time,
                            'daily_end_time':end_time
                            })
                        return {"WasSuccessful": True, "message": "Timesheet hasbeen created!"}
                    else:
                        return {"WasSuccessful": False, "message": "Assignee has no employees for create timesheets"}
                        
    @http.route("/api/get/Contacts", type='json', methods=['GET'],auth='public', csrf=False)
    def get_contacts(self, **kwargs):
        contact_ids = request.env['res.partner'].sudo().search([('active','=',True)])
        if not contact_ids:
            return {"WasSuccessful": False, "message": "Contacts does not exists!!"}
        else:
            list_contact = []
            for contact in contact_ids:
                adress = {
                    "street":contact.street or ' ',
                    "street2":contact.street2 or ' ', 
                    "city":contact.city or ' ',
                    "state":contact.state_id.name or ' ',
                    "zip":contact.zip or ' ',
                    "country":contact.country_id.name or ' ',
                }
                contact_info = {
                    "name":contact.name or ' ',
                    "contact_type":contact.company_type or ' ',
                    "youth_company_type":contact.youth_company_type or ' ',
                    "youth_contact_type":contact.youth_contact_type or ' ',
                    "related_company_id":contact.parent_id.id or ' ',
                    "host_site_id":contact.host_site_id.id if contact.host_site_id else False,
                    "job_position":contact.function or ' ',
                    "primary_number":contact.mobile or ' ',
                    "secondary_number":contact.phone or ' ',
                    "youth_id":contact.youth_id.id if contact.youth_id else False, 
                    "adress":adress,
                }
                list_contact.append(contact_info)
            response = {"WasSuccessful": True,}
            response['contacts'] = list_contact
            return response

    @http.route("/api/get/Cohort", type='json', methods=['GET'],auth='public', csrf=False)
    def get_cohort(self, **kwargs):
        cohort_ids = request.env['cohort.cohort'].sudo().search([])
        if not cohort_ids:
            return {"WasSuccessful": False, "message": "Cohort does not exists!!"}
        else:
            list_cohort = []
            for cohort_id in cohort_ids:
                sector_list = []
                sector_list.append(cohort_id.sector_ids.ids)
                cohort_info = {
                    "cohort_name":cohort_id.name or ' ',
                    "start_date":cohort_id.start_date,
                    "end_date":cohort_id.end_date,
                    "age_range":cohort_id.age_range or ' ',
                    "yes_phones":cohort_id.yes_phones,
                    "compliance_target":cohort_id.compliance_target or ' ',
                    "payroll_type":cohort_id.payroll_type or ' ',
                    "organization_type":cohort_id.organization_type or ' ',
                    "placement_type":cohort_id.placement_type or ' ',
                    "allocation_target":cohort_id.allocation_target or ' ',
                    "cohort_buffer":cohort_id.cohort_buffer or ' ',
                    "extra_youth":cohort_id.extra_youth or ' ',
                    "total_allocation":cohort_id.total_allocation or ' ',
                    "sector_ids":sector_list,
                    "male_requirement":cohort_id.male_requirement or ' ',
                    "female_requirement":cohort_id.female_requirement or ' ',
                    "disability_requirement":cohort_id.disability_requirement or ' ',
                    "funder_id":cohort_id.funder_id.id if cohort_id.funder_id else False,
                    "youth_salary":cohort_id.youth_salary or ' ',
                    "employment_details":cohort_id.employment_details.id if cohort_id.employment_details else False,
                    "contract_type":cohort_id.contract_type or ' ',
                    "journey_id":cohort_id.journey_id.id if cohort_id.journey_id else False,
                    "drop_off_replacement_target":cohort_id.drop_off_replacement_target or ' ',
                    "absorption_target_yes":cohort_id.absorption_target_yes or ' ',
                    "drop_off_replacement":cohort_id.drop_off_replacement or ' ',
                    "absorption_needed_yes":cohort_id.absorption_needed_yes or ' ',
                    "absorption_target_funder":cohort_id.absorption_target_funder or ' ',
                    "absorption_needed_funder":cohort_id.absorption_needed_funder or ' '
                }
                list_cohort.append(cohort_info)
            response = {"WasSuccessful": True,}
            response['cohorts'] = list_cohort
            return response

    @http.route("/api/get/Vacancies", type='json', methods=['GET'],auth='public', csrf=False)
    def get_vacancies(self, **kwargs):
        task_ids = request.env['project.task'].sudo().search([('project_id','=',65)])
        if not task_ids:
            return {"WasSuccessful": False, "message": "Vacancies does not exists !"}
        else:
            task_list = []
            for task in task_ids:
                task_info = {
                    "vacancies_name":task.name or '',
                    "youth":task.employee_id.id if task.employee_id else False,
                    "cohort":task.cohort_id.id if task.cohort_id else False,
                    "vacancies":task.vacancies or '',
                    "partner":task.partner_id.id if task.partner_id else False,
                    "host_site":task.host_site_id.id if task.host_site_id else False,
                    "partner_mobile":task.partner_mobile or ' ',
                    "partner_phone":task.partner_phone or ''
                }
                task_list.append(task_info)
            response = {"WasSuccessful": True,}
            response['vacancies'] = task_list
            return response

    @http.route("/api/get/JobRoles", type='json', methods=['GET'],auth='public', csrf=False)
    def get_jobroles(self, **kwargs):
        job_roles = request.env['hr.job'].sudo().search([])
        if not job_roles:
            return {"WasSuccessful": False, "message": "Job does not exists !"}
        else:
            job_role_list = []
            for job in job_roles:
                job_info = {
                    "Job_name":job.name or '',
                    "department_id":job.department_id.id if job.department_id else False,
                    "application_count":job.application_count or '',
                    "number_of_recruitment":job.no_of_recruitment or '',
                    'is_published':job.is_published,
                    'alias_id':job.alias_id.id if job.alias_id else False,
                    "recruiter":job.user_id.name if job.user_id else False,
                    "website_id":job.website_id.id if job.website_id else False,
                    "number_of_employee":job.no_of_employee or '',
                    "expected_employees":job.expected_employees  or ''
                }
                job_role_list.append(job_info)
        response = {"WasSuccessful": True,}
        response['Jobroles'] = job_role_list
        return response

    @http.route("/api/get/Employees", type='json', methods=['GET'],auth='public', csrf=False)
    def get_employees(self, **kwargs):
        employees = request.env['hr.employee'].sudo().search([])
        if not employees:
            return {"WasSuccessful": False, "message": "Employees does not exists !"}
        else:
            employees_list = []
            for emp in employees:
                employee_info = {
                    "name":emp.name or '',
                    "user_roles_id":emp.user_roles_id.id if emp.user_roles_id else False,
                    "employee_type":emp.employee_type or '',
                    "related_user_id":emp.user_id.id if emp.user_id else False,
                    "department_id":emp.department_id.id if emp.department_id else False,
                    "primary_number":emp.mobile_phone or '',
                    "secondary_number":emp.work_phone or '',
                    "work_email":emp.work_email or '',
                    "contract_id":emp.contract_id.id if emp.contract_id else False,
                    "parent_id":emp.parent_id.id if emp.parent_id else False,
                    "funder_id":emp.funder_id.id if emp.funder_id else False,
                    "cohort_id":emp.cohort_id.id if emp.cohort_id else False,
                    "payroll_type":emp.payroll_type or '',
                    "work_contact_id":emp.work_contact_id.id if emp.work_contact_id else False,
                    "host_site_id":emp.host_site_id if emp.host_site_id else False,
                    "host_site_province_id":emp.host_site_province_id.id if emp.host_site_province_id else False,
                    "sector_id":emp.sector_id.id if emp.sector_id else False,
                    "gender":emp.gender or ''
                 }
                employees_list.append(employee_info)
            response = {"WasSuccessful": True,}
            response['employees'] = employees_list
            return response

    @http.route("/api/create/Employees", type='json', methods=['POST'],auth='public', csrf=False)
    def create_employees(self, **kwargs):
        for employee in kwargs.get('employees'):
            if employee.get('name'):
                vals = {
                    'name':employee.get('name'),
                    "user_roles_id":employee.get('user_roles_id'),
                    "mobile_phone":employee.get('primary_number'),
                    "work_phone":employee.get('secondary_number'),
                    "work_email":employee.get('work_email'),
                    "department_id":employee.get('department_id'),
                    "parent_id":employee.get('parent_id')
                }
                employee_id = request.env['hr.employee'].sudo().search([('name','=',employee.get('name'))],limit=1)
                if employee_id:
                    employee_id.sudo().write(vals)
                    response = {"WasSuccessful": True, "message": "Employees hasbeen updated !", "employee_id":employee_id.id}
                else:
                    employee_id = request.env['hr.employee'].sudo().create(vals)
                    response = {"WasSuccessful": True, "message": "Employees hasbeen created !", "employee_id":employee_id.id}
                return response
            else:
                {"WasSuccessful": True, "message": "Mandatory field not set"}

    @http.route("/api/Hrissue", methods=['GET'], type='json', auth='public', csrf=False)
    def get_hr_issue(self, **kwargs):
        user = request.env['res.users'].sudo().search([('phone', '=', kwargs.get('phone'))])
        if not user:
            return {"WasSuccessful": False, "message": "User with given phone does not exists !"}
        else:
            task_ids = request.env['project.task'].sudo().search([('project_id','=',58)])
            if not task_ids:
                return {"WasSuccessful": False, "message": "Hrissue does not exists !"}
            else:
                task_list = []
                for task in task_ids:
                    task_info = {
                        "name":task.name or '',
                        'partner_id':task.partner_id.id if task.partner_id else False,
                        'host_site_id':task.host_site_id.id if task.host_site_id else False,
                        'priority':task.issue_priority or '',
                        'issue_reporter':task.issue_reporter_id.name if task.issue_reporter_id else False,
                        'date_closed':task.issue_date_closed,
                        'youth':task.employee_id.id if task.employee_id else False,
                        'session':task.session_id.id if task.session_id else False,
                        'issue_type':task.issue_type or '',
                        'deadline':task.date_deadline 
                    }
                    task_list.append(task_info)
                response = {"WasSuccessful": True,}
                response['hr_issues'] = task_list
                return response

    @http.route('/api/create/Hrissue', methods=['POST'], type='json', auth='public', csrf=False)
    def create_hrissue(self, **kwargs):
        user = request.env['res.users'].sudo().search([('phone', '=', kwargs.get('phone'))])
        if not user:
            return {"WasSuccessful": False, "message": "User with given phone does not exists !"}
        else:
            for rec in kwargs.get('hr_issues'):
                if rec.get('name'):
                    vals = {
                        'name':rec.get('name'),
                        'project_id':58,
                        'user_ids':[(6,0,[rec.get('assignee')])],
                        'partner_id':rec.get('partner_id'),
                        'host_site_id':rec.get('host_site_id'),
                        'issue_priority':rec.get('priority'),
                        'issue_reporter_id':rec.get('issue_reporter'),
                        'employee_id':rec.get('youth'),
                        'issue_type':rec.get('issue_type')
                    }
                    hr_issue = request.env['project.task'].sudo().search([('name','=',rec.get('name')),('project_id.id','=',58)],limit=1)
                    if hr_issue:
                        hr_issue.sudo().write(vals)
                        response = {"WasSuccessful": True, "message": "HrIssue hasbeen updated !", "hr_issue_id":hr_issue.id}
                    else:
                        hr_issue = request.env['project.task'].sudo().create(vals)
                        response = {"WasSuccessful": True, "message": "HrIssue hasbeen created !", "hr_issue_id":hr_issue.id}
                    return response
                else:
                    {"WasSuccessful": True, "message": "Mandatory field not set"}


    @http.route('/api/PayCurve', methods=['POST'], type='json', auth='public', csrf=False)
    def get_youth_eligibility(self, **kwargs):
        user_id = kwargs.get('user_id')
        # id_numbers = kwargs.get('id_number', [])
        cohort_name = kwargs.get('cohort_id')
        
        if not user_id:
            return {"WasSuccessful": False, "message": "User ID is required"}
        
        user = request.env['res.users'].sudo().search([('id', '=', user_id)], limit=1)
        if not user:
            return {"WasSuccessful": False, "message": "User not found"}
        
        if not cohort_name:
            return {"WasSuccessful": False, "message": "Cohort ID are required"}
        
        # employees = request.env['hr.employee'].sudo().search([
        #     ('id_number', 'in', id_numbers),
        #     ('cohort_id.name', '=', cohort_name)
        # ])

        employees = request.env['hr.employee'].sudo().search([
            ('cohort_id.name', '=', cohort_name)
        ])
        
        if not employees:
            return {"WasSuccessful": False, "message": "User not found by cohort"}

        youth_details = []
        eligible_count = 0
        
        for employee in employees:
            weekly_registers = request.env['project.task'].sudo().search([
                ('employee_id', '=', employee.id),
                ('project_id', '=', 66)
            ])
            
            payment_allowed = all(task.stage_id.name == 'Submitted' for task in weekly_registers)
            if payment_allowed:
                eligible_count += 1
            
            youth_details.append({
                "name": employee.name,
                "youth_id": employee.identification_id,
                "cohort": employee.cohort_id.name,
                "payment_allowed": payment_allowed
            })
        
        response_data = {
            "cohort": cohort_name,
            "total_youth": len(employees),
            "eligible_youth": eligible_count,
            "youth_details": youth_details
        }
        
        return response_data