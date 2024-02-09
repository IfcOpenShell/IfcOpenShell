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
    operator.AddRepresentation,
    operator.CopyRepresentation,
    operator.DisableEditingRepresentationItems,
    operator.EditObjectPlacement,
    operator.EnableEditingRepresentationItems,
    operator.FlipObject,
    operator.GetRepresentationIfcParameters,
    operator.DuplicateMoveLinkedAggregate,
    operator.DuplicateMoveLinkedAggregateMacro,
    operator.OverrideDelete,
    operator.OverrideDuplicateMove,
    operator.OverrideDuplicateMoveLinked,
    operator.OverrideDuplicateMoveLinkedMacro,
    operator.OverrideDuplicateMoveMacro,
    operator.OverrideJoin,
    operator.OverrideMeshSeparate,
    operator.OverrideModeSetEdit,
    operator.OverrideModeSetObject,
    operator.OverrideOriginSet,
    operator.OverrideOutlinerDelete,
    operator.OverridePasteBuffer,
    operator.PurgeUnusedRepresentations,
    operator.RefreshLinkedAggregate,
    operator.RemoveConnection,
    operator.RemoveRepresentation,
    operator.SelectConnection,
    operator.SwitchRepresentation,
    operator.UpdateParametricRepresentation,
    operator.UpdateRepresentation,
    operator.RemoveRepresentationItem,
    operator.EnableEditingRepresentationItemStyle,
    operator.EditRepresentationItemStyle,
    operator.DisableEditingRepresentationItemStyle,
    operator.UnassignRepresentationItemStyle,
    operator.EnableEditingRepresentationItemShapeAspect,
    operator.EditRepresentationItemShapeAspect,
    operator.DisableEditingRepresentationItemShapeAspect,
    operator.RemoveRepresentationItemFromShapeAspect,
    prop.RepresentationItem,
    prop.ShapeAspect,
    prop.BIMObjectGeometryProperties,
    prop.BIMGeometryProperties,
    ui.BIM_PT_placement,
    ui.BIM_PT_representations,
    ui.BIM_PT_representation_items,
    ui.BIM_PT_connections,
    ui.BIM_PT_mesh,
    ui.BIM_PT_derived_coordinates,
    ui.BIM_PT_workarounds,
    ui.BIM_MT_object_set_origin,
    ui.BIM_MT_separate,
    ui.BIM_MT_hotkey_separate,
    ui.BIM_UL_representation_items,
)


addon_keymaps = []


def register():
    operator.OverrideDuplicateMoveMacro.define("BIM_OT_override_object_duplicate_move")
    operator.OverrideDuplicateMoveMacro.define("TRANSFORM_OT_translate")
    operator.OverrideDuplicateMoveLinkedMacro.define("BIM_OT_override_object_duplicate_move_linked")
    operator.OverrideDuplicateMoveLinkedMacro.define("TRANSFORM_OT_translate")
    operator.DuplicateMoveLinkedAggregateMacro.define("BIM_OT_object_duplicate_move_linked_aggregate")
    operator.DuplicateMoveLinkedAggregateMacro.define("TRANSFORM_OT_translate")

    bpy.types.Object.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMObjectGeometryProperties)
    bpy.types.Scene.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMGeometryProperties)
    bpy.types.VIEW3D_MT_object.append(ui.object_menu)
    bpy.types.OUTLINER_MT_object.append(ui.outliner_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(ui.object_menu)
    bpy.types.VIEW3D_MT_edit_mesh.append(ui.edit_mesh_menu)
    bpy.types.VIEW3D_HT_header.append(ui.mode_menu)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_object_join", "J", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_duplicate_move_macro", "D", "PRESS", shift=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_duplicate_move_linked_macro", "D", "PRESS", alt=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(
            "bim.object_duplicate_move_linked_aggregate_macro", "D", "PRESS", ctrl=True, shift=True
        )
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_mode_set_edit", "TAB", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_delete", "X", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_delete", "DEL", "PRESS")
        kmi.properties.confirm = False
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Mesh", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_mode_set_object", "TAB", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("wm.call_menu", "P", "PRESS")
        kmi.properties.name = ui.BIM_MT_hotkey_separate.bl_idname
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Curve", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_mode_set_object", "TAB", "PRESS")
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Outliner", space_type="OUTLINER")
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_outliner_delete", "X", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_outliner_delete", "DEL", "PRESS")
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.types.VIEW3D_MT_object.remove(ui.object_menu)
    bpy.types.OUTLINER_MT_object.remove(ui.outliner_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(ui.outliner_menu)
    bpy.types.VIEW3D_MT_edit_mesh.remove(ui.edit_mesh_menu)
    bpy.types.VIEW3D_HT_header.remove(ui.mode_menu)
    del bpy.types.Scene.BIMGeometryProperties
    del bpy.types.Object.BIMGeometryProperties
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
