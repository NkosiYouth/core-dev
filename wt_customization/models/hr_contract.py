# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class HrLeaveAccrualPlan(models.Model):
    _inherit = 'hr.leave.accrual.plan'

    contract_id = fields.Many2one('hr.contract')


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    contract_id = fields.Many2one('hr.contract')


class HrContract(models.Model):
    _inherit = "hr.contract"
    _description = "HR Contract"

    cohort_id = fields.Many2one('cohort.cohort', string="Cohort")
    contract_signed = fields.Boolean('Contract Signed')
    month_into_program = fields.Integer('Month Into Program')
    latest_end_week = fields.Date('Latest Week (End)')
    month = fields.Integer('Month')
    number_of_weeks = fields.Integer('Number of Weeks')
    week_counter = fields.Integer('Week')
    youth_contract = fields.Boolean()


    def update_employee_details(self):
        for employee in self.employee_ids:
            try:
                employee.write({
                    'job_title':self.function,
                    'work_phone':self.phone,
                    'work_email':self.email
                })
            except Exception as e:
                raise UserError(">>>>>>>>>>>>%s" % e)

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        # res.create_allocation()
        res.change_staus()
        return res
        
    def write(self, vals):
        res = super(HrContract, self).write(vals)
        # self.change_staus()
        # if vals.get('date_start') or vals.get('date_end') or vals.get('state'):
        #     self.create_allocation()
        return res

    def set_youth(self):
        for rec in self.env['hr.contract'].search([]):
            if rec.employee_id.user_roles_id and rec.employee_id.user_roles_id.id == 2 and rec.employee_id.active == True :
                rec.youth_contract = True
                _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>> %s" % rec.youth_contract)
            else:
                pass



    def change_staus(self):
        for rec in self.search([('state','=','draft')]):
            if rec.date_start and rec.date_end:
                if rec.date_end >= datetime.now().date():
                    rec.state = 'open'
                elif rec.date_end < datetime.now().date():
                    rec.state = 'close'
                _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> %s" % rec.state)
                self._cr.commit()



    def create_allocation(self):
        annual_leave_timeoff = 13
        study_leave_timeoff = 15
        sick_leave_timeoff = 9
        maternity_leave_timeoff = 12
        family_responsibility_timeoff = 14

        yearly_annual_leave = 15
        yearly_study_sick_leave = 10
        yearly_maternity_leave = 120
        yearly_family_responsibility_leave = 3

        data = {annual_leave_timeoff: ["Annual Leave ", yearly_annual_leave],
        study_leave_timeoff: ["Study/Eaxam Leave ", yearly_study_sick_leave],
        sick_leave_timeoff: ["Sick Leave ", yearly_study_sick_leave],
        maternity_leave_timeoff: ["Maternity Leave ", yearly_maternity_leave],
        family_responsibility_timeoff: ["Family Responsibility Leave ", yearly_family_responsibility_leave]}
        try:
          if self.date_start and self.date_end and self.state == 'open':# Annual Leave Plan
            yearly_month = self.date_start.strftime('%b').lower()
            accrual_level_vals = {'yearly_month': yearly_month, 'maximum_leave': yearly_annual_leave, 'frequency':'monthly', 'start_count': 0, 'added_value': 1.25, 'action_with_unused_accruals': 'lost', 'first_day_display': 'last' if self.date_start.day > 28 else str(self.date_start.day)}
            accrual_plan_id = self.env['hr.leave.accrual.plan'].search([('time_off_type_id', '=', annual_leave_timeoff), ('contract_id', '=', self.id)])
            if not accrual_plan_id:
              accrual_plan_id = self.env['hr.leave.accrual.plan'].create({'name': "Annual plan FOR "+ self.employee_id.name,
              'time_off_type_id': annual_leave_timeoff,
              'contract_id': self.id,
              'level_ids': [(0, 0, accrual_level_vals)]
              })
            else:
              accrual_level_id = self.env['hr.leave.accrual.level'].search([('accrual_plan_id', '=', accrual_plan_id.id)])
              if not accrual_level_id:
                accrual_level_vals.update({'accrual_plan_id': accrual_plan_id.id})
                accrual_level_id = self.env['hr.leave.accrual.level'].create(accrual_level_vals)
              else:
                accrual_level_id.write(accrual_level_vals)
            
            # Annual Allocation
            annual_leave_allocation = self.env['hr.leave.allocation'].search([('contract_id', '=', self.id), ('holiday_status_id', '=', annual_leave_timeoff), ('state', '!=', 'cancel')])
            annual_allocation_vals = {'holiday_status_id': annual_leave_timeoff, 
            'holiday_type': 'employee',
            'employee_id': self.employee_id.id,
            'name' : "Annual Leave For " +  self.name,
            'allocation_type':'accrual',
            'accrual_plan_id': accrual_plan_id.id,
            'date_from': self.date_start + relativedelta(months=1),
            'date_to': self.date_end
            }

            if not annual_leave_allocation:
              annual_leave_allocation = self.env['hr.leave.allocation'].create(annual_allocation_vals)
            else:
              annual_leave_allocation.write(annual_allocation_vals)
            
            annual_leave_allocation._onchange_allocation_type()
            annual_leave_allocation.action_confirm()
            
            for timeoff in [study_leave_timeoff, sick_leave_timeoff, maternity_leave_timeoff, family_responsibility_timeoff]:
            # for timeoff in [maternity_leave_timeoff, family_responsibility_timeoff]:
              if timeoff == maternity_leave_timeoff and self.employee_id.gender != 'female':
                continue
              
              if timeoff in [study_leave_timeoff, sick_leave_timeoff, maternity_leave_timeoff]:
                date_from = self.date_start - relativedelta(years=1)
              elif timeoff == family_responsibility_timeoff:
                date_from = self.date_start + relativedelta(months=4) - relativedelta(years=1)
              
              yearly_month = date_from.strftime('%b').lower()

              # Accrual Plan
              level_vals = {'yearly_month': yearly_month, 'maximum_leave': data.get(timeoff)[1], 'frequency':'yearly', 'start_count': 0, 'added_value': data.get(timeoff)[1], 'action_with_unused_accruals': 'lost', 'yearly_day_display': 'last' if date_from.day > 28 else str(date_from.day)}
              plan_id = self.env['hr.leave.accrual.plan'].search([('time_off_type_id', '=', timeoff), ('contract_id', '=', self.id)])
              if not plan_id:
                plan_id = self.env['hr.leave.accrual.plan'].create({'name': data.get(timeoff)[0] + self.employee_id.name,
                'time_off_type_id': timeoff,
                'contract_id': self.id,
                'level_ids': [(0, 0, level_vals)]
                })
              else:
                level_id = self.env['hr.leave.accrual.level'].search([('accrual_plan_id', '=', plan_id.id)])
                if not level_id:
                  level_vals.update({'accrual_plan_id': plan_id.id})
                  level_id = self.env['hr.leave.accrual.level'].create(level_vals)
                else:
                  level_id.write(level_vals)
              
              # Allocation
              leave_allocation = self.env['hr.leave.allocation'].search([('contract_id', '=', self.id), ('holiday_status_id', '=', timeoff), ('state', '!=', 'cancel')])
              allocation_vals = {'holiday_status_id': timeoff, 
              'holiday_type': 'employee',
              'employee_id': self.employee_id.id,
              'name' : data.get(timeoff)[0] +  self.name,
              'allocation_type':'accrual',
              'accrual_plan_id': plan_id.id,
              'date_from': date_from,
              'date_to': self.date_end
              }
          
              if not leave_allocation:
                leave_allocation = self.env['hr.leave.allocation'].create(allocation_vals)
              else:
                leave_allocation.write(allocation_vals)
              self.env.cr.commit()
              leave_allocation._onchange_allocation_type()
              leave_allocation.action_confirm()
            
          self.env['hr.leave.allocation']._update_accrual()
        except Exception as e:
          raise UserError("%s" % e)



    def create_allocation_cron(self):
        for rec in self:
            rec.create_allocation()


    def create_allocation_contract(self):
        contracts = self.env['hr.contract'].search([])
        # import pdb; pdb.set_trace()
        for contract in contracts:
            if contract.employee_id:
                contract.create_allocation()
                _logger.info("---------------ALLOCATION------------------ %s" %contract.employee_id.name)
            _logger.info(">>>>>>>>>>>>>>>>no employee>>>>>>>>>>>>> %s" %contract)


    def create_allocations(self):
        employees = self.env['hr.employee'].search([('user_roles_id.name', '=', 'Youth'), ('active', '=', True)])
        for employee in employees:
            if employee.contract_ids:
                employee.contract_ids.create_allocation()
                _logger.info("---------------ALLOCATION------------------ %s" %employee.name)
