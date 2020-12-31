import bpy
from . import grid, wall, stair, door, window, slab, opening

classes = (
    grid.BIM_OT_add_object,
    wall.BIM_OT_add_object,
    stair.BIM_OT_add_object,
    door.BIM_OT_add_object,
    window.BIM_OT_add_object,
    slab.BIM_OT_add_object,
    opening.BIM_OT_add_object,
)


def register():
    bpy.types.VIEW3D_MT_mesh_add.append(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(wall.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(slab.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.append(opening.add_object_button)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(grid.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(wall.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(stair.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(door.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(window.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(slab.add_object_button)
    bpy.types.VIEW3D_MT_mesh_add.remove(opening.add_object_button)
