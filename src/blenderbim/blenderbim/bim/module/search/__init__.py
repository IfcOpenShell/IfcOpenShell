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
    operator.ActivateIfcTypeFilter,
    operator.ColourByAttribute,
    operator.ColourByClass,
    operator.ColourByPset,
    operator.IfcTypeFilterSelectingAction, #Add selecting/deselecting all operator
    operator.ResetObjectColours,
    operator.SelectAttribute,
    operator.SelectGlobalId,
    operator.SelectIfcClass,
    operator.SelectPset,
    prop.BIMFilterClasses,
    prop.BIMSearchProperties,
    ui.BIM_PT_search,
    ui.BIM_UL_ifctype_filter,
)


def register():
    bpy.types.Scene.BIMSearchProperties = bpy.props.PointerProperty(type=prop.BIMSearchProperties)


def unregister():
    del bpy.types.Scene.BIMSearchProperties
