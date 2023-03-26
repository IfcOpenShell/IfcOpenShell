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
    operator.EditObjectPlacement,
    operator.GetRepresentationIfcParameters,
    operator.OverrideDelete,
    operator.OverrideDuplicateMove,
    operator.OverrideDuplicateMoveLinked,
    operator.OverrideModeSetEdit,
    operator.OverrideModeSetObject,
    operator.OverrideOutlinerDelete,
    operator.OverridePasteBuffer,
    operator.RemoveConnection,
    operator.RemoveRepresentation,
    operator.SelectConnection,
    operator.SwitchRepresentation,
    operator.UpdateParametricRepresentation,
    operator.UpdateRepresentation,
    prop.BIMObjectGeometryProperties,
    prop.BIMGeometryProperties,
    ui.BIM_PT_derived_placements,
    ui.BIM_PT_representations,
    ui.BIM_PT_connections,
    ui.BIM_PT_mesh,
    ui.BIM_PT_workarounds,
)


addon_keymaps = []


def register():
    bpy.types.Object.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMObjectGeometryProperties)
    bpy.types.Scene.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMGeometryProperties)
    bpy.types.OBJECT_PT_transform.append(ui.BIM_PT_transform)
    bpy.types.VIEW3D_MT_object.append(ui.object_menu)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_object_duplicate_move", "D", "PRESS", shift=True)
        kmi = km.keymap_items.new("bim.override_object_duplicate_move_linked", "D", "PRESS", alt=True)
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        kmi = km.keymap_items.new("bim.override_mode_set_edit", "TAB", "PRESS")
        kmi = km.keymap_items.new("bim.override_object_delete", "X", "PRESS")
        kmi = km.keymap_items.new("bim.override_object_delete", "DEL", "PRESS")
        kmi.properties.confirm = False

        km = wm.keyconfigs.addon.keymaps.new(name="Mesh", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.override_mode_set_object", "TAB", "PRESS")

        km = wm.keyconfigs.addon.keymaps.new(name="Outliner", space_type="OUTLINER")
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        kmi = km.keymap_items.new("bim.override_outliner_delete", "X", "PRESS")
        kmi = km.keymap_items.new("bim.override_outliner_delete", "DEL", "PRESS")


def unregister():
    bpy.types.VIEW3D_MT_object.remove(ui.object_menu)
    bpy.types.OBJECT_PT_transform.remove(ui.BIM_PT_transform)
    del bpy.types.Scene.BIMGeometryProperties
    del bpy.types.Object.BIMGeometryProperties
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
