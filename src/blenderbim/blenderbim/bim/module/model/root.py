import bpy
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.style.data import Data as StyleData


def sync_name(usecase_path, ifc_file, settings):
    if "Name" not in settings["attributes"]:
        return
    obj = IfcStore.get_element(settings["product"].id())
    if not obj:
        return
    if isinstance(obj, bpy.types.Object):
        new_name = "{}/{}".format(settings["product"].is_a(), settings["attributes"]["Name"] or "Unnamed")
    elif isinstance(obj, bpy.types.Material):
        new_name = settings["attributes"]["Name"] or "Unnamed"
        if obj.BIMMaterialProperties.ifc_style_id:
            IfcStore.get_file().by_id(obj.BIMMaterialProperties.ifc_style_id).Name = new_name
            StyleData.load(IfcStore.get_file(), obj.BIMMaterialProperties.ifc_style_id)
    collection = bpy.data.collections.get(obj.name)
    if collection:
        collection.name = new_name
    obj.name = new_name
