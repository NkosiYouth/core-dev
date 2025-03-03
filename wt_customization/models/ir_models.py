# -*- coding: utf-8 -*-

from odoo import models,fields

class WebsiteFormModel(models.Model):
    _inherit = "ir.model"
    
    def _get_form_writable_fields(self):
        if self.model == "project.task":
            included = {
                field.name
                for field in self.env['ir.model.fields'].sudo().search([
                    ('model_id', '=', self.id),
                ])
            }
            return {k: v for k, v in self.get_authorized_fields(self.model).items() if k in included}
        else:
            return super(WebsiteFormModel, self)._get_form_writable_fields()