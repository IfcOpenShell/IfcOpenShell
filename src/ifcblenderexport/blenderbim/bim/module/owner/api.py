import bpy
import addon_utils
import blenderbim.bim.module.owner.create_owner_history as create_owner_history_usecase
from blenderbim.bim.ifc import IfcStore


def create_owner_history(change_action=None):
    file = IfcStore.get_file()
    return create_owner_history_usecase.Usecase(
        file,
        {
            "person": file.by_id(int(bpy.context.scene.BIMOwnerProperties.user_person)),
            "organisation": file.by_id(int(bpy.context.scene.BIMOwnerProperties.user_organisation)),
            "ApplicationIdentifier": "BlenderBIM",
            "ApplicationFullName": "BlenderBIM Add-on",
            "Version": get_application_version(),
            "ChangeAction": change_action or "ADDED",
        },
    ).execute()


def get_application_version():
    return ".".join(
        [
            str(x)
            for x in [
                addon.bl_info.get("version", (-1, -1, -1))
                for addon in addon_utils.modules()
                if addon.bl_info["name"] == "BlenderBIM"
            ][0]
        ]
    )
