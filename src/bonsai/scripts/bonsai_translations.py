try:
    import bpy

    # Ensure it's not fake-bpy-module.
    if not hasattr(bpy, "context"):
        raise ModuleNotFoundError
    import bl_i18n_utils
    import addon_utils

    BPY_IS_LOADED = True
except ModuleNotFoundError:
    BPY_IS_LOADED = False

import shutil
import tempfile
import importlib
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

bl_info = {
    "name": "Bonsai Translations",
    "description": "",
    "author": "IfcOpenShell Contributors",
    "blender": (2, 80, 0),
    "version": (0, 0, 999999),
    "location": "Properties -> Render -> BBIM Update Translation",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "System",
}

# NOTE: list of available languages in Blender can be retrieved
# by the command below:
# bpy.context.preferences.view.language = "test"
ADDON_NAME = "bonsai"
TRANSLATION_UI_IS_LOADED = False


def is_addon_loaded(addon_name) -> bool:
    loaded_default, loaded_state = addon_utils.check(addon_name)
    return loaded_state


def get_branches_directory():
    return Path(bpy.context.preferences.filepaths.i18n_branches_directory)


def get_addon_directory() -> Path:
    addon_module = importlib.import_module(ADDON_NAME)
    return Path(addon_module.__file__).parent


def rearrange_files_for_po_import(po_dir_path: Path, temp_directory: tempfile.TemporaryDirectory):
    """I18n directory also has a bit different format then `ui_translate.export/import`,
    every .po file has a parent folder with the same name.
    So we rearrange the data that way"""
    # NOTE: TemporaryDirectory is cleared automatically as variable goes out of scope
    # so we expect it as an argument so it won't get cleared right away

    temp_po_dir_path = Path(temp_directory.name)
    for file in po_dir_path.glob("**/*"):
        if file.suffix != ".po":
            continue
        shutil.copy(file, temp_po_dir_path / file.name)


@dataclass
class Message:
    msgid: str
    msgctxt: str | None
    sources: Optional[List[str]] = field(default_factory=list)
    # mapping languages to translated strings
    translations: Optional[Dict[str, str]] = field(default_factory=dict)


def bonsai_strings_parse(addon_directory=None, po_directory=None):
    # NOTE: we decided to use our own parser due bug in Blender parser
    # as it tends to pick up strings from other addons and other Blender parts
    # and this bug probably would be to low of a priority for Blender to fix
    # ref: https://projects.blender.org/blender/blender/issues/116579

    if addon_directory is None:
        addon_directory = get_addon_directory()
    directory = addon_directory / "bim"

    if po_directory is None:
        po_directory = get_branches_directory()

    patterns = [
        r'bl_label\s*=\s*"(.*)"',  # operator labels
        r'bl_description\s*=\s*"(.*)"',  # operator descriptions
        r'text\s*=\s*"(.*?)"',  # UI labels
        r'Property\(.*?name\s*=\s*"(.*?)"',  # property names
        r'report\(\{.*?\}\s*,\s*"(.*?)"',  # operator reports
        r'info\(\{.*?\}\s*,\s*"(.*?)"',  # operator info
        r'\b_\("(.*?)"\)',  # gettext called with `_`
    ]
    regexes = [re.compile(pattern) for pattern in patterns]
    matched_dict: Dict[str, Message] = dict()

    # NOTE: currently there is no special handling same message with different contexts
    for root, dirs, files in os.walk(directory):
        root = Path(root)
        for file in files:
            if not file.endswith(".py"):
                continue
            filepath = root / file
            source_rel_path = filepath.relative_to(addon_directory).as_posix()
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                for i, regex in enumerate(regexes):
                    # NOTE: operator tooltips doesnt seem to need Operator context
                    is_operator = i < 1
                    for regex_match in regex.finditer(content):
                        string = regex_match.group(1)
                        if string == "":
                            continue
                        elif "{" in string:
                            # Includes a formatting string. To fix.
                            # print(match.group(1))
                            continue
                        elif is_operator:
                            ctx = "Operator"
                        else:
                            ctx = None
                        message = matched_dict.get(string)
                        if message is None:
                            message = Message(string, ctx)
                            matched_dict[string] = message
                        elif ctx != message.msgctxt and False:
                            print(
                                f'WARNING. Message "{string}" was already registered with different context {message.context}. '
                                f"Current context: {ctx}. File: {source_rel_path}"
                            )
                        message.sources.append(source_rel_path)

    pot_filepath = po_directory / "bonsai.pot"
    with open(pot_filepath, "w", encoding="utf-8") as fo:
        for msg in matched_dict.values():
            # make sure sources are unique but keep the order
            sources = list(dict.fromkeys(msg.sources))
            for source in sources:
                fo.write(f"#: {source}\n")
            if msg.msgctxt != None:
                fo.write(f'msgctxt "{msg.msgctxt}"\n')
            fo.write(f'msgid "{msg.msgid}"\n')
            fo.write('msgstr ""\n')
            fo.write("\n")


def update_translations_from_po(po_directory: Path, translations_module: Path):
    translation_data: Dict[str, Message] = dict()

    def process_po_entry(language, current_chunk: list[str]):
        sources = []
        msgid = None
        msgstr = None
        msgctxt = None
        parse_message_attr = lambda line, attr_name: line.removeprefix(f'{attr_name} "').removesuffix('"')

        for line in current_chunk:
            line = line.strip()
            if line.startswith('msgid "'):
                msgid = parse_message_attr(line, "msgid")
            elif line.startswith('msgstr "'):
                msgstr = parse_message_attr(line, "msgstr")
            elif line.startswith('msgctxt "'):
                msgctxt = parse_message_attr(line, "msgctxt")
            elif line.startswith("#:"):
                sources.append(line.removeprefix("# ").strip())

        msg = translation_data.get(msgid)
        if msg is None:
            msg = Message(msgid, msgctxt, sources, {language: msgstr})
            translation_data[msgid] = msg
        else:
            msg.sources.extend(sources)
            msg.translations[language] = msgstr

    # load data from .po files
    langs = set()
    for po_file_path in po_directory.glob("**/*.po"):
        lang = po_file_path.stem
        langs.add(lang)
        with open(po_file_path, "r") as po_file:
            current_chunk = []
            for line in po_file:
                current_chunk.append(line)
                if line.startswith("msgstr"):
                    process_po_entry(lang, current_chunk)
                    current_chunk = []

    # generate translations.py file
    tab = "    "
    default_context = "*"
    ret = ["translations_dict = {"]

    for lang in langs:
        ret.append(f'{tab}"{lang}": {{')
        for msgid, msg in translation_data.items():
            if (msgstr := msg.translations[lang]) in (None, ""):
                continue
            msgctxt = msg.msgctxt
            if not msgctxt:
                msgctxt = default_context
            ret.append(f"{tab*2}({msgctxt!r}, {msgid!r}): {msgstr!r},")
        ret.append(f"{tab}}},")

    ret.append("}")

    with open(translations_module / "translations.py", "w") as fo:
        fo.write("\n".join(ret))


if BPY_IS_LOADED:

    class SetupTranslationUI(bpy.types.Operator):
        bl_idname = "bim.setup_translation_ui"
        bl_label = "Setup Translation UI"
        bl_options = set()

        def execute(self, context):
            if not is_addon_loaded("ui_translate"):
                addon_utils.enable("ui_translate", default_set=True)
                self.report({"INFO"}, '"Manage UI translations" addon was not enabled, it\'s enabled now.')

            addon_prefs = context.preferences.addons["ui_translate"].preferences

            def is_valid_path(path: Path):
                return path.is_dir() and path.is_absolute()

            # check branches directory
            branches_dir = get_branches_directory()
            if not is_valid_path(branches_dir):
                raise Exception(
                    f"I18n Branches directory is not set up or doesn't exist ({branches_dir}).\n"
                    "Setup I18n branches directory below (or in Preferences > File Paths > Development > I18n Branches) "
                    "to a folder containing (or that will contain) .po files."
                )

            # check translations directory
            i18n_dir = Path(addon_prefs.I18N_DIR)
            # we won't really use the translations directory, we just need addon to stop complaining about it
            if not is_valid_path(i18n_dir):
                addon_prefs.I18N_DIR = str(branches_dir)
                self.report(
                    {"INFO"},
                    f'Translations directory ({i18n_dir}) doesn\'t exist. It was reset to I18n branches directory: "{branches_dir}"',
                )

            # check source directory
            source_dir = Path(addon_prefs.SOURCE_DIR)
            default_source_path = Path(bpy.app.binary_path).parent / ".".join([str(i) for i in bpy.app.version[:2]])

            if not is_valid_path(source_dir):
                addon_prefs.SOURCE_DIR = str(default_source_path)
                self.report(
                    {"INFO"},
                    f'Source directory ({source_dir}) doesn\'t exist. It was reset to default directory: "{default_source_path}"',
                )
                source_dir = default_source_path

            source_locale_path = source_dir / "locale/po"
            # Blender UI translations also expect "scripts/presets/keyconfig" to be present in SOURCE_DIR
            # but default directory has it by default
            if not source_locale_path.is_dir():
                source_locale_path.mkdir(parents=True, exist_ok=True)
                self.report(
                    {"INFO"},
                    f"Couldn't find locale path in the source directory, creating dummy directory: {source_locale_path}.",
                )

            from ui_translate.settings import settings as ui_translate_settings
            from ui_translate.update_ui import UI_OT_i18n_updatetranslation_init_settings

            i18n_settings = context.window_manager.i18n_update_settings
            if not i18n_settings.is_init:
                # if it's not loaded yet, we'll try to reload it one more time
                # since we default values we set up during the current operator might helped
                UI_OT_i18n_updatetranslation_init_settings.execute_static(context, ui_translate_settings)
                if not i18n_settings.is_init:
                    raise Exception(
                        "UI Translation settings are not initalized. Make sure the following directories exist:\n"
                        f" - {ui_translate_settings.WORK_DIR}\n"
                        f" - {ui_translate_settings.BLENDER_I18N_PO_DIR}\n"
                    )

            global TRANSLATION_UI_IS_LOADED
            TRANSLATION_UI_IS_LOADED = True

            return {"FINISHED"}

    class ParseBonsaiStrings(bpy.types.Operator):
        bl_idname = "bim.parse_bonsai_strings"
        bl_label = "Parse Bonsai strings To .pot"
        bl_description = "Parse strings from Bonsai and save to .pot"
        bl_options = set()

        def execute(self, context):
            bonsai_strings_parse()
            self.report({"INFO"}, "String were parsed and saved to .pot file.")
            return {"FINISHED"}

    class UpdateTranslationsFromPo(bpy.types.Operator):
        bl_idname = "bim.update_translations_from_po"
        bl_label = "Update Translations From .po"
        bl_description = (
            "Load translation strings from po files at I18n Branches back to translations.py\n"
            "Also updates current addon translations in UI"
        )
        bl_options = set()

        def execute(self, context):
            branches_dir = get_branches_directory()
            update_translations_from_po(branches_dir, get_addon_directory())

            if is_addon_loaded(ADDON_NAME):
                bpy.app.translations.unregister(ADDON_NAME)
                addon_module = importlib.import_module(ADDON_NAME)
                translations_module = getattr(addon_module, "translations")
                importlib.reload(translations_module)
                bpy.app.translations.register(ADDON_NAME, translations_module.translations_dict)

            self.report({"INFO"}, f"Addon's translation updated from .po in {branches_dir}")
            return {"FINISHED"}

    class Bonsai_PT_translations(bpy.types.Panel):
        bl_label = "Bonsai Translations"
        bl_idname = "Bonsai_PT_translations"
        bl_space_type = "PROPERTIES"
        bl_region_type = "WINDOW"
        bl_context = "render"

        def draw(self, context):
            layout = self.layout
            layout.prop(context.preferences.view, "language")
            layout.prop(context.preferences.filepaths, "i18n_branches_directory")

            if not TRANSLATION_UI_IS_LOADED:
                layout.operator("bim.setup_translation_ui")
                return

            layout.label(text="Developer UI:")
            layout.operator("bim.parse_bonsai_strings", icon="FILE_REFRESH")

            layout.separator()
            layout.label(text="Translator UI:")
            layout.operator("bim.update_translations_from_po", icon="IMPORT")

    classes = (
        ParseBonsaiStrings,
        UpdateTranslationsFromPo,
        SetupTranslationUI,
        Bonsai_PT_translations,
    )

    def register():
        for cls in classes:
            bpy.utils.register_class(cls)

    def unregister():
        for cls in classes:
            bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    # Example:
    # py src/bonsai/scripts/bbim_translations.py -i "C:/bonsai-translations" -o "C:/Blender/4.0/scripts/addons/bonsai/translations.py"
    import argparse

    parser = argparse.ArgumentParser(description="Converts .po files to translations.py")
    parser.add_argument("-i", "--input", type=str, required=True, help="Directory with .po files")
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="translations.py module location (file may not exist yet)"
    )
    args = parser.parse_args()
    update_translations_from_po(po_directory=Path(args.input), translations_module=Path(args.output))
