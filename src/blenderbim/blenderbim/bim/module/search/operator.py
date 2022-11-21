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

import re
import bpy
import ifcopenshell
import ifcopenshell.util.element
from ifcopenshell.api.group.data import Data
from ifcopenshell.util.selector import Selector
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import close_operator_panel
from blenderbim.bim.module.group import ui
from itertools import cycle
from bpy.types import PropertyGroup, Operator
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


colour_list = [
    (0.651, 0.81, 0.892, 1),
    (0.121, 0.471, 0.706, 1),
    (0.699, 0.876, 0.54, 1),
    (0.199, 0.629, 0.174, 1),
    (0.983, 0.605, 0.602, 1),
    (0.89, 0.101, 0.112, 1),
    (0.989, 0.751, 0.427, 1),
    (0.986, 0.497, 0.1, 1),
    (0.792, 0.699, 0.839, 1),
    (0.414, 0.239, 0.603, 1),
    (0.993, 0.999, 0.6, 1),
    (0.693, 0.349, 0.157, 1),
]


def does_keyword_exist(pattern, string, context):
    string = str(string)
    props = context.scene.BIMSearchProperties
    if props.should_use_regex and props.should_ignorecase and re.search(pattern, string, flags=re.IGNORECASE):
        return True
    elif props.should_use_regex and re.search(pattern, string):
        return True
    elif props.should_ignorecase and string.lower() == pattern.lower():
        return True
    elif string == pattern:
        return True


class SelectGlobalId(Operator):
    """Click to select the objects that match with the given Global ID"""

    bl_idname = "bim.select_global_id"
    bl_label = "Select GlobalId"
    bl_options = {"REGISTER", "UNDO"}
    global_id: StringProperty()

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.BIMSearchProperties
        global_id = self.global_id or props.global_id
        entity = ifc_file.by_guid(global_id)
        obj = tool.Ifc.get_object(entity)
        if not obj:
            self.report({"ERROR"}, "No object found")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"FINISHED"}


class SelectIfcClass(Operator):
    """Click to select all objects that match with the given IFC class"""

    bl_idname = "bim.select_ifc_class"
    bl_label = "Select IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id or obj.is_library_indirect:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if does_keyword_exist(self.ifc_class, element.is_a(), context):
                obj.select_set(True)
        return {"FINISHED"}


class SelectAttribute(Operator):
    """Click to select all objects that match with the given Attribute Name and Value"""

    bl_idname = "bim.select_attribute"
    bl_label = "Select Attribute"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMSearchProperties
        pattern = props.search_attribute_value
        attribute_name = props.search_attribute_name
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if context.scene.BIMSearchProperties.should_ignorecase:
                data = element.get_info()
                value = next((v for k, v in data.items() if k.lower() == attribute_name.lower()), None)
            else:
                value = getattr(element, attribute_name, None)
            if does_keyword_exist(pattern, value, context):
                obj.select_set(True)
        return {"FINISHED"}


class SelectPset(Operator):
    """Click to select all objects that match with the given Pset Name, Properties Name and Value"""

    bl_idname = "bim.select_pset"
    bl_label = "Select Pset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMSearchProperties
        search_pset_name = props.search_pset_name
        search_prop_name = props.search_prop_name
        pattern = props.search_pset_value
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            psets = ifcopenshell.util.element.get_psets(element)
            if search_pset_name == "":
                props = {}
                [props.update(p) for p in psets.values()]
            else:
                props = None
            if context.scene.BIMSearchProperties.should_ignorecase:
                props = props or next((v for k, v in psets.items() if k.lower() == search_pset_name.lower()), {})
                value = str(next((v for k, v in props.items() if k.lower() == search_prop_name.lower()), None))
            else:
                props = props or psets.get(search_pset_name, {})
                value = props.get(search_prop_name, None)
            if does_keyword_exist(pattern, value, context):
                obj.select_set(True)
        return {"FINISHED"}


class ColourByAttribute(Operator):
    """Click to colour different objects according to given Attribute Name"""

    bl_idname = "bim.colour_by_attribute"
    bl_label = "Colour by Attribute"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = IfcStore.get_file()
        colours = cycle(colour_list)
        values = {}
        attribute_name = context.scene.BIMSearchProperties.search_attribute_name
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if context.scene.BIMSearchProperties.should_ignorecase:
                data = element.get_info()
                value = next((v for k, v in data.items() if k.lower() == attribute_name.lower()), None)
            else:
                value = getattr(element, attribute_name, None)
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            areas[0].spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}

    def store_state(self, context):
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            self.transaction_data = {"area": areas[0], "color_type": areas[0].spaces[0].shading.color_type}

    def rollback(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = data["color_type"]

    def commit(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = "OBJECT"


class ColourByPset(Operator):
    """Click to colour different objects according to given Prop Name"""

    bl_idname = "bim.colour_by_pset"
    bl_label = "Colour by Pset"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = IfcStore.get_file()
        colours = cycle(colour_list)
        values = {}
        search_pset_name = context.scene.BIMSearchProperties.search_pset_name
        search_prop_name = context.scene.BIMSearchProperties.search_prop_name
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            psets = ifcopenshell.util.element.get_psets(element)
            if search_pset_name == "":
                props = {}
                [props.update(p) for p in psets.values()]
            else:
                props = None
            if context.scene.BIMSearchProperties.should_ignorecase:
                props = props or next((v for k, v in psets.items() if k.lower() == search_pset_name.lower()), {})
                value = str(next((v for k, v in props.items() if k.lower() == search_prop_name.lower()), None))
            else:
                props = props or psets.get(search_pset_name, {})
                value = str(props.get(search_prop_name, None))
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            areas[0].spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}

    def store_state(self, context):
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            self.transaction_data = {"area": areas[0], "color_type": areas[0].spaces[0].shading.color_type}

    def rollback(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = data["color_type"]

    def commit(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = "OBJECT"


class ColourByClass(Operator):
    """Click to colour different objects according to their IFC Classes"""

    bl_idname = "bim.colour_by_class"
    bl_label = "Colour by Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = IfcStore.get_file()
        colours = cycle(colour_list)
        ifc_classes = {}
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            ifc_class = element.is_a()
            if ifc_class not in ifc_classes:
                ifc_classes[ifc_class] = next(colours)
            obj.color = ifc_classes[ifc_class]
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            areas[0].spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}

    def store_state(self, context):
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            self.transaction_data = {"area": areas[0], "color_type": areas[0].spaces[0].shading.color_type}

    def rollback(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = data["color_type"]

    def commit(self, data):
        if data:
            data["area"].spaces[0].shading.color_type = "OBJECT"


class ResetObjectColours(Operator):
    """Reset the colour of selected objects"""

    bl_idname = "bim.reset_object_colours"
    bl_label = "Reset Colours"

    def execute(self, context):
        for obj in context.selected_objects:
            obj.color = (1, 1, 1, 1)
        return {"FINISHED"}


class ToggleFilterSelection(Operator):
    "Click to select/deselect current selection"
    bl_idname = "bim.toggle_filter_selection"
    bl_label = "Toggle Filter Selection"
    action: EnumProperty(items=(("SELECT", "Select", ""), ("DESELECT", "Deselect", "")))

    def execute(self, context):
        props = bpy.context.scene.BIMSearchProperties
        if self.action == "SELECT":
            self.selecting_actionbool = True
        else:
            self.selecting_actionbool = False
        if props.filter_type == "CLASSES":
            for ifc_class in props.filter_classes:
                ifc_class.is_selected = self.selecting_actionbool
        elif props.filter_type == "BUILDINGSTOREYS":
            for building_storey in props.filter_building_storeys:
                building_storey.is_selected = self.selecting_actionbool
        return {"FINISHED"}


class ActivateIfcClassFilter(Operator):
    """Filter the current selection by IFC class"""

    bl_idname = "bim.activate_ifc_class_filter"
    bl_label = "Filter by Class"

    def invoke(self, context, event):
        props = bpy.context.scene.BIMSearchProperties
        props.filter_classes.clear()
        ifc_types = {}
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            ifc_types.setdefault(element.is_a(), 0)
            ifc_types[element.is_a()] += 1

        for name, total in dict(sorted(ifc_types.items())).items():
            new = props.filter_classes.add()
            new.name = name
            new.total = total
        props.filter_type = "CLASSES"

        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        bpy.context.scene.BIMSearchProperties.filter_classes.clear()
        return {"FINISHED"}

    def draw(self, context):
        self.layout.template_list(
            "BIM_UL_ifc_class_filter",
            "",
            context.scene.BIMSearchProperties,
            "filter_classes",
            context.scene.BIMSearchProperties,
            "filter_classes_index",
            rows=20
            if len(bpy.context.scene.BIMSearchProperties.filter_classes) > 20
            else len(bpy.context.scene.BIMSearchProperties.filter_classes),
        )
        row = self.layout.row(align=True)
        row.operator("bim.toggle_filter_selection", text="Select All").action = "SELECT"
        row.operator("bim.toggle_filter_selection", text="Deselect All").action = "DESELECT"


class ActivateIfcBuildingStoreyFilter(Operator):
    """Filter the current selection by Building Storey"""

    bl_idname = "bim.activate_ifc_building_storey_filter"
    bl_label = "Filter by Building Storey"

    def invoke(self, context, event):
        props = bpy.context.scene.BIMSearchProperties
        props.filter_building_storeys.clear()

        ifc_building_storeys = {}
        for obj in context.selected_objects:
            storey = tool.Misc.get_object_storey(obj)
            if not storey:
                continue
            ifc_building_storeys.setdefault(storey.Name, 0)
            ifc_building_storeys[storey.Name] += 1

        for name, total in dict(sorted(ifc_building_storeys.items())).items():
            new = props.filter_building_storeys.add()
            new.name = name
            new.total = total

        props.filter_type = "BUILDINGSTOREYS"

        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        bpy.context.scene.BIMSearchProperties.filter_building_storeys.clear()
        return {"FINISHED"}

    def draw(self, context):
        self.layout.template_list(
            "BIM_UL_ifc_building_storey_filter",
            "",
            context.scene.BIMSearchProperties,
            "filter_building_storeys",
            context.scene.BIMSearchProperties,
            "filter_building_storeys_index",
            rows=20
            if len(bpy.context.scene.BIMSearchProperties.filter_building_storeys) > 20
            else len(bpy.context.scene.BIMSearchProperties.filter_building_storeys),
        )
        row = self.layout.row(align=True)
        row.operator("bim.toggle_filter_selection", text="Select All").action = "SELECT"
        row.operator("bim.toggle_filter_selection", text="Deselect All").action = "DESELECT"


class UnhideAllElements(Operator):
    """Filter model elements based on selection"""

    bl_idname = "bim.reset_3d_view"
    bl_label = "Reset 3D View"
    bl_idname = "bim.unhide_all_elements"
    bl_label = "Unhide All Elements"

    def execute(self, context):
        for obj in bpy.data.scenes["Scene"].objects:
            obj.hide_set(False)
        return {"FINISHED"}


class FilterModelElements(Operator):
    """Filter model elements based on selection"""

    bl_idname = "bim.filter_model_elements"
    bl_label = "Filter Model Elements"
    option: StringProperty("select|isolate|hide")

    def execute(self, context):
        selector = context.scene.IfcSelectorProperties
        selection = selector.selector_query_syntax if selector.manual_override else self.add_groups(selector)
        selector.selector_query_syntax = selection
        self.update_model_view(context, selection)
        return {"FINISHED"}

    def add_groups(self, selector):
        selection = ""
        for group_index, group in enumerate(selector.groups):
            if group_index != 0:
                selection += " | "
            selection += "(" if len(selector.groups) > 1 else ""
            selection = self.add_queries(selection, group)

            selection += ")" if len(selector.groups) > 1 else ""
        return selection

    def add_queries(self, selection, group):
        for query_index, query in enumerate(group.queries):
            if query_index != 0:
                selection += " & " if query.and_or == "and" else " | "

            if query.selector == "IFC Class":
                active_option = query.active_option.split(": ")[1]
                selection += f".{active_option}"
                selection = self.add_filters(selection, query)

            elif query.selector == "GlobalId":
                selection += f"#{query.value}"

            elif query.selector == "IfcElementType":
                index = int(query.active_sub_option.split(":")[0])
                selection += f"* #{query.sub_options[index].global_id}"

            elif query.selector == "IfcSpatialElement":
                index = int(query.active_sub_option.split(":")[0])
                selection += f"@ #{query.sub_options[index].global_id}"
        return selection

    def add_filters(self, selection, query):
        for f_index, f in enumerate(query.filters):

            if f_index != 0:
                selection += " & " if f.and_or == "and" else " | "
                selection += f".{query.active_option}"

            selection += "["

            if f.selector == "IfcPropertySet":
                selection += f'{f.active_option.split(": ")[1]}.{f.active_sub_option.split(": ")[1]} {"!" if f.negation else ""}="{f.value}"'
            elif f.selector == "Attribute":
                selection += f'{f.attribute} {"!" if f.negation else ""}= "{f.value}"'

            selection += "]"
        return selection

    def update_model_view(self, context, selection):
        query = Selector.parse(IfcStore.file, selection)
        sel_element_ids = [e.id() for e in query]
        bpy.ops.object.select_all(action="DESELECT")

        for obj in bpy.data.scenes["Scene"].objects:
            obj.hide_set(False)  # reset 3d view

            if self.option == "select":
                if obj.BIMObjectProperties.ifc_definition_id in sel_element_ids:
                    obj.select_set(True)
            elif self.option == "isolate":
                if obj.BIMObjectProperties.ifc_definition_id not in sel_element_ids:
                    obj.hide_set(True)
            elif self.option == "hide":
                if obj.BIMObjectProperties.ifc_definition_id in sel_element_ids:
                    obj.hide_set(True)


# This needs to be moved into ui code, I know ;) - vulevukusej
class IfcSelector(Operator):
    """Select elements in model with IFC Selector"""

    bl_idname = "bim.ifc_selector"
    bl_label = "Select elements with IFC Selector"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=800)

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        return {"FINISHED"}

    def draw(self, context):
        from . import ui

        ui.IfcSelectorUI.draw(context, self.layout)


class SaveSelectorQuery(Operator):
    bl_idname = "bim.save_selector_query"
    bl_label = "Save Selector Query"
    save_name: StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "save_name")

    def execute(self, context):
        ifc_selector = context.scene.IfcSelectorProperties
        new = ifc_selector.query_library.add()
        new.name = self.save_name
        new.query = ifc_selector.selector_query_syntax
        return {"FINISHED"}


class OpenQueryLibrary(Operator):
    """Open Query Library"""

    bl_idname = "bim.open_query_library"
    bl_label = "Open Query Library"

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout
        ifc_selector = context.scene.IfcSelectorProperties

        for index, query in enumerate(ifc_selector.query_library):
            row = layout.row(align=True)
            row.prop(query, "query", text=query.name)
            op = row.operator("bim.load_query", icon="SORT_ASC", text="")
            op.index = index

            row.context_pointer_set(name="bim_prop_group", data=ifc_selector)
            op = row.operator("bim.edit_blender_collection", icon="REMOVE", text="")
            op.option = "remove"
            op.collection = "query_library"
            op.index = index

    def execute(self, context):
        return {"FINISHED"}


class LoadQuery(Operator):
    bl_idname = "bim.load_query"
    bl_label = "Load Query"
    index: IntProperty()

    def invoke(self, context, event):
        close_operator_panel(event)
        return self.execute(context)

    def execute(self, context):
        ifc_selector = context.scene.IfcSelectorProperties
        ifc_selector.selector_query_syntax = ifc_selector.query_library[self.index].query
        return {"FINISHED"}


class AddToIfcGroup(Operator):
    bl_idname = "bim.add_to_ifc_group"
    bl_label = "Add to IFC Group"
    group_name: StringProperty(name="Group Name")

    def invoke(self, context, event):
        bpy.ops.bim.load_groups()
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.props = context.scene.BIMGroupProperties
        row = self.layout.row()
        row.operator("bim.add_group")

        self.layout.template_list(
            "BIM_UL_groups",
            "",
            self.props,
            "groups",
            self.props,
            "active_group_index",
        )

        if self.props.active_group_id:
            for attribute in self.props.group_attributes:
                if attribute.name in ["Name", "Description"]:
                    row = self.layout.row(align=True)
                    row.prop(attribute, "string_value", text=attribute.name)

    def execute(self, context):
        active_group_index = self.props.active_group_index
        ifc_definition_id = self.props.groups[active_group_index].ifc_definition_id

        bpy.ops.bim.enable_editing_group(group=ifc_definition_id)

        selector_query_syntax = context.scene.IfcSelectorProperties.selector_query_syntax

        for attribute in self.props.group_attributes:
            if attribute.name == "Description":
                if "*selector*" not in attribute.string_value:
                    attribute.string_value += f" *selector*{selector_query_syntax}*selector*"
                else:
                    new_description = attribute.string_value.split("*selector*")
                    new_description[1] = selector_query_syntax
                    attribute.string_value = "*selector*".join(new_description)

        bpy.ops.bim.edit_group()
        bpy.ops.bim.disable_group_editing_ui()
        return {"FINISHED"}
