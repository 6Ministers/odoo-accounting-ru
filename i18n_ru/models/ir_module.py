import logging
import os

from odoo import api, models
from odoo.modules import get_module_path
from odoo.tools.translate import TranslationImporter, get_po_paths

_logger = logging.getLogger(__name__)

modelname = os.path.basename(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.model
    def _load_module_terms(self, modules, langs, overwrite=False):
        if modelname not in modules:
            return super()._load_module_terms(modules, langs, overwrite=overwrite)
        # load i18n files
        translation_importer = TranslationImporter(self.env.cr, verbose=False)
        for module_name in modules:
            modpath = get_module_path(module_name)
            if not modpath:
                continue
            for lang in langs:
                po_paths = get_po_paths(module_name, lang)
                for po_path in po_paths:
                    _logger.info(
                        "module %s: loading translation file %s for language %s",
                        module_name,
                        po_path,
                        lang,
                    )
                    translation_importer.load_file(po_path, lang)
                if lang != "en_US" and not po_paths:
                    _logger.info(
                        "module %s: no translation for language %s", module_name, lang
                    )

        translation_importer.save(overwrite=overwrite, force_overwrite=overwrite)
