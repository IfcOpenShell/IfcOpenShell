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
    operator.AddResource,
    operator.AddResourceQuantity,
    operator.AddProductivityData,
    operator.AssignResource,
    operator.CalculateResourceWork,
    operator.ConstrainResourceWork,
    operator.ContractResource,
    operator.DisableEditingResource,
    operator.DisableEditingResourceCostValue,
    operator.DisableEditingResourceQuantity,
    operator.DisableEditingResourceTime,
    operator.DisableResourceEditingUI,
    operator.EditProductivityData,
    operator.EditResource,
    operator.EditResourceCostValue,
    operator.EditResourceCostValueFormula,
    operator.EditResourceQuantity,
    operator.EditResourceTime,
    operator.EnableEditingResource,
    operator.EnableEditingResourceBaseQuantity,
    operator.EnableEditingResourceCosts,
    operator.EnableEditingResourceCostValue,
    operator.CalculateResourceUsage,
    operator.EnableEditingResourceCostValueFormula,
    operator.EnableEditingResourceQuantity,
    operator.EnableEditingResourceTime,
    operator.ExpandResource,
    operator.GoToResource,
    operator.ImportResources,
    operator.LoadResources,
    operator.RemoveResource,
    operator.RemoveResourceQuantity,
    operator.RemoveUsageConstraint,
    operator.UnassignResource,
    prop.Resource,
    prop.BIMResourceProperties,
    prop.BIMResourceTreeProperties,
    prop.ISODuration,
    prop.BIMResourceProductivity,
    ui.BIM_PT_resources,
    ui.BIM_UL_resources,
)


def register():
    bpy.types.Scene.BIMResourceProperties = bpy.props.PointerProperty(type=prop.BIMResourceProperties)
    bpy.types.Scene.BIMResourceTreeProperties = bpy.props.PointerProperty(type=prop.BIMResourceTreeProperties)
    bpy.types.Scene.BIMResourceProductivity = bpy.props.PointerProperty(type=prop.BIMResourceProductivity)


def unregister():
    del bpy.types.Scene.BIMResourceProperties
    del bpy.types.Scene.BIMResourceTreeProperties
    del bpy.types.Scene.BIMResourceProductivity
