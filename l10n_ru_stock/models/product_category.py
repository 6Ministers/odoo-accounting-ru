# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    name = fields.Char(translate=True)

    def write(self, vals):
        if "property_valuation" in vals and vals["property_valuation"] != "real_time":
            fiscal_country = self.env.company.account_fiscal_country_id
            if fiscal_country.code == "ru":
                raise UserWarning(
                    _("You can't use Manual valuation method for Russian Accounting")
                )

        return super().write(vals)
