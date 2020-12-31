import bpy
import ifcopenshell


class IfcStore:
    path = ""
    file = None
    pset_template_path = ""
    pset_template_file = None

    @staticmethod
    def get_file():
        if IfcStore.file is None:
            IfcStore.path = bpy.context.scene.BIMProperties.ifc_file
            if IfcStore.path:
                IfcStore.file = ifcopenshell.open(IfcStore.path)
        return IfcStore.file
