# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2024 Digital-autoparts

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class PosSession(models.Model):
    _inherit = "pos.session"

    def _create_non_reconciliable_move_lines(self, data):
        # Create account.move.line records for
        #   - sales
        #   - taxes
        #   - stock expense
        #   - non-cash split receivables (not for automatic reconciliation)
        #   - non-cash combine receivables (not for automatic reconciliation)
        #   + добавляем сумму НДС на 90.1.1
        #   + добавляем встречную проводку по НДС: 90.2 - 68.2.1

        if self.env.company.chart_template != "by":
            return super()._create_non_reconciliable_move_lines(self, data)

        taxes = data.get("taxes")
        sales = data.get("sales")
        stock_expense = data.get("stock_expense")
        rounding_difference = data.get("rounding_difference")
        MoveLine = data.get("MoveLine")

        # sales = данные о продажах, корректируем amount = |amount+НДС|
        # для формирования на 90.1.1 суммы выручки с НДС
        for item in sales:
            sales[item]["amount"] = sales[item]["amount"] - sales[item]["tax_amount"]
            sales[item]["amount_converted"] = (
                sales[item]["amount_converted"] - sales[item]["tax_amount"]
            )

        tax_vals = [
            self._get_tax_vals(
                key,
                amounts["amount"],
                amounts["amount_converted"],
                amounts["base_amount_converted"],
            )
            for key, amounts in taxes.items()
        ]
        # Check if all taxes lines have account_id assigned. If not, there are
        # repartition lines of the tax that have no account_id.

        # добавляем набор данных для формирования встречной проводки 90.2 - 68.2.1
        for element in tax_vals:
            if (
                element.get("account_id", 0)
                == self.env.ref(f"""account.{self.env.company.id}_{"by_680201"}""").id
            ):
                new_taxline = {}
                for key, value in element.items():
                    new_taxline[key] = value
                    if key == "account_id":
                        new_taxline[key] = self.env.ref(
                            f"""account.{self.env.company.id}_{"by_900200"}"""
                        ).id
                new_taxline["credit"] = element["debit"]
                new_taxline["debit"] = element["credit"]
                tax_vals.append(new_taxline)

        tax_names_no_account = [
            line["name"] for line in tax_vals if not line["account_id"]
        ]
        if tax_names_no_account:
            raise UserError(
                _(
                    "Unable to close and validate the session.\n"
                    "Please set corresponding tax account in each"
                    " repartition line of the following taxes: \n%s",
                    ", ".join(tax_names_no_account),
                )
            )
        rounding_vals = []

        if not float_is_zero(
            rounding_difference["amount"], precision_rounding=self.currency_id.rounding
        ) or not float_is_zero(
            rounding_difference["amount_converted"],
            precision_rounding=self.currency_id.rounding,
        ):
            rounding_vals = [
                self._get_rounding_difference_vals(
                    rounding_difference["amount"],
                    rounding_difference["amount_converted"],
                )
            ]

        MoveLine.create(tax_vals)
        move_line_ids = MoveLine.create(
            [
                self._get_sale_vals(key, amounts["amount"], amounts["amount_converted"])
                for key, amounts in sales.items()
            ]
        )
        for key, ml_id in zip(sales.keys(), move_line_ids.ids, strict=False):
            sales[key]["move_line_id"] = ml_id
        MoveLine.create(
            [
                self._get_stock_expense_vals(
                    key, amounts["amount"], amounts["amount_converted"]
                )
                for key, amounts in stock_expense.items()
            ]
            + rounding_vals
        )
        return data
