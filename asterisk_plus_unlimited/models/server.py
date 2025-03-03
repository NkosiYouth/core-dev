# -*- coding: utf-8 -*-
# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2023
import json
import logging
import requests
import time
import sys
import urllib3
if sys.version_info[0] > 2:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import uuid
from odoo import api, models, fields, SUPERUSER_ID, registry, release, tools, _
from odoo.exceptions import ValidationError, UserError


logger = logging.getLogger(__name__)


class Server(models.Model):
    _inherit = 'asterisk_plus.server'

    agent_url = fields.Char(string='Agent URL', required=True, default='https://localhost:48000')
    agent_token = fields.Char(required=True, default=lambda x: uuid.uuid4().hex)

    def local_job(self, fun, args=None, kwargs={}, timeout=6,
                  res_model=None, res_method=None, res_notify_uid=None,
                  res_notify_title='PBX', pass_back=None, 
                  raise_exc=True):
        self.ensure_one()
        res = {}
        response = None
        # debug(self, 'Server job, args: {}, kwargs: {}, res: {}.{}, pass_back: {}'.format(
        #    args, kwargs, res_model, res_method, pass_back))
        try:
            data = {
                'fun': fun, 'args': args, 'kwargs': kwargs,
                'res_model': res_model, 'res_method': res_method,
                'res_notify_uid': res_notify_uid,
                'res_notify_title': res_notify_title, 'pass_back': pass_back,
            }
            response = requests.post(
                urljoin(self.agent_url, 'app/asterisk_plus/agent'),
                headers={
                    'x-token': self.agent_token,
                }, json=data, timeout=timeout, verify=False)
            response.raise_for_status()
            # debug(self, 'API response: %s' % response.text)
            return response
        except Exception as e:
            if raise_exc:
                if response is None:
                    raise ValidationError(str(e))
                else:
                    raise ValidationError(response.text)
            else:
                logger.exception('Local job error:')            
