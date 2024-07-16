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
from . import ui, prop, operator, workspace

classes = (
    operator.AssignContainer,
    operator.ChangeSpatialLevel,
    operator.ContractContainer,
    operator.CopyToContainer,
    operator.DeleteContainer,
    operator.DereferenceStructure,
    operator.DisableEditingContainer,
    operator.EditContainerAttributes,
    operator.EnableEditingContainer,
    operator.ExpandContainer,
    operator.ImportSpatialDecomposition,
    operator.ReferenceStructure,
    operator.RemoveContainer,
    operator.SelectContainer,
    operator.SelectDecomposedElements,
    operator.SelectProduct,
    operator.SelectSimilarContainer,
    operator.SetContainerVisibility,
    operator.SetDefaultContainer,
    prop.SpatialElement,
    prop.Element,
    prop.BIMSpatialProperties,
    prop.BIMObjectSpatialProperties,
    prop.BIMContainer,
    prop.BIMSpatialDecompositionProperties,
    ui.BIM_PT_spatial,
    ui.BIM_UL_containers,
    ui.BIM_UL_containers_manager,
    ui.BIM_UL_elements,
    ui.BIM_PT_spatial_decomposition,
    workspace.Hotkey,
)


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.SpatialTool, after={"bim.annotation_tool"}, separator=False, group=False)
    bpy.types.Scene.BIMSpatialProperties = bpy.props.PointerProperty(type=prop.BIMSpatialProperties)
    bpy.types.Object.BIMObjectSpatialProperties = bpy.props.PointerProperty(type=prop.BIMObjectSpatialProperties)
    bpy.types.Scene.BIMSpatialDecompositionProperties = bpy.props.PointerProperty(type=prop.BIMSpatialDecompositionProperties)


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.SpatialTool)
    del bpy.types.Scene.BIMSpatialProperties
    del bpy.types.Object.BIMObjectSpatialProperties
    del bpy.types.Scene.BIMSpatialDecompositionProperties
