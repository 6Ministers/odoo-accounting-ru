# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2024 Digital-autoparts

from collections import defaultdict

from odoo import _, api, models
from odoo.tools.misc import formatLang


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.model
    def _prepare_tax_totals(
        self, base_lines, currency, tax_lines=None, is_company_currency_requested=False
    ):
        """Compute the tax totals details for the business documents.
        :param base_lines:  A list of python dictionaries created using the '
                            _convert_to_tax_base_line_dict' method.
        :param currency:    The currency set on the business document.
        :param tax_lines:   Optional list of python dictionaries created using the
                            '_convert_to_tax_line_dict' method. If specified,
                            the taxes will be recomputed using them instead of
                            recomputing the taxes on the provided base lines.
        :param is_company_currency_requested :  Optional boolean which indicates
                            whether or not the company currency is
                            requested from the function. This can typically be
                            used when using an invoice in foreign currency
                            and the company currency is required.

        :return: A dictionary in the following form:
            {
                'amount_total': The total amount to be displayed
                                on the document, including every total
                                types.
                'amount_untaxed':   The untaxed amount to be displayed on the document.
                'formatted_amount_total':   Same as amount_total, but as a
                                string formatted accordingly with
                                partner's locale.
                'formatted_amount_untaxed': Same as amount_untaxed, but
                                as a string formatted accordingly with
                                partner's locale.
                'groups_by_subtotals': A dictionary formed liked
                                {'subtotal': groups_data}
                                Where total_type is a subtotal name defined
                                on a tax group, or the
                                default one: 'Untaxed Amount'.
                                And groups_data is a list of dict in the
                                following form:
                    {
                        'tax_group_name':   The name of the tax
                                groups this total is made for.
                        'tax_group_amount': The total tax amount in this tax group.
                        'tax_group_base_amount':    The base amount for this tax group.
                        'formatted_tax_group_amount':   Same as tax_group_amount,
                                but as a string formatted accordingly
                                with partner's locale.
                        'formatted_tax_group_base_amount':  Same as
                                tax_group_base_amount, but as a string formatted
                                accordingly with partner's locale.
                        'tax_group_id': The id of the tax group corresponding to
                                this dict.
                        'tax_group_base_amount_company_currency':   OPTIONAL:
                                the base amount of the tax group expressed in
                                the company currency when the parameter
                                is_company_currency_requested is True
                        'tax_group_amount_company_currency':
                                OPTIONAL: the tax amount of the tax group expressed in
                                the company currency when the parameter
                                is_company_currency_requested is True
                    }
                'subtotals':    A list of dictionaries in the following form,
                                one for each subtotal in
                                'groups_by_subtotals' keys.
                    {
                        'name': The name of the subtotal
                        'amount':   The total amount for this subtotal,
                                summing all the tax groups
                                belonging to preceding subtotals and the base amount
                        'formatted_amount': Same as amount, but as a string
                                formatted accordingly with partner's locale.
                        'amount_company_currency':
                                OPTIONAL: The total amount in company currency when the
                                parameter is_company_currency_requested is True
                    }
                'subtotals_order': A list of keys of `groups_by_subtotals`
                                defining the order in which it needs
                                to be displayed
            }
        """
        if self.env.company.chart_template != "by":
            return super()._prepare_tax_totals(base_lines, currency, tax_lines=None)

        # ==== Compute the taxes ====
        to_process = []
        for base_line in base_lines:
            to_update_vals, tax_values_list = self._compute_taxes_for_single_line(
                base_line
            )
            to_process.append((base_line, to_update_vals, tax_values_list))

        def grouping_key_generator(base_line, tax_values):
            source_tax = tax_values["tax_repartition_line"].tax_id
            return {"tax_group": source_tax.tax_group_id}

        global_tax_details = self._aggregate_taxes(
            to_process, grouping_key_generator=grouping_key_generator
        )

        tax_group_vals_list = []
        for tax_detail in global_tax_details["tax_details"].values():
            tax_group_vals = {
                "tax_group": tax_detail["tax_group"],
                "base_amount": tax_detail["base_amount_currency"],
                "tax_amount": tax_detail["tax_amount_currency"],
            }
            if is_company_currency_requested:
                tax_group_vals["base_amount_company_currency"] = tax_detail[
                    "base_amount"
                ]
                tax_group_vals["tax_amount_company_currency"] = tax_detail["tax_amount"]

            # Handle a manual edition of tax lines.
            # Add a check to the Belarusian chart of accounts
            # Добавляем проверку на наличие проводок по 90.2 и исключаем
            # их из общей суммы долга по инвойсу
            # иначе в сумме долга задвоится НДС
            if tax_lines is not None:
                matched_tax_lines = [
                    x
                    for x in tax_lines
                    if x["tax_repartition_line"].tax_id.tax_group_id
                    == tax_detail["tax_group"]
                    and x["account"].code
                    != self.env.ref(
                        f"""account.{self.env.company.id}_{"by_900200"}"""
                    ).code
                ]
                if matched_tax_lines:
                    tax_group_vals["tax_amount"] = sum(
                        x["tax_amount"] for x in matched_tax_lines
                    )
            tax_group_vals_list.append(tax_group_vals)

        tax_group_vals_list = sorted(
            tax_group_vals_list,
            key=lambda x: (x["tax_group"].sequence, x["tax_group"].id),
        )
        # ==== Partition the tax group values by subtotals ====

        amount_untaxed = global_tax_details["base_amount_currency"]
        amount_tax = 0.0

        amount_untaxed_company_currency = global_tax_details["base_amount"]
        amount_tax_company_currency = 0.0

        subtotal_order = {}
        groups_by_subtotal = defaultdict(list)
        for tax_group_vals in tax_group_vals_list:
            tax_group = tax_group_vals["tax_group"]

            subtotal_title = tax_group.preceding_subtotal or _("Untaxed Amount")
            sequence = tax_group.sequence

            subtotal_order[subtotal_title] = min(
                subtotal_order.get(subtotal_title, float("inf")), sequence
            )
            groups_by_subtotal[subtotal_title].append(
                {
                    "group_key": tax_group.id,
                    "tax_group_id": tax_group.id,
                    "tax_group_name": tax_group.name,
                    "tax_group_amount": tax_group_vals["tax_amount"],
                    "tax_group_base_amount": tax_group_vals["base_amount"],
                    "formatted_tax_group_amount": formatLang(
                        self.env, tax_group_vals["tax_amount"], currency_obj=currency
                    ),
                    "formatted_tax_group_base_amount": formatLang(
                        self.env, tax_group_vals["base_amount"], currency_obj=currency
                    ),
                }
            )
            if is_company_currency_requested:
                groups_by_subtotal[subtotal_title][-1][
                    "tax_group_amount_company_currency"
                ] = tax_group_vals["tax_amount_company_currency"]
                groups_by_subtotal[subtotal_title][-1][
                    "tax_group_base_amount_company_currency"
                ] = tax_group_vals["base_amount_company_currency"]

        # ==== Build the final result ====

        subtotals = []
        for subtotal_title in sorted(
            subtotal_order.keys(), key=lambda k: subtotal_order[k]
        ):
            amount_total = amount_untaxed + amount_tax
            subtotals.append(
                {
                    "name": subtotal_title,
                    "amount": amount_total,
                    "formatted_amount": formatLang(
                        self.env, amount_total, currency_obj=currency
                    ),
                }
            )
            if is_company_currency_requested:
                subtotals[-1]["amount_company_currency"] = (
                    amount_untaxed_company_currency + amount_tax_company_currency
                )
                amount_tax_company_currency += sum(
                    x["tax_group_amount_company_currency"]
                    for x in groups_by_subtotal[subtotal_title]
                )

            amount_tax += sum(
                x["tax_group_amount"] for x in groups_by_subtotal[subtotal_title]
            )

        amount_total = amount_untaxed + amount_tax

        display_tax_base = (
            len(global_tax_details["tax_details"]) == 1
            and currency.compare_amounts(
                tax_group_vals_list[0]["base_amount"], amount_untaxed
            )
            != 0
        ) or len(global_tax_details["tax_details"]) > 1

        return {
            "amount_untaxed": currency.round(amount_untaxed)
            if currency
            else amount_untaxed,
            "amount_total": currency.round(amount_total) if currency else amount_total,
            "formatted_amount_total": formatLang(
                self.env, amount_total, currency_obj=currency
            ),
            "formatted_amount_untaxed": formatLang(
                self.env, amount_untaxed, currency_obj=currency
            ),
            "groups_by_subtotal": groups_by_subtotal,
            "subtotals": subtotals,
            "subtotals_order": sorted(
                subtotal_order.keys(), key=lambda k: subtotal_order[k]
            ),
            "display_tax_base": display_tax_base,
        }
