# -*- coding: utf-8 -*-
from odoo import models, fields


class RecentlyCall(models.Model):
    _name = 'asterisk_plus_phone.recently_call'
    _rec_name = 'rec_name'
    _order = 'last_call_date desc'
    _description = 'Recently Call'

    rec_name = fields.Char(compute="_get_rec_name")
    calling_number = fields.Char(index=True)
    called_number = fields.Char(index=True)
    last_call_date = fields.Datetime()
    calling_user = fields.Many2one('res.users', ondelete='set null')
    answered_user = fields.Many2one('res.users', ondelete='set null')
    partner = fields.Many2one('res.partner', ondelete='set null')

    calls = fields.One2many("asterisk_plus.call", "recently")

    def _get_rec_name(self):
        for rec in self:
            rec.rec_name = f"{rec.calling_number} - {rec.called_number}"
