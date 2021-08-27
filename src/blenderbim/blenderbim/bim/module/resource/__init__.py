
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
    operator.DisableResourceEditingUI,
    operator.DisableEditingResource,
    operator.EnableEditingResource,
    operator.LoadResources,
    operator.AddResource,
    operator.EditResource,
    operator.RemoveResource,
    operator.LoadResourceProperties,
    operator.ExpandResource,
    operator.ContractResource,
    operator.AssignResource,
    operator.UnassignResource,
    operator.EnableEditingResourceTime,
    operator.EnableEditingResourceCosts,
    operator.EnableEditingResourceCostValueFormula,
    operator.EnableEditingResourceCostValue,
    operator.EditResourceTime,
    operator.EditResourceCostValue,
    operator.EditResourceCostValueFormula,
    operator.DisableEditingResourceTime,
    operator.DisableEditingResourceCostValue,
    operator.CalculateResourceWork,
    prop.Resource,
    prop.BIMResourceProperties,
    prop.BIMResourceTreeProperties,
    ui.BIM_PT_resources,
    ui.BIM_UL_resources,
)


def register():
    bpy.types.Scene.BIMResourceProperties = bpy.props.PointerProperty(type=prop.BIMResourceProperties)
    bpy.types.Scene.BIMResourceTreeProperties = bpy.props.PointerProperty(type=prop.BIMResourceTreeProperties)

def unregister():
    del bpy.types.Scene.BIMResourceProperties
    del bpy.types.Scene.BIMResourceTreeProperties
