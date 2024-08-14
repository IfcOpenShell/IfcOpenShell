# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# from datetime import date
import bpy
import json
import math
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell.util.doc import get_attribute_doc, get_predefined_type_doc, get_property_doc
from mathutils import geometry
from mathutils import Vector
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from typing import Optional, Callable, Any, Union


def draw_attributes(props, layout, copy_operator=None, popup_active_attribute=None):
    """you can set attribute active in popup with `active_attribute`
    meaning you will be able to type into attribute's field without having to click
    on it first
    """
    for attribute in props:
        row = layout.row(align=True)
        if attribute == popup_active_attribute:
            row.activate_init = True
        draw_attribute(attribute, row, copy_operator)


def draw_attribute(attribute, layout, copy_operator=None):
    value_name = attribute.get_value_name()
    if not value_name:
        layout.label(text=attribute.name)
        return
    if value_name == "enum_value":
        prop_with_search(layout, attribute, "enum_value", text=attribute.name)
    elif value_name == "filepath_value":
        attribute.filepath_value.layout_file_select(layout, filter_glob=attribute.filter_glob, text=attribute.name)
    elif attribute.name in ["ScheduleDuration", "ActualDuration", "FreeFloat", "TotalFloat"]:
        propis = bpy.context.scene.BIMWorkScheduleProperties
        for item in propis.durations_attributes:
            if item.name == attribute.name:
                duration_props = item
                layout.label(text=attribute.name)
                layout.prop(duration_props, "years", text="Y")
                layout.prop(duration_props, "months", text="M")
                layout.prop(duration_props, "days", text="D")
                layout.prop(duration_props, "hours", text="H")
                layout.prop(duration_props, "minutes", text="Min")
                layout.prop(duration_props, "seconds", text="S")
                break
    else:
        layout.prop(
            attribute,
            value_name,
            text=attribute.name,
        )

    if attribute.is_uri:
        op = layout.operator("bim.select_uri_attribute", text="", icon="FILE_FOLDER")
        op.data_path = attribute.path_from_id("string_value")
    if attribute.is_optional:
        layout.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")

    if attribute.name == "GlobalId":
        layout.operator("bim.generate_global_id", icon="FILE_REFRESH", text="")

    if copy_operator:
        op = layout.operator(f"{copy_operator}", text="", icon="COPYDOWN")
        op.name = attribute.name


def import_attributes(ifc_class, props, data, callback=None):
    for attribute in IfcStore.get_schema().declaration_by_name(ifc_class).all_attributes():
        import_attribute(attribute, props, data, callback=callback)


# A more elegant attribute importer signature, intended to supersede import_attributes
def import_attributes2(
    element: Union[str, ifcopenshell.entity_instance],
    props: bpy.types.PropertyGroup,
    callback: Optional[Callable] = None,
) -> None:
    if isinstance(element, str):
        attributes = tool.Ifc.schema().declaration_by_name(element).as_entity().all_attributes()
        info = {a.name(): None for a in attributes}
        info["type"] = element
    else:
        attributes = element.wrapped_data.declaration().as_entity().all_attributes()
        info = element.get_info()
    for attribute in attributes:
        import_attribute(attribute, props, info, callback=callback)


def import_attribute(attribute, props, data, callback=None):
    data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
    if isinstance(data_type, tuple) or data_type == "entity":
        callback(attribute.name(), None, data) if callback else None
        return
    new = props.add()
    new.name = attribute.name()
    new.is_null = data[attribute.name()] is None
    new.is_optional = attribute.optional()
    new.data_type = data_type if isinstance(data_type, str) else ""
    new.ifc_class = data["type"]
    is_handled_by_callback = callback(attribute.name(), new, data) if callback else None

    if is_handled_by_callback:
        pass  # Our job is done
    elif is_handled_by_callback is False:
        props.remove(len(props) - 1)
    elif data_type == "string":
        new.string_value = "" if new.is_null else str(data[attribute.name()]).replace("\n", "\\n")
        if attribute.type_of_attribute().declared_type().name() == "IfcURIReference":
            new.is_uri = True
    elif data_type == "boolean":
        new.bool_value = False if new.is_null else bool(data[attribute.name()])
    elif data_type == "integer":
        new.int_value = 0 if new.is_null else int(data[attribute.name()])
    elif data_type == "float":
        new.float_value = 0.0 if new.is_null else float(data[attribute.name()])
    elif data_type == "enum":
        enum_items = ifcopenshell.util.attribute.get_enum_items(attribute)
        new.enum_items = json.dumps(enum_items)
        add_attribute_enum_items_descriptions(new, enum_items)
        if data[new.name]:
            new.enum_value = data[new.name]
    add_attribute_description(new, data)
    add_attribute_min_max(new)


ATTRIBUTE_MIN_MAX_CONSTRAINTS = {"IfcMaterialLayer": {"Priority": {"value_min": 0, "value_max": 100}}}


def add_attribute_min_max(attribute_blender):
    if attribute_blender.ifc_class in ATTRIBUTE_MIN_MAX_CONSTRAINTS:
        constraints = ATTRIBUTE_MIN_MAX_CONSTRAINTS[attribute_blender.ifc_class].get(attribute_blender.name, {})
        for constraint, value in constraints.items():
            setattr(attribute_blender, constraint, value)
            setattr(attribute_blender, constraint + "_constraint", True)


def add_attribute_enum_items_descriptions(attribute_blender, enum_items):
    attribute_blender.enum_descriptions.clear()
    if isinstance(enum_items, dict):
        enum_items = enum_items.keys()
    version = tool.Ifc.get_schema()
    for enum_item in enum_items:
        new_enum_description = attribute_blender.enum_descriptions.add()
        try:
            description = get_predefined_type_doc(version, attribute_blender.ifc_class, enum_item) or ""
        except KeyError:  # TODO this only supports predefined type enums. Add support for other types of enums ?
            description = ""
        new_enum_description.name = description


