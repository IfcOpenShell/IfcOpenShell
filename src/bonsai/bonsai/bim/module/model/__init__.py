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
#
# This file was modified with the assistance of an AI coding tool.

from typing import NamedTuple

import bpy

import bonsai.tool as tool

from . import (
    array,
    covering,
    decorator,
    door,
    external,
    grid,
    handler,
    host_add_opening_gizmo,
    mep,
    mep_bend_preview,
    opening,
    product,
    profile,
    prop,
    railing,
    roof,
    slab,
    space,
    stair,
    sverchok_modifier,
    ui,
    wall,
    window,
    workspace,
)

classes = (
    array.AddArray,
    array.CancelEditingArray,
    array.EnableEditingArray,
    array.FinishEditingArray,
    array.ApplyArray,
    array.RegenerateArray,
    array.RemoveArray,
    array.SelectAllArrayObjects,
    array.SelectArrayParent,
    array.ArrayParentGizmoClick,
    array.EditArrayFromChild,
    array.Input3DCursorXArray,
    array.Input3DCursorYArray,
    array.Input3DCursorZArray,
    array.EnableEditingParametric,
    array.AddArrayFromFeatureEdit,
    array.ArrayGizmoClick,
    array.ToggleArrayMethod,
    array.RemoveArrayLayerFromEdit,
    array.InputArrayCount,
    array.AdjustArrayCount,
    array.GizmoArrayEdition,
    array.GizmoArrayChild,
    product.AddDefaultType,
    product.AddEmptyType,
    product.AddOccurrence,
    product.AlignProduct,
    product.ChangeTypePage,
    product.DrawOccurrence,
    product.LoadTypeThumbnails,
    product.MirrorElements,
    product.SetActiveType,
    workspace.Hotkey,
    workspace.BIM_MT_add_representation_item,
    wall.AddPerpendicularWall,
    wall.AddWallsFromSlab,
    wall.AlignWall,
    wall.CancelEditingWall,
    wall.ChangeExtrusionDepth,
    wall.ChangeExtrusionXAngle,
    wall.ChangeLayerLength,
    wall.CycleWallOffset,
    wall.DrawPolylineWall,
    wall.EnableEditingWall,
    wall.ExtendWallHeightToCursor,
    wall.ExtendWallsToUnderside,
    wall.RegenerateWallToUnderside,
    wall.ExtendWallsToWall,
    wall.ExtendWallsToPolylinePoint,
    wall.ExtendWallToCursor,
    wall.FinishEditingWall,
    wall.FlipWall,
    host_add_opening_gizmo.GizmoHostAddOpening,
    host_add_opening_gizmo.GizmoHostToggleOpenings,
    wall.GizmoWallEdition,
    wall.GizmoWallExtendVertically,
    wall.GizmoWallFilletPreview,
    wall.GizmoWallFilletReedit,
    wall.GizmoWallFilletToggleOpenings,
    wall.GizmoPairDisconnect,
    wall.GizmoSlabEdition,
    wall.GizmoSlabUnjoinWalls,
    wall.GizmoWallJoinIntersection,
    wall.GizmoWallLinkToggle,
    wall.GizmoWallUnjoinSingle,
    wall.JoinWallsIntersection,
    wall.MergeWall,
    wall.OffsetWalls,
    wall.RecalculateWall,
    wall.RotateWall90,
    wall.SplitWall,
    wall.SplitWallAtCursor,
    wall.DisconnectElements,
    wall.UnjoinWalls,
    wall.EnableWallFilletPreview,
    wall.FinishWallFilletPreview,
    wall.CancelWallFilletPreview,
    wall.EnableWallFilletPreviewFromCorner,
    wall.CreateWallFillet,
    opening.AddBoolean,
    opening.CloneOpening,
    opening.EditOpenings,
    opening.FlipFill,
    opening.HideAllOpenings,
    opening.HideOpenings,
    opening.PurgeUnusedOpenings,
    opening.RecalculateFill,
    opening.RemoveBoolean,
    opening.SelectBoolean,
    opening.ShowOpenings,
    opening.ToggleHostOpenings,
    opening.UpdateOpeningsFocus,
    profile.ChangeCardinalPoint,
    profile.ChangeProfileDepth,
    profile.DisableEditingExtrusionAxis,
    profile.DrawPolylineProfile,
    profile.EditExtrusionAxis,
    profile.EnableEditingExtrusionAxis,
    profile.ExtendProfile,
    profile.RecalculateProfile,
    profile.Rotate90,
    profile.PatchNonParametricMepSegment,
    roof.GenerateHippedRoof,
    slab.DisableEditingExtrusionProfile,
    slab.DisableEditingSketchExtrusionProfile,
    slab.AddSlabFromWall,
    slab.CancelEditingSlab,
    slab.DrawPolylineSlab,
    slab.EditExtrusionProfile,
    slab.EditSketchExtrusionProfile,
    slab.EnableEditingExtrusionProfile,
    slab.EnableEditingSketchExtrusionProfile,
    slab.EnableEditingSlab,
    slab.FinishEditingSlab,
    slab.RecalculateSlab,
    slab.ResetVertex,
    slab.SetArcIndex,
    space.GenerateSpace,
    space.GenerateSpacesFromWalls,
    covering.AddInstanceFlooringCoveringsFromWalls,
    covering.AddInstanceCeilingCoveringsFromWalls,
    covering.AddInstanceFlooringCoveringFromCursor,
    covering.AddInstanceCeilingCoveringFromCursor,
    covering.RegenSelectedCoveringObject,
    space.ToggleSpaceVisibility,
    space.ToggleHideSpaces,
    mep.FitFlowSegments,
    mep.RegenerateDistributionElement,
    prop.SnapMousePoint,
    prop.PolylinePoint,
    prop.Polyline,
    prop.ProductPreviewItem,
    prop.BIMModelProperties,
    prop.BIMArrayProperties,
    prop.BIMStairProperties,
    prop.BIMSverchokProperties,
    prop.BIMWindowProperties,
    prop.BIMDoorProperties,
    prop.BIMRailingProperties,
    prop.BIMRoofProperties,
    prop.BIMSlabProperties,
    prop.BIMWallProperties,
    prop.BIMPipeSegmentProperties,
    prop.BIMDuctSegmentProperties,
    prop.BIMPolylineProperties,
    prop.BIMExternalParametricGeometryProperties,
    prop.BIMBendPreviewProperties,
    prop.BIMWallFilletPreviewProperties,
    prop.BIMPreviewProperties,
    prop.BIMParametricEditDialogPrefs,
    ui.BIM_PT_array,
    ui.BIM_PT_stair,
    ui.BIM_PT_wall,
    ui.BIM_PT_sverchok,
    ui.BIM_PT_window,
    ui.BIM_PT_door,
    ui.BIM_PT_railing,
    ui.BIM_PT_roof,
    ui.BIM_MT_type_manager_menu,
    ui.BIM_MT_type_menu,
    ui.BIM_PT_external_parametric_geometry,
    ui.LaunchTypeMenu,
    ui.LaunchTypeManager,
    grid.BIM_OT_add_object,
    stair.BIM_OT_add_stair,
    stair.AddStair,
    stair.CancelEditingStair,
    stair.FinishEditingStair,
    stair.EnableEditingStair,
    stair.RemoveStair,
    stair.ToggleStairProperty,
    stair.AdjustStairTreads,
    stair.SetStairTreads,
    stair.InputStairTreads,
    stair.PickStairType,
    stair.GizmoStairEdition,
    sverchok_modifier.CreateNewSverchokGraph,
    sverchok_modifier.UpdateDataFromSverchok,
    sverchok_modifier.DeleteSverchokGraph,
    sverchok_modifier.ImportSverchokGraph,
    sverchok_modifier.ExportSverchokGraph,
    window.BIM_OT_add_window,
    window.AddWindow,
    window.CancelEditingWindow,
    window.FinishEditingWindow,
    window.EnableEditingWindow,
    window.RemoveWindow,
    window.PickWindowType,
    window.GizmoWindowEdition,
    door.BIM_OT_add_door,
    door.AddDoor,
    door.CancelEditingDoor,
    door.FinishEditingDoor,
    door.EnableEditingDoor,
    door.RemoveDoor,
    door.ToggleDoorSwing,
    door.PickDoorType,
    door.GizmoDoorEdition,
    railing.BIM_OT_add_railing,
    railing.CopyRailingParameters,
    railing.AddRailing,
    railing.CancelEditingRailing,
    railing.CycleRailingType,
    railing.FinishEditingRailing,
    railing.PickRailingTerminalType,
    railing.FlipRailingPathOrder,
    railing.EnableEditingRailing,
    railing.GizmoRailingSchematic,
    railing.ToggleRailingUseManualSupports,
    railing.CancelEditingRailingPath,
    railing.FinishEditingRailingPath,
    railing.EnableEditingRailingPath,
    railing.RemoveRailing,
    roof.BIM_OT_add_roof,
    roof.AddRoof,
    roof.CancelEditingRoof,
    roof.CopyRoofParameters,
    roof.CycleRoofGenerationMethod,
    roof.FinishEditingRoof,
    roof.EnableEditingRoof,
    roof.CancelEditingRoofPath,
    roof.FinishEditingRoofPath,
    roof.EnableEditingRoofPath,
    roof.GizmoRoofEdition,
    roof.RemoveRoof,
    roof.SetGableRoofEdgeAngle,
    mep.MEPAddObstruction,
    mep.MEPAddTransition,
    mep.MEPAddBend,
    mep.MEPRemoveTerminalFitting,
    mep.SelectMEPPathMembers,
    mep.MEPJoinSegments,
    mep_bend_preview.EnableBendPreview,
    mep_bend_preview.FinishBendPreview,
    mep_bend_preview.CancelBendPreview,
    mep_bend_preview.EnableBendPreviewFromBend,
    mep_bend_preview.GizmoBendPreview,
    mep.EnableEditingPipeSegment,
    mep.FinishEditingPipeSegment,
    mep.CancelEditingPipeSegment,
    mep.EnableEditingDuctSegment,
    mep.FinishEditingDuctSegment,
    mep.CancelEditingDuctSegment,
    mep.ExtendPipeSegmentToCursor,
    mep.ExtendDuctSegmentToCursor,
    mep.SplitPipeSegmentAtCursor,
    mep.SplitDuctSegmentAtCursor,
    mep.GizmoPipeSegmentEdition,
    mep.GizmoDuctSegmentEdition,
    mep.GizmoMEPActions,
    external.ApplyExternalParametricGeometry,
)

