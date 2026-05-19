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

from . import operator, prop, ui

classes = (
    operator.ActivateContainerFilter,
    operator.ActivateIfcClassFilter,
    operator.AddFilter,
    operator.AddFilterGroup,
    operator.ApplyFilterFromText,
    operator.ColourByProperty,
    operator.EditFilterQuery,
    operator.FilterValueSuggestions,
    operator.LoadColourscheme,
    operator.LoadSearch,
    operator.RemoveFilter,
    operator.RemoveFilterGroup,
    operator.RemoveSearch,
    operator.ResetObjectColours,
    operator.SaveColourscheme,
    operator.SaveSearch,
    operator.Search,
    operator.SelectByProperty,
    operator.SelectFilterElements,
    operator.SelectGlobalId,
    operator.SelectQueryElements,
    operator.SelectIfcClass,
    operator.SelectSimilar,
    operator.ShowAllElements,
    operator.ToggleFilterInclusion,
    operator.ToggleFilterSelection,
    prop.BIMColour,
    prop.BIMFilterItem,
    prop.BIMSearchProperties,
    ui.BIM_PT_search,
    ui.BIM_PT_filter,
    ui.BIM_PT_colour_by_property,
    ui.BIM_PT_select_similar,
    ui.BIM_UL_colourscheme,
    ui.BIM_UL_ifc_filter,
)


def register():
    bpy.types.Scene.BIMSearchProperties = bpy.props.PointerProperty(type=prop.BIMSearchProperties)
    bpy.types.TEXT_HT_header.append(operator.draw_text_editor_header)


def unregister():
    del bpy.types.Scene.BIMSearchProperties
    bpy.types.TEXT_HT_header.remove(operator.draw_text_editor_header)
