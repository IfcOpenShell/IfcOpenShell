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
)

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
    product.AddConstrTypeInstance,
    product.AddDefaultType,
    product.AddEmptyType,
    product.AddOccurrence,
    product.AlignProduct,
    product.ChangeTypePage,
    product.LoadTypeThumbnails,
    product.MirrorElements,
    product.SetActiveType,
    workspace.Hotkey,
    workspace.BIM_MT_add_representation_item,
    wall.AlignWall,
    wall.ChangeExtrusionDepth,
    wall.ChangeExtrusionXAngle,
    wall.ChangeLayerLength,
    wall.DrawPolylineWall,
    wall.FlipWall,
    wall.MergeWall,
    wall.RecalculateWall,
    wall.SplitWall,
    wall.UnjoinWalls,
    opening.AddBoolean,
    opening.AddFilledOpening,
    opening.AddPotentialHalfSpaceSolid,
    opening.AddPotentialOpening,
    opening.EditOpenings,
    opening.CloneOpening,
    opening.FlipFill,
    opening.HideBooleans,
    opening.HideOpenings,
    opening.RecalculateFill,
    opening.RemoveBooleans,
    opening.ShowBooleans,
    opening.ShowOpenings,
    profile.ChangeCardinalPoint,
    profile.ChangeProfileDepth,
    profile.DisableEditingExtrusionAxis,
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
    prop.BIMModelProperties,
    prop.BIMArrayProperties,
    prop.BIMStairProperties,
    prop.BIMSverchokProperties,
    prop.BIMWindowProperties,
    prop.BIMDoorProperties,
    prop.BIMRailingProperties,
    prop.BIMRoofProperties,
    prop.BIMPolylineProperties,
    ui.BIM_PT_array,
    ui.BIM_PT_stair,
    ui.BIM_PT_sverchok,
    ui.BIM_PT_window,
    ui.BIM_PT_door,
    ui.BIM_PT_railing,
    ui.BIM_PT_roof,
    ui.BIM_MT_type_manager_menu,
    ui.BIM_MT_type_menu,
    ui.LaunchTypeMenu,
    ui.LaunchTypeManager,
    ui.BIM_MT_elements,
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
)

addon_keymaps = []


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.WallTool, after={"bim.explore_tool"}, separator=True, group=False)
        bpy.utils.register_tool(workspace.SlabTool, after={"bim.wall_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.DoorTool, after={"bim.slab_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.WindowTool, after={"bim.door_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.ColumnTool, after={"bim.window_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.BeamTool, after={"bim.column_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.BimTool, after={"bim.beam_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.DuctTool, after={"bim.beam_tool"}, separator=False, group=True)
        bpy.utils.register_tool(workspace.PipeTool, after={"bim.duct_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.CableCarrierTool, after={"bim.pipe_tool"}, separator=False, group=False)
        bpy.utils.register_tool(workspace.CableTool, after={"bim.cable_carrier_tool"}, separator=False, group=False)

    bpy.types.Scene.BIMModelProperties = bpy.props.PointerProperty(type=prop.BIMModelProperties)
    bpy.types.Scene.BIMPolylineProperties = bpy.props.PointerProperty(type=prop.BIMPolylineProperties)
    bpy.types.Object.BIMArrayProperties = bpy.props.PointerProperty(type=prop.BIMArrayProperties)
    bpy.types.Object.BIMStairProperties = bpy.props.PointerProperty(type=prop.BIMStairProperties)
    bpy.types.Object.BIMSverchokProperties = bpy.props.PointerProperty(type=prop.BIMSverchokProperties)
    bpy.types.Object.BIMWindowProperties = bpy.props.PointerProperty(type=prop.BIMWindowProperties)
    bpy.types.Object.BIMDoorProperties = bpy.props.PointerProperty(type=prop.BIMDoorProperties)
    bpy.types.Object.BIMRailingProperties = bpy.props.PointerProperty(type=prop.BIMRailingProperties)
    bpy.types.Object.BIMRoofProperties = bpy.props.PointerProperty(type=prop.BIMRoofProperties)

    bpy.types.VIEW3D_MT_add.prepend(ui.add_menu)
    bpy.app.handlers.load_post.append(handler.load_post)

    workspace.load_custom_icons()


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.WallTool)
        bpy.utils.unregister_tool(workspace.SlabTool)
        bpy.utils.unregister_tool(workspace.DoorTool)
        bpy.utils.unregister_tool(workspace.WindowTool)
        bpy.utils.unregister_tool(workspace.ColumnTool)
        bpy.utils.unregister_tool(workspace.BeamTool)
        bpy.utils.unregister_tool(workspace.DuctTool)
        bpy.utils.unregister_tool(workspace.PipeTool)
        bpy.utils.unregister_tool(workspace.CableCarrierTool)
        bpy.utils.unregister_tool(workspace.CableTool)
        bpy.utils.unregister_tool(workspace.BimTool)

    del bpy.types.Scene.BIMModelProperties
    del bpy.types.Scene.BIMPolylineProperties
    del bpy.types.Object.BIMArrayProperties
    del bpy.types.Object.BIMStairProperties
    del bpy.types.Object.BIMSverchokProperties
    del bpy.types.Object.BIMWindowProperties
    del bpy.types.Object.BIMDoorProperties
    del bpy.types.Object.BIMRailingProperties
    del bpy.types.Object.BIMRoofProperties

    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.types.VIEW3D_MT_add.remove(ui.add_menu)

    workspace.unload_custom_icons()
