# -*- coding: utf-8 -*-

from odoo import fields,models

class UserRole(models.Model):
    _name = "user.role"

    name = fields.Char()
    