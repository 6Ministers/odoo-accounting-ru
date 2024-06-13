# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models


def _l10n_ru_stock_post_init_hook(env):
    _init_product_category(env)


def _init_product_category(env):
    for company in env["res.company"].search(
        [("account_fiscal_country_id.code", "=", "RU")]
    ):
        account_chart_template = env["account.chart.template"].with_company(company)
        categories = account_chart_template._get_ru_product_category()
        for xmlid in categories:
            values = categories[xmlid]
            to_write = {}
            for value in values.items():
                deref_value = account_chart_template.ref(
                    value[1], raise_if_not_found=False
                )
                to_write[value[0]] = deref_value or value[1]
            env.ref(xmlid).with_company(company).write(to_write)
