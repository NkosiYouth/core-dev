from odoo import models, fields

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_acc_type = fields.Selection([
        ('Savings', 'Savings'),
        ('Cheque', 'Cheque'),
        ('Transmission', 'Transmission'),
        ('Current', 'Current'),
    ], string='Account Type')

    branch_code = fields.Char(
        string='Branch Code',
        related='bank_id.bank_branch_code',
        store=True,
        readonly=False
    )

    tax_number = fields.Char(string='Tax Number')