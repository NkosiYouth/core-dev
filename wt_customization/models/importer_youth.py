# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from dateutil.parser import parse


class ImporterYouth(models.Model):
    _name = "importer.youth"
    _description = "Importer Youth"

    funder = fields.Char('Funder')
    matched_cohort = fields.Char('Matched Cohort')
    id_number = fields.Char('ID Number')
    youth_name = fields.Char('Youth Name')
    start_date = fields.Char('Start Date')
    end_date = fields.Char('End Date')
    host_site = fields.Char('Host Site')
    private_phone = fields.Char('Private Phone')
    private_email = fields.Char('Private Email')
    gender = fields.Char('Gender')
    race = fields.Char('Race')
    sector = fields.Char('Sector')
    manager = fields.Char('Manager')
    partner = fields.Char('Partner')
    linked_emergency_contact = fields.Char('Linked Emergency Contact')
    salary = fields.Char('Salary')
    job_title = fields.Char('Job Title (SARS)')
    title = fields.Char('Title')
    disabled = fields.Char('Disabled')
    drop_off_replacement = fields.Char('Drop Off/Replacement')
    absorption_indication = fields.Char('Absorption Indication')
    is_active = fields.Char('Is Active?')
    role = fields.Char('Role')
    is_imported = fields.Boolean()
    fail_reason = fields.Char()

    def import_youth(self):
            for rec in self.browse(self._context.get('active_ids')):
                if rec.manager:
                    manager_id = self.env['hr.employee'].search([('name','=',rec.manager)],limit=1)
                    if not manager_id:
                        manager_id = self.env['hr.employee'].create({'name':rec.manager})
                else:
                    manager_id = False
                if rec.funder:
                    funder_id = self.env['res.partner'].search([('name','=',rec.funder)],limit=1).id
                else:
                    funder_id = False
                if rec.matched_cohort:
                    cohort_id = self.env['cohort.cohort'].search([('name','=',rec.matched_cohort)],limit=1).id
                else:
                    cohort_id = False
                if rec.host_site:
                    host_site_id = self.env['res.partner'].search([('name','=',rec.host_site)],limit=1).id
                else:
                    host_site_id = False
                if rec.job_title:
                    job_title_id = self.env['hr.job'].search([('name','=',rec.job_title)],limit=1).id
                    if not job_title_id:
                        job_title_id = self.env['hr.job'].create({'name':rec.job_title}).id
                else:
                    job_title_id = False

                title_id = self.env['res.partner.title'].search([('name','=',rec.title)],limit=1)
                if not title_id:
                    title_id = self.env['res.partner.title'].create({
                        'name':rec.title,
                        'shortcut':rec.title
                        })

                if not rec.linked_emergency_contact == "#N/A":
                    emergency_contract_id = self.env['res.partner'].search([('name','=',rec.linked_emergency_contact)]).ids
                else:
                    emergency_contract_id = False

                if rec.disabled == "Yes":
                    disabled = True
                else:
                    disabled = False

                if rec.is_active == "Yes":
                    active = True
                else:
                    active = False

                if not rec.absorption_indication in ['Permanent Employment', 'Fixed-term Employment']:
                    absorption_indication = False

                if rec.absorption_indication == 'Permanent Employment':
                    absorption_indication = 'Permanent Employment'
                if rec.absorption_indication == 'Fixed-term Employment':
                    absorption_indication = 'Fixed Term Employment'

                if rec.role == 'Youth':
                    user_role_id = self.env['user.role'].search([('name','=','Youth')],limit=1).id
                else:
                    user_role_id = False
                if not rec.race == "#N/A":
                    race = rec.race
                else:
                    race = False

                youth_vals = {
                    'identification_id':rec.id_number,
                    'name':rec.youth_name,
                    'mobile_phone':rec.private_phone,
                    'work_email':rec.private_email,
                    'gender':rec.gender.lower(),
                    'race':race,
                    'parent_id':manager_id.id if manager_id else False,
                    'job_id':job_title_id if job_title_id else False,
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
                youth_id = self.env['hr.employee'].search([('id_number','=',rec.id_number),('active','in',[True, False])])
                if not youth_id:
                    try:
                        youth_id = self.env['hr.employee'].create(youth_vals)
                        rec.is_imported = True
                        rec.fail_reason = False
                    except Exception as e: 
                        self.env.cr.rollback()
                        rec.fail_reason = str(e)
                else:
                    try:
                        youth_id.write(youth_vals)
                        rec.is_imported = True
                    except Exception as e: 
                        self.env.cr.rollback()
                        rec.fail_reason = str(e)
                        rec.is_imported = False

                self._cr.commit()

                try:
                    start_date_object = parse(rec.start_date, dayfirst=True)
                    start_date_object = start_date_object.date()
                    end_date_object = parse(rec.end_date, dayfirst=True)
                    end_date_object = end_date_object.date()
                except :
                    pass
                if youth_id:
                    youth_id.update_employee_details()
                    contract_vals = {
                        'name':youth_id.name + " " +"Contract",
                        'employee_id':youth_id.id,
                        'date_start':start_date_object,
                        'date_end':end_date_object,
                        'hr_responsible_id':self.env.user.id,
                        'wage':rec.salary
                    }
                    if end_date_object > start_date_object:
                        contract_id = self.env['hr.contract'].search([('name','=',youth_id.name + " " +"Contract")],limit=1)
                        if not contract_id:
                            try:
                                contract_id = self.env['hr.contract'].create(contract_vals)
                            except Exception as e:
                                self.env.cr.rollback()
                                rec.fail_reason = str(e)
                                rec.is_imported = False

                        else:
                            try:
                                contract_id.write(contract_vals)
                            except Exception as e:
                                self.env.cr.rollback()
                                rec.fail_reason = str(e)
                                rec.is_imported = False
                                
                        self._cr.commit()

            delete_importer = self.search([('is_imported','=',True)])
            delete_importer.unlink()