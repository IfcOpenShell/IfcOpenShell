import bpy


bpy.ops.preferences.addon_enable(module='blenderbim')
bpy.ops.wm.save_userpref()

print("enabled blenderbim addon successfully.")