addon_keymaps = []


class ToolsData(NamedTuple):
    tool: type[bpy.types.WorkSpaceTool]
    after: set[str]
    separator: bool
    group: bool


tools: tuple[ToolsData, ...] = (
    ToolsData(workspace.BimTool, {"bim.explore_tool"}, False, False),
    ToolsData(workspace.DuctTool, {"bim.explore_tool"}, False, True),
    ToolsData(workspace.PipeTool, {"bim.duct_tool"}, False, False),
    ToolsData(workspace.CableCarrierTool, {"bim.pipe_tool"}, False, False),
    ToolsData(workspace.CableTool, {"bim.cable_carrier_tool"}, False, False),
    ToolsData(workspace.FurnitureTool, {"bim.explore_tool"}, False, True),
    ToolsData(workspace.SanitaryTerminalTool, {"bim.furniture_tool"}, False, False),
    ToolsData(workspace.LightFixtureTool, {"bim.sanitary_terminal_tool"}, False, False),
    ToolsData(workspace.ElectricApplianceTool, {"bim.light_fixture_tool"}, False, False),
    ToolsData(workspace.GeographicElement, {"bim.electric_appliance_tool"}, False, False),
    ToolsData(workspace.ColumnTool, {"bim.explore_tool"}, False, True),
    ToolsData(workspace.BeamTool, {"bim.column_tool"}, False, False),
    ToolsData(workspace.MemberTool, {"bim.beam_tool"}, False, False),
    ToolsData(workspace.PlateTool, {"bim.member_tool"}, False, False),
    ToolsData(workspace.FootingTool, {"bim.plate_tool"}, False, False),
    ToolsData(workspace.PileTool, {"bim.footing_tool"}, False, False),
    ToolsData(workspace.DoorTool, {"bim.explore_tool"}, False, True),
    ToolsData(workspace.WindowTool, {"bim.door_tool"}, False, False),
    ToolsData(workspace.SlabTool, {"bim.explore_tool"}, False, True),
    ToolsData(workspace.RoofTool, {"bim.slab_tool"}, False, False),
    ToolsData(workspace.StairFlightTool, {"bim.roof_tool"}, False, False),
    ToolsData(workspace.RampFlightTool, {"bim.stair_flight_tool"}, False, False),
    ToolsData(workspace.WallTool, {"bim.explore_tool"}, True, True),
    ToolsData(workspace.RailingTool, {"bim.wall_tool"}, False, False),
)


