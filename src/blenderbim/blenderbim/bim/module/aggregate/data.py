import bpy
import blenderbim.tool as tool
import ifcopenshell.util.element


def refresh():
    AggregateData.is_loaded = False


class AggregateData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_aggregate": cls.has_aggregate(),
            "label": cls.get_label(),
            "relating_object_id": cls.get_relating_object_id(),
        }
        cls.is_loaded = True

    @classmethod
    def has_aggregate(cls):
        return ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))

    @classmethod
    def get_label(cls):
        aggregate = ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))
        if aggregate:
            return f"{aggregate.is_a()}/{aggregate.Name or ''}"

    @classmethod
    def get_relating_object_id(cls):
        aggregate = ifcopenshell.util.element.get_aggregate(tool.Ifc.get_entity(bpy.context.active_object))
        if aggregate:
            return aggregate.id()
