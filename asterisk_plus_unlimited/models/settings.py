from odoo import models, fields


class Settings(models.Model):
    _inherit = 'asterisk_plus.settings'

    is_registered = fields.Boolean(compute='_get_unlimited_registration')
    is_subscribed = fields.Boolean(compute='_get_unlimited_registration')

    def _get_unlimited_registration(self):
        for rec in self:
            rec.is_registered = True
            rec.is_subscribed = True
