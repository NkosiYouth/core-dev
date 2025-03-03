# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    bee_level = fields.Selection([('BEE Level 1', 'BEE Level 1'),
                                ('BEE Level 2', 'BEE Level 2'),
                                ('BEE Level 3', 'BEE Level 3'),
                                ('BEE Level 4', 'BEE Level 4'),
                                ('BEE Level 5', 'BEE Level 5'),
                                ('BEE Level 6', 'BEE Level 6'),
                                ('BEE Level 7', 'BEE Level 7'),
                                ('BEE Level 8', 'BEE Level 8')], string="BEE Level")
    business_id = fields.Many2one('business.business', string="Business ID")
    business_size = fields.Selection([('Small', 'Small'),
                                    ('Medium', 'Medium'),
                                    ('Large', 'Large')], string="Business Size")
    capacity = fields.Integer(string="Capacity")
    cohort_ids = fields.One2many('cohort.cohort', 'funder_id', string="Cohort ID")
    cohorts_ids = fields.Many2many('cohort.cohort', 'res_partner_cohort_rel', 'res_partner_id', 'cohort_id', string="Cohorts")
    youth_company_type = fields.Selection([('Funder', 'Funder'),
                                    ('Partner', 'Partner'),
                                    ('Host Site', 'Host Site'),
                                    ('Host Site & Partner', 'Host Site & Partner')], string="Company Type")
    youth_contact_type = fields.Selection([('Youth', 'Youth'),
                                    ('Supervisor', 'Supervisor'),
                                    ('Provincial Coordinator', 'Provincial Coordinator'),
                                    ('Partner', 'Partner'),
                                    ('Next of Kin', 'Next of Kin'),
                                    ('Y@W Employee', 'Y@W Employee'),
                                    ('Contact', 'Contact')], string="Contact Type")
    dummy_field = fields.Boolean(compute='_compute_x_contact_type')
    female_ownership = fields.Float(string="Female Ownership")
    host_partner_task_id = fields.Many2one('project.task', string="Host Partner Task")
    host_partner_ticket_id = fields.Many2one('helpdesk.ticket', string="Host Partner Ticket")
    host_site_id = fields.Many2one('res.partner', related='youth_id.host_site_id', string='Host Site')
    id_number = fields.Char(string="ID Number")
    next_of_kin_ids = fields.Many2many('hr.employee', 'hr_employee_res_partner_rel', 'res_partner_id', 'hr_employee_id', string="Youth")
    next_of_kin_relationship = fields.Selection([('mother', 'Mother'),
                                                ('father', 'Father'),
                                                ('aunt', 'Aunt'),
                                                ('brother', 'Brother'),
                                                ('brother-in-law', 'Brother-in-law'),
                                                ('cousin', 'Cousin'),
                                                ('fiance', 'Fiance'),
                                                ('sister', 'Sister'),
                                                ('uncle', 'Uncle'),
                                                ('grandfather', 'Grandfather'),
                                                ('grandmother', 'Grandmother'),
                                                ('husband', 'Husband'),
                                                ('life partner', 'Life Partner'),
                                                ('wife', 'Wife')], string='Next of Kin Relationship')
    no_of_vaccancies = fields.Integer(string="Number of Vaccancies", readonly=True)
    recruitment_id	= fields.Many2one('hr.applicant', string='Recruitment')
    sector_id = fields.Many2one('res.partner.industry', string="Sector")
    status = fields.Selection([('Active', 'Active'),
                            ('Inactive', 'Inactive')], string="Status")
    # user_ids = fields.One2many('hr.employee', 'partner_id', string="User")
    vacancies_task_ids = fields.One2many('project.task', 'host_site_id', string="Vacancies Tasks")
    youth_id = fields.Many2one('hr.employee', string="Youth Name", compute='_compute_linked_user', store=True)


    cohort_id = fields.Many2one('cohort.cohort', string="Cohort", compute='_compute_cohort_id', store=True)

    @api.depends('employee_ids.cohort_id')
    def _compute_cohort_id(self):
        """Find the related employee and set the cohort_id in res.partner"""
        for partner in self:
            employees = self.env['hr.employee'].search([('active', 'in', [True, False])]).filtered(
                lambda employee: employee.related_contact_ids and partner in employee.related_contact_ids
            )
            partner.cohort_id = employees.cohort_id if employees else False


    def set_cohort_id_by_cron(self):
        partners = self.env['res.partner'].search([])
        for contact in partners:
            if not contact.cohort_id:
                contact._compute_cohort_id()
                self._cr.commit()
                _logger.info("-----contact-cohort--------: %s" % (contact.name))


    @api.depends()
    def _compute_linked_user(self):
        for contact in self:
            contact.youth_id = False
            employees = contact.env['hr.employee'].search([('active','in',[True, False])]).filtered(lambda employee: employee.related_contact_ids and contact in employee.related_contact_ids)
            if employees: 
                contact.youth_id = employees[0].id if len(employees) > 1 else employees.id
                contact.youth_contact_type = contact.youth_id.user_roles_id.name

    def _compute_x_contact_type(self):
        for rec in self:
            rec.dummy_field = True
            # rec.youth_contact_type = rec.youth_id.user_roles_id.name


    @api.onchange("email", "function", "youth_contact_type")
    def update_employee_details(self):
        for employee in self.employee_ids:
            try:
                employee.write({
                    # 'job_title':self.function,
                    'work_phone':self.phone,
                    'work_email':self.email
                })
            except Exception as e:
                raise UserError("%s" % e)
    
    

    def set_linked_user_contact(self):
        partners = self.env['res.partner'].search([
            ('youth_id', '=', False), 
            ('youth_contact_type', 'in', ['Youth', 'Supervisor'])
        ])        
        for partner in partners:
            employees = self.env['hr.employee'].search([('active', 'in', [True, False])]).filtered(
                lambda employee: employee.related_contact_ids and partner in employee.related_contact_ids
            )

            if employees:
                partner.youth_id = employees[0].id if len(employees) > 1 else employees.id
                _logger.info("-----linked user for-------- %s : %s" % (partner.id, partner.youth_id))
                partner.youth_contact_type = partner.youth_id.user_roles_id.name
                self._cr.commit()