def register():
    if not bpy.app.background:
        for tool_data in tools:
            bpy.utils.register_tool(
                tool_data.tool, after=tool_data.after, separator=tool_data.separator, group=tool_data.group
            )

    bpy.types.Scene.BIMModelProperties = bpy.props.PointerProperty(type=prop.BIMModelProperties)
    bpy.types.Scene.BIMPolylineProperties = bpy.props.PointerProperty(type=prop.BIMPolylineProperties)
    bpy.types.Object.BIMArrayProperties = bpy.props.PointerProperty(type=prop.BIMArrayProperties)
    bpy.types.Object.BIMSverchokProperties = bpy.props.PointerProperty(type=prop.BIMSverchokProperties)
    # Per-parametric-type ``BIM<Name>Properties`` PointerProperties — driven by
    # ``tool.Parametric.EDIT_TYPES``; adding a registry entry is the single touchpoint.
    tool.Parametric.register_object_properties(prop)
    bpy.types.Object.BIMExternalParametricGeometryProperties = bpy.props.PointerProperty(
        type=prop.BIMExternalParametricGeometryProperties
    )
    bpy.types.Scene.BIMPreviewProperties = bpy.props.PointerProperty(type=prop.BIMPreviewProperties)
    bpy.types.WindowManager.BIMParametricEditDialogPrefs = bpy.props.PointerProperty(
        type=prop.BIMParametricEditDialogPrefs
    )

    bpy.types.VIEW3D_MT_add.prepend(ui.add_menu)
    bpy.app.handlers.load_post.append(handler.load_post)

    workspace.load_custom_icons()


def unregister():
    # DecorationsHandler is installed lazily by bim.show_openings; tear it down
    # (along with its persistent depsgraph / undo / redo / load cache handlers)
    # before the rest of unregister so those handlers can't fire against
    # half-unloaded module state.
    opening.DecorationsHandler.uninstall()

    # Network path overlays attach SpaceView3D draw handlers on toggle;
    # uninstall here so addon disable / Blender shutdown doesn't leak them.
    decorator.MEPSystemPathDecorator.uninstall()
    decorator.WallSystemPathDecorator.uninstall()

    if not bpy.app.background:
        for tool_data in reversed(tools):
            bpy.utils.unregister_tool(tool_data.tool)

    del bpy.types.Scene.BIMModelProperties
    del bpy.types.Scene.BIMPolylineProperties
    del bpy.types.Object.BIMArrayProperties
    del bpy.types.Object.BIMSverchokProperties
    tool.Parametric.unregister_object_properties()
    del bpy.types.Object.BIMExternalParametricGeometryProperties
    del bpy.types.Scene.BIMPreviewProperties
    del bpy.types.WindowManager.BIMParametricEditDialogPrefs

    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.types.VIEW3D_MT_add.remove(ui.add_menu)

    workspace.unload_custom_icons()
