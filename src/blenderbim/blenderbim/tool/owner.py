import bpy
import blenderbim.core.tool
import blenderbim.tool as tool

class Owner(blenderbim.core.tool.Owner):
    @classmethod
    def set_user(cls, user):
        bpy.context.scene.BIMOwnerProperties.active_user_id = user.id()

    @classmethod
    def get_user(cls):
        if bpy.context.scene.BIMOwnerProperties.active_user_id:
            return tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_user_id)

    @classmethod
    def clear_user(cls):
        bpy.context.scene.BIMOwnerProperties.active_user_id = 0
