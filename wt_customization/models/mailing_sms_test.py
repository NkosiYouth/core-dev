# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.addons.phone_validation.tools import phone_validation
import requests
import json

class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'


    @api.model
    def _send_sms_batch(self, messages):
        if any(message.get('simcloud') == False or not message.get('simcloud') for message in messages):
            res = super()._send_sms_batch(messages)
            return res
        else:
            params = {
                'messages': messages
                }
            return self._contact_iap('https://simcloud.co.za/api/sms.php', params)


    @api.model
    def _contact_iap(self, local_endpoint, params):
        if any(msg.get('simcloud') == False or not msg.get('simcloud') for msg in params.get('messages')):
            res = super()._contact_iap(local_endpoint, params)
            return res
        else:
            responses = []
            for msg in params.get('messages'):
                if msg.get('simcloud'):
                    url = local_endpoint
                    payload = json.dumps({
                        "recipient": msg.get('number'),
                        "message": msg.get('content')
                        })
                    headers = {
                        'Authorization': 'Bearer ' + msg.get('token'),
                        'Content-Type': 'application/json'
                            }
                    response = requests.request("POST", url, headers=headers, data=payload)
                    res = json.loads(response.text)
                    responses.append(res)
            return responses




class MassSMSTest(models.TransientModel):
    _inherit = 'mailing.sms.test'

    def action_send_sms(self):
        if not self.mailing_id.is_simcloud_api:
            res = super(MassSMSTest, self).action_send_sms() 
            return res
        else:
            numbers = [number.strip() for number in self.numbers.splitlines()]
            sanitize_res = phone_validation.phone_sanitize_numbers_w_record(numbers, self.env.user)
            sanitized_numbers = [info['sanitized'] for info in sanitize_res.values() if info['sanitized']]
            invalid_numbers = [number for number, info in sanitize_res.items() if info['code']]

            record = self.env[self.mailing_id.mailing_model_real].search([], limit=1)
            body = self.mailing_id.body_plaintext
            if record:
                body = self.env['mail.render.mixin']._render_template(body, self.mailing_id.mailing_model_real, record.ids)[record.id]
            token = self.env['ir.config_parameter'].sudo().get_param("simcloud_token")
            sent_sms_list = self.env['sms.api']._send_sms_batch([{
                'res_id': number,
                'number': number,
                'content': body,
                'simcloud':self.mailing_id.is_simcloud_api,
                'token':token
            } for number in sanitized_numbers])

            
            error_messages = {}
            notification_messages = []

            for sent_sms in sent_sms_list:
                if sent_sms.get('status') == "success":
                    notification_messages.append(
                    _('Test SMS successfully sent'))


            if notification_messages:
                self.mailing_id._message_log(body='<ul>%s</ul>' % ''.join(['<li>%s</li>' % notification_message for notification_message in notification_messages]))
            return True


