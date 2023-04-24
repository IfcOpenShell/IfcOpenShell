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
    stair,
    window,
    opening,
    pie,
    workspace,
    profile,
    sverchok_modifier,
    door,
    railing,
    roof,
)

classes = (
    array.AddArray,
    array.DisableEditingArray,
    array.EditArray,
    array.EnableEditingArray,
    array.RemoveArray,
    array.SelectArrayParent,
    array.Input3DCursorXArray,
    array.Input3DCursorYArray,
    array.Input3DCursorZArray,
    product.AddConstrTypeInstance,
    product.AddEmptyType,
    product.AlignProduct,
    product.ChangeTypePage,
    product.LoadTypeThumbnails,
    product.MirrorElements,
    workspace.Hotkey,
    wall.AlignWall,
    wall.ChangeExtrusionDepth,
    wall.ChangeExtrusionXAngle,
    wall.ChangeLayerLength,
    wall.FlipWall,
    wall.JoinWall,
    wall.MergeWall,
    wall.RecalculateWall,
    wall.SplitWall,
    opening.AddBoolean,
    opening.AddFilledOpening,
    opening.AddPotentialHalfSpaceSolid,
    opening.AddPotentialOpening,
    opening.EditOpenings,
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
    roof.GenerateHippedRoof,
    slab.DisableEditingExtrusionProfile,
    slab.DisableEditingSketchExtrusionProfile,
    slab.EditExtrusionProfile,
    slab.EditSketchExtrusionProfile,
    slab.EnableEditingExtrusionProfile,
    slab.EnableEditingSketchExtrusionProfile,
    slab.ResetVertex,
    slab.SetArcIndex,
    space.GenerateSpace,
    prop.BIMModelProperties,
    prop.BIMArrayProperties,
    prop.BIMStairProperties,
    prop.BIMSverchokProperties,
    prop.BIMWindowProperties,
    prop.BIMDoorProperties,
    prop.BIMRailingProperties,
    prop.BIMRoofProperties,
    ui.BIM_PT_authoring,
    ui.BIM_PT_array,
    ui.BIM_PT_stair,
    ui.BIM_PT_sverchok,
    ui.BIM_PT_window,
    ui.BIM_PT_door,
    ui.BIM_PT_railing,
    ui.BIM_PT_roof,
    ui.LaunchTypeManager,
    ui.BIM_MT_model,
    grid.BIM_OT_add_object,
    stair.BIM_OT_add_object,
    stair.BIM_OT_add_clever_stair,
    stair.AddStair,
    stair.CancelEditingStair,
    stair.FinishEditingStair,
    stair.EnableEditingStair,
    stair.RemoveStair,
    pie.OpenPieClass,
    pie.PieUpdateContainer,
    pie.PieAddOpening,
    pie.VIEW3D_MT_PIE_bim,
    pie.VIEW3D_MT_PIE_bim_class,
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
)

addon_keymaps = []


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.BimTool, after={"builtin.scale_cage"}, separator=True, group=True)
    bpy.types.Scene.BIMModelProperties = bpy.props.PointerProperty(type=prop.BIMModelProperties)
    bpy.types.Object.BIMArrayProperties = bpy.props.PointerProperty(type=prop.BIMArrayProperties)
    bpy.types.Object.BIMStairProperties = bpy.props.PointerProperty(type=prop.BIMStairProperties)
    bpy.types.Object.BIMSverchokProperties = bpy.props.PointerProperty(type=prop.BIMSverchokProperties)
    bpy.types.Object.BIMWindowProperties = bpy.props.PointerProperty(type=prop.BIMWindowProperties)
    bpy.types.Object.BIMDoorProperties = bpy.props.PointerProperty(type=prop.BIMDoorProperties)
    bpy.types.Object.BIMRailingProperties = bpy.props.PointerProperty(type=prop.BIMRailingProperties)
    bpy.types.Object.BIMRoofProperties = bpy.props.PointerProperty(type=prop.BIMRoofProperties)
    bpy.types.VIEW3D_MT_mesh_add.append(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(railing.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(roof.add_object_button)
    bpy.types.VIEW3D_MT_add.append(ui.add_menu)
    bpy.app.handlers.load_post.append(handler.load_post)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu_pie", "E", "PRESS", shift=True)
        kmi.properties["name"] = "VIEW3D_MT_PIE_bim"
        addon_keymaps.append((km, kmi))


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.BimTool)
    del bpy.types.Scene.BIMModelProperties
    del bpy.types.Object.BIMArrayProperties
    del bpy.types.Object.BIMStairProperties
    del bpy.types.Object.BIMSverchokProperties
    del bpy.types.Object.BIMWindowProperties
    del bpy.types.Object.BIMDoorProperties
    del bpy.types.Object.BIMRailingProperties
    del bpy.types.Object.BIMRoofProperties
    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.types.VIEW3D_MT_mesh_add.remove(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(railing.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(roof.add_object_button)
    bpy.types.VIEW3D_MT_add.remove(ui.add_menu)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
