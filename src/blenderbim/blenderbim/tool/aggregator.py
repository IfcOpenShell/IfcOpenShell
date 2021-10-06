import blenderbim.core.tool
import blenderbim.tool as tool


class Aggregator(blenderbim.core.tool.Aggregator):
    @classmethod
    def enable_editing(cls, obj):
        obj.BIMObjectAggregateProperties.is_editing = True

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMObjectAggregateProperties.is_editing = False

    @classmethod
    def can_aggregate(cls, relating_obj, related_obj):
        relating_object = tool.Ifc.get_entity(relating_obj)
        related_object = tool.Ifc.get_entity(related_obj)
        if not relating_object or not related_object:
            return False
        if relating_object.is_a("IfcElement") and related_object.is_a("IfcElement"):
            if relating_obj.data:
                return False
            return True
        if tool.Ifc.get_schema() == "IFC2X3":
            if relating_object.is_a("IfcSpatialStructureElement") and related_object.is_a("IfcSpatialStructureElement"):
                return True
            if relating_object.is_a("IfcProject") and related_object.is_a("IfcSpatialStructureElement"):
                return True
        else:
            if relating_object.is_a("IfcSpatialElement") and related_object.is_a("IfcSpatialElement"):
                return True
            if relating_object.is_a("IfcProject") and related_object.is_a("IfcSpatialElement"):
                return True
        return False
