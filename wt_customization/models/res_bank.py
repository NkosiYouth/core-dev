from odoo import models, fields

class ResBank(models.Model):
    _inherit = 'res.bank'

    bank_branch_code = fields.Char(string='Bank Branch Code')