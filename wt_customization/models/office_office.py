# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _



class Journey(models.Model):
    _name = "office.office"


    name = fields.Char("Office Name", required=True)
    user_ids = fields.Many2many('res.users', string="Users")
    team_ids = fields.Many2many('helpdesk.ticket.team', string="Teams")
    province_id = fields.Many2one('res.country.state', "Province")
    office_type = fields.Selection(
        selection=[
            ("type1", "Type 1"),
            ("type2", "Type 2")
        ],string="Office Type")
