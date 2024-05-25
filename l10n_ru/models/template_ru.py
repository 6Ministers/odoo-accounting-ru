# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("ru")
    def _get_ru_template_data(self):
        return {
            # "name": "План счетов РФ",
            "name": _("Russian Chart of Accounts"),
            "code_digits": "2",
            "property_account_receivable_id": "ru_acc_62_01",
            "property_account_payable_id": "ru_acc_60_01",
            "property_account_expense_categ_id": "ru_acc_90_02_1",
            "property_account_income_categ_id": "ru_acc_90_01_1",
            "property_stock_account_input_categ_id": "ru_acc_41_00_60",
            "property_stock_account_output_categ_id": "ru_acc_90_00_41",
            "property_stock_valuation_account_id": "ru_acc_41_01",
            "property_tax_payable_account_id": "ru_acc_68",
            "property_tax_receivable_account_id": "ru_acc_68",
            "property_advance_tax_payment_account_id": "ru_acc_68",
            "property_cash_basis_base_account_id": "ru_acc_99",
            "use_storno_accounting": True,
            "display_invoice_amount_total_words": True,
        }

    @template("ru", "res.company")
    def _get_ru_res_company(self):
        return {
            self.env.company.id: {
                "anglo_saxon_accounting": True,
                "account_fiscal_country_id": "base.ru",
                "bank_account_code_prefix": "51.",
                "cash_account_code_prefix": "50.",
                "transfer_account_code_prefix": "57.",
                "account_default_pos_receivable_account_id": "ru_acc_62_P",
                "income_currency_exchange_account_id": "ru_acc_91_01",
                "expense_currency_exchange_account_id": "ru_acc_91_02",
                "default_cash_difference_income_account_id": "ru_acc_91_01",
                "default_cash_difference_expense_account_id": "ru_acc_91_02",
                "account_journal_early_pay_discount_loss_account_id": "ru_acc_76_05",
                "account_journal_early_pay_discount_gain_account_id": "ru_acc_76_05",
                "account_sale_tax_id": "tax_vat_20_sale_included",
                "account_purchase_tax_id": "tax_vat_20_purchase_included",
                "account_journal_suspense_account_id": "ru_acc_51_00_00",
                "account_journal_payment_debit_account_id": "ru_acc_51_00_62",
                "account_journal_payment_credit_account_id": "ru_acc_51_00_60",
                "transfer_account_id": "ru_acc_57_01",
            },
        }
