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

import bpy
import json
import bisect
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.selector
import bonsai.tool as tool
import bonsai.core.search as core
from bonsai.bim.ifc import IfcStore
from natsort import natsorted
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


class AddFilterGroup(Operator):
    bl_idname = "bim.add_filter_group"
    bl_label = "Add Filter Group"
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        filter_groups.add()
        return {"FINISHED"}


class RemoveFilterGroup(Operator):
    bl_idname = "bim.remove_filter_group"
    bl_label = "Remove Filter Group"
    index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        filter_groups.remove(self.index)
        return {"FINISHED"}


class RemoveFilter(Operator):
    bl_idname = "bim.remove_filter"
    bl_label = "Remove Filter Group"
    group_index: IntProperty()
    index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        filter_groups[self.group_index].filters.remove(self.index)
        return {"FINISHED"}


class AddFilter(Operator):
    bl_idname = "bim.add_filter"
    bl_label = "Add Filter"
    index: IntProperty()
    type: StringProperty()
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        new = filter_groups[self.index].filters.add()
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
        filter_groups = tool.Search.get_filter_groups(self.module)
        query = tool.Search.get_query_for_selected_elements()
        filter_groups[self.group_index].filters[self.index].value = query
        if query.startswith("bpy.data.texts['"):
            self.report({"INFO"}, f'List of Global Ids was saved to the text file "{name}" in the current .blend file')
        return {"FINISHED"}


