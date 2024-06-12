# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("ru", "product.category")
    def _get_ru_product_category(self):
        return {
            "l10n_ru_stock.category_mrp": {
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_account_input_categ_id": "ru_acc_10_00_60",
                "property_stock_account_output_categ_id": "ru_acc_20_01",
                "property_stock_valuation_account_id": "ru_acc_10_01",
            },
            "l10n_ru_stock.category_mrp_materials": {
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_account_input_categ_id": "ru_acc_10_00_60",
                "property_stock_account_output_categ_id": "ru_acc_20_01",
                "property_stock_valuation_account_id": "ru_acc_10_01",
            },
            "l10n_ru_stock.category_mrp_parts": {
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_account_input_categ_id": "ru_acc_10_00_60",
                "property_stock_account_output_categ_id": "ru_acc_20_01",
                "property_stock_valuation_account_id": "ru_acc_10_05",
            },
            "l10n_ru_stock.category_mrp_semi_finished": {
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_account_input_categ_id": "ru_acc_20_01",
                "property_stock_account_output_categ_id": "ru_acc_20_01",
                "property_stock_valuation_account_id": "ru_acc_21",
            },
            "l10n_ru_stock.category_mrp_finished": {
                "property_valuation": "real_time",
                "property_cost_method": "average",
                "property_stock_account_input_categ_id": "ru_acc_20_01",
                "property_stock_account_output_categ_id": "ru_acc_41_00_90",
                "property_stock_valuation_account_id": "ru_acc_43",
            },
        }
