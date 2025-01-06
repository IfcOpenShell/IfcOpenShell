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
from . import ui, prop, operator, workspace

classes = (
    operator.AssignContainer,
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
    operator.SelectDecomposedElement,
    operator.SelectDecomposedElements,
    operator.SelectProduct,
    operator.SelectSimilarContainer,
    operator.SetContainerVisibility,
    operator.SetDefaultContainer,
    operator.ToggleContainerElement,
    operator.ToggleGrids,
    operator.ToggleSpatialElements,
    prop.Element,
    prop.BIMObjectSpatialProperties,
    prop.BIMContainer,
    prop.BIMSpatialDecompositionProperties,
    prop.BIMGridProperties,
    ui.BIM_PT_spatial,
    ui.BIM_UL_containers_manager,
    ui.BIM_UL_elements,
    ui.BIM_PT_spatial_decomposition,
    ui.BIM_PT_grids,
    workspace.Hotkey,
)


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.SpatialTool, after={"bim.annotation_tool"}, separator=False, group=False)
    bpy.types.Object.BIMObjectSpatialProperties = bpy.props.PointerProperty(type=prop.BIMObjectSpatialProperties)
    bpy.types.Scene.BIMSpatialDecompositionProperties = bpy.props.PointerProperty(
        type=prop.BIMSpatialDecompositionProperties
    )
    bpy.types.Scene.BIMGridProperties = bpy.props.PointerProperty(type=prop.BIMGridProperties)


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.SpatialTool)
    del bpy.types.Object.BIMObjectSpatialProperties
    del bpy.types.Scene.BIMSpatialDecompositionProperties
    del bpy.types.Scene.BIMGridProperties
