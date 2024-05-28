# This is monkeypatch for changing default get_po_paths function
# from odoo.tools.translate import get_po_paths

import sys
import os
import re
from contextlib import suppress
from os.path import join
from pathlib import Path

from odoo.tools.misc import file_path


dir_path = os.path.dirname(os.path.realpath(__file__))
po_files_dir = os.path.join(dir_path, "po_files")
list_of_supported_modules = [
    Path(file_name).stem for file_name in os.listdir(po_files_dir)
]


def get_po_paths_fixed(module_name: str, lang: str):
    lang_base = lang.split("_")[0]
    if lang_base == "es" and lang != "es_ES":
        # force es_419 as fallback language for the spanish variations
        if lang == "es_419":
            langs = ["es_419"]
        else:
            langs = ["es_419", lang]
    else:
        langs = [lang_base, lang]

    po_paths = [
        path
        for lang_ in langs
        for dir_ in ("i18n", "i18n_extra")
        if (path := join(module_name, dir_, lang_ + ".po"))
    ]
    for path in po_paths:
        if module_name in list_of_supported_modules and lang_base.strip() == "ru":
            path = join(po_files_dir, module_name + ".po")
        with suppress(FileNotFoundError):
            yield file_path(path)


def _push_translation_fixed(
    self, module, ttype, name, res_id, source, comments=None, record_id=None, value=None
):
    """Insert a translation that will be used in the file generation
    In po file will create an entry
    #: <ttype>:<name>:<res_id>
    #, <comment>
    msgid "<source>"
    record_id is the database id of the record being translated
    """
    # empty and one-letter terms are ignored, they probably are not meant to be
    # translated, and would be very hard to translate anyway.

    sanitized_term = (source or "").strip()
    # remove non-alphanumeric chars
    sanitized_term = re.sub(r"\W+", "", sanitized_term)
    if not sanitized_term or len(sanitized_term) < 1:
        return
    self._to_translate.append(
        (module, source, name, res_id, ttype, tuple(comments or ()), record_id, value)
    )


module = sys.modules["odoo.addons.base.models.ir_module"]
module.get_po_paths = get_po_paths_fixed

module = sys.modules["odoo.tools.translate"]
module.get_po_paths = get_po_paths_fixed

module = sys.modules["odoo.tools.translate"]
module.TranslationReader._push_translation = _push_translation_fixed


from . import models  # noqa
