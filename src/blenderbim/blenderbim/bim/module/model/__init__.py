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
from . import handler, prop, ui, grid, product, wall, slab, stair, opening, pie, workspace, profile

classes = (
    product.AddEmptyType,
    product.AddConstrTypeInstance,
    product.DisplayConstrTypes,
    product.AlignProduct,
    product.DynamicallyVoidProduct,
    workspace.Hotkey,
    wall.JoinWall,
    wall.AlignWall,
    wall.FlipWall,
    wall.SplitWall,
    opening.AddElementOpening,
    profile.ExtendProfile,
    prop.BIMModelProperties,
    prop.ConstrTypeInfo,
    ui.BIM_PT_authoring,
    ui.DisplayConstrTypesUI,
    ui.HelpConstrTypes,
    grid.BIM_OT_add_object,
    stair.BIM_OT_add_object,
    opening.BIM_OT_add_object,
    pie.OpenPieClass,
    pie.PieUpdateContainer,
    pie.PieAddOpening,
    pie.VIEW3D_MT_PIE_bim,
    pie.VIEW3D_MT_PIE_bim_class,
)

addon_keymaps = []


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.BimTool, after={"builtin.scale_cage"}, separator=True, group=True)
    bpy.types.Scene.BIMModelProperties = bpy.props.PointerProperty(type=prop.BIMModelProperties)
    bpy.types.Scene.ConstrTypeInfo = bpy.props.CollectionProperty(type=prop.ConstrTypeInfo)
    bpy.types.VIEW3D_MT_mesh_add.append(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(opening.add_object_button)
    bpy.types.VIEW3D_MT_add.append(product.add_empty_type_button)
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
    del bpy.types.Scene.ConstrTypeInfo
    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.types.VIEW3D_MT_mesh_add.remove(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(opening.add_object_button)
    bpy.types.VIEW3D_MT_add.remove(product.add_empty_type_button)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
