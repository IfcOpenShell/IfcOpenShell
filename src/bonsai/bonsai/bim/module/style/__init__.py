# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from . import ui, prop, operator

classes = (
    operator.ActivateExternalStyle,
    operator.AddPresentationStyle,
    operator.AddStyle,
    operator.AddSurfaceTexture,
    operator.AssignStyleToSelected,
    operator.BrowseExternalStyle,
    operator.RemoveTextureMap,
    operator.ChooseTextureMapPath,
    operator.DisableAddingPresentationStyle,
    operator.DisableEditingStyle,
    operator.DisableEditingStyles,
    operator.DuplicateStyle,
    operator.EditStyle,
    operator.EditSurfaceStyle,
    operator.EnableAddingPresentationStyle,
    operator.EnableEditingStyle,
    operator.EnableEditingSurfaceStyle,
    operator.LoadStyles,
    operator.RemoveStyle,
    operator.SaveUVToStyle,
    operator.SelectByStyle,
    operator.SelectStyleInStylesUI,
    operator.UnlinkStyle,
    operator.UpdateCurrentStyle,
    operator.UpdateStyleColours,
    operator.UpdateStyleTextures,
    prop.ColourRgb,
    prop.Style,
    prop.Texture,
    prop.BIMStylesProperties,
    prop.BIMStyleProperties,
    ui.BIM_PT_styles,
    ui.BIM_UL_styles,
    ui.BIM_PT_style,
)


def register():
    bpy.types.Scene.BIMStylesProperties = bpy.props.PointerProperty(type=prop.BIMStylesProperties)
    bpy.types.Material.BIMStyleProperties = bpy.props.PointerProperty(type=prop.BIMStyleProperties)


def unregister():
    del bpy.types.Scene.BIMStylesProperties
    del bpy.types.Material.BIMStyleProperties
