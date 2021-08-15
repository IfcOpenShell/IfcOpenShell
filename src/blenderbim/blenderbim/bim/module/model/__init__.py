import bpy
from . import handler, prop, ui, grid, product, wall, slab, stair, door, window, opening, pie, workspace

classes = (
    product.AddEmptyType,
    product.AddTypeInstance,
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
    ui.BIM_PT_authoring,
    ui.BIM_PT_authoring_architectural,
    ui.BIM_PT_misc_utilities,
    grid.BIM_OT_add_object,
    stair.BIM_OT_add_object,
    door.BIM_OT_add_object,
    window.BIM_OT_add_object,
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
    bpy.types.VIEW3D_MT_mesh_add.append(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(window.add_object_button)
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
    bpy.app.handlers.load_post.remove(handler.load_post)
    bpy.types.VIEW3D_MT_mesh_add.remove(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(opening.add_object_button)
    bpy.types.VIEW3D_MT_add.remove(product.add_empty_type_button)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