def add_attribute_description(attribute_blender, attribute_ifc=None):
    if not attribute_blender.name:
        return
    version = tool.Ifc.get_schema()
    description = ""
    try:
        description = get_attribute_doc(version, attribute_blender.ifc_class, attribute_blender.name)
    except RuntimeError:  # It's not an Entity Attribute. Let's try a Property Set attribute.
        doc = get_property_doc(version, attribute_blender.ifc_class, attribute_blender.name)
        if doc:
            description = doc.get("description", "")
        else:  # It's a custom property set. Check if this attribute has a description
            if attribute_ifc is not None:
                description = getattr(attribute_ifc, "Description", "")
    if description:
        attribute_blender.description = description


def export_attributes(props, callback: Optional[Callable] = None) -> dict[str, Any]:
    attributes = {}
    for prop in props:
        is_handled_by_callback = callback(attributes, prop) if callback else False
        if is_handled_by_callback:
            continue  # Our job is done
        attributes[prop.name] = prop.get_value()
    return attributes


def prop_with_search(layout, data, prop_name, **kwargs):
    # kwargs are layout.prop arguments (text, icon, etc.)
    row = layout.row(align=True)
    row.prop(data, prop_name, **kwargs)
    try:
        if len(get_enum_items(data, prop_name)) > 10:
            # Magick courtesy of https://blender.stackexchange.com/a/203443/86891
            row.context_pointer_set(name="data", data=data)
            op = row.operator("bim.enum_property_search", text="", icon="VIEWZOOM")
            op.prop_name = prop_name
    except TypeError:  # Prop is not iterable
        pass


def get_enum_items(data, prop_name, context=None):
    # Retrieve items from a dynamic EnumProperty, which is otherwise not supported
    # Or throws an error in the console when the items callback returns an empty list
    # See https://blender.stackexchange.com/q/215781/86891
    prop = data.__annotations__[prop_name]
    items = prop.keywords.get("items")
    if items is None:
        return
    if not isinstance(items, (list, tuple)):
        # items are retrieved through a callback, not a static list :
        items = items(data, context or bpy.context)
    return items


def convert_property_group_from_si(property_group, skip_props=()):
    """Method converts property group values from si to current ifc project units

    based on default values of the properties.

    List of properties to skip can be supplied in `skip_props`."""
    conversion_k = 1.0 / ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    skip_props = ("rna_type", "name") + skip_props
    for prop_name in property_group.bl_rna.properties.keys():
        if prop_name in skip_props:
            continue
        prop_value = tool.Blender.get_blender_prop_default_value(property_group, prop_name)
        if type(prop_value) is float:
            prop_value = prop_value * conversion_k
        elif type(prop_value) is bpy.types.bpy_prop_array:
            prop_value = [el * conversion_k for el in prop_value]
        setattr(property_group, prop_name, prop_value)


def draw_filter(layout, filter_groups, data, module):
    if not data.is_loaded:
        data.load()

    sprops = bpy.context.scene.BIMSearchProperties

    if tool.Ifc.get():
        row = layout.row(align=True)
        row.label(text=f"{len(data.data['saved_searches'])} Saved Searches")

        if data.data["saved_searches"]:
            row.operator("bim.load_search", text="", icon="IMPORT").module = module
        row.operator("bim.save_search", text="", icon="EXPORT").module = module

    row = layout.row(align=True)
    row.operator("bim.add_filter_group", text="Add Search Group", icon="ADD").module = module
    row.operator("bim.edit_filter_query", text="", icon="FILTER").module = module

    for i, filter_group in enumerate(filter_groups):
        box = layout.box()

        row = box.row(align=True)
        row.prop(sprops, "facet", text="")
        op = row.operator("bim.add_filter", text="Add Filter", icon="ADD")
        op.type = sprops.facet
        op.index = i
        op.module = module
        op = row.operator("bim.remove_filter_group", text="", icon="X")
        op.index = i
        op.module = module

        for j, ifc_filter in enumerate(filter_group.filters):
            if ifc_filter.type == "entity":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="FILE_3D")
            elif ifc_filter.type == "attribute":
                row = box.row(align=True)
                row.prop(ifc_filter, "name", text="", icon="COPY_ID")
                row.prop(ifc_filter, "value", text="")
            elif ifc_filter.type == "type":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="FILE_VOLUME")
            elif ifc_filter.type == "material":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="MATERIAL")
            elif ifc_filter.type == "property":
                row = box.row(align=True)
                row.prop(ifc_filter, "pset", text="", icon="PROPERTIES")
                row.prop(ifc_filter, "name", text="")
                row.prop(ifc_filter, "comparison", text="")
                row.prop(ifc_filter, "value", text="")
            elif ifc_filter.type == "classification":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="OUTLINER")
            elif ifc_filter.type == "location":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="PACKAGE")
            elif ifc_filter.type == "group":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="OUTLINER_COLLECTION")
            elif ifc_filter.type == "parent":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="FILE_PARENT")
            elif ifc_filter.type == "query":
                row = box.row(align=True)
                row.prop(ifc_filter, "name", text="", icon="POINTCLOUD_DATA")
                row.prop(ifc_filter, "value", text="")
            elif ifc_filter.type == "instance":
                row = box.row(align=True)
                row.prop(ifc_filter, "value", text="", icon="GRIP")
                op = row.operator("bim.select_filter_elements", text="", icon="EYEDROPPER")
                op.group_index = i
                op.index = j
                op.module = module
            op = row.operator("bim.remove_filter", text="", icon="X")
            op.group_index = i
            op.index = j
            op.module = module
