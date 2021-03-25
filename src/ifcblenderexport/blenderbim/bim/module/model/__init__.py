import bpy
from . import grid, wall, stair, door, window, slab, opening, pie

classes = (
    grid.BIM_OT_add_object,
    wall.BIM_OT_add_object,
    stair.BIM_OT_add_object,
    door.BIM_OT_add_object,
    window.BIM_OT_add_object,
    slab.BIM_OT_add_object,
    opening.BIM_OT_add_object,
    pie.OpenPieClass,
    pie.PieUpdateContainer,
    pie.PieAddOpening,
    pie.AssignIfcWall,
    pie.AssignIfcSlab,
    pie.AssignIfcStair,
    pie.AssignIfcDoor,
    pie.AssignIfcWindow,
    pie.AssignIfcColumn,
    pie.AssignIfcBeam,
    pie.VIEW3D_MT_PIE_bim,
    pie.VIEW3D_MT_PIE_bim_class,
)

addon_keymaps = []


def register():
    bpy.types.VIEW3D_MT_mesh_add.append(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(wall.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(slab.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(opening.add_object_button)
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("wm.call_menu_pie", "E", "PRESS", shift=True)
        kmi.properties["name"] = "VIEW3D_MT_PIE_bim"
        addon_keymaps.append((km, kmi))


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(wall.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(slab.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(opening.add_object_button)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
