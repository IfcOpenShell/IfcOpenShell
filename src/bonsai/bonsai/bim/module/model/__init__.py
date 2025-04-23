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
from . import (
    handler,
    prop,
    ui,
    grid,
    array,
    product,
    wall,
    roof,
    slab,
    space,
    covering,
    stair,
    window,
    opening,
    mep,
    workspace,
    profile,
    sverchok_modifier,
    door,
    railing,
    roof,
    mep,
    external,
)
from typing import NamedTuple

classes = (
    array.AddArray,
    array.DisableEditingArray,
    array.EditArray,
    array.EnableEditingArray,
    array.ApplyArray,
    array.RemoveArray,
    array.SelectArrayParent,
    array.SelectAllArrayObjects,
    array.Input3DCursorXArray,
    array.Input3DCursorYArray,
    array.Input3DCursorZArray,
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
    wall.AddWallsFromSlab,
    wall.AlignWall,
    wall.ChangeExtrusionDepth,
    wall.ChangeExtrusionXAngle,
    wall.ChangeLayerLength,
    wall.DrawPolylineWall,
    wall.ExtendWallsToUnderside,
    wall.ExtendWallsToWall,
    wall.FlipWall,
    wall.MergeWall,
    wall.OffsetWalls,
    wall.RecalculateWall,
    wall.SplitWall,
    wall.UnjoinWalls,
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
    slab.DrawPolylineSlab,
    slab.EditExtrusionProfile,
    slab.EditSketchExtrusionProfile,
    slab.EnableEditingExtrusionProfile,
    slab.EnableEditingSketchExtrusionProfile,
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
    prop.BIMPolylineProperties,
    prop.BIMProductPreviewProperties,
    prop.BIMExternalParametricGeometryProperties,
    ui.BIM_PT_array,
    ui.BIM_PT_stair,
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
    door.BIM_OT_add_door,
    door.AddDoor,
    door.CancelEditingDoor,
    door.FinishEditingDoor,
    door.EnableEditingDoor,
    door.RemoveDoor,
    railing.BIM_OT_add_railing,
    railing.CopyRailingParameters,
    railing.AddRailing,
    railing.CancelEditingRailing,
    railing.FinishEditingRailing,
    railing.FlipRailingPathOrder,
    railing.EnableEditingRailing,
    railing.CancelEditingRailingPath,
    railing.FinishEditingRailingPath,
    railing.EnableEditingRailingPath,
    railing.RemoveRailing,
    roof.BIM_OT_add_roof,
    roof.AddRoof,
    roof.CancelEditingRoof,
    roof.CopyRoofParameters,
    roof.FinishEditingRoof,
    roof.EnableEditingRoof,
    roof.CancelEditingRoofPath,
    roof.FinishEditingRoofPath,
    roof.EnableEditingRoofPath,
    roof.RemoveRoof,
    roof.SetGableRoofEdgeAngle,
    mep.MEPAddObstruction,
    mep.MEPAddTransition,
    mep.MEPAddBend,
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
    bpy.types.Scene.BIMProductPreviewProperties = bpy.props.PointerProperty(type=prop.BIMProductPreviewProperties)
    bpy.types.Object.BIMArrayProperties = bpy.props.PointerProperty(type=prop.BIMArrayProperties)
    bpy.types.Object.BIMStairProperties = bpy.props.PointerProperty(type=prop.BIMStairProperties)
    bpy.types.Object.BIMSverchokProperties = bpy.props.PointerProperty(type=prop.BIMSverchokProperties)
    bpy.types.Object.BIMWindowProperties = bpy.props.PointerProperty(type=prop.BIMWindowProperties)
    bpy.types.Object.BIMDoorProperties = bpy.props.PointerProperty(type=prop.BIMDoorProperties)
    bpy.types.Object.BIMRailingProperties = bpy.props.PointerProperty(type=prop.BIMRailingProperties)
    bpy.types.Object.BIMRoofProperties = bpy.props.PointerProperty(type=prop.BIMRoofProperties)
    bpy.types.Object.BIMExternalParametricGeometryProperties = bpy.props.PointerProperty(
        type=prop.BIMExternalParametricGeometryProperties
    )

    bpy.types.VIEW3D_MT_add.prepend(ui.add_menu)
    bpy.app.handlers.load_post.append(handler.load_post)

    workspace.load_custom_icons()


def unregister():
    if not bpy.app.background:
        for tool_data in reversed(tools):
            bpy.utils.unregister_tool(tool_data.tool)

    del bpy.types.Scene.BIMModelProperties
    del bpy.types.Scene.BIMPolylineProperties
    del bpy.types.Scene.BIMProductPreviewProperties
    del bpy.types.Object.BIMArrayProperties
    del bpy.types.Object.BIMStairProperties
    del bpy.types.Object.BIMSverchokProperties
    del bpy.types.Object.BIMWindowProperties
    del bpy.types.Object.BIMDoorProperties
    del bpy.types.Object.BIMRailingProperties
    del bpy.types.Object.BIMRoofProperties
    del bpy.types.Object.BIMExternalParametricGeometryProperties

    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.types.VIEW3D_MT_add.remove(ui.add_menu)

    workspace.unload_custom_icons()
