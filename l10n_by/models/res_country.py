from odoo import fields, models


class Country(models.Model):
    _inherit = "res.country"

    decimal_code = fields.Integer(
        string="Decimal Code",
        help="Decimal Code from OKRB 017-99",
    )
