# -*- coding: utf-8 -*-

import csv
import io
import logging
import base64
from odoo import fields, models, api, _
from datetime import datetime
from dateutil.parser import parse

_logger = logging.getLogger(__name__)

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO



class ImportYouth(models.TransientModel):
    _name = "import.youth"
    _description = "Youth Import"
   
    file_path = fields.Binary(type='binary', string="File To Import")

    def _read_csv_data(self, binary_data):
        """
            Reads CSV from given path and Return list of dict with Mapping
        """
        data = csv.reader(StringIO(base64.b64decode(self.file_path).decode('utf-8')), quotechar='"', delimiter=',')

        # Read the column names from the first line of the file
        fields = next(data)
        data_lines = []
        for row in data:
            items = dict(zip(fields, row))
            data_lines.append(items)
        return fields, data_lines


    def do_import_youth_data(self):
        file_path = self.file_path
        if not file_path or file_path == "":
            _logger.warning("Import can not be started. Configure your schedule Actions.")
            return True
        fields = data_lines = False

        try:
            fields, data_lines = self._read_csv_data(file_path)
        except:
            _logger.warning("Can not read source file(csv) '%s', Invalid file path or File not reachable on file system."%(file_path))
            return True
        if not data_lines:
            _logger.info("File '%s' has no data or it has been already imported, please update the file."%(file_path))
            return True
            
        for data in data_lines:
            id_number = data.get('ID Number')
            youth_name = data.get('Youth Name')
            mobile_phone = data.get('Private Phone')
            private_email = data.get('Private Email')
            gender = data.get('Gender').lower()
            race = data.get('Race')
            manager_name = data.get('Manager')
            job_title = data.get('Job Title (SARS)')
            title = data.get('Title') 
            disabled = data.get('Disabled')
            active = data.get('Is Active?')
            user_role = data.get('Role')
            funder_name = data.get('Funder')
            cohort_name = data.get('Matched Cohort')
            host_site_name = data.get('Host Site')
            start_date = data.get('Start Date')
            end_date = data.get('End Date')
            salary = data.get('Salary')
            absorption_indication = data.get('Absorption Indication')

            id_number = id_number.strip()
            youth_name = youth_name.strip()
            mobile_phone = mobile_phone.strip()
            private_email = private_email.strip()
            gender = gender.strip()
            race = race.strip()
            job_title = job_title.strip()
            user_role = user_role.strip()
            start_date = start_date.strip()
            end_date = end_date.strip()
            salary = salary.strip()
            absorption_indication = absorption_indication.strip()

            try:
                start_date_object = parse(start_date, dayfirst=True)  # Prioritize day-first format
                start_date_object = start_date_object.date()
                end_date_object = parse(end_date, dayfirst=True)  # Prioritize day-first format
                end_date_object = end_date_object.date()
            except :
                pass

            if not absorption_indication in ['Permanent Employment', 'Fixed-term Employment']:
                absorption_indication = False

            if absorption_indication == 'Permanent Employment':
                absorption_indication = 'Permanent Employment'
            if absorption_indication == 'Fixed-term Employment':
                absorption_indication = 'Fixed Term Employment'

            if salary == "#N/A":
                salary = 0.0

            if race == "#N/A":
                race = False

            if user_role == 'Youth':
                user_role_id = self.env['user.role'].search([('name','=','Youth')],limit=1).id
            else:
                user_role_id = False

            if disabled == "Yes":
                disabled = True
            else:
                False

            if active == "Yes":
                active = True
            else:
                False

            funder_id = self.env['res.partner'].search([('name','=',funder_name.strip())],limit=1).id
            cohort_id = self.env['cohort.cohort'].search([('name','=',cohort_name.strip())],limit=1).id
            host_site_id = self.env['res.partner'].search([('name','=',host_site_name.strip())],limit=1).id

            manager_id = self.env['hr.employee'].search([('name','=',manager_name.strip())],limit=1).id
            title_id = self.env['res.partner.title'].search([('name','=',title.strip())],limit=1)
            if not title_id:
                title_id = self.env['res.partner.title'].create({
                    'name':title.strip(),
                    'shortcut':title.strip()
                    })
            emergency_contract_name = data.get('Linked Emergency Contact')
            emergency_contract_name = emergency_contract_name.strip()
            emergency_contract_id = False
            if not emergency_contract_name == "#N/A":
                emergency_contract_id = self.env['res.partner'].search([('name','=',emergency_contract_name)]).ids
            else:
                False

            vals = {
                'id_number':id_number,
                'name':youth_name,
                'mobile_phone':mobile_phone,
                'private_email':private_email,
                'gender':gender,
                'race':race,
                'parent_id':manager_id if manager_id else False,
                'job_title':job_title,
                'title_id':title_id.id,
                'disabled':disabled,
                'active':active,
                'user_roles_id':user_role_id,
                'funder_id':funder_id if funder_id else False,
                'cohort_id':cohort_id if cohort_id else False,
                'host_site_id':host_site_id if host_site_id else False,
                'next_of_kin_ids': [(6, 0,emergency_contract_id)] if emergency_contract_id else False,
                'absorption_indication':absorption_indication
            }

            youth_id = self.env['hr.employee'].search([('id_number','=',id_number),('active','in',[True, False])])
            if not youth_id:
                youth_id = self.env['hr.employee'].create(vals)
            else:
                youth_id.write(vals)
            self._cr.commit()

            contract_vals = {
                'name':youth_id.name + " " +"Contract",
                'employee_id':youth_id.id,
                'date_start':start_date_object,
                'date_end':end_date_object,
                'hr_responsible_id':self.env.user.id,
                'wage':salary
            }
            if end_date_object > start_date_object:
                contract_id = self.env['hr.contract'].search([('name','=',youth_id.name + " " +"Contract")],limit=1)
                if not contract_id:
                    contract_id = self.env['hr.contract'].create(contract_vals)
                else:
                    contract_id.write(contract_vals)
                self._cr.commit()
