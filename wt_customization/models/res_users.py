# -*- coding: utf-8 -*-

from odoo import fields,models

class ResUsers(models.Model):
    _inherit = "res.users"


    bee_level = fields.Selection(related="partner_id.bee_level", string="BEE Level")
    business_id = fields.Many2one('business.business', related="partner_id.business_id", string="Business ID")
    business_size = fields.Selection(related='partner_id.business_size',string='Business Size')
    capacity = fields.Integer(related='partner_id.capacity', string="Capacity")
    cohort_ids = fields.One2many('cohort.cohort', related="partner_id.cohort_ids", string="Cohort ID")
    cohorts_ids = fields.Many2many('cohort.cohort', related="partner_id.cohorts_ids", string="Cohorts")
    company_type = fields.Selection(related='partner_id.youth_company_type', string="Company Type")
    contact_type = fields.Selection(related='partner_id.youth_contact_type', string="Contact Type")
    female_ownership = fields.Float(related='partner_id.female_ownership', string="Female Ownership")
    host_partner_task_id = fields.Many2one('project.task', related='partner_id.host_partner_task_id', string="Host Partner Task")
    host_site_id = fields.Many2one('res.partner', related="partner_id.host_site_id", string="Host Site")
    id_number = fields.Char(related='partner_id.id_number', string="ID Number")
    next_of_kin_ids = fields.Many2many('hr.employee', related="partner_id.next_of_kin_ids", string='Youth')
    next_of_kin_relationship = fields.Selection(related='partner_id.next_of_kin_relationship', string="Next of Kin Relationship")
    no_of_vaccancies = fields.Integer(related="partner_id.no_of_vaccancies", string="Number of Vaccancies")
    recruitment_id = fields.Many2one('hr.applicant', related='partner_id.recruitment_id', string="Recruitment")
    sector_id = fields.Many2one('res.partner.industry', related="partner_id.sector_id", string="Sector")
    status = fields.Selection(related="partner_id.status", string="Status")
    user_ids = fields.One2many('hr.employee', related="partner_id.user_ids", string="User")
    vacancies_task_ids = fields.One2many('project.task', related="partner_id.vacancies_task_ids", string="Vacancies Tasks")
    youth_id = fields.Many2one('hr.employee', related="partner_id.youth_id", string='Youth Name')
    office_ids = fields.Many2many('office.office', string="Offices")