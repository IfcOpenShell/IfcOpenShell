import bpy
import addon_utils
from pathlib import Path
import shutil

context = bpy.context
SUPPORT_LANGUAGES = ["ru_RU", "de_DE"]
ADDON_NAME = "localization_test"
BRANCHES_DIR = Path(context.preferences.filepaths.i18n_branches_directory)
_LOCALE_DIR = None


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


def get_locale_dir() -> Path:
    global _LOCALE_DIR
    if _LOCALE_DIR is None:
        addon_dir = Path(bpy.utils.script_path_user()) / "addons" / ADDON_NAME
        _LOCALE_DIR = addon_dir / "locale"
        _LOCALE_DIR.mkdir(exist_ok=True)
    return _LOCALE_DIR


def convert_translations_to_po():
    """extract current translation strings from translation.py to .po files and saved them in
    both `locale` folder in addon's directory and I18n Branches directory"""

    locale_dir = get_locale_dir()

    if not BRANCHES_DIR.is_dir():
        raise Exception(f"I18n Branches directory doesn't exist: {BRANCHES_DIR.as_posix()}")

    bpy.ops.ui.i18n_addon_translation_export(
        module_name=ADDON_NAME, directory=locale_dir.as_posix(), use_export_pot=False
    )

    # NOTE: we also setup I18n branches directory
    # because it later will be used to edit translation from UI
    for file in locale_dir.iterdir():
        if file.suffix != ".po":
            continue
        branches_subdir = BRANCHES_DIR / file.stem
        branches_subdir.mkdir(exist_ok=True)
        shutil.copy(file, branches_subdir / file.name)


def update_translations_from_po():
    """load translation strings from po files at I18n Branches
    back to translations.py (they also get copied to `locale` directory of the addon)
    """
    locale_dir = get_locale_dir()
    for file in BRANCHES_DIR.glob("**/*"):
        if file.suffix != ".po":
            continue
        shutil.copy(file, locale_dir / file.name)

    bpy.ops.ui.i18n_addon_translation_import(
        module_name=ADDON_NAME,
        directory=locale_dir.as_posix(),
    )


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
