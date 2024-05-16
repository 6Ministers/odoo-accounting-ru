# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UoM(models.Model):
    _inherit = "uom.uom"

    # Работа над единицами измерения проведена согласно данной таблице
    # https://pravo.by/document/?guid=3871&p0=F92000346

    # Код
    code = fields.Char(
        string="Code of Utits",
        help="Code Utits of Measure by EuroAsia Economic Ution",
    )
    # Международный код
    code_international = fields.Char(
        string="Code of Utits International",
        help="Code of Utits International",
    )

    # Наименование на английском языке
    full_name = fields.Char(
        string="Name of Utits EN",
        help="Name of Units in English Language",
    )