class EditFilterQuery(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_filter_query"
    bl_label = "Edit Filter Query"
    bl_description = "Edit the underlying filter query for advanced users"
    bl_options = {"REGISTER", "UNDO"}
    query: StringProperty(name="Query")
    old_query: StringProperty(name="Old Query")
    module: StringProperty()

    def _execute(self, context):
        if self.query == self.old_query:
            return

        filter_groups = tool.Search.get_filter_groups(self.module)
        try:
            tool.Search.import_filter_query(self.query, filter_groups)
        except:
            return

    def draw(self, context):
        row = self.layout.row()
        row.prop(self, "query", text="")

    def invoke(self, context, event):
        filter_groups = tool.Search.get_filter_groups(self.module)

        self.query = tool.Search.export_filter_query(filter_groups)
        self.old_query = self.query

        return context.window_manager.invoke_props_dialog(self)


class Search(Operator):
    bl_idname = "bim.search"
    bl_label = "Search"

    property_group: bpy.props.StringProperty(name="Property Group", default="")

    def execute(self, context):
        if self.property_group == "CsvProperties":
            props = context.scene.CsvProperties
        elif self.property_group == "BIMSearchProperties":
            props = context.scene.BIMSearchProperties
        else:
            raise Exception(f"bim.search - unexpected property group name '{self.property_group}'.")

        results = ifcopenshell.util.selector.filter_elements(
            tool.Ifc.get(), tool.Search.export_filter_query(props.filter_groups)
        )

        total_selected = 0
        for element in results:
            if obj := tool.Ifc.get_object(element):
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

        filter_groups = tool.Search.get_filter_groups(self.module)

        try:
            query = tool.Search.export_filter_query(filter_groups)
            results = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query)
        except:
            return

        description = json.dumps({"type": "BBIM_Search", "query": query})
        group = [g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == self.name]
        if group:
            group = group[0]
            group.Description = description
        else:
            group = ifcopenshell.api.run("group.add_group", tool.Ifc.get(), name=self.name, description=description)
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
        filter_groups = tool.Search.get_filter_groups(self.module)
        group = tool.Ifc.get().by_id(int(context.scene.BIMSearchProperties.saved_searches))
        tool.Search.import_filter_query(tool.Search.get_group_query(group), filter_groups)

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
        query = props.colourscheme_query if props.colourscheme_key == "QUERY" else props.colourscheme_key

        if not query:
            self.report({"ERROR"}, "No Query Provided")
            return {"CANCELLED"}

        palette = props.palette
        is_qualitative = palette in ("tab10", "paired")

        if is_qualitative:
            colours = tool.Search.get_qualitative_palette(palette)

        colourscheme = {}

        obj_values = {}
        min_mode = props.min_mode
        max_mode = props.max_mode
        min_value = props.min_value if min_mode == "MANUAL" else None
        max_value = props.max_value if max_mode == "MANUAL" else None

        if is_qualitative and len(props.colourscheme):
            colourscheme = {cs.name: {"colour": cs.colour[0:3], "total": 0} for cs in props.colourscheme}

        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            value = ifcopenshell.util.selector.get_element_value(element, query)
            if is_qualitative:
                value = str(value)
                if value in colourscheme:
                    colourscheme[value]["total"] += 1
                else:
                    colourscheme[value] = {"colour": next(colours)[0:3], "total": 1}
                obj.color = (*colourscheme[value]["colour"], 1)
            else:
                if value is None:
                    obj.color = (0, 0, 0, 1)
                    if "None" in colourscheme:
                        colourscheme["None"]["total"] += 1
                    else:
                        colourscheme["None"] = {"colour": (0, 0, 0), "total": 1}
                else:
                    try:
                        value = float(value)
                        if min_mode == "AUTO":
                            if min_value is None or value < min_value:
                                min_value = value
                        if max_mode == "AUTO":
                            if max_value is None or value > max_value:
                                max_value = value
                        obj_values[obj] = value
                    except:
                        obj.color = (0, 0, 0, 1)

        if not is_qualitative:
            steps = 10 if max_value is not None and min_value is not None else 0
            step_size = (max_value - min_value) / (steps - 1)
            values = []
            for i in range(steps):
                step_value = min_value + i * step_size
                values.append(step_value)
                colourscheme[str(step_value)] = {
                    "colour": tool.Search.get_quantitative_palette(palette, step_value, min_value, max_value),
                    "total": 0,
                }

            for obj, value in obj_values.items():
                index = bisect.bisect_right(values, value)
                if index >= len(values):
                    index = -1
                colourscheme[str(values[index])]["total"] += 1
                obj.color = (*tool.Search.get_quantitative_palette(palette, value, min_value, max_value), 1)

        if areas := [a for a in context.screen.areas if a.type == "VIEW_3D"]:
            areas[0].spaces[0].shading.color_type = "OBJECT"

        props.colourscheme.clear()

        if is_qualitative:
            keys = natsorted(colourscheme.keys())
        else:
            keys = sorted(colourscheme.keys(), key=self.sort_quantitative_key)

        for value in keys:
            data = colourscheme[value]
            new = props.colourscheme.add()
            new.name = str(value)
            new.total = data["total"]
            new.colour = data["colour"][0:3]
        return {"FINISHED"}

    def sort_quantitative_key(self, value):
        try:
            return (0, float(value))
        except ValueError:
            return (1, value)

    def store_state(self, context):
        if areas := [a for a in context.screen.areas if a.type == "VIEW_3D"]:
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
        query = props.colourscheme_query if props.colourscheme_key == "QUERY" else props.colourscheme_key

        if not query:
            self.report({"ERROR"}, "No Query Provided")
            return {"CANCELLED"}

        active_value = props.colourscheme[props.active_colourscheme_index].name
        palette = props.palette

        is_qualitative = palette in ("tab10", "paired")

        if not is_qualitative:
            values = []
            for colour in props.colourscheme:
                try:
                    values.append(float(colour.name))
                except:
                    pass
            values = sorted(values)

        for obj in context.visible_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            value = ifcopenshell.util.selector.get_element_value(element, query)
            if is_qualitative:
                if str(value) == active_value:
                    obj.select_set(True)
            else:
                if active_value == "None":
                    if value is None:
                        obj.select_set(True)
                else:
                    try:
                        value = float(value)
                        index = bisect.bisect_right(values, value)
                        if index >= len(values):
                            index = -1
                        if values[index] == float(active_value):
                            obj.select_set(True)
                    except:
                        pass

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
        colourscheme = {cs.name: {"colour": cs.colour[0:3], "total": cs.total} for cs in props.colourscheme}
        if group:
            group = group[0]
            description = json.loads(group.Description)
            description["colourscheme"] = colourscheme
            description["colourscheme_query"] = query
            group.Description = json.dumps(description)
        else:
            description = json.dumps({"type": "BBIM_Search", "colourscheme": colourscheme, "colourscheme_query": query})
            group = ifcopenshell.api.run("group.add_group", tool.Ifc.get(), name=self.name, description=description)

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
        for name, data in description.get("colourscheme", {}).items():
            new = props.colourscheme.add()
            new.name = name
            new.total = data["total"]
            new.colour = data["colour"]

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
    """Click to select all objects that match with the given IFC class\nSHIFT + Click to also match Predefined Type"""

    bl_idname = "bim.select_ifc_class"
    bl_label = "Select IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    should_filter_predefined_type: BoolProperty(default=False)

    def invoke(self, context, event):
        self.should_filter_predefined_type = event.shift
        return self.execute(context)

    def execute(self, context):
        objects = context.selected_objects
        classes = set()
        predefined_types = set()
        for obj in objects:
            if element := tool.Ifc.get_entity(obj):
                classes.add(element.is_a())
                predefined_types.add(ifcopenshell.util.element.get_predefined_type(element))
        result = ""
        for cls in classes:
            for element in tool.Ifc.get().by_type(cls):
                if (
                    self.should_filter_predefined_type
                    and ifcopenshell.util.element.get_predefined_type(element) not in predefined_types
                ):
                    continue
                if obj := tool.Ifc.get_object(element):
                    tool.Blender.select_object(obj)

            # copy selection query to clipboard
            if not result:
                result = f"{cls}"
            else:
                result += f", {cls}"
            bpy.context.window_manager.clipboard = result
            self.report({"INFO"}, f"({result}) was copied to the clipboard.")

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
        self.selecting_actionbool = self.action == "SELECT"
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
            rows=min(len(bpy.context.scene.BIMSearchProperties.filter_classes), 20),
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
            rows=min(len(bpy.context.scene.BIMSearchProperties.filter_container), 20),
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


