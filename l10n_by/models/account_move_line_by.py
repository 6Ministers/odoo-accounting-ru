# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2024 Digital-autoparts

from contextlib import contextmanager

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @contextmanager
    def _sync_invoice_contextmanager(self, container):
        if container["records"].env.context.get("skip_invoice_line_sync"):
            yield
            return  # avoid infinite recursion

        def existing():
            return {
                line: {
                    "amount_currency": line.currency_id.round(line.amount_currency),
                    "balance": line.company_id.currency_id.round(line.balance),
                    "currency_rate": line.currency_rate,
                    "price_subtotal": line.currency_id.round(line.price_subtotal),
                    "move_type": line.move_id.move_type,
                }
                for line in container["records"]
                .with_context(
                    skip_invoice_line_sync=True,
                )
                .filtered(lambda line: line.move_id.is_invoice(True))
            }

        def changed(fname):
            return line not in before or before[line][fname] != after[line][fname]

        before = existing()
        yield
        after = existing()
        for line in after:
            if line.display_type == "product" and (
                not changed("amount_currency") or line not in before
            ):
                # change price line.price_subtotal to line.price_total
                # (sell_price + VAT in invoice)
                # в исходящих инвойсах для проводк с параметром
                # display_type = 'product' (90.1), меняем расчёт
                # amount_currency т.к. на 90.1 д.б. сумма продажи
                # с НДС, а в оригинале стоит сумма продажи без НДС
                if line.move_type == "out_invoice":
                    amount_currency = (
                        line.move_id.direction_sign
                        * line.currency_id.round(line.price_total)
                    )
                else:
                    amount_currency = (
                        line.move_id.direction_sign
                        * line.currency_id.round(line.price_subtotal)
                    )
                if line.amount_currency != amount_currency or line not in before:
                    line.amount_currency = amount_currency
                if line.currency_id == line.company_id.currency_id:
                    line.balance = amount_currency

        after = existing()
        for line in after:
            if (
                changed("amount_currency")
                or changed("currency_rate")
                or changed("move_type")
            ) and (not changed("balance") or (line not in before and not line.balance)):  # noqa
                balance = line.company_id.currency_id.round(
                    line.amount_currency / line.currency_rate
                )
                line.balance = balance

        # Since this method is called during the sync, inside of
        # `create`/`write`, these fields already have been computed
        # and marked as so. But this method should re-trigger it since
        # it changes the dependencies.
        self.env.add_to_compute(self._fields["debit"], container["records"])
        self.env.add_to_compute(self._fields["credit"], container["records"])

    def _sync_invoice(self, container):
        if self.env.company.chart_template != "by":
            return super()._sync_invoice(container)
        else:
            return self._sync_invoice_contextmanager(container)
