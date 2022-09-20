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
    operator.OverrideOutlinerDelete,
    operator.OverridePasteBuffer,
    operator.RemoveConnection,
    operator.RemoveRepresentation,
    operator.SelectConnection,
    operator.SwitchRepresentation,
    operator.UpdateParametricRepresentation,
    operator.UpdateRepresentation,
    prop.BIMGeometryProperties,
    ui.BIM_PT_derived_placements,
    ui.BIM_PT_representations,
    ui.BIM_PT_connections,
    ui.BIM_PT_mesh,
    ui.BIM_PT_workarounds,
)


addon_keymaps = []


def register():
    bpy.types.Scene.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMGeometryProperties)
    bpy.types.OBJECT_PT_transform.append(ui.BIM_PT_transform)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        kmi.properties["name"] = "bim.override_paste_buffer"
        addon_keymaps.append((km, kmi))
        km = wm.keyconfigs.addon.keymaps.new(name="Outliner", space_type="OUTLINER")
        kmi = km.keymap_items.new("bim.override_paste_buffer", "V", "PRESS", ctrl=True)
        kmi.properties["name"] = "bim.override_paste_buffer"
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.types.OBJECT_PT_transform.remove(ui.BIM_PT_transform)
    del bpy.types.Scene.BIMGeometryProperties
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
