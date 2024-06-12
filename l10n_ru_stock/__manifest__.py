# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Russia - Accounting - Stock",
    "icon": "/account/static/description/l10n.png",
    "countries": ["ru"],
    "author": "Iterra-IT",
    "website": "https://github.com/6Ministers/odoo-accounting-ru",
    "version": "17.0.1.0.1",
    "summary": """
Russia - Chart of accounts with stock.
======================================
    """,
    "category": "Accounting/Localizations/Account Charts",
    "depends": [
        "l10n_ru",
        "stock_account",
    ],
    "data": [
        "data/product_category.xml",
    ],
    "demo": [],
    "license": "LGPL-3",
    "post_init_hook": "_l10n_ru_stock_post_init_hook",
}
