# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import date
import math

class Cohort(models.Model):
    _name = "cohort.cohort"
    _description = "Cohort"

    name = fields.Char(string="Cohort Name")
    active = fields.Boolean(string="Active", compute="_compute_active_status", store=True, tracking=True)
    cohort_buffer = fields.Integer(string="Cohort Buffer")
    total_allocation = fields.Integer(string="Total Allocation")

    drop_off_replacement_target = fields.Float(
        string="Drop-off Replacement Target (%)", 
        default=5.0  # Default value set to 5%
    )
    drop_off_replacement = fields.Integer(
        string="Drop-off Replacement", 
        compute='_compute_drop_off_replacement', 
        readonly=True
    )

    replacement_enabled = fields.Boolean(
        string="Enable Drop-off Replacements", 
        default=True
    )

    absorption_target_yes = fields.Float(string="YES Absorption Target (%)", default=10.0)
    absorption_target_funder = fields.Float(string="Funder Absorption Target (%)", default=5.0)
    absorption_needed_yes = fields.Integer(string="Absorption Needed (YES)", compute='_compute_absorption_needed', readonly=True)
    absorption_needed_funder = fields.Integer(string="Absorption Needed (Funder)", compute='_compute_absorption_needed', readonly=True)

    compliance_target = fields.Integer(
        string="Compliance Target", 
        compute='_compute_compliance_target', 
        readonly=True
    )

    cost_centre = fields.Char(string="Cost Centre")

    payroll_type = fields.Selection([
        ('ip', 'IP'),
        ('Funder', 'Funder')
    ], string="Payroll Type")
    organization_type = fields.Selection([
        ('NPO', 'NPO'),
        ('Pty Ltd', 'Pty Ltd')
    ], string="Organization Type")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    
    sector_ids = fields.Many2many(
        'res.partner.industry',
        'res_partner_industry_cohort_rel',
        'cohort_id',
        'res_partner_industry_id',
        string="Sectors"
    )

    male_requirement = fields.Float(string="Male Requirement (%)")
    female_requirement = fields.Float(string="Female Requirement (%)")
    disability_requirement = fields.Float(string="Disability Requirement (%)")

    funder_id = fields.Many2one(
        'res.partner',
        string="Funder",
        domain="[('youth_company_type', '=', 'Funder')]"
    )

    youth_salary = fields.Float(string="Youth Salary")

    employment_details = fields.Many2one(
        'hr.employee',
        string="Employment Details"
    )

    contract_type = fields.Selection([
        ('fixed_term_6', '6 Month Fixed Term'),
        ('fixed_term_12', '12 Month Fixed Term')
    ], string="Contract Type")

    journey_id = fields.Many2one(
        'journey.journey',
        string="Journey"
    )

    age_range = fields.Selection([
        ('18_24', '18 - 24'),
        ('18_28', '18 - 28'),
        ('18_34', '18 - 34')
    ], string="Age Range")

    yes_phones = fields.Boolean(string="YES Phones")

    placement_type = fields.Selection([
        ('Yes', 'YES'),
        ('direct', 'Direct'),
        ('funder', 'Funder')
    ], string="Placement Type")

    extra_requests = fields.Text(string="Extra Funder Requests")
    internal_placements = fields.Integer(string="Internal Placements")
    external_placements = fields.Integer(string="External Placements")
    geographical_placemeent = fields.Text(string="Geographical Placement Areas")
    notes = fields.Text(string="Notes")

    # Computed Fields
    @api.depends('end_date')
    def _compute_active_status(self):
        today = date.today()
        for record in self:
            record.active = not (record.end_date and record.end_date < today)
    
    @api.model
    def _update_active_status(self):
        self.search([])._compute_active_status()

    @api.depends('drop_off_replacement_target', 'total_allocation', 'replacement_enabled')
    def _compute_drop_off_replacement(self):
        for record in self:
            if record.replacement_enabled and record.total_allocation and record.drop_off_replacement_target:
                drop_off_number = record.total_allocation * (record.drop_off_replacement_target / 100.0)
                record.drop_off_replacement = int(math.ceil(drop_off_number))
            else:
                record.drop_off_replacement = 0

    @api.depends('absorption_target_yes', 'absorption_target_funder', 'total_allocation')
    def _compute_absorption_needed(self):
        for record in self:
            if record.total_allocation:
                # Compute YES absorption
                if record.absorption_target_yes:
                    yes_absorption_number = record.total_allocation * (record.absorption_target_yes / 100.0)
                    record.absorption_needed_yes = int(math.ceil(yes_absorption_number))
                else:
                    record.absorption_needed_yes = 0
                # Compute Funder absorption
                if record.absorption_target_funder:
                    funder_absorption_number = record.total_allocation * (record.absorption_target_funder / 100.0)
                    record.absorption_needed_funder = int(math.ceil(funder_absorption_number))
                else:
                    record.absorption_needed_funder = 0
            else:
                record.absorption_needed_yes = 0
                record.absorption_needed_funder = 0

    @api.depends('cohort_buffer', 'total_allocation')
    def _compute_compliance_target(self):
        """
        Compliance Target = Total Allocation - Cohort Buffer
        - The buffer is built-in, so the compliance starts from the required youth count.
        """
        for record in self:
            if record.total_allocation and record.cohort_buffer:
                record.compliance_target = record.total_allocation - record.cohort_buffer
            else:
                record.compliance_target = record.total_allocation