import bpy
import json
import math
import ifcopenshell
import ifcopenshell.util.attribute
from mathutils import geometry
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


def draw_attributes(props, layout):
    for attribute in props:
        row = layout.row(align=True)
        if attribute.data_type == "string":
            row.prop(attribute, "string_value", text=attribute.name)
        elif attribute.data_type == "boolean":
            row.prop(attribute, "bool_value", text=attribute.name)
        elif attribute.data_type == "integer":
            row.prop(attribute, "int_value", text=attribute.name)
        elif attribute.data_type == "float":
            row.prop(attribute, "float_value", text=attribute.name)
        elif attribute.data_type == "enum":
            row.prop(attribute, "enum_value", text=attribute.name)
        if attribute.is_optional:
            row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


def import_attributes(ifc_class, props, data, callback=None):
    for attribute in IfcStore.get_schema().declaration_by_name(ifc_class).all_attributes():
        data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
        if data_type == "entity" or (isinstance(data_type, tuple) and "entity" in ".".join(data_type)):
            continue
        new = props.add()
        new.name = attribute.name()
        new.is_null = data[attribute.name()] is None
        new.is_optional = attribute.optional()
        new.data_type = data_type if isinstance(data_type, str) else ""
        is_handled_by_callback = callback(attribute.name(), new, data) if callback else None
        if is_handled_by_callback:
            pass  # Our job is done
        elif is_handled_by_callback is False:
            props.remove(len(props) - 1)
        elif data_type == "string":
            new.string_value = "" if new.is_null else data[attribute.name()]
        elif data_type == "boolean":
            new.bool_value = False if new.is_null else data[attribute.name()]
        elif data_type == "integer":
            new.int_value = 0 if new.is_null else data[attribute.name()]
        elif data_type == "float":
            new.float_value = 0.0 if new.is_null else data[attribute.name()]
        elif data_type == "enum":
            new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
            if data[attribute.name()]:
                new.enum_value = data[attribute.name()]


def export_attributes(props, callback=None):
    attributes = {}
    for attribute in props:
        is_handled_by_callback = callback(attributes, attribute) if callback else False
        if attribute.is_null:
            attributes[attribute.name] = None
        elif is_handled_by_callback:
            pass  # Our job is done
        elif attribute.data_type == "string":
            attributes[attribute.name] = attribute.string_value
        elif attribute.data_type == "boolean":
            attributes[attribute.name] = attribute.bool_value
        elif attribute.data_type == "integer":
            attributes[attribute.name] = attribute.int_value
        elif attribute.data_type == "float":
            attributes[attribute.name] = attribute.float_value
        elif attribute.data_type == "enum":
            attributes[attribute.name] = attribute.enum_value
    return attributes
