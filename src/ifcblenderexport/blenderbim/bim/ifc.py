import bpy
import ifcopenshell
import blenderbim.bim.handler


class IfcStore:
    path = ""
    file = None
    schema = None
    id_map = {}
    guid_map = {}
    pset_template_path = ""
    pset_template_file = None

    @staticmethod
    def get_file():
        if IfcStore.file is None:
            IfcStore.path = bpy.context.scene.BIMProperties.ifc_file
            if IfcStore.path:
                try:
                    IfcStore.file = ifcopenshell.open(IfcStore.path)
                except:
                    IfcStore.file
        return IfcStore.file

    @staticmethod
    def get_schema():
        if IfcStore.file is None:
            return
        elif IfcStore.schema is None:
            IfcStore.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(IfcStore.file.schema)
        return IfcStore.schema

    @staticmethod
    def link_element(element, obj):
        IfcStore.id_map[element.id()] = obj
        if hasattr(element, "GlobalId"):
            IfcStore.guid_map[element.GlobalId] = obj
        obj.BIMObjectProperties.ifc_definition_id = element.id()
        blenderbim.bim.handler.subscribe_to(obj, "mode", blenderbim.bim.handler.mode_callback)
        blenderbim.bim.handler.subscribe_to(obj, "name", blenderbim.bim.handler.name_callback)

    @staticmethod
    def unlink_element(element, obj=None):
        del IfcStore.id_map[element.id()]
        if hasattr(element, "GlobalId"):
            del IfcStore.guid_map[element.GlobalId]
        if obj:
            obj.BIMObjectProperties.ifc_definition_id = 0
