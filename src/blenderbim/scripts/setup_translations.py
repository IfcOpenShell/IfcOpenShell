import bpy
import addon_utils
import shutil
import tempfile
import importlib
from pathlib import Path

context = bpy.context
SUPPORT_LANGUAGES = ["ru_RU", "de_DE"]
ADDON_NAME = "localization_test"
BRANCHES_DIR = Path(context.preferences.filepaths.i18n_branches_directory)


def is_addon_loaded(addon_name):
    loaded_default, loaded_state = addon_utils.check(addon_name)
    return loaded_state


def reload_translations():
    """Parse strings from Blender objects of the addon to `translations.py`"""
    if is_addon_loaded(ADDON_NAME):
        # ref: https://projects.blender.org/blender/blender/issues/116579
        raise Exception(
            f"'{ADDON_NAME}' addon is enabled.\n"
            "Need to disable it, restart Blender and start reloading translations again.\n"
            "Otherwise some strings to translate might get lost due Blender bug."
        )

    bpy.ops.ui.i18n_addon_translation_update("INVOKE_DEFAULT", module_name=ADDON_NAME)


def convert_translations_to_po():
    """extract current translation strings from translation.py to .po files
    and saves them to I18n Branches directory"""

    temp_po_dir = tempfile.TemporaryDirectory()

    if not BRANCHES_DIR.is_dir():
        raise Exception(f"I18n Branches directory doesn't exist: {BRANCHES_DIR.as_posix()}")

    bpy.ops.ui.i18n_addon_translation_export(module_name=ADDON_NAME, directory=temp_po_dir.name, use_export_pot=False)

    # NOTE: we use I18n branches directory
    # because it is the directory that later will be used to edit translation from UI.
    # I18n directory also has a bit different format then `ui_translate.export/import`,
    # every .po file has a parent folder with the same name
    # so we rearrange the exported data that way
    for file in Path(temp_po_dir.name).iterdir():
        branches_subdir = BRANCHES_DIR / file.stem
        branches_subdir.mkdir(exist_ok=True)
        file.rename(branches_subdir / file.name)

    temp_po_dir.cleanup()


def update_translations_from_po():
    """load translation strings from po files at I18n Branches
    back to translations.py (they also get copied to `locale` directory of the addon)
    """
    temp_po_dir = tempfile.TemporaryDirectory()
    temp_po_dir_path = Path(temp_po_dir.name)
    for file in BRANCHES_DIR.glob("**/*"):
        if file.suffix != ".po":
            continue
        shutil.copy(file, temp_po_dir_path / file.name)

    bpy.ops.ui.i18n_addon_translation_import(
        module_name=ADDON_NAME,
        directory=temp_po_dir.name,
    )

    temp_po_dir.cleanup()

    # update translations in current Blender session
    bpy.app.translations.unregister(ADDON_NAME)
    addon_module = importlib.import_module(ADDON_NAME)
    translations_module = getattr(addon_module, "translations")
    importlib.reload(translations_module)
    bpy.app.translations.register(ADDON_NAME, translations_module.translations_dict)


if __name__ == "__main__":
    if not is_addon_loaded("ui_translate"):
        raise Exception('"Manage UI translations" addon is not enabled')

    from ui_translate.settings import settings as ui_translate_settings

    i18n_settings = context.window_manager.i18n_update_settings
    if not i18n_settings.is_init:
        raise Exception(
            "UI Translation settings are not initalized. Make sure the following directories exist:\n"
            f" - {ui_translate_settings.WORK_DIR}\n"
            f" - {ui_translate_settings.BLENDER_I18N_PO_DIR}\n"
        )

    # setup selected languages
    for lang in i18n_settings.langs:
        lang.use = lang.uid in SUPPORT_LANGUAGES

    # uncomment the action you want to perform:
    # reload_translations()
    # convert_translations_to_po()
    # update_translations_from_po()