class SelectSimilar(Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_similar"
    bl_label = "Select Similar"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select objects with a similar value\n\n" + "SHIFT+CLICK display the sum of all selected objects"

    key: bpy.props.StringProperty()
    calculate_sum: bpy.props.BoolProperty(
        name="Calculate Sum of Selected Objects", default=False, options={"SKIP_SAVE"}
    )
    calculated_sum: bpy.props.FloatProperty(name="Calculated Sum", default=0.0)

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.shift:
            self.calculate_sum = True
        return self.execute(context)

    def _execute(self, context):
        props = context.scene.BIMSearchProperties
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        key = self.key
        if key == "PredefinedType":
            key = "predefined_type"
        value = ifcopenshell.util.selector.get_element_value(element, key)
        tolerance = bpy.context.scene.DocProperties.tolerance

        # Determine the number of decimal places based on the magnitude of the rounding value
        if tolerance < 1:
            decimal_places = max(0, -int(f"{tolerance:.1e}".split("e")[-1]))  # Exponent in scientific notation
            formatted_tolerance = f"{tolerance:.{decimal_places}f}"
        else:
            formatted_tolerance = f"{tolerance:.1f}"  # For values >= 1, one decimal place is enough

        if self.calculate_sum and isinstance(value, (int, float)):
            total = 0
            for obj in context.selected_objects:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue
                value = ifcopenshell.util.selector.get_element_value(element, key)
                if value:
                    total += value
            self.calculated_sum = total
            bpy.context.window_manager.clipboard = str(self.calculated_sum)
            self.report({"INFO"}, f"({self.calculated_sum}) was copied to the clipboard.")
        else:
            self.calculated_sum = 0
            for obj in context.visible_objects:
                element = tool.Ifc.get_entity(obj)
                if not element:
                    continue
                obj_value = ifcopenshell.util.selector.get_element_value(element, key)
                if isinstance(obj_value, (int, float)):
                    # Check within rounding value
                    if abs(obj_value - value) <= tolerance:
                        obj.select_set(True)
                elif obj_value == value:
                    obj.select_set(True)
            if isinstance(value, (int, float)):
                self.report(
                    {"INFO"},
                    f"Selected all objects that share the same ({key}) value--within a ({formatted_tolerance}) tolerance.",
                )
            else:
                self.report({"INFO"}, f"Selected all objects that share the same ({key}) value")

        # copy selection query to clipboard
        if not self.calculate_sum:
            result = ""
            if value == True:
                value = "TRUE"
            if value == False:
                value = "FALSE"
            if key == "predefined_type":
                key = "PredefinedType"
            if isinstance(value, list) and value:
                for item in value:
                    sub_result = f'{key} = "{item}"'
                    if not result:
                        result = sub_result
                    else:
                        result += f", {sub_result}"
            else:
                result = f'{key} = "{value}"'
            bpy.context.window_manager.clipboard = result
            self.report({"INFO"}, f"({result}) was copied to the clipboard.")
