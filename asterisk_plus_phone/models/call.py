from datetime import datetime

from odoo import api, fields, models


class Call(models.Model):
    _inherit = 'asterisk_plus.call'

    recently = fields.Many2one("asterisk_plus_phone.recently_call")

    @api.model
    def create(self, values):
        recently = self.env['asterisk_plus_phone.recently_call'].search([
            ('calling_number', '=', values['calling_number']),
            '|', ('called_number', '=', values['called_number']),
            ('called_number', '=', values['calling_number']),
            ('calling_number', '=', values['called_number']),
        ], limit=1)
        if not recently:
            recently = self.env['asterisk_plus_phone.recently_call'].create({
                'calling_number': values['calling_number'],
                'called_number': values['called_number'],
                'calling_user': values.get('calling_user'),
                'answered_user': values.get('answered_user'),
                'partner': values.get('partner'),
                'last_call_date': datetime.utcnow()
            })
        else:
            recently.write({
                'last_call_date': datetime.utcnow(),
                'calling_number': values['calling_number'],
                'called_number': values['called_number'],
            })
        values.update({"recently": recently.id})

        return super(Call, self).create(values)

    def write(self, values):
        if 'partner' in values:
            self.recently.partner = values['partner']
        return super(Call, self).write(values)
