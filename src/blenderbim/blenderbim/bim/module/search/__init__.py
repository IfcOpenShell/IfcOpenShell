# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import ui, prop, operator

classes = (
    operator.ActivateIfcClassFilter,
    operator.ActivateIfcBuildingStoreyFilter,
    operator.ColourByAttribute,
    operator.ColourByClass,
    operator.ColourByPset,
    operator.ToggleFilterSelection,
    operator.ResetObjectColours,
    operator.SelectAttribute,
    operator.SelectGlobalId,
    operator.SelectIfcClass,
    operator.SelectPset,
    operator.UnhideAllElements,
    operator.FilterModelElements,
    operator.IfcSelector,
    operator.SaveSelectorQuery,
    operator.OpenQueryLibrary,
    operator.LoadQuery,
    operator.AddToIfcGroup,
    prop.BIMFilterClasses,
    prop.BIMFilterBuildingStoreys,
    prop.BIMSearchProperties,
    prop.SearchCollection,
    prop.SearchQueryFilter,
    prop.SearchQuery,
    prop.SearchQueryGroup,
    prop.IfcSelectorProperties,
    ui.BIM_PT_search,
    ui.BIM_UL_ifc_class_filter,
    ui.BIM_UL_ifc_building_storey_filter,
    ui.BIM_PT_IFCSelector,
)


def register():
    bpy.types.Scene.BIMSearchProperties = bpy.props.PointerProperty(type=prop.BIMSearchProperties)
    bpy.types.Scene.IfcSelectorProperties = bpy.props.PointerProperty(type=prop.IfcSelectorProperties)


def unregister():
    del bpy.types.Scene.BIMSearchProperties
    del bpy.types.Scene.IfcSelectorProperties
