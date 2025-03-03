# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    name = fields.Char(
        'Description',
        required=False,
    )
    date = fields.Date(
        'Date',
        required=False,
        index=True,
        store=True,
        default=fields.Date.context_today,
    )
    daily_type = fields.Selection([("Session","Session"),("Weekly","Weekly")],string="Daily Attendance Type")
    daily_attendance_status = fields.Selection([("Present","Present"),("Annual Leave","Annual Leave"),("Annual Leave Half Day","Annual Leave Half Day"),("Sick Leave","Sick Leave"),("Sick Leave Half Day","Sick Leave Half Day"),
                                                ("Study Leave","Study Leave"),("Study Leave Half Day","Study Leave Half Day"),("Maternity Leave","Maternity Leave"),("Unpaid Leave","Unpaid Leave"),
                                                ("Weekend","Weekend")],string="Daily Status Selection")
    daily_leave_form = fields.Binary(string="Leave Form")
    has_register_issues = fields.Boolean(string="Has Register Issues")
    ticket_id = fields.Many2one('helpdesk.ticket')
    issue_ticket_id = fields.Many2one('helpdesk.ticket')
    registration_issue_task_id = fields.Many2one('project.task')
    daily_start_time = fields.Datetime(string="Start Time")
    daily_end_time = fields.Datetime(string="End Time")

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        leave = self.env['hr.leave'].search([('request_date_from', '=',res.date)],limit=1)
        if leave:
            res.daily_attendance_status = leave.holiday_status_id.name
        return res


    @api.onchange('date', 'daily_start_time', 'daily_end_time')
    def onchange_start_time_end_time(self):
        if self.date:
            if self.daily_start_time:
                # Extract the time part from daily_start_time
                start_time = self.daily_start_time.time()
                # Combine the date from date with the time
                combined_start_datetime_str = f"{self.date} {start_time}"
                # Prepare the value to update
                self.daily_start_time = combined_start_datetime_str

            # Handle daily_end_time
            if self.daily_end_time:
                # Extract the time part from daily_end_time
                end_time = self.daily_end_time.time()
                # Combine the date from date with the time
                combined_end_datetime_str = f"{self.date} {end_time}"
                # Prepare the value to update
                self.daily_end_time = combined_end_datetime_str
        else:
            self.daily_end_time = self.daily_start_time = False

        if self.daily_start_time and self.daily_end_time and (self.daily_start_time > self.daily_end_time):
            raise UserError("Start time should be lower than the end time")

        if self.daily_end_time and self.daily_start_time:
            diff = self.daily_end_time - self.daily_start_time
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60
            time = hours + round(minutes / 60, 2)
            self.unit_amount = time

    def write(self, vals):
        res = super(AccountAnalyticLine, self).write(vals)
        timesheets = self.task_id.timesheet_ids
        timesheet_remaining = timesheets.filtered(lambda x: not x.daily_attendance_status)
        present_timesheet_ids = timesheets.filtered(lambda x:x.daily_attendance_status in ["Present", 'Annual Leave Half Day', 'Sick Leave Half Day','Study Leave Half Day'])
        # if self.date and self.date.strftime('%A') in ['Saturday', 'Sunday']:
        #    self.daily_attendance_status = 'Weekend'
        if not timesheet_remaining and not self._context.get('test'):
            if all(pre.daily_start_time and pre.daily_end_time for pre in present_timesheet_ids) and not self.task_id.stage_id.id == 721:
                self.task_id.with_context(timesheet='timesheet').write({'stage_id': 644})
        elif not self._context.get('bypass_stage'):
            self.task_id.with_context(timesheet='timesheet').write({'stage_id': 625})
        if vals.get('date') and (vals.get('daily_attendance_status') and vals.get('daily_attendance_status') in ['Annual Leave', 'Annual Leave Half Day', 'Sick Leave', 'Sick Leave Half Day', 'Study Leave', 'Study Leave Half Day', 'Maternity Leave', 'Unpaid Leave']):
            self.create_leave()
        return res


    def create_leave(self):
        timeoff_data = {"Annual Leave": 13, "Annual Leave Half Day": 13, "Sick Leave": 9, "Sick Leave Half Day": 9, "Study Leave": 15, "Study Leave Half Day": 15, "Maternity Leave": 12, "Unpaid Leave": 10}
        is_half_day = False
        if self.daily_attendance_status in ['Annual Leave Half Day', 'Sick Leave Half Day', 'Study Leave Half Day']:
            is_half_day = True
        vals = {
        'holiday_status_id': timeoff_data.get(self.daily_attendance_status), 
        'request_date_from': self.date,
        'date_from': self.date,
        'employee_id': self.employee_id.id,
        'timesheet_id': self.id,
        'request_unit_half':is_half_day
        }
        
        if self.daily_attendance_status in ['Annual Leave Half Day', 'Sick Leave Half Day', 'Study Leave Half Day']:
            vals.update({'date_to': self.date,'request_date_to': self.date,'request_date_from_period': 'am', 'number_of_days': 0.5, 'number_of_days_display': 0.5})
        else:
            vals.update({'request_date_to': self.date, 'date_to': self.date, 'number_of_days': 1, 'number_of_days_display': 1})
      
        leave = self.env['hr.leave'].search([('timesheet_id', '=',  self.id)])
        if not leave and vals.get('holiday_status_id'):
            leave = self.env['hr.leave'].create(vals)
        elif leave.state != 'refuse':
            leave.write(vals)   
        if leave and self.daily_leave_form and leave.state != 'refuse' and self.task_id.stage_id.id == 721:
            try:
                leave.action_approve()
            except Exception as error:
                raise UserError("%s" % error)
        elif leave and (self.daily_attendance_status == 'Present' or not self.daily_attendance_status) and leave.state != 'refuse':
            leave.action_refuse()
        