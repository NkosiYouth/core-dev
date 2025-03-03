# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    sandwich = fields.Boolean(string="Apply")
    leave_notification = fields.Boolean(string="Show Notification")
