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
    operator.AddClashSet,
    operator.AddClashSource,
    operator.ExecuteIfcClash,
    operator.ExportClashSets,
    operator.ImportClashSets,
    operator.LoadSmartGroupsForActiveClashSet,
    operator.RemoveClashSet,
    operator.RemoveClashSource,
    operator.SelectClash,
    operator.SelectClashResults,
    operator.SelectClashSource,
    operator.SelectSmartGroup,
    operator.SelectSmartGroupedClashesPath,
    operator.SmartClashGroup,
    prop.Clash,
    prop.ClashSource,
    prop.ClashSet,
    prop.SmartClashGroup,
    prop.BIMClashProperties,
    ui.BIM_PT_ifcclash,
    ui.BIM_PT_clash_manager,
    ui.BIM_PT_smart_clash_manager,
    ui.BIM_UL_clashes,
    ui.BIM_UL_clash_sets,
    ui.BIM_UL_smart_groups,
)


def register():
    bpy.types.Scene.BIMClashProperties = bpy.props.PointerProperty(type=prop.BIMClashProperties)


def unregister():
    del bpy.types.Scene.BIMClashProperties
