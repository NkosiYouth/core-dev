# -*- coding: utf-8 -*-

from odoo import models, fields

class Session(models.Model):
    _name = "session.session"
    _description = "Sessions"
    
    name = fields.Char(string="Name")