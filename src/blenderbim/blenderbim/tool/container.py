import bpy
import blenderbim.core.tool
import blenderbim.tool as tool

class Container(blenderbim.core.tool.Container):
    @classmethod
    def can_contain(cls, structure_obj, element_obj):
        structure = tool.Ifc.get_entity(structure_obj)
        element = tool.Ifc.get_entity(element_obj)
        if not structure or not element:
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not structure.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not structure.is_a("IfcSpatialElement"):
                return False
        if not element.is_a("IfcElement"):
            return False
        return True

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = True

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = False

    @classmethod
    def import_containers(cls, parent=None):
        props = bpy.context.scene.BIMSpatialProperties
        props.containers.clear()

        if not parent:
            parent = tool.Ifc.get().by_type("IfcProject")[0]

        props.active_container_id = parent.id()

        for rel in parent.IsDecomposedBy or []:
            for element in rel.RelatedObjects:
                new = props.containers.add()
                new.name = element.Name or "Unnamed"
                new.long_name = element.LongName or ""
                new.has_decomposition = bool(element.IsDecomposedBy)
                new.ifc_definition_id = element.id()
