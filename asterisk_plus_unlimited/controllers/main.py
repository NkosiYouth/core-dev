# -*- coding: utf-8 -*
# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import json
import logging
import uuid
from odoo import http, SUPERUSER_ID, registry, release
from odoo.api import Environment
from werkzeug.exceptions import BadRequest, NotFound
from odoo.addons.asterisk_plus.controllers.main import error_response, AsteriskPlusController

logger = logging.getLogger(__name__)

class AsteriskPlusUnlimitedController(AsteriskPlusController):

    def _initialize_server(self, env):
        # Check if Server is already initialized.
        server = env.ref('asterisk_plus.default_server').sudo()
        if server.agent_initialized:
            return error_response('Agent is already initialized.')
        if not server.permit_agent_initialization:
            return error_response('Agent initialization is not permitted!')
        # Close init and set token
        agent_token = str(uuid.uuid4())
        odoo_password = str(uuid.uuid4())
        # Set Odoo password
        server.user.password = odoo_password
        # Get connection data and pass to the agent        
        data = {
            'agent_token': agent_token,
            'odoo_user': server.user.login,
            'odoo_password': odoo_password,
            'odoo_db': env.cr.dbname,
        }
        server.write({
            'agent_initialized': True,
            'permit_agent_initialization': False,
            'agent_token': agent_token,
        })
        # Set initialized flag to disable future requests.
        logger.info('Agent initialization complete.')
        return http.request.make_response(json.dumps(data))
