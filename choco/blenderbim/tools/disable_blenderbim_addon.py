import bpy


bpy.ops.preferences.addon_disable(module='blenderbim')
bpy.ops.wm.save_userpref()

print("disabled blenderbim addon successfully.")

