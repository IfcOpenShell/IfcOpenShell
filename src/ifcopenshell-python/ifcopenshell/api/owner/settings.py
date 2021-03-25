# import bpy
# import addon_utils

settings = {
    "person": None,
    "organisation": None,
    "ApplicationIdentifier": "",
    "ApplicationFullName": "",
    "Version": "",
    "ChangeAction": "NOTDEFINED",
}


# settings = {
#     "person": file.by_id(int(bpy.context.scene.BIMOwnerProperties.user_person)),
#     "organisation": file.by_id(int(bpy.context.scene.BIMOwnerProperties.user_organisation)),
#     "ApplicationIdentifier": "BlenderBIM",
#     "ApplicationFullName": "BlenderBIM Add-on",
#     "Version": get_application_version(),
# }
# 
# 
# def get_application_version():
#     return ".".join(
#         [
#             str(x)
#             for x in [
#                 addon.bl_info.get("version", (-1, -1, -1))
#                 for addon in addon_utils.modules()
#                 if addon.bl_info["name"] == "BlenderBIM"
#             ][0]
#         ]
#     )
