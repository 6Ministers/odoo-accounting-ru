# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("by")
    def _get_by_template_data(self):
        return {
            "property_account_receivable_id": "by_620100",
            "property_account_payable_id": "by_600100",
            "property_account_expense_categ_id": "by_900401",
            "property_account_income_categ_id": "by_900101",
            "property_stock_account_input_categ_id": "by_410101",
            # allow reconciliation = true
            "property_stock_account_output_categ_id": "by_410102",
            # allow reconciliation = true
            "property_stock_valuation_account_id": "by_410100",
            "name": "План счетов РБ",
            "code_digits": "8",
            "use_storno_accounting": True,
            "display_invoice_amount_total_words": True,
        }

    @template("by", "res.company")
    def _get_by_res_company(self):
        return {
            self.env.company.id: {
                "anglo_saxon_accounting": True,
                "account_fiscal_country_id": "base.by",
                "bank_account_code_prefix": "51.01.",
                "cash_account_code_prefix": "50.04.",
                "transfer_account_code_prefix": "57.04.",
                "account_default_pos_receivable_account_id": "by_500499",
                "income_currency_exchange_account_id": "by_970401",
                "expense_currency_exchange_account_id": "by_970402",
                "account_sale_tax_id": "sale_tax_template_vat20incl_by",
                "account_purchase_tax_id": "purchase_tax_template_vat20_by",
            },
        }

    @template("by", "res.company")
    def _get_by_bank_accounts(self):
        """переопределяем банковские счета по умолчанию"""
        return {
            self.env.company.id: {
                "account_journal_suspense_account_id": "by_510100",
                "account_journal_payment_debit_account_id": "by_510101",
                "account_journal_payment_credit_account_id": "by_510102",
                "transfer_account_id": "by_570401",
            },
        }
