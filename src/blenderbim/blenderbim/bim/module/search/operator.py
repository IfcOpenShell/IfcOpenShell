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
import json
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.selector
from ifcopenshell.util.selector import Selector
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import close_operator_panel
from blenderbim.bim.module.group import ui
import blenderbim.core.search as core
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


class AddFilterGroup(Operator):
    bl_idname = "bim.add_filter_group"
    bl_label = "Add Filter Group"
    module: StringProperty()

    def execute(self, context):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties
        props.filter_groups.add()
        return {"FINISHED"}


class RemoveFilterGroup(Operator):
    bl_idname = "bim.remove_filter_group"
    bl_label = "Remove Filter Group"
    index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties
        props.filter_groups.remove(self.index)
        return {"FINISHED"}


class RemoveFilter(Operator):
    bl_idname = "bim.remove_filter"
    bl_label = "Remove Filter Group"
    group_index: IntProperty()
    index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties
        props.filter_groups[self.group_index].filters.remove(self.index)
        return {"FINISHED"}


class AddFilter(Operator):
    bl_idname = "bim.add_filter"
    bl_label = "Add Filter"
    index: IntProperty()
    type: StringProperty()
    module: StringProperty()

    def execute(self, context):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties
        new = props.filter_groups[self.index].filters.add()
        new.type = self.type
        return {"FINISHED"}


class SelectFilterElements(bpy.types.Operator):
    bl_idname = "bim.select_filter_elements"
    bl_label = "Select Filter Elements"
    bl_options = {"REGISTER", "UNDO"}
    group_index: IntProperty()
    index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties
        global_ids = []
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                global_id = getattr(element, "GlobalId", None)
                if global_id:
                    global_ids.append(global_id)
        if len(global_ids) > 50:
            # Too much to store in a string property
            name = "globalid-filter-" + ifcopenshell.guid.new()
            text_data = bpy.data.texts.new(name)
            text_data.from_string(",".join(global_ids))
            props.filter_groups[self.group_index].filters[self.index].value = f"bpy.data.texts['{name}']"
        else:
            props.filter_groups[self.group_index].filters[self.index].value = ",".join(global_ids)
        return {"FINISHED"}


class EditFilterQuery(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_filter_query"
    bl_label = "Edit Filter Query"
    bl_description = "Edit the underlying filter query for advanced users"
    bl_options = {"REGISTER", "UNDO"}
    query: StringProperty(name="Query")
    module: StringProperty()

    def _execute(self, context):
        if self.query == self.old_query:
            return

        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties

        try:
            tool.Search.import_filter_query(self.query, props.filter_groups)
        except:
            return

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "query", text="")

    def invoke(self, context, event):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties

        self.query = tool.Search.export_filter_query(props.filter_groups)
        self.old_query = self.query

        return context.window_manager.invoke_props_dialog(self)


class Search(Operator):
    bl_idname = "bim.search"
    bl_label = "Search"

    def execute(self, context):
        props = context.scene.BIMSearchProperties
        results = ifcopenshell.util.selector.filter_elements(
            tool.Ifc.get(), tool.Search.export_filter_query(props.filter_groups)
        )

        total_selected = 0
        for element in results:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)
        self.report({"INFO"}, f"{len(results)} Results")
        return {"FINISHED"}


