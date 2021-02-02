import bpy
import ifcopenshell


class IfcStore:
    path = ""
    file = None
    schema = None
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
