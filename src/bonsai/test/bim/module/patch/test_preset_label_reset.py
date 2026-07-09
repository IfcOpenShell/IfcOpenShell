# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.patch


class TestPresetMenuLabelResetsOnRecipeChange(NewFile):
    """Blender's ``script.execute_preset`` mutates the menu class's bl_label
    to the loaded preset's display name as a "currently-selected" indicator.
    Without a recipe-change callback, that label persists into the next
    recipe's menu — falsely advertising a preset that belongs to a
    different recipe's subdir and isn't selectable from the new menu."""

    def test_changing_recipe_restores_canonical_label(self):
        # Simulate the state Blender leaves after the user picked a preset
        # for the previous recipe.
        menu_cls = bpy.types.BIM_MT_ifc_patch_presets
        menu_cls.bl_label = "Structural"

        # Switching the recipe must fire update_ifc_patch_recipe, which
        # resets the menu label.
        props = tool.Patch.get_patch_props()
        props.ifc_patch_recipes = "Migrate"

        assert menu_cls.bl_label == "IFC Patch Presets"

    def test_canonical_label_is_used_when_no_preset_was_loaded(self):
        # Fresh state — label is the bl_label-default from the class declaration.
        menu_cls = bpy.types.BIM_MT_ifc_patch_presets
        props = tool.Patch.get_patch_props()
        props.ifc_patch_recipes = "ExtractElements"
        assert menu_cls.bl_label == "IFC Patch Presets"