class SaveSearch(Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_search"
    bl_label = "Save Search"
    bl_description = "Save search filter to an IFC group"
    bl_options = {"REGISTER", "UNDO"}
    name: StringProperty(name="Name")
    module: StringProperty()

    def _execute(self, context):
        if not self.name:
            return

        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties

        try:
            query = tool.Search.export_filter_query(props.filter_groups)
            results = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query)
        except:
            return

        description = json.dumps({"type": "BBIM_Search", "query": query})
        group = [g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == self.name]
        if group:
            group = group[0]
            group.Description = description
        else:
            group = ifcopenshell.api.run("group.add_group", tool.Ifc.get(), Name=self.name, Description=description)
        if results:
            ifcopenshell.api.run("group.assign_group", tool.Ifc.get(), products=list(results), group=group)

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class LoadSearch(Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_search"
    bl_label = "Load Search"
    bl_description = "Load search filter from an IFC group"
    bl_options = {"REGISTER", "UNDO"}
    module: StringProperty()

    def _execute(self, context):
        if self.module == "search":
            props = context.scene.BIMSearchProperties
        elif self.module == "csv":
            props = context.scene.CsvProperties
        group = tool.Ifc.get().by_id(int(context.scene.BIMSearchProperties.saved_searches))
        query = tool.Search.import_filter_query(tool.Search.get_group_query(group), props.filter_groups)

    def draw(self, context):
        props = context.scene.BIMSearchProperties
        row = self.layout.row()
        row.prop(props, "saved_searches", text="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class ColourByProperty(Operator):
    bl_idname = "bim.colour_by_property"
    bl_label = "Colour by Property"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = context.scene.BIMSearchProperties
        query = props.colourscheme_query

        if not query:
            self.report({"ERROR"}, "No Query Provided")
            return {"CANCELLED"}

        colours = cycle(colour_list)
        colourscheme = {}

        if len(props.colourscheme):
            colourscheme = {cs.name: cs.colour[0:3] for cs in props.colourscheme}

        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            value = str(ifcopenshell.util.selector.get_element_value(element, query))
            if value not in colourscheme:
                colourscheme[value] = next(colours)[0:3]
            obj.color = (*colourscheme[value], 1)
        areas = [a for a in context.screen.areas if a.type == "VIEW_3D"]
        if areas:
            areas[0].spaces[0].shading.color_type = "OBJECT"

        props.colourscheme.clear()
        for value, colour in colourscheme.items():
            new = props.colourscheme.add()
            new.name = str(value)
            new.colour = colour[0:3]
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


class SelectByProperty(Operator):
    bl_idname = "bim.select_by_property"
    bl_label = "Select by Property"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMSearchProperties
        return props.active_colourscheme_index < len(props.colourscheme)

    def execute(self, context):
        props = context.scene.BIMSearchProperties
        query = props.colourscheme_query

        if not query:
            self.report({"ERROR"}, "No Query Provided")
            return {"CANCELLED"}

        active_value = props.colourscheme[props.active_colourscheme_index].name

        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            value = str(ifcopenshell.util.selector.get_element_value(element, query))
            if value == active_value:
                obj.select_set(True)
        return {"FINISHED"}


class SaveColourscheme(Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_colourscheme"
    bl_label = "Save Colourscheme"
    bl_description = "Save colourscheme to an IFC group"
    bl_options = {"REGISTER", "UNDO"}
    name: StringProperty(name="Name")

    def _execute(self, context):
        if not self.name:
            return

        props = context.scene.BIMSearchProperties
        query = props.colourscheme_query

        group = [g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == self.name]
        coulour_scheme = {cs.name: cs.colour[0:3] for cs in props.colourscheme}
        if group:
            group = group[0]
            description = json.loads(group.Description)
            description["colourscheme"] = coulour_scheme
            description["colourscheme_query"] = query
            group.Description = json.dumps(description)
        else:
            description = json.dumps(
                {"type": "BBIM_Search", "colourscheme": coulour_scheme, "colourscheme_query": query}
            )
            group = ifcopenshell.api.run("group.add_group", tool.Ifc.get(), Name=self.name, Description=description)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class LoadColourscheme(Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_colourscheme"
    bl_label = "Load Colourscheme"
    bl_description = "Load colourscheme from an IFC group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMSearchProperties
        group = tool.Ifc.get().by_id(int(props.saved_colourschemes))
        description = json.loads(group.Description)
        props.colourscheme_query = description.get("colourscheme_query")
        props.colourscheme.clear()
        for name, colour in description.get("colourscheme", {}).items():
            new = props.colourscheme.add()
            new.name = name
            new.colour = colour

    def draw(self, context):
        props = context.scene.BIMSearchProperties
        row = self.layout.row()
        row.prop(props, "saved_colourschemes", text="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class SelectGlobalId(Operator):
    """Click to select the objects that match with the given Global ID"""

    bl_idname = "bim.select_global_id"
    bl_label = "Select GlobalId"
    bl_options = {"REGISTER", "UNDO"}
    global_id: StringProperty()

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        global_id = self.global_id.strip()

        if not global_id:
            self.report({"ERROR"}, "Set Global ID for search.")
            return {"CANCELLED"}

        try:
            entity = ifc_file.by_guid(global_id)
        except RuntimeError:
            self.report({"ERROR"}, f"No IFC entity found with guid '{global_id}'.")
            return {"CANCELLED"}

        obj = tool.Ifc.get_object(entity)
        if not obj:
            self.report({"ERROR"}, f"No Blender object found with guid '{global_id}'.")
            return {"CANCELLED"}

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
        for element in tool.Ifc.get().by_type(self.ifc_class):
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)
        return {"FINISHED"}


class ResetObjectColours(Operator):
    """Reset the colour of visible objects"""

    bl_idname = "bim.reset_object_colours"
    bl_label = "Reset Colours"

    def execute(self, context):
        for obj in context.visible_objects:
            obj.color = (1, 1, 1, 1)
        props = context.scene.BIMSearchProperties
        props.colourscheme.clear()
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
        elif props.filter_type == "CONTAINER":
            for building_storey in props.filter_container:
                building_storey.is_selected = self.selecting_actionbool
        return {"FINISHED"}


class ActivateIfcClassFilter(Operator):
    """Filter the current selection by IFC class"""

    bl_idname = "bim.activate_ifc_class_filter"
    bl_label = "Filter by Class"

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("Select objects to filter.")
            return False
        return True

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


class ActivateContainerFilter(Operator):
    """Filter the current selection by Building Storey"""

    bl_idname = "bim.activate_ifc_container_filter"
    bl_label = "Filter by Container"

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("Select objects to filter.")
            return False
        return True

    def invoke(self, context, event):
        props = bpy.context.scene.BIMSearchProperties
        props.filter_container.clear()

        containers = {}
        containers.setdefault("None", 0)
        for obj in context.selected_objects:
            container = tool.Spatial.get_container(tool.Ifc.get_entity(obj))
            if not container:
                containers["None"] += 1
                continue
            containers.setdefault(container.Name, 0)
            containers[container.Name] += 1

        for name, total in dict(sorted(containers.items())).items():
            new = props.filter_container.add()
            new.name = name
            new.total = total

        props.filter_type = "CONTAINER"

        return context.window_manager.invoke_props_dialog(self, width=250)

    def execute(self, context):
        bpy.context.scene.BIMSearchProperties.filter_container.clear()
        return {"FINISHED"}

    def draw(self, context):
        self.layout.template_list(
            "BIM_UL_ifc_building_storey_filter",
            "",
            context.scene.BIMSearchProperties,
            "filter_container",
            context.scene.BIMSearchProperties,
            "filter_container_index",
            rows=20
            if len(bpy.context.scene.BIMSearchProperties.filter_container) > 20
            else len(bpy.context.scene.BIMSearchProperties.filter_container),
        )
        row = self.layout.row(align=True)
        row.operator("bim.toggle_filter_selection", text="Select All").action = "SELECT"
        row.operator("bim.toggle_filter_selection", text="Deselect All").action = "DESELECT"


class ShowAllElements(Operator):
    """Show all Physical objects in the 3D View.
    Warning: Pressing this button will not work if collections are excluded in the outliner Panel.
    """

    bl_idname = "bim.show_scene_elements"
    bl_label = "Shows All Elements"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.show_scene_elements(tool.Spatial)
        return {"FINISHED"}


class FilterModelElements(Operator):
    """Filter model elements based on selection"""

    bl_idname = "bim.filter_model_elements"
    bl_label = "Filter Model Elements"
    option: StringProperty("select|isolate|hide")

    def execute(self, context):
        selection_props = context.scene.IfcSelectorProperties
        selection = (
            selection_props.selector_query_syntax
            if selection_props.manual_override
            else self.add_groups(selection_props)
        )
        selection_props.selector_query_syntax = selection
        r = core.search(tool.Search, tool.Spatial, query=selection, action=self.option)
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}

    def add_groups(self, selector: str) -> str:
        selection = ""
        for group_index, group in enumerate(selector.groups):
            if group_index != 0:
                selection += " | "
            selection += "(" if len(selector.groups) > 1 else ""
            selection = self.add_queries(selection, group)

            selection += ")" if len(selector.groups) > 1 else ""
        return selection

    def add_queries(self, selection: str, group: str) -> str:
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

    def add_filters(self, selection: str, query: str) -> str:
        for f_index, f in enumerate(query.filters):
            if f_index != 0:
                selection += " & " if f.and_or == "and" else " | "
                selection += f".{query.active_option}"

            if f.value in ("True", "False"):
                value = f.value
            elif f.value.isnumeric() and str(float(f.value))[0] == f.value[0]:
                value = f.value
            else:
                value = f'"{f.value}"'

            selection += "["

            if f.selector == "IfcPropertySet":
                selection += f'{f.active_option.split(": ")[1]}.{f.active_sub_option.split(": ")[1]} {"!" if f.negation else ""}{f.comparison} {value}'
            elif f.selector == "Attribute":
                # we're using the prop_search functionality in blender which returns the index of the option.  Sometimes the user can override this and enter a value that doesn't exist in the list.  In this case there is no index and we need to handle it. @vulevukusej
                pattern = re.compile(r"^[0-9]+:")
                match = pattern.search(f.active_option)
                selection += f'{f.active_option.split(": ")[1] if match else f.active_option} {"!" if f.negation else ""}{f.comparison} {value}'
            selection += "]"
        return selection


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


class SelectSimilar(Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_similar"
    bl_label = "Select Similar"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMSearchProperties
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        key = props.element_key
        if props.element_key == "PredefinedType":
            key = "predefined_type"
        value = ifcopenshell.util.selector.get_element_value(element, key)
        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if ifcopenshell.util.selector.get_element_value(element, key) == value:
                obj.select_set(True)
