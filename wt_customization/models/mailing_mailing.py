# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.phone_validation.tools import phone_validation
import requests
import json

class Mailing(models.Model):
    _inherit = 'mailing.mailing'


    is_simcloud_api = fields.Boolean()
    token = fields.Char("Authantication Token")


    def action_send_sms(self, res_ids=None):
        if not self.is_simcloud_api:
            return super().action_send_sms()
        else:
            for mailing in self:
                if not res_ids:
                    res_ids = mailing._get_remaining_recipients()
                if res_ids:
                    composer = self.env['sms.composer'].with_context(active_id=False).create(mailing._send_sms_get_composer_values(res_ids))
                    composer._action_send_sms(is_simcloud_api=True)


                mailing.write({
                    'state': 'done',
                    'sent_date': fields.Datetime.now(),
                    'kpi_mail_required': not mailing.sent_date,
                    })
            return True



class SendSMS(models.TransientModel):
    _inherit = 'sms.composer'


    is_simcloud_api = fields.Boolean(default=True)


    def action_send_sms(self):
        if self.is_simcloud_api:
            token = self.env['ir.config_parameter'].sudo().get_param("simcloud_token")
            url = 'https://simcloud.co.za/api/sms.php'
            payload = json.dumps({
                "recipient": self.recipient_single_number_itf,
                "message": self.body
                })
            headers = {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
                    }
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
            except:
                pass

        else:
            if self.composition_mode in ('numbers', 'comment'):
                if self.comment_single_recipient and not self.recipient_single_valid:
                    raise UserError(_('Invalid recipient number. Please update it.'))
                elif not self.comment_single_recipient and self.recipient_invalid_count:
                    raise UserError(_('%s invalid recipients', self.recipient_invalid_count))
            self._action_send_sms()
            return False

    def _action_send_sms(self, is_simcloud_api=False):
        self.mailing_id.write({'state':'done'}) 
        records = self._get_records()
        if is_simcloud_api:
            numbers = []
            if self.mailing_id.mailing_model_id.model == 'mailing.list':
                for contact_list in self.mailing_id.contact_list_ids:
                    for contact in contact_list.contact_ids:
                        numbers.append(contact.mobile)

                for num in numbers:
                    if num != False:
                        token = self.env['ir.config_parameter'].sudo().get_param("simcloud_token")
                        url = 'https://simcloud.co.za/api/sms.php'
                        payload = json.dumps({
                            "recipient": num,
                            "message": self.mailing_id.body_plaintext
                            })
                        headers = {
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                                }
                        try:
                            response = requests.request("POST", url, headers=headers, data=payload)
                        except:
                            pass
        else:
            if self.composition_mode == 'numbers':
                return self._action_send_sms_numbers()
            elif self.composition_mode == 'comment':
                if records is None or not isinstance(records, self.pool['mail.thread']):
                    return self._action_send_sms_numbers()
                if self.comment_single_recipient:
                    return self._action_send_sms_comment_single(records)
                else:
                    return self._action_send_sms_comment(records)
            else:
                return self._action_send_sms_mass(records)



    # def _action_send_sms_mass(self, records=None):
    #     records = records if records is not None else self._get_records()

    #     sms_record_values = self._prepare_mass_sms_values(records)
    #     sms_all = self._prepare_mass_sms(records, sms_record_values)

    #     if sms_all and self.mass_keep_log and records and isinstance(records, self.pool['mail.thread']):
    #         log_values = self._prepare_mass_log_values(records, sms_record_values)
    #         records._message_log_batch(**log_values)

    #     if sms_all and self.mass_force_send:
    #         sms_all.filtered(lambda sms: sms.state == 'outgoing').send(auto_commit=False, raise_exception=False)
    #         return self.env['sms.sms'].sudo().search([('id', 'in', sms_all.ids)])
    #     return sms_all