import bpy
import ifcopenshell


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
                IfcStore.file = ifcopenshell.open(IfcStore.path)
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
        IfcStore.guid_map[element.GlobalId] = obj
        obj.BIMObjectProperties.ifc_definition_id = element.id()

    @staticmethod
    def unlink_element(element, obj=None):
        del IfcStore.id_map[element.id()]
        del IfcStore.guid_map[element.GlobalId]
        if obj:
            obj.BIMObjectProperties.ifc_definition_id = 0
