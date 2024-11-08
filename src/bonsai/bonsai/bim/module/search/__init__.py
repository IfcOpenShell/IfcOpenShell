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
    operator.ActivateContainerFilter,
    operator.ActivateIfcClassFilter,
    operator.AddFilter,
    operator.AddFilterGroup,
    operator.ColourByProperty,
    operator.EditFilterQuery,
    operator.LoadColourscheme,
    operator.LoadSearch,
    operator.RemoveFilter,
    operator.RemoveFilterGroup,
    operator.ResetObjectColours,
    operator.SaveColourscheme,
    operator.SaveSearch,
    operator.Search,
    operator.SelectByProperty,
    operator.SelectFilterElements,
    operator.SelectGlobalId,
    operator.SelectIfcClass,
    operator.SelectSimilar,
    operator.ShowAllElements,
    operator.ToggleFilterSelection,
    prop.BIMColour,
    prop.BIMFilterClasses,
    prop.BIMFilterBuildingStoreys,
    prop.BIMSearchProperties,
    ui.BIM_PT_search,
    ui.BIM_PT_filter,
    ui.BIM_PT_colour_by_property,
    ui.BIM_PT_select_similar,
    ui.BIM_UL_colourscheme,
    ui.BIM_UL_ifc_class_filter,
    ui.BIM_UL_ifc_building_storey_filter,
)


def register():
    bpy.types.Scene.BIMSearchProperties = bpy.props.PointerProperty(type=prop.BIMSearchProperties)


def unregister():
    del bpy.types.Scene.BIMSearchProperties
