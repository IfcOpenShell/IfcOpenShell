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
    operator.ShowLoads,
    operator.LoadStructuralAnalysisModels,
    operator.DisableStructuralAnalysisModelEditingUI,
    operator.AddStructuralAnalysisModel,
    operator.EditStructuralAnalysisModel,
    operator.RemoveStructuralAnalysisModel,
    operator.AssignStructuralAnalysisModel,
    operator.UnassignStructuralAnalysisModel,
    operator.EnableEditingStructuralAnalysisModel,
    operator.DisableEditingStructuralAnalysisModel,
    operator.AddStructuralBoundaryCondition,
    operator.EditStructuralBoundaryCondition,
    operator.RemoveStructuralBoundaryCondition,
    operator.EnableEditingStructuralBoundaryCondition,
    operator.DisableEditingStructuralBoundaryCondition,
    operator.AddStructuralMemberConnection,
    operator.EnableEditingStructuralConnectionCondition,
    operator.DisableEditingStructuralConnectionCondition,
    operator.RemoveStructuralConnectionCondition,
    operator.EnableEditingStructuralItemAxis,
    operator.DisableEditingStructuralItemAxis,
    operator.EditStructuralItemAxis,
    operator.EnableEditingStructuralConnectionCS,
    operator.DisableEditingStructuralConnectionCS,
    operator.EditStructuralConnectionCS,
    operator.AddStructuralLoadCase,
    operator.EditStructuralLoadCase,
    operator.RemoveStructuralLoadCase,
    operator.AddStructuralLoadGroup,
    operator.RemoveStructuralLoadGroup,
    operator.AddStructuralActivity,
    operator.EnableEditingStructuralLoadCase,
    operator.EnableEditingStructuralLoadCaseGroups,
    operator.DisableEditingStructuralLoadCase,
    operator.EnableEditingStructuralLoadGroupActivities,
    operator.LoadStructuralLoads,
    operator.DisableStructuralLoadEditingUI,
    operator.AddStructuralLoad,
    operator.EnableEditingStructuralLoad,
    operator.DisableEditingStructuralLoad,
    operator.RemoveStructuralLoad,
    operator.EditStructuralLoad,
    operator.ToggleFilterStructuralLoads,
    operator.LoadBoundaryConditions,
    operator.DisableBoundaryConditionEditingUI,
    operator.AddBoundaryCondition,
    operator.EnableEditingBoundaryCondition,
    operator.DisableEditingBoundaryCondition,
    operator.RemoveBoundaryCondition,
    operator.EditBoundaryCondition,
    operator.ToggleFilterBoundaryConditions,
    prop.StructuralAnalysisModel,
    prop.StructuralActivity,
    prop.StructuralLoad,
    prop.BoundaryCondition,
    prop.BIMStructuralProperties,
    prop.BIMObjectStructuralProperties,
    ui.BIM_PT_structural_analysis_models,
    ui.BIM_PT_structural_member,
    ui.BIM_PT_structural_connection,
    ui.BIM_PT_structural_boundary_conditions,
    ui.BIM_PT_connected_structural_members,
    ui.BIM_UL_structural_analysis_models,
    ui.BIM_UL_structural_activities,
    ui.BIM_PT_show_structural_activities,
    ui.BIM_PT_structural_load_cases,
    ui.BIM_UL_structural_loads,
    ui.BIM_PT_structural_loads,
    ui.BIM_UL_boundary_conditions,
    ui.BIM_PT_boundary_conditions,
    workspace.Hotkey,
)


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.StructuralTool, after={"bim.spatial_tool"}, separator=False, group=False)
    bpy.types.Scene.BIMStructuralProperties = bpy.props.PointerProperty(type=prop.BIMStructuralProperties)
    bpy.types.Object.BIMStructuralProperties = bpy.props.PointerProperty(type=prop.BIMObjectStructuralProperties)


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.StructuralTool)
    del bpy.types.Scene.BIMStructuralProperties
    del bpy.types.Object.BIMStructuralProperties
