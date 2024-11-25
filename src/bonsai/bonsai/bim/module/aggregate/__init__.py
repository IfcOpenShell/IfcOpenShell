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

classes = (
    operator.BIM_OT_add_aggregate,
    operator.BIM_OT_add_part_to_object,
    operator.BIM_OT_aggregate_assign_object,
    operator.BIM_OT_disable_editing_aggregate,
    operator.BIM_OT_enable_editing_aggregate,
    operator.BIM_OT_select_aggregate,
    operator.BIM_OT_select_parts,
    operator.BIM_OT_aggregate_unassign_object,
    operator.BIM_OT_break_link_to_other_aggregates,
    operator.BIM_OT_select_linked_aggregates,
    operator.BIM_OT_mode_set_aggregate,
    operator.BIM_OT_disable_mode_set_aggregate,
    operator.BIM_OT_toggle_mode_set_aggregate,
    prop.BIMObjectAggregateProperties,
    prop.NotEditingObjects,
    prop.BIMAggregateProperties,
    ui.BIM_PT_aggregate,
    ui.BIM_PT_linked_aggregate,
)

addon_keymaps = []

def register():
    bpy.types.Object.BIMObjectAggregateProperties = bpy.props.PointerProperty(type=prop.BIMObjectAggregateProperties)
    bpy.types.Scene.BIMAggregateProperties = bpy.props.PointerProperty(type=prop.BIMAggregateProperties)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
        kmi = km.keymap_items.new("bim.toggle_mode_set_aggregate", "TAB", "PRESS", ctrl=True)
        addon_keymaps.append((km, kmi))


def unregister():
    del bpy.types.Object.BIMObjectAggregateProperties
    del bpy.types.Scene.BIMAggregateProperties
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
