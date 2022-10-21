# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

# from datetime import date
import bpy
import json
import math
import zipfile
import ifcopenshell
import ifcopenshell.util.attribute
from blenderbim.bim.prop import get_ifc_entity_doc_url
from mathutils import geometry
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore
import blenderbim.tool as tool


def draw_attributes(props, layout, copy_operator=None):
    for attribute in props:
        row = layout.row(align=True)
        draw_attribute(attribute, row, copy_operator)


def draw_attribute(attribute, layout, copy_operator=None):
    value_name = attribute.get_value_name()
    if not value_name:
        layout.label(text=attribute.name)
        return
    if value_name == "enum_value":
        prop_with_search(layout, attribute, "enum_value", text=attribute.name)
    else:
        layout.prop(
            attribute,
            value_name,
            text=attribute.name,
        )
    if "ScheduleDuration" in attribute.name:
        layout.prop(bpy.context.scene.BIMDuration, "duration_days", text="D")
        layout.prop(bpy.context.scene.BIMDuration, "duration_hours", text="H")
        layout.prop(bpy.context.scene.BIMDuration, "duration_minutes", text="M")

    if attribute.is_optional:
        layout.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")
    if copy_operator:
        op = layout.operator(f"{copy_operator}", text="", icon="COPYDOWN")
        op.name = attribute.name
    if attribute.is_uri:
        op = layout.operator("bim.select_uri_attribute", text="", icon="FILE_FOLDER")
        op.data_path = attribute.path_from_id("string_value")


def import_attributes(ifc_class, props, data, callback=None):
    for attribute in IfcStore.get_schema().declaration_by_name(ifc_class).all_attributes():
        import_attribute(attribute, props, data, callback=callback)


# A more elegant attribute importer signature, intended to supersede import_attributes
def import_attributes2(element, props, callback=None):
    for attribute in element.wrapped_data.declaration().as_entity().all_attributes():
        import_attribute(attribute, props, element.get_info(), callback=callback)


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
    is_handled_by_callback = callback(attribute.name(), new, data) if callback else None

    if is_handled_by_callback:
        pass  # Our job is done
    elif is_handled_by_callback is False:
        props.remove(len(props) - 1)
    elif data_type == "string":
        new.string_value = "" if new.is_null else data[attribute.name()]
        if attribute.type_of_attribute().declared_type().name() == "IfcURIReference":
            new.is_uri = True
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
    for prop in props:
        is_handled_by_callback = callback(attributes, prop) if callback else False
        if is_handled_by_callback:
            continue  # Our job is done
        attributes[prop.name] = prop.get_value()
    return attributes


def prop_with_search(layout, data, prop_name, **kwargs):
    # kwargs are layout.prop arguments (text, icon, etc.)
    row = layout.row(align=True)
    # Magick courtesy of https://blender.stackexchange.com/a/203443/86891
    row.context_pointer_set(name="data", data=data)
    row.prop(data, prop_name, **kwargs)
    op = row.operator("bim.enum_property_search", text="", icon="VIEWZOOM")
    op.prop_name = prop_name

    add_entity_url_button(row, getattr(data, prop_name))


def add_entity_url_button(layout, entity):
    if entity:
        try:
            url = get_ifc_entity_doc_url(entity)
        except KeyError:
            # TODO : support attributes, pset, etc.
            pass
        else:
            if url:
                url_op = layout.operator("bim.open_webbrowser", icon="INFO", text="")
                url_op.url = url


def get_enum_items(data, prop_name, context):
    # Retrieve items from a dynamic EnumProperty, which is otherwise not supported
    # Or throws an error in the console when the items callback returns an empty list
    # See https://blender.stackexchange.com/q/215781/86891
    prop = data.__annotations__[prop_name]
    items = prop.keywords.get("items")
    if items is None:
        return
    if not isinstance(items, (list, tuple)):
        # items are retrieved through a callback, not a static list :
        items = items(data, context)
    return items


def get_obj_ifc_definition_id(context, obj, obj_type):
    if obj_type == "Object":
        return bpy.data.objects.get(obj).BIMObjectProperties.ifc_definition_id
    elif obj_type == "Material":
        return bpy.data.materials.get(obj).BIMObjectProperties.ifc_definition_id
    elif obj_type == "Task":
        return context.scene.BIMTaskTreeProperties.tasks[
            context.scene.BIMWorkScheduleProperties.active_task_index
        ].ifc_definition_id
    elif obj_type == "Cost":
        return context.scene.BIMCostProperties.cost_items[
            context.scene.BIMCostProperties.active_cost_item_index
        ].ifc_definition_id
    elif obj_type == "Resource":
        return context.scene.BIMResourceTreeProperties.resources[
            context.scene.BIMResourceProperties.active_resource_index
        ].ifc_definition_id
    elif obj_type == "Profile":
        return context.scene.BIMProfileProperties.profiles[
            context.scene.BIMProfileProperties.active_profile_index
        ].ifc_definition_id
    elif obj_type == "WorkSchedule":
        return context.scene.BIMWorkScheduleProperties.active_work_schedule_id


# hack to close popup
# https://blender.stackexchange.com/a/202576/130742
def close_operator_panel(event):
    x, y = event.mouse_x, event.mouse_y
    bpy.context.window.cursor_warp(10, 10)
    move_back = lambda: bpy.context.window.cursor_warp(x, y)
    bpy.app.timers.register(move_back, first_interval=0.01)


class IfcHeaderExtractor:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract(self):
        extension = self.filepath.split(".")[-1]
        if extension.lower() == "ifc":
            with open(self.filepath) as ifc_file:
                return self.extract_ifc_spf(ifc_file)
        elif extension.lower() == "ifczip":
            return self.extract_ifc_zip()

    def extract_ifc_spf(self, ifc_file):
        # https://www.steptools.com/stds/step/IS_final_p21e3.html#clause-8
        data = {}
        max_lines_to_parse = 50
        for _ in range(max_lines_to_parse):
            line = next(ifc_file)
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            if line.startswith("FILE_DESCRIPTION"):
                for i, part in enumerate(line.split("'")):
                    if i == 1:
                        data["description"] = part
                    elif i == 3:
                        data["implementation_level"] = part
            elif line.startswith("FILE_NAME"):
                for i, part in enumerate(line.split("'")):
                    if i == 1:
                        data["name"] = part
                    elif i == 3:
                        data["time_stamp"] = part
            elif line.startswith("FILE_SCHEMA"):
                data["schema_name"] = line.split("'")[1]
                break
        return data

    def extract_ifc_zip(self):
        archive = zipfile.ZipFile(self.filepath, "r")
        return self.extract_ifc_spf(archive.open(archive.filelist[0]))
