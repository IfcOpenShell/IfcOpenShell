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
from bpy.app.handlers import persistent
import ifcopenshell.util.element

classes = (
    operator.AddCurvelikeItem,
    operator.AddHalfSpaceSolidItem,
    operator.AddMeshlikeItem,
    operator.AddRepresentation,
    operator.AddSweptAreaSolidItem,
    operator.AssignRepresentationLayer,
    operator.CopyRepresentation,
    operator.DisableEditingRepresentationItemShapeAspect,
    operator.DisableEditingRepresentationItemStyle,
    operator.DisableEditingRepresentationItems,
    operator.DuplicateLinkedAggregateTo3dCursor,
    operator.DuplicateMoveLinkedAggregate,
    operator.DuplicateMoveLinkedAggregateMacro,
    operator.EditObjectPlacement,
    operator.EditRepresentationItemLayer,
    operator.EditRepresentationItemShapeAspect,
    operator.EditRepresentationItemStyle,
    operator.EnableEditingRepresentationItemShapeAspect,
    operator.EnableEditingRepresentationItemStyle,
    operator.EnableEditingRepresentationItems,
    operator.FlipObject,
    operator.GetRepresentationIfcParameters,
    operator.ImportRepresentationItems,
    operator.NameProfile,
    operator.OverrideDelete,
    operator.OverrideDuplicateMove,
    operator.OverrideDuplicateMoveLinked,
    operator.OverrideDuplicateMoveLinkedMacro,
    operator.OverrideDuplicateMoveMacro,
    operator.OverrideEscape,
    operator.OverrideJoin,
    operator.OverrideMeshSeparate,
    operator.OverrideModeSetEdit,
    operator.OverrideModeSetObject,
    operator.OverrideMove,
    operator.OverrideMoveMacro,
    operator.OverrideOriginSet,
    operator.OverrideOutlinerDelete,
    operator.OverridePasteBuffer,
    operator.PurgeUnusedRepresentations,
    operator.RefreshLinkedAggregate,
    operator.RemoveConnection,
    operator.RemoveRepresentation,
    operator.RemoveRepresentationItem,
    operator.RemoveRepresentationItemFromShapeAspect,
    operator.SelectConnection,
    operator.SelectRepresentationItem,
    operator.SwitchRepresentation,
    operator.UnassignRepresentationItemLayer,
    operator.UnassignRepresentationItemStyle,
    operator.UnassignRepresentationLayer,
    operator.UpdateItemAttributes,
    operator.UpdateParametricRepresentation,
    operator.UpdateRepresentation,
    prop.RepresentationItem,
    prop.RepresentationItemObject,
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


addon_keymaps: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []


@persistent
def block_scale(scene: bpy.types.Scene) -> None:
    import bonsai.tool as tool

    if obj := (getattr(bpy.context, "active_object", None) or bpy.context.view_layer.objects.active):
        if isinstance(obj, bpy.types.Object) and tool.Blender.get_ifc_definition_id(obj):
            if obj.type == "CAMERA":
                camera = tool.Ifc.get_entity(obj)
                if ifcopenshell.util.element.get_pset(camera, "EPset_Drawing", "TargetView") == "REFLECTED_PLAN_VIEW":
                    obj.scale = (-1, -1, -1)
            else:
                if obj.scale != (1, 1, 1):
                    obj.scale = (1, 1, 1)
        elif isinstance(obj, bpy.types.Mesh) and tool.Geometry.get_mesh_props(obj).ifc_definition_id:
            if obj.scale != (1, 1, 1):
                obj.scale = (1, 1, 1)


def register():
    bpy.app.handlers.depsgraph_update_pre.append(block_scale)

    operator.OverrideDuplicateMoveMacro.define("BIM_OT_override_object_duplicate_move")
    operator.OverrideDuplicateMoveMacro.define("TRANSFORM_OT_translate")
    operator.OverrideDuplicateMoveLinkedMacro.define("BIM_OT_override_object_duplicate_move_linked")
    operator.OverrideDuplicateMoveLinkedMacro.define("TRANSFORM_OT_translate")
    operator.DuplicateMoveLinkedAggregateMacro.define("BIM_OT_object_duplicate_move_linked_aggregate")
    operator.DuplicateMoveLinkedAggregateMacro.define("BIM_OT_override_move")
    operator.DuplicateMoveLinkedAggregateMacro.define("TRANSFORM_OT_translate")
    operator.OverrideMoveMacro.define("BIM_OT_override_move")
    operator.OverrideMoveMacro.define("TRANSFORM_OT_translate")

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
        kmi = km.keymap_items.new("bim.override_move_macro", "G", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_mode_set_edit", "TAB", "PRESS")
        addon_keymaps.append((km, kmi))
        # Deletion.
        kmi = km.keymap_items.new("bim.override_object_delete", "X", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_delete", "X", "PRESS", shift=True)
        kmi.properties.use_global = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_delete", "DEL", "PRESS")
        kmi.properties.confirm = False
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_object_delete", "DEL", "PRESS", shift=True)
        kmi.properties.confirm = False
        kmi.properties.use_global = True
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Mesh", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_mode_set_object", "TAB", "PRESS")
        kmi.properties.should_save = True
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("wm.call_menu", "P", "PRESS")
        kmi.properties.name = ui.BIM_MT_hotkey_separate.bl_idname
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Curve", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_mode_set_object", "TAB", "PRESS")
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("bim.override_escape", "ESC", "PRESS")
        addon_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(name="Outliner", space_type="OUTLINER")
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_outliner_delete", "X", "PRESS")
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new("bim.override_outliner_delete", "DEL", "PRESS")
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(block_scale)

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
