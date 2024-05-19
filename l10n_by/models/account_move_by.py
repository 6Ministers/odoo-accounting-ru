# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2024 Digital-autoparts

from contextlib import contextmanager

from odoo import api, models
from odoo.tools import frozendict


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends(
        "line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.balance",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        "line_ids.payment_id.state",
        "line_ids.full_reconcile_id",
        "state",
    )
    def _compute_amount(self):
        if self.env.company.chart_template != "by":
            return super()._compute_amount()
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0
            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type == "tax" or (
                        line.display_type == "rounding" and line.tax_repartition_line_id
                    ):
                        # Tax amount.
                        # Суммируем значения НДС всех "tax"-line, для всех проводок,
                        # кроме нами созданной 90.2
                        if (
                            self.env.ref(
                                f"""account.{self.env.company.id}_{"by_900200"}"""
                            ).id
                            != line.account_id.id
                            # and line.move_type in ("out_invoice", "in_invoice")
                        ):
                            total_tax += line.balance
                            total_tax_currency += line.amount_currency

                        # Skeep add tax to balance in some cases
                        # Суммируем total и total_currency только для документов
                        # "in_invoice", т.к. в них не вносились изменения в
                        # учёт НДС. т.о. исключаем сумму созданной встречной
                        # проводки по НДС (90.2) из общей суммы в документах
                        # типа "исходящий инвойс" и др.
                        if line.move_type == "in_invoice":
                            total += line.balance
                            total_currency += line.amount_currency
                    elif line.display_type in ("product", "rounding"):
                        # В связи с тем, что у нас в проводке продукта
                        # указывается цена с НДС, нам для корректного
                        # расчета цены без налога необходимо вычесть
                        # из общего баланса записи(линии) сумму налогов.
                        if (
                            self.env.ref(
                                f"""account.{self.env.company.id}_{"by_900101"}"""
                            ).id
                            == line.account_id.id
                        ):
                            __, tax_values_list = self.env[
                                "account.tax"
                            ]._compute_taxes_for_single_line(
                                line._convert_to_tax_base_line_dict()
                            )
                            final_line_balance = 0
                            final_amount_currency = 0
                            tax_amount = 0
                            tax_amount_currency = 0
                            if tax_values_list:
                                tax_amount = sum(
                                    [
                                        tax_item["tax_amount"]
                                        for tax_item in tax_values_list
                                    ]
                                )
                                tax_amount_currency = sum(
                                    [
                                        tax_item["tax_amount_currency"]
                                        for tax_item in tax_values_list
                                    ]
                                )
                            if line.balance < 0:
                                final_line_balance = line.balance + tax_amount
                                final_amount_currency = (
                                    line.amount_currency + tax_amount_currency
                                )
                            else:
                                final_line_balance = line.balance - tax_amount
                                final_amount_currency = (
                                    line.amount_currency - tax_amount_currency
                                )
                            total_untaxed += final_line_balance
                            total_untaxed_currency += final_amount_currency
                        else:
                            total_untaxed += line.balance
                            total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == "payment_term":
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency
            sign = move.direction_sign
            move.amount_untaxed = sign * total_untaxed_currency
            move.amount_tax = sign * total_tax_currency
            move.amount_total = sign * total_currency
            move.amount_residual = -sign * total_residual_currency
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = (
                abs(total) if move.move_type == "entry" else -total
            )
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = (
                abs(move.amount_total)
                if move.move_type == "entry"
                else -(sign * move.amount_total)
            )

    def add_account_line_by(self, res):
        """добавляем ещё одну проводку для баланса учёта НДС (=90.2)"""
        res1 = {}
        for k in res:
            if (
                "account_id" in k
                and k["account_id"]
                == self.env.ref(f"""account.{self.env.company.id}_{"by_680201"}""").id
            ):
                k_new = dict(k.copy())
                k_new["account_id"] = self.env.ref(
                    f"""account.{self.env.company.id}_{"by_900200"}"""
                ).id
                v_new = dict(res[k])
                if "balance" in res[k]:
                    v_new["balance"] = v_new["balance"] * -1
                    v_new["amount_currency"] = v_new["amount_currency"] * -1
                res1[frozendict(k_new)] = v_new
        for k, v in res1.items():
            res[k] = v
        return res

    @contextmanager
    def _sync_dynamic_line_contextmanager(  # noqa
        self,
        existing_key_fname,
        needed_vals_fname,
        needed_dirty_fname,
        line_type,
        container,
    ):
        def existing():
            variable = {
                line[existing_key_fname]: line
                for line in container["records"].line_ids
                if line[existing_key_fname]
            }
            return variable

        def needed():
            res = {}
            for computed_needed in container["records"].mapped(needed_vals_fname):
                if computed_needed is False:
                    continue  # there was an invalidation,
                    # let's hope nothing needed to be changed...
                for key, values in computed_needed.items():
                    if key not in res:
                        res[key] = dict(values)
                    else:
                        ignore = True
                        for fname in res[key]:
                            if (
                                self.env["account.move.line"]._fields[fname].type
                                == "monetary"
                            ):
                                res[key][fname] += values[fname]
                                if res[key][fname]:
                                    ignore = False
                        if ignore:
                            del res[key]

            # Convert float values to their "ORM cache" one to
            # prevent different rounding calculations
            for dict_key in res:
                move_id = dict_key.get("move_id")
                if not move_id:
                    continue
                record = self.env["account.move"].browse(move_id)
                for fname, current_value in res[dict_key].items():
                    field = self.env["account.move.line"]._fields[fname]
                    if isinstance(current_value, float):
                        new_value = field.convert_to_cache(current_value, record)
                        res[dict_key][fname] = new_value

            # при формировании tax_key проводок, добавляем
            # дополнительную проводку (НДС с продаж на 90.2)
            # вызываем доп.функцию для формирования проводки
            # это зеркальная проводка для существующей с 68.2
            if existing_key_fname == "tax_key":
                res = self.add_account_line_by(res)

            return res

        def dirty():
            *path, dirty_fname = needed_dirty_fname.split(".")
            eligible_recs = container["records"].mapped(".".join(path))
            if eligible_recs._name == "account.move.line":
                eligible_recs = eligible_recs.filtered(
                    lambda line: line.display_type != "cogs"
                )
            dirty_recs = eligible_recs.filtered(dirty_fname)
            return dirty_recs, dirty_fname

        existing_before = existing()
        needed_before = needed()
        dirty_recs_before, dirty_fname = dirty()
        dirty_recs_before[dirty_fname] = False
        yield
        dirty_recs_after, dirty_fname = dirty()
        if dirty_recs_before and not dirty_recs_after:  # TODO improve filter
            return
        existing_after = existing()
        needed_after = needed()

        # Filter out deleted lines from `needed_before` to not
        # recompute lines if not necessary or wanted
        line_ids = set(
            self.env["account.move.line"]
            .browse(k["id"] for k in needed_before if "id" in k)
            .exists()
            .ids
        )
        needed_before = {
            k: v
            for k, v in needed_before.items()
            if "id" not in k or k["id"] in line_ids
        }

        # old key to new key for the same line
        inv_existing_before = {v: k for k, v in existing_before.items()}
        inv_existing_after = {v: k for k, v in existing_after.items()}
        before2after = {
            before: inv_existing_after[bline]
            for bline, before in inv_existing_before.items()
            if bline in inv_existing_after
        }

        if needed_after == needed_before:
            return

        to_delete = [
            line.id
            for key, line in existing_before.items()
            if key not in needed_after
            and key in existing_after
            and before2after[key] not in needed_after
        ]
        to_delete_set = set(to_delete)
        to_delete.extend(
            line.id
            for key, line in existing_after.items()
            if key not in needed_after and line.id not in to_delete_set
        )
        to_create = {
            key: values
            for key, values in needed_after.items()
            if key not in existing_after
        }
        to_write = {
            existing_after[key]: values
            for key, values in needed_after.items()
            if key in existing_after
            and any(
                self.env["account.move.line"]
                ._fields[fname]
                .convert_to_write(existing_after[key][fname], self)
                != values[fname]
                for fname in values
            )
        }

        while to_delete and to_create:
            key, values = to_create.popitem()
            line_id = to_delete.pop()
            self.env["account.move.line"].browse(line_id).write(
                {**key, **values, "display_type": line_type}
            )
        if to_delete:
            self.env["account.move.line"].browse(to_delete).with_context(
                dynamic_unlink=True
            ).unlink()
        if to_create:
            self.env["account.move.line"].create(
                [
                    {**key, **values, "display_type": line_type}
                    for key, values in to_create.items()
                ]
            )
        if to_write:
            for line, values in to_write.items():
                line.write(values)

    def _sync_dynamic_line(
        self,
        existing_key_fname,
        needed_vals_fname,
        needed_dirty_fname,
        line_type,
        container,
    ):
        # проверка на используемый в компании план счетов.
        # Т.к. родная функция задекорирована контекст-менеджером,
        # вызываем её из этой функции, а не напрямую.
        if self.env.company.chart_template != "by":
            return super()._sync_dynamic_line(
                existing_key_fname,
                needed_vals_fname,
                needed_dirty_fname,
                line_type,
                container,
            )
        else:
            return self._sync_dynamic_line_contextmanager(
                existing_key_fname,
                needed_vals_fname,
                needed_dirty_fname,
                line_type,
                container,
            )

    # При изменении статуса документа с проводками на draft, отключена проверка,
    # которая запрещает в ранее проведённом документе изменить журнал.
    # Последствия отмены проверки до конца не изучены.
    def button_draft(self):
        if self.env.company.chart_template != "by":
            return super().button_draft()
        res = super().button_draft()
        self.write(
            {
                "posted_before": False,
                "name": "/",
            }
        )
        return res
