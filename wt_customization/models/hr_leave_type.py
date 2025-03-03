# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import format_date

class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    allows_negative = fields.Boolean(string='Allow Negative Cap',
        help="If checked, users request can exceed the allocated days and balance can go in negative.")
    max_allowed_negative = fields.Integer(string="Amount in Negative",
        help="Define the maximum level of negative days this kind of time off can reach. Value must be at least 1.")

    @api.depends('requires_allocation')
    def _compute_valid(self):
        date_to = self._context.get('default_date_to', fields.Datetime.today())
        date_from = self._context.get('default_date_from', fields.Datetime.today())
        employee_id = self._context.get('default_employee_id', self._context.get('employee_id', self.env.user.employee_id.id))
        for holiday_type in self:
            if holiday_type.requires_allocation == 'yes':
                allocation = self.env['hr.leave.allocation'].search([   
                    ('holiday_status_id', '=', holiday_type.id),
                    ('employee_id', '=', employee_id),
                    '|',
                    ('date_to', '>=', date_to),
                    '&',
                    ('date_to', '=', False),
                    ('date_from', '<=', date_from)])
                allowed_excess = holiday_type.max_allowed_negative if holiday_type.allows_negative else 0
                allocations = allocations.filtered(lambda alloc: alloc.allocation_type == 'accrual' or (alloc.max_leaves > 0 and alloc.virtual_remaining_leaves > -allowed_excess))
                holiday_type.has_valid_allocation = bool(allocation)
            else:
                holiday_type.has_valid_allocation = True


    def _get_days_request(self):
        self.ensure_one()
        result = self._get_employees_days_per_allocation(self.closest_allocation_to_expire.employee_id.ids)
        closest_allocation_remaining = 0
        if self.closest_allocation_to_expire:
            # Shows the sum of allocation expiring on the same day as the closest to expire
            employee_allocations = result[self.closest_allocation_to_expire.employee_id.id][self].items()
            closest_allocation_remaining = sum(
                res['virtual_remaining_leaves']
                for alloc, res in employee_allocations
                if alloc and alloc.date_to == self.closest_allocation_to_expire.date_to
            )
        if self.allows_negative:
            leaves = self.env['hr.leave'].search([('holiday_status_id','=',self.id)])
            if leaves:
                self.virtual_leaves_taken = sum(leaves.mapped('number_of_days_display'))
        return (self.name, {
                'remaining_leaves': ('%.2f' % self.remaining_leaves).rstrip('0').rstrip('.'),
                'usable_remaining_leaves': ('%.2f' % self.virtual_remaining_leaves).rstrip('0').rstrip('.'),
                'virtual_remaining_leaves': ('%.2f' % (self.max_leaves - self.virtual_leaves_taken)).rstrip('0').rstrip('.'),
                'max_leaves': ('%.2f' % self.max_leaves).rstrip('0').rstrip('.'),
                'leaves_taken': ('%.2f' % self.leaves_taken).rstrip('0').rstrip('.'),
                'virtual_leaves_taken': ('%.2f' % self.virtual_leaves_taken).rstrip('0').rstrip('.'),
                'leaves_requested': ('%.2f' % (self.virtual_leaves_taken - self.leaves_taken)).rstrip('0').rstrip('.'),
                'leaves_approved': ('%.2f' % self.leaves_taken).rstrip('0').rstrip('.'),
                'closest_allocation_remaining': ('%.2f' % closest_allocation_remaining).rstrip('0').rstrip('.'),
                'closest_allocation_expire': format_date(self.env, self.closest_allocation_to_expire.date_to) if self.closest_allocation_to_expire.date_to else False,
                'request_unit': self.request_unit,
                'icon': self.sudo().icon_id.url,
                }, self.requires_allocation, self.id)