# -*- coding: utf-8 -*-

from odoo import models, fields 

class Business(models.Model):
    _name = 'business.business'
    _description = "Business"

    name = fields.Char(string="name")
    bee_level = fields.Selection([('BEE Level 1', 'BEE Level 1'),
                                ('BEE Level 2', 'BEE Level 2'),
                                ('BEE Level 3', 'BEE Level 3'),
                                ('BEE Level 4', 'BEE Level 4'),
                                ('BEE Level 5', 'BEE Level 5'),
                                ('BEE Level 6', 'BEE Level 6'),
                                ('BEE Level 7', 'BEE Level 7'),
                                ('BEE Level 8', 'BEE Level 8')], string="BEE Level")
    business_size = fields.Selection([('Small', 'Small'),
                                    ('Medium', 'Medium'),
                                    ('Large', 'Large')], string="Business Size")
    cohort_id = fields.Many2one('cohort.cohort  ', string="Cohort ID")
    contact_pp_info_id = fields.Many2one('res.partner', string="Contact PP Info")
    female_ownership = fields.Float(string="Female Ownership")
    internal_relationship = fields.Selection([('Funder', 'Funder'),
                                            ('Corporate', 'Corporate'),
                                            ('Host', 'Host'),
                                            ('Partner', 'Partner')], string="Internal Relationship")
    payroll_type = fields.Selection([('Funder', 'Funder'),
                                    ('youth@WORK', 'youth@WORK'),
                                    ('Corporate', 'Corporate')], string="Payroll Type")