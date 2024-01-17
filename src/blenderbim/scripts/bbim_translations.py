import bpy
import addon_utils
import shutil
import tempfile
import importlib
import os
import sys
import re
import bl_i18n_utils
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

bl_info = {
    "name": "BlenderBIM Translations",
    "description": "",
    "author": "IfcOpenShell Contributors",
    "blender": (2, 80, 0),
    "version": (0, 0, 999999),
    "location": "Properties -> Render -> BBIM Update Translation",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "System",
}

context = bpy.context
# NOTE: list of available languages in Blender can be retrieved
# by the command below:
# bpy.context.preferences.view.language = "test"
ADDON_NAME = "blenderbim"
TRANSLATION_UI_IS_LOADED = False


def is_addon_loaded(addon_name) -> bool:
    loaded_default, loaded_state = addon_utils.check(addon_name)
    return loaded_state


def get_branches_directory():
    return Path(context.preferences.filepaths.i18n_branches_directory)


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
    msg_id: str
    context: str | None
    sources: list[str]


def blenderbim_strings_parse(addon_directory=None, po_directory=None):
    # NOTE: we decided to use our own parser due bug in Blender parser
    # as it tends to pick up strings from other addons and other Blender parts
    # and this bug probably would be to low of a priority for Blender to fix
    # ref: https://projects.blender.org/blender/blender/issues/116579

    if addon_directory is None:
        addon_module = importlib.import_module(ADDON_NAME)
        addon_directory = Path(addon_module.__file__).parent
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
        r'\b_\("(.*?)"\)' # gettext called with `_`
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
                    is_operator = i < 2
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
                            message = Message(string, ctx, [])
                            matched_dict[string] = message
                        elif ctx != message.context and False:
                            print(
                                f'WARNING. Message "{string}" was already registered with different context {message.context}. '
                                f"Current context: {ctx}. File: {source_rel_path}"
                            )
                        message.sources.append(source_rel_path)

    pot_filepath = po_directory / "blenderbim.pot"
    with open(pot_filepath, "w", encoding="utf-8") as fo:
        for msg in matched_dict.values():
            # make sure sources are unique but keep the order
            sources = list(dict.fromkeys(msg.sources))
            for source in sources:
                fo.write(f"#: {source}\n")
            if msg.context != None:
                fo.write(f'msgctxt "{msg.context}"\n')
            fo.write(f'msgid "{msg.msg_id}"\n')
            fo.write('msgstr ""\n')
            fo.write("\n")


def dump_py_messages_monkey_patch(msgs, reports, addons, settings, addons_only=False):
    ignore_addon_dirs = ["libs"]

    def _get_files(path, ignore_dirs=tuple()):
        if not os.path.exists(path):
            return []
        if os.path.isdir(path):
            files = []
            for dpath, subdirs, fnames in os.walk(path, topdown=True, followlinks=True):
                if Path(dpath) in ignore_dirs:
                    subdirs.clear()  # skip walking through `subdirs`
                    continue

                for fn in fnames:
                    if not fn.endswith(".py"):
                        continue
                    if fn.startswith("_") and fn != "__init__.py":
                        continue
                    files.append(os.path.join(dpath, fn))

            return files

        return [path]

    files = []
    if not addons_only:
        for path in settings.CUSTOM_PY_UI_FILES:
            for root in (bpy.utils.resource_path(t) for t in ("USER", "LOCAL", "SYSTEM")):
                files += _get_files(os.path.join(root, path))

    # Add all given addons.
    for mod in addons:
        fn = mod.__file__
        if os.path.basename(fn) == "__init__.py":
            parent_dir = Path(fn).parent
            ignore_dirs = [parent_dir / dpath for dpath in ignore_addon_dirs]
            files += _get_files(os.path.dirname(fn), ignore_dirs=ignore_dirs)
        else:
            files.append(fn)

    bl_i18n_utils.bl_extract_messages.dump_py_messages_from_files(msgs, reports, sorted(files), settings)


def dump_addon_messages(module_name, do_checks, settings):
    import datetime
    import addon_utils
    import bl_i18n_utils.utils as utils
    from bl_i18n_utils.bl_extract_messages import (
        _gen_reports,
        _gen_check_ctxt,
        dump_rna_messages,
        _diff_check_ctxt,
        dump_py_messages,
        dump_addon_bl_info,
        print_info,
    )

    # Enable our addon.
    ver = module_name
    rev = 0
    date = datetime.datetime.now()
    pot = utils.I18nMessages.gen_empty_messages(
        settings.PARSER_TEMPLATE_ID, ver, rev, date, date.year, settings=settings
    )
    msgs = pot.msgs

    minus_pot = utils.I18nMessages.gen_empty_messages(
        settings.PARSER_TEMPLATE_ID, ver, rev, date, date.year, settings=settings
    )
    minus_msgs = minus_pot.msgs

    check_ctxt = _gen_check_ctxt(settings) if do_checks else None
    minus_check_ctxt = _gen_check_ctxt(settings) if do_checks else None

    # Get strings from RNA, our addon being disabled
    print("D")
    reports = _gen_reports(check_ctxt)
    print("E")
    dump_rna_messages(minus_msgs, reports, settings)
    print("F")

    # Now enable our addon, and re-scan RNA.
    addon = utils.enable_addons(addons={module_name})[0]
    print("A")
    reports["check_ctxt"] = minus_check_ctxt
    print("B")
    dump_rna_messages(msgs, reports, settings)
    print("C")

    # and make the diff!
    for key in minus_msgs:
        if key != settings.PO_HEADER_KEY:
            if key in msgs:
                del msgs[key]
            else:
                # This should not happen, but some messages seem to have
                # leaked on add-on unregister and register?
                print(f"Key not found in msgs: {key}")

    if check_ctxt:
        _diff_check_ctxt(check_ctxt, minus_check_ctxt)

    # and we are done with those!
    del minus_pot
    del minus_msgs
    del minus_check_ctxt

    # get strings from UI layout definitions text="..." args
    reports["check_ctxt"] = check_ctxt
    dump_py_messages(msgs, reports, {addon}, settings, addons_only=True)

    # Get strings from the addon's bl_info
    dump_addon_bl_info(msgs, reports, addon, settings)

    pot.unescape()  # Strings gathered in py/C source code may contain escaped chars...
    print_info(reports, pot)

    print("Finished extracting UI messages!")

    return pot


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

        # we monkey patch `bl_i18n_utils.bl_extract_messages.dump_py_messages`
        # as it's doesn't support ignoring folders
        # and we need it, otherwise translation addon will try to parse strings
        # from all BlenderBIM dependencies :O
        bl_i18n_utils.bl_extract_messages.dump_py_messages = dump_py_messages_monkey_patch
        bl_i18n_utils.bl_extract_messages.dump_addon_messages = dump_addon_messages

        # setup selected languages
        for lang in i18n_settings.langs:
            lang.use = lang.uid == context.preferences.view.language

        global TRANSLATION_UI_IS_LOADED
        TRANSLATION_UI_IS_LOADED = True

        return {"FINISHED"}


class ReloadPyTranslations(bpy.types.Operator):
    bl_idname = "bim.reload_py_translations"
    bl_label = "Reload Py Translations"
    bl_description = "Parse strings from Blender objects of the addon to `translations.py`"
    bl_options = set()
    use_bbim_parser: bpy.props.BoolProperty(
        name="Use BlenderBIM Parser", description="As oppose to Blender parser", default=True
    )

    def execute(self, context):
        if self.use_bbim_parser:
            blenderbim_strings_parse()
        else:
            if is_addon_loaded(ADDON_NAME):
                # ref: https://projects.blender.org/blender/blender/issues/116579
                raise Exception(
                    f"'{ADDON_NAME}' addon is enabled.\n"
                    "Need to disable it, restart Blender and start reloading translations again.\n"
                    "Otherwise some strings to translate might get lost due Blender bug."
                )

            bpy.ops.ui.i18n_addon_translation_update("INVOKE_DEFAULT", module_name=ADDON_NAME)
        self.report({"INFO"}, "Translations py data is saved.")
        return {"FINISHED"}


class ConvertTranslationsToPo(bpy.types.Operator):
    bl_idname = "bim.convert_translations_to_po"
    bl_label = "Convert Translations To .po"
    bl_description = (
        "Extract current translation strings from translation.py to .po files and saves them to I18n Branches directory"
    )
    bl_options = set()

    def execute(self, context):
        temp_po_dir = tempfile.TemporaryDirectory()
        branches_dir = get_branches_directory()

        bpy.ops.ui.i18n_addon_translation_export(
            module_name=ADDON_NAME, directory=temp_po_dir.name, use_export_pot=True
        )

        # NOTE: we use I18n branches directory
        # because it is the directory that later will be used to edit translation from UI.
        # I18n directory also has a bit different format then `ui_translate.export/import`,
        # every .po file has a parent folder with the same name
        # so we rearrange the exported data that way
        for file in Path(temp_po_dir.name).iterdir():
            branches_subdir = branches_dir / file.stem
            branches_subdir.mkdir(exist_ok=True)
            file.replace(branches_subdir / file.name)

        temp_po_dir.cleanup()
        self.report({"INFO"}, f"Translations .po files are saved to {branches_dir}.")
        return {"FINISHED"}


class UpdateTranslationsFromPo(bpy.types.Operator):
    bl_idname = "bim.update_translations_from_po"
    bl_label = "Update Translations From .po"
    bl_description = (
        "Load translation strings from po files at I18n Branches\n"
        "back to translations.py (they also get copied to `locale` directory of the addon)"
    )
    bl_options = set()

    def execute(self, context):
        temp_po_dir = tempfile.TemporaryDirectory()
        branches_dir = get_branches_directory()
        rearrange_files_for_po_import(branches_dir, temp_po_dir)

        bpy.ops.ui.i18n_addon_translation_import(
            module_name=ADDON_NAME,
            directory=temp_po_dir.name,
        )

        # update translations in current Blender session
        if is_addon_loaded(ADDON_NAME):
            bpy.app.translations.unregister(ADDON_NAME)
            addon_module = importlib.import_module(ADDON_NAME)
            translations_module = getattr(addon_module, "translations")
            importlib.reload(translations_module)
            bpy.app.translations.register(ADDON_NAME, translations_module.translations_dict)
        self.report({"INFO"}, f"Addon's translation updated from .po in {branches_dir}")
        return {"FINISHED"}


class DisableEnableAddon(bpy.types.Operator):
    bl_idname = "bim.disable_enable_addon"
    bl_label = "Disable/Enable addon"
    bl_description = "Will enable addon if it's disabled, will disable it and restart Blender otherwise"
    bl_options = set()

    def execute(self, context):
        if not is_addon_loaded(ADDON_NAME):
            addon_utils.enable("blenderbim", default_set=True)
            return {"FINISHED"}

        import os
        import subprocess

        addon_utils.disable("blenderbim", default_set=True)

        blender_exe = bpy.app.binary_path
        head, tail = os.path.split(blender_exe)
        blender_launcher = os.path.join(head, "blender-launcher.exe")
        subprocess.run([blender_launcher, "-con", "--python-expr", "import bpy; bpy.ops.wm.recover_last_session()"])
        bpy.ops.wm.quit_blender()
        return {"FINISHED"}


class BBIM_PT_translations(bpy.types.Panel):
    bl_label = "BlenderBIM Translations"
    bl_idname = "BBIM_PT_translations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.preferences.view, "language")

        if not TRANSLATION_UI_IS_LOADED:
            layout.operator("bim.setup_translation_ui")
            layout.prop(context.preferences.filepaths, "i18n_branches_directory", text="I18n branches directory")
            return

        layout.label(text="Developer UI:")
        layout.operator("bim.reload_py_translations", icon="FILE_REFRESH")

        # blender restart is disabled as we'll parse strings with BBIM parser
        addon_enabled = is_addon_loaded(ADDON_NAME)
        row = layout.row()
        row.operator(
            "bim.disable_enable_addon",
            icon="QUIT" if addon_enabled else "PLUGIN",
            text="Disable Addon And Restart Blender" if addon_enabled else "Enable Addon",
        )
        row.enabled = False

        layout.operator("bim.convert_translations_to_po", icon="EXPORT")
        layout.separator(factor=3)
        layout.label(text="Translator UI:")
        layout.prop(context.preferences.filepaths, "i18n_branches_directory")
        layout.operator("bim.update_translations_from_po", icon="IMPORT")


classes = (
    ReloadPyTranslations,
    ConvertTranslationsToPo,
    UpdateTranslationsFromPo,
    SetupTranslationUI,
    DisableEnableAddon,
    BBIM_PT_translations,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


def update_translations_from_po(po_directory: Path, translations_module: Path):
    from bl_i18n_utils.settings import I18nSettings
    import bl_i18n_utils.utils as utils_i18n

    temp_po_dir = tempfile.TemporaryDirectory()
    rearrange_files_for_po_import(po_directory, temp_po_dir)

    settings = I18nSettings()

    trans = utils_i18n.I18n(kind="PY", src=translations_module.as_posix(), settings=settings)
    po_files = dict(utils_i18n.get_po_files_from_dir(temp_po_dir.name))

    for po_uid, po_filepath in po_files.items():
        po_uid = po_uid[0]
        msgs = utils_i18n.I18nMessages(uid=po_uid, kind="PO", key=po_uid, src=po_filepath, settings=settings)
        if po_uid in trans.trans:
            trans.trans[po_uid].merge(msgs, replace=True)
        else:
            trans.trans[po_uid] = msgs

    trans.write(kind="PY")


if __name__ == "__main__":
    # Example:
    # py src/blenderbim/scripts/bbim_translations.py -i "C:/blenderbim-translations" -o "C:/Blender/4.0/scripts/addons/blenderbim/translations.py"
    import argparse

    parser = argparse.ArgumentParser(description="Converts .po files to translations.py")
    parser.add_argument("-i", "--input", type=str, required=True, help="Directory with .po files")
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="translations.py module location (file may not exist yet)"
    )
    args = parser.parse_args()
    update_translations_from_po(po_directory=Path(args.input), translations_module=Path(args.output))
