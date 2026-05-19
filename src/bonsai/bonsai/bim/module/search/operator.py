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

import bisect
import json
import traceback
from typing import TYPE_CHECKING, Any, Literal, assert_never, get_args

import bpy
import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.util.element
import ifcopenshell.util.selector
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import Operator
from natsort import natsorted

import bonsai.core.search as core
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.prop import StrProperty

if TYPE_CHECKING:
    from bpy.stub_internal import rna_enums

    from bonsai.bim.prop import BIMFacet


def draw_text_editor_header(self: bpy.types.TEXT_HT_header, context: bpy.types.Context) -> None:
    assert isinstance(context.space_data, bpy.types.SpaceTextEditor)
    if context.space_data.text and context.space_data.text.name.startswith("FilterQuery_"):
        layout = self.layout
        layout.separator()
        op = layout.operator("bim.apply_filter_from_text", text="Apply Filter Configuration", icon="CHECKMARK")


def update_filter_search_value(self: "FilterValueSuggestions", context: bpy.types.Context) -> None:
    filter_groups = tool.Search.get_filter_groups(self.module)
    ifc_filter = filter_groups[self.group_index].filters[self.filter_index]

    value = self.search_value

    if " < " in value:
        value = value.split(" < ")[-1]

    if ifc_filter.type == "entity":
        if " (superclass)" in value:
            value = value.replace(" (superclass)", "")
        if " > " in value:
            value = value.split(" > ")[-1]

    elif ifc_filter.type == "instance":
        if ": " in value:
            value = value.split(": ")[-1]
        elif " (" in value:
            hierarchy_class = value.split(" (")
            element_class = hierarchy_class[-1].rstrip(")")
            element_name = hierarchy_class[0] if len(hierarchy_class) > 1 else None

            ifc_file = tool.Ifc.get()
            if ifc_file:
                for element_id in IfcStore.id_map.keys():
                    try:
                        element = ifc_file.by_id(element_id)
                        if element.is_a() == element_class:
                            if element_name is None or (hasattr(element, "Name") and element.Name == element_name):
                                value = element.GlobalId
                                break
                    except:
                        continue

    elif ifc_filter.type == "parent":
        if " (" in value:
            value = value.split(" (")[0]

    if ifc_filter.type == "property":
        if self.suggestion_type == "pset":
            ifc_filter.pset = value
        elif self.suggestion_type == "property_name":
            ifc_filter.name = value
        else:
            ifc_filter.value = value
    elif ifc_filter.type == "attribute":
        if self.suggestion_type == "attribute_name":
            ifc_filter.name = value
        else:
            ifc_filter.value = value
    else:
        ifc_filter.value = value

    if self.first_launch:
        self.first_launch = False
    else:
        context.window.screen = context.window.screen


class FilterValueSuggestions(Operator):
    bl_idname = "bim.filter_value_suggestions"
    bl_label = "Filter Value Suggestions"
    bl_description = "Get suggestions for filter values from the current IFC file"
    bl_options = {"REGISTER", "UNDO"}

    group_index: IntProperty()
    filter_index: IntProperty()
    module: StringProperty(default="search")
    filter_type: StringProperty()
    suggestion_type: StringProperty(default="value")

    first_launch: BoolProperty(default=True, options={"SKIP_SAVE"})
    search_value: StringProperty(
        name="Search",
        description="Search for filter values",
        update=update_filter_search_value,
        default="",
        options={"SKIP_SAVE"},
    )
    collection_values: CollectionProperty(type=StrProperty, options={"SKIP_SAVE"})

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"WARNING"}, "No IFC file loaded")
            return {"CANCELLED"}

        filter_groups = tool.Search.get_filter_groups(self.module)
        ifc_filter = filter_groups[self.group_index].filters[self.filter_index]

        string_suggestions = self.get_suggestions(ifc_file, ifc_filter)
        if not string_suggestions:
            self.report({"INFO"}, f"No suggestions available")
            return {"CANCELLED"}

        self.collection_values.clear()
        for suggestion in natsorted(string_suggestions):
            self.collection_values.add().name = suggestion

        return context.window_manager.invoke_props_dialog(self, width=800)

    def draw(self, context):
        layout = self.layout
        assert layout

        filter_groups = tool.Search.get_filter_groups(self.module)
        ifc_filter = filter_groups[self.group_index].filters[self.filter_index]

        label_map = {
            "entity": "Select Class",
            "type": "Select Type",
            "material": "Select Material",
            "location": "Select Location",
            "group": "Select Group",
            "classification": "Select Classification",
            "parent": "Select Parent",
            "instance": "Select GlobalId",
        }

        if ifc_filter.type == "attribute":
            if self.suggestion_type == "attribute_value":
                label = f"Select Value for {ifc_filter.name}"
            else:
                label = "Select Attribute Name"
        elif ifc_filter.type == "property":
            if self.suggestion_type == "property_value":
                label = f"Select Value for {ifc_filter.pset}.{ifc_filter.name}"
            elif self.suggestion_type == "property_name":
                label = f"Select Property from {ifc_filter.pset}"
            else:
                label = "Select Property Set"
        else:
            label = label_map.get(ifc_filter.type, "Select Value")

        row = layout.row()
        row.label(text=label)
        row = layout.row()
        row.prop_search(
            self,
            "search_value",
            self,
            "collection_values",
            text="",
            results_are_suggestions=True,
        )

    def get_suggestions(self, ifc_file: ifcopenshell.file, ifc_filter: "BIMFacet") -> set[str]:
        suggestions: set[str] = set()

        if ifc_filter.type == "entity":
            suggestions = self.get_entity_suggestions(ifc_file)
        elif ifc_filter.type == "type":
            suggestions = self.get_type_suggestions(ifc_file)
        elif ifc_filter.type == "material":
            suggestions = self.get_material_suggestions(ifc_file)
        elif ifc_filter.type == "location":
            suggestions = self.get_location_suggestions(ifc_file)
        elif ifc_filter.type == "group":
            suggestions = self.get_group_suggestions(ifc_file)
        elif ifc_filter.type == "classification":
            suggestions = self.get_classification_suggestions(ifc_file)
        elif ifc_filter.type == "parent":
            suggestions = self.get_parent_suggestions(ifc_file)
        elif ifc_filter.type == "instance":
            suggestions = self.get_instance_suggestions(ifc_file)
        elif ifc_filter.type == "attribute":
            if self.suggestion_type == "attribute_name":
                suggestions = self.get_attribute_names(ifc_file)
            else:
                suggestions = self.get_attribute_values(ifc_file, ifc_filter.name)
        elif ifc_filter.type == "property":
            if self.suggestion_type == "pset":
                suggestions = self.get_property_sets(ifc_file)
            elif self.suggestion_type == "property_name":
                suggestions = self.get_property_names(ifc_file, ifc_filter.pset)
            else:
                suggestions = self.get_property_values(ifc_file, ifc_filter.pset, ifc_filter.name)

        return suggestions

    def build_hierarchy_path(self, element: ifcopenshell.entity_instance) -> list[str]:
        path: list[str] = []
        current = element

        while current:
            if hasattr(current, "Name") and current.Name:
                path.insert(0, current.Name)

            parent = None

            if hasattr(current, "Decomposes") and current.Decomposes:
                for rel in current.Decomposes:
                    if hasattr(rel, "RelatingObject"):
                        parent = rel.RelatingObject
                        break

            if not parent and hasattr(current, "ContainedInStructure") and current.ContainedInStructure:
                for rel in current.ContainedInStructure:
                    if hasattr(rel, "RelatingStructure"):
                        parent = rel.RelatingStructure
                        break

            current = parent

        return path

    def get_entity_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        all_classes: set[str] = set()
        schema = tool.Ifc.schema()

        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                class_name = element.is_a()

                try:
                    entity = schema.declaration_by_name(class_name).as_entity()
                    assert entity
                    current = entity

                    chain_names = [class_name]
                    while current.supertype():
                        supertype = current.supertype()
                        assert supertype
                        chain_names.insert(0, supertype.name())
                        current = supertype

                    if len(chain_names) > 1:
                        all_classes.add(" > ".join(chain_names))
                        for i in range(len(chain_names) - 1):
                            superclass_chain = " > ".join(chain_names[: i + 1])
                            all_classes.add(f"{superclass_chain} (superclass)")
                    else:
                        all_classes.add(class_name)
                except:
                    all_classes.add(class_name)
            except:
                continue

        return all_classes

    def get_type_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions: set[str] = set()
        for element_type in ifc_file.by_type("IfcTypeObject"):
            if element_type.Name:
                hierarchy_path = self.build_hierarchy_path(element_type)
                if len(hierarchy_path) > 1:
                    suggestions.add(" < ".join(hierarchy_path))
                else:
                    suggestions.add(element_type.Name)
        return suggestions

    def get_material_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions = set()
        for material in ifc_file.by_type("IfcMaterial"):
            if material.Name:
                suggestions.add(material.Name)
        return suggestions

    def get_location_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions: set[str] = set()
        for spatial in ifc_file.by_type("IfcSpatialStructureElement"):
            if spatial.Name:
                hierarchy_path = self.build_hierarchy_path(spatial)
                if len(hierarchy_path) > 1:
                    suggestions.add(" < ".join(hierarchy_path))
                else:
                    suggestions.add(spatial.Name)
        return suggestions

    def get_group_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions: set[str] = set()
        for group in ifc_file.by_type("IfcGroup"):
            if group.Name:
                hierarchy_path = self.build_hierarchy_path(group)
                if len(hierarchy_path) > 1:
                    suggestions.add(" < ".join(hierarchy_path))
                else:
                    suggestions.add(group.Name)
        return suggestions

    def get_classification_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions: set[str] = set()
        for ref in ifc_file.by_type("IfcClassificationReference"):
            if ref.Identification:
                suggestions.add(ref.Identification)
        return suggestions

    def get_parent_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions: set[str] = set()
        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                has_children = False

                if hasattr(element, "IsDecomposedBy") and element.IsDecomposedBy:
                    has_children = True
                elif hasattr(element, "ContainsElements") and element.ContainsElements:
                    has_children = True
                elif hasattr(element, "HasOpenings") and element.HasOpenings:
                    has_children = True

                if has_children:
                    hierarchy_path = self.build_hierarchy_path(element)
                    element_class = element.is_a()

                    if len(hierarchy_path) > 0:
                        hierarchy_str = " < ".join(hierarchy_path)
                        suggestions.add(f"{hierarchy_str} ({element_class})")
                    else:
                        element_name = element.Name if hasattr(element, "Name") and element.Name else element_class
                        suggestions.add(f"{element_name} ({element_class})")
            except:
                continue

        return suggestions

    def get_instance_suggestions(self, ifc_file: ifcopenshell.file) -> set[str]:
        suggestions: set[str] = set()
        element_data: list[tuple[str, str]] = []

        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                if hasattr(element, "GlobalId") and element.GlobalId:
                    hierarchy_path = self.build_hierarchy_path(element)
                    element_class = element.is_a()

                    if len(hierarchy_path) > 0:
                        hierarchy_str = " < ".join(hierarchy_path)
                        display_str = f"{hierarchy_str} ({element_class})"
                    else:
                        display_str = f"({element_class})"

                    element_data.append((display_str, element.GlobalId))
            except:
                continue

        display_counts: dict[str, int] = {}
        for display_str, global_id in element_data:
            display_counts[display_str] = display_counts.get(display_str, 0) + 1

        for display_str, global_id in element_data:
            if display_counts[display_str] > 1:
                suggestions.add(f"{display_str}: {global_id}")
            else:
                suggestions.add(display_str)

        return suggestions

    def get_property_sets(self, ifc_file: ifcopenshell.file) -> set[str]:
        psets: set[str] = set()
        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                for definition in getattr(element, "IsDefinedBy", []):
                    if definition.is_a("IfcRelDefinesByProperties"):
                        pset = definition.RelatingPropertyDefinition
                        if pset.is_a("IfcPropertySet") and pset.Name:
                            psets.add(pset.Name)
            except:
                continue
        return psets

    def get_property_names(self, ifc_file: ifcopenshell.file, pset_name: str) -> set[str]:
        property_names: set[str] = set()
        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                for definition in getattr(element, "IsDefinedBy", []):
                    if definition.is_a("IfcRelDefinesByProperties"):
                        pset = definition.RelatingPropertyDefinition
                        if pset.is_a("IfcPropertySet") and pset.Name == pset_name:
                            if pset.HasProperties:
                                for prop in pset.HasProperties:
                                    if hasattr(prop, "Name") and prop.Name:
                                        property_names.add(prop.Name)
            except:
                continue
        return property_names

    def get_property_values(self, ifc_file: ifcopenshell.file, pset_name: str, property_name: str) -> set[str]:
        property_values: set[str] = set()
        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                for definition in getattr(element, "IsDefinedBy", []):
                    if definition.is_a("IfcRelDefinesByProperties"):
                        pset = definition.RelatingPropertyDefinition
                        if pset.is_a("IfcPropertySet") and pset.Name == pset_name:
                            if pset.HasProperties:
                                for prop in pset.HasProperties:
                                    if hasattr(prop, "Name") and prop.Name == property_name:
                                        if prop.is_a("IfcPropertyEnumeratedValue"):
                                            if hasattr(prop, "EnumerationReference") and prop.EnumerationReference:
                                                enum_reference = prop.EnumerationReference
                                                if hasattr(enum_reference, "EnumerationValues"):
                                                    for enum_value in enum_reference.EnumerationValues:
                                                        property_values.add(str(enum_value.wrappedValue))
                                            if hasattr(prop, "EnumerationValues") and prop.EnumerationValues:
                                                for enum_value in prop.EnumerationValues:
                                                    property_values.add(str(enum_value.wrappedValue))
                                        elif hasattr(prop, "NominalValue") and prop.NominalValue:
                                            property_values.add(str(prop.NominalValue.wrappedValue))
            except:
                continue
        return property_values

    def get_attribute_names(self, ifc_file: ifcopenshell.file) -> set[str]:
        attribute_names: set[str] = set()
        schema = tool.Ifc.schema()

        ifc_classes = set()
        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)
                ifc_classes.add(element.is_a())
            except:
                continue

        for ifc_class in ifc_classes:
            try:
                entity = schema.declaration_by_name(ifc_class).as_entity()
                assert entity
                attributes = entity.all_attributes()
                for attr in attributes:
                    attribute_names.add(attr.name())
            except:
                continue

        return attribute_names

    def get_attribute_values(self, ifc_file: ifcopenshell.file, attribute_name: str) -> set[str]:
        attribute_values: set[str] = set()

        for element_id in IfcStore.id_map.keys():
            try:
                element = ifc_file.by_id(element_id)

                if element.is_a("IfcRelationship") or element.is_a("IfcTypeObject"):
                    continue

                if hasattr(element, attribute_name):
                    value = getattr(element, attribute_name, None)

                    if value is not None and value != "":
                        if not hasattr(value, "is_a") and not isinstance(value, (tuple, list)):
                            str_value = str(value)
                            if not str_value.startswith("#") and not str_value.startswith("("):
                                attribute_values.add(str_value)
            except:
                continue

        return attribute_values


class AddFilterGroup(Operator):
    bl_idname = "bim.add_filter_group"
    bl_label = "Add Filter Group"
    bl_options = {"REGISTER", "UNDO"}

    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        filter_groups.add()
        return {"FINISHED"}


class RemoveFilterGroup(Operator):
    bl_idname = "bim.remove_filter_group"
    bl_label = "Remove Filter Group"
    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        filter_groups.remove(self.index)
        return {"FINISHED"}


class RemoveFilter(Operator):
    bl_idname = "bim.remove_filter"
    bl_label = "Remove Filter Group"
    bl_options = {"REGISTER", "UNDO"}

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
    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty()
    type: StringProperty()
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        if self.index >= len(filter_groups):
            filter_groups.add()
        new = filter_groups[self.index].filters.add()
        new.type = self.type
        return {"FINISHED"}


class ToggleFilterInclusion(Operator):
    bl_idname = "bim.toggle_filter_inclusion"
    bl_label = "Toggle Filter Mode"
    bl_description = "Cycle between Add (+), Subtract (-), and Filter modes for this filter"
    bl_options = {"REGISTER", "UNDO"}

    group_index: IntProperty()
    filter_index: IntProperty()
    module: StringProperty()

    def execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        filter_group = filter_groups[self.group_index]
        ifc_filter = filter_group.filters[self.filter_index]

        if ifc_filter.filter_mode == "ADD":
            ifc_filter.filter_mode = "SUBTRACT"
        elif ifc_filter.filter_mode == "SUBTRACT":
            ifc_filter.filter_mode = "FILTER"
        else:
            ifc_filter.filter_mode = "ADD"

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
            text: bpy.types.Text = eval(query)
            name = text.name
            self.report({"INFO"}, f'List of Global Ids was saved to the text file "{name}" in the current .blend file')
        return {"FINISHED"}


class ApplyFilterFromText(Operator):
    bl_idname = "bim.apply_filter_from_text"
    bl_label = "Apply Filter Configuration"
    bl_description = "Apply the JSON filter configuration from the current text block"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area and context.area.type == "TEXT_EDITOR":
            space = context.space_data
            if space.text and space.text.name.startswith("FilterQuery_"):
                return True
        return False

    def execute(self, context):
        space = context.space_data
        text = space.text

        if not text or not text.name.startswith("FilterQuery_"):
            self.report({"ERROR"}, "No valid filter configuration text block")
            return {"CANCELLED"}

        module = text.name.replace("FilterQuery_", "")

        try:
            json_data = json.loads(text.as_string())
            filter_structure = json_data.get("filter_structure", [])
            filter_groups = tool.Search.get_filter_groups(module)
            tool.Search.import_filter_structure(filter_structure, filter_groups)
            self.report({"INFO"}, "Filter configuration applied successfully")

            if len(context.window_manager.windows) > 1:
                bpy.ops.wm.window_close()

        except Exception as e:
            self.report({"ERROR"}, f"Invalid JSON: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}


class EditFilterQuery(Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_filter_query"
    bl_label = "Edit Filter Query"
    bl_description = "Edit the underlying filter query for advanced users"
    bl_options = {"REGISTER", "UNDO"}
    query: StringProperty(name="Query")
    old_query: StringProperty(name="Old Query")
    module: StringProperty(default="search")

    def _execute(self, context):
        module = getattr(self, "module", "search")

        if not tool.Blender.get_addon_preferences().chain_filter_with_set_operations:
            if self.query == self.old_query:
                return

            filter_groups = tool.Search.get_filter_groups(module)
            try:
                tool.Search.import_filter_query(self.query, filter_groups)
            except:
                return

    def draw(self, context):

        if not tool.Blender.get_addon_preferences().chain_filter_with_set_operations:
            row = self.layout.row()
            row.prop(self, "query", text="")

    def invoke(self, context, event):
        module = getattr(self, "module", "search")
        filter_groups = tool.Search.get_filter_groups(module)

        if tool.Blender.get_addon_preferences().chain_filter_with_set_operations:
            filter_structure: list[list[dict[str, Any]]] = []
            for filter_group in filter_groups:
                group_data: list[dict[str, Any]] = []
                for ifc_filter in filter_group.filters:
                    filter_data = {
                        "type": ifc_filter.type,
                        "name": ifc_filter.name,
                        "value": ifc_filter.value,
                        "pset": ifc_filter.pset,
                        "comparison": ifc_filter.comparison,
                        "filter_mode": ifc_filter.filter_mode,
                    }
                    group_data.append(filter_data)
                filter_structure.append(group_data)

            query = tool.Search.export_filter_query(filter_groups)
            json_data = {"type": "BBIM_Search", "query": query, "filter_structure": filter_structure}

            text_block_name = f"FilterQuery_{module}"
            text = bpy.data.texts.get(text_block_name)
            if not text:
                text = bpy.data.texts.new(text_block_name)

            text.clear()
            text.write(json.dumps(json_data, indent=2))

            bpy.ops.wm.window_new()
            new_window = context.window_manager.windows[-1]

            new_area = new_window.screen.areas[0]
            new_area.type = "TEXT_EDITOR"

            text_space = None
            for space in new_area.spaces:
                if space.type == "TEXT_EDITOR":
                    text_space = space
                    break

            if text_space:
                text_space.text = text

            self.report(
                {"INFO"}, "Compact text editor opened. Edit JSON and click 'Apply Filter Configuration' in header"
            )
            return {"FINISHED"}

        else:
            self.query = tool.Search.export_filter_query(filter_groups)
            self.old_query = self.query
            return context.window_manager.invoke_props_dialog(self, width=400)


class Search(Operator):
    bl_idname = "bim.search"
    bl_label = "Search"
    bl_description = "Search IFC elements by the provided query and add them to the current selection."
    bl_options = {"REGISTER", "UNDO"}

    PropertyGroupType = Literal["CsvProperties", "BIMSearchProperties"]
    property_group: bpy.props.EnumProperty(
        name="Property Group", items=[(i, i, "") for i in get_args(PropertyGroupType)]
    )

    if TYPE_CHECKING:
        property_group: PropertyGroupType

    def execute(self, context):
        if self.property_group == "CsvProperties":
            props = tool.Blender.get_csv_props()
        elif self.property_group == "BIMSearchProperties":
            props = tool.Search.get_search_props()
        else:
            assert_never(self.property_group)

        preferences = tool.Blender.get_addon_preferences()

        # Migrate old ! prefix filters to new filter_mode system when preferences are enabled
        if preferences.chain_filter_with_set_operations:
            for filter_group in props.filter_groups:
                for ifc_filter in filter_group.filters:
                    if ifc_filter.type not in ["entity", "instance"]:
                        continue
                    if ifc_filter.value.startswith("!"):
                        ifc_filter.value = ifc_filter.value[1:]
                        ifc_filter.filter_mode = "SUBTRACT"

            results = tool.Search.execute_filter_groups(props.filter_groups)
        else:
            results = ifcopenshell.util.selector.filter_elements(
                tool.Ifc.get(), tool.Search.export_filter_query(props.filter_groups)
            )

        objs = [obj for e in results if isinstance(obj := tool.Ifc.get_object(e), bpy.types.Object)]
        active_object = next(iter(objs), None)
        selection = tool.Blender.validate_object_selection(context, active_object, objs)
        tool.Blender.set_objects_selection(*selection, clear_previous_selection=False)
        self.report({"INFO"}, f"{len(results)} Results, {len(selection.selected_objects)} Objects Selected")
        return {"FINISHED"}


class SelectQueryElements(Operator):
    bl_idname = "bim.select_query_elements"
    bl_label = "Select Query Elements"
    bl_description = "Select elements matching an provided selector query"
    bl_options = {"REGISTER", "UNDO"}

    query: StringProperty(name="Query")

    if TYPE_CHECKING:
        query: str

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        results = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), self.query)
        objs = [obj for e in results if isinstance(obj := tool.Ifc.get_object(e), bpy.types.Object)]
        active_object = context.active_object or next(iter(objs), None)
        selection = tool.Blender.validate_object_selection(context, active_object, objs)
        tool.Blender.set_objects_selection(*selection, clear_previous_selection=False)
        self.report({"INFO"}, f"{len(results)} Results, {len(selection.selected_objects)} Objects Selected")
        return {"FINISHED"}


class SaveSearch(Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_search"
    bl_label = "Save Search"
    bl_description = (
        "Save search filter to an IFC group.\n\n"
        "Search query will be saved to group description, query elements will be assigned to the group."
    )
    bl_options = {"REGISTER", "UNDO"}

    name_search_items: list[str] = []

    def get_name_search_items(self, context: object, text: str) -> list[str]:
        # Extra item so it will be easy to select current text.
        return [text] + SaveSearch.name_search_items

    name: StringProperty(
        name="Name",
        search=get_name_search_items,
        search_options={"SORT"},
    )
    module: StringProperty()

    def update_use_all_ifcgroups(self, context: object = None) -> None:
        ifc_file = tool.Ifc.get()
        groups = {
            g.Name or "Unnamed"
            for g in ifc_file.by_type("IfcGroup")
            if self.use_all_ifcgroups or g.ObjectType == "SEARCH"
        }
        self.name_search_items[:] = natsorted(groups)

    use_all_ifcgroups: BoolProperty(
        name="Use Any IfcGroup",
        description=(
            "By default we're targeting only IfcGroups with SEARCH ObjectType "
            "to prevent breaking internal IfcGroups (e.g. IfcGroups used for Bonsai drawings).\n\n"
            "Enabling this option allows saving search to any IfcGroup matched by the provided name.\n"
            "Use with caution."
        ),
        update=update_use_all_ifcgroups,
    )

    if TYPE_CHECKING:
        name: str
        module: str
        use_all_ifcgroups: bool

    def _execute(self, context):
        if not self.name:
            return

        filter_groups = tool.Search.get_filter_groups(self.module)

        try:
            query = tool.Search.export_filter_query(filter_groups)
            results = tool.Search.execute_filter_groups(filter_groups)

            filter_structure: list[list[dict[str, Any]]] = []
            for filter_group in filter_groups:
                group_data: list[dict[str, Any]] = []
                for ifc_filter in filter_group.filters:
                    filter_data = {
                        "type": ifc_filter.type,
                        "name": ifc_filter.name,
                        "value": ifc_filter.value,
                        "pset": ifc_filter.pset,
                        "comparison": ifc_filter.comparison,
                        "filter_mode": ifc_filter.filter_mode,
                    }
                    group_data.append(filter_data)
                filter_structure.append(group_data)
        except:
            print(traceback.format_exc())
            self.report({"ERROR"}, "Error occurred trying save search.")
            return

        description = json.dumps({"type": "BBIM_Search", "query": query, "filter_structure": filter_structure})
        ifc_file = tool.Ifc.get()
        group = next(
            (
                g
                for g in ifc_file.by_type("IfcGroup")
                if g.Name == self.name and (self.use_all_ifcgroups or g.ObjectType == "SEARCH")
            ),
            None,
        )
        if group:
            group.Description = description
        else:
            group = ifcopenshell.api.group.add_group(tool.Ifc.get(), name=self.name, description=description)
            group.ObjectType = "SEARCH"
        if results:
            ifcopenshell.api.group.assign_group(tool.Ifc.get(), products=list(results), group=group)

    def draw(self, context):
        assert (layout := self.layout)
        layout.prop(self, "name")
        layout.prop(self, "use_all_ifcgroups")

    def invoke(self, context, event):
        assert context.window_manager
        tool.Search.patch_search_ifcgroups()
        self.update_use_all_ifcgroups()
        return context.window_manager.invoke_props_dialog(self)


class LoadSearch(Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_search"
    bl_label = "Load Search"
    bl_description = "Load search filter from an IFC group"
    bl_options = {"REGISTER", "UNDO"}
    module: StringProperty()

    def _execute(self, context):
        filter_groups = tool.Search.get_filter_groups(self.module)
        props = tool.Search.get_search_props()
        group = tool.Ifc.get().by_id(int(props.saved_searches))

        group_data = tool.Search.get_group_data(group)
        if group_data and "filter_structure" in group_data:
            tool.Search.import_filter_structure(group_data["filter_structure"], filter_groups)
        else:
            tool.Search.import_filter_query(tool.Search.get_group_query(group), filter_groups)

    def draw(self, context):
        assert self.layout
        props = tool.Search.get_search_props()
        row = self.layout.row()
        row.prop(props, "saved_searches", text="")

    def invoke(self, context, event):
        tool.Search.patch_search_ifcgroups()
        return context.window_manager.invoke_props_dialog(self)


class RemoveSearch(Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_search"
    bl_label = "Remove Search"
    bl_description = "Remove a saved search filter"
    bl_options = {"REGISTER", "UNDO"}
    module: StringProperty()

    def _execute(self, context):
        props = tool.Search.get_search_props()
        group_id = props.saved_searches
        if not group_id:
            self.report({"ERROR"}, "No search selected for removal")
            return

        group = tool.Ifc.get().by_id(int(group_id))
        group_name = group.Name or "Unnamed"
        ifcopenshell.api.group.remove_group(tool.Ifc.get(), group=group)
        tool.Search.patch_search_ifcgroups()
        self.report({"INFO"}, f"Removed saved search: {group_name}")

    def draw(self, context):
        self.layout.label(text="Select search to remove:", icon="ERROR")
        row = self.layout.row()
        props = tool.Search.get_search_props()
        row.prop(props, "saved_searches", text="")

    def invoke(self, context, event):
        tool.Search.patch_search_ifcgroups()
        from bonsai.bim.module.search.data import SearchData

        if not SearchData.is_loaded:
            SearchData.load()
        return context.window_manager.invoke_props_dialog(self)


class ColourByProperty(Operator):
    bl_idname = "bim.colour_by_property"
    bl_label = "Colour by Property"
    bl_description = "Color all visible objects by the provided property."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.store_state(context)
        result = self._execute(context)
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = tool.Search.get_search_props()
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
            if obj.type not in ("MESH", "CURVE"):
                continue
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

        assert (space := tool.Blender.get_view3d_space())
        space.shading.color_type = "OBJECT"

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
        if space := tool.Blender.get_view3d_space():
            self.transaction_data = {"color_type": space.shading.color_type}

    def rollback(self, data):
        if data:
            assert (space := tool.Blender.get_view3d_space())
            space.shading.color_type = data["color_type"]

    def commit(self, data):
        if data:
            assert (space := tool.Blender.get_view3d_space())
            space.shading.color_type = "OBJECT"


class SelectByProperty(Operator):
    bl_idname = "bim.select_by_property"
    bl_label = "Select by Property"
    bl_description = "Select objects based on currently selected colored property value."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = tool.Search.get_search_props()
        return props.active_colourscheme_index < len(props.colourscheme)

    def execute(self, context):
        props = tool.Search.get_search_props()
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

        props = tool.Search.get_search_props()
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
            group = ifcopenshell.api.group.add_group(tool.Ifc.get(), name=self.name, description=description)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class LoadColourscheme(Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_colourscheme"
    bl_label = "Load Colourscheme"
    bl_description = "Load colourscheme from an IFC group"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Search.get_search_props()
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
        props = tool.Search.get_search_props()
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
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for obj in context.visible_objects:
            obj.color = (1, 1, 1, 1)
        props = tool.Search.get_search_props()
        props.colourscheme.clear()
        return {"FINISHED"}


class ToggleFilterSelection(Operator):
    "Click to select/deselect current selection"

    bl_idname = "bim.toggle_filter_selection"
    bl_label = "Toggle Filter Selection"
    bl_options = {"REGISTER", "UNDO"}

    action: EnumProperty(items=(("SELECT", "Select", ""), ("DESELECT", "Deselect", "")))

    def execute(self, context):
        props = tool.Search.get_search_props()
        self.selecting_actionbool = self.action == "SELECT"
        for item in props.filter_items:
            item.is_selected = self.selecting_actionbool
        return {"FINISHED"}


class ActivateFilter(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            cls.poll_message_set("Select objects to filter.")
            return False
        return True

    def execute(self, context):
        props = tool.Search.get_search_props()
        props.filter_items.clear()
        return {"FINISHED"}

    def draw(self, context):
        props = tool.Search.get_search_props()
        assert self.layout
        self.layout.template_list(
            "BIM_UL_ifc_filter",
            "",
            props,
            "filter_items",
            props,
            "filter_items_index",
            rows=min(len(props.filter_items), 20),
        )
        row = self.layout.row(align=True)
        row.operator("bim.toggle_filter_selection", text="Select All").action = "SELECT"
        row.operator("bim.toggle_filter_selection", text="Deselect All").action = "DESELECT"


class ActivateIfcClassFilter(ActivateFilter):
    """Filter the current selection by IFC class"""

    bl_idname = "bim.activate_ifc_class_filter"
    bl_label = "Filter by Class"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        props = tool.Search.get_search_props()
        props.filter_items.clear()
        ifc_types: dict[str, int] = {}
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            ifc_types.setdefault(element.is_a(), 0)
            ifc_types[element.is_a()] += 1

        for name, total in dict(sorted(ifc_types.items())).items():
            new = props.filter_items.add()
            new.name = name
            new.total = total
        props.filter_type = "CLASS"

        return context.window_manager.invoke_props_dialog(self, width=250)


class ActivateContainerFilter(ActivateFilter):
    """Filter the current selection by Building Storey"""

    bl_idname = "bim.activate_ifc_container_filter"
    bl_label = "Filter by Container"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        props = tool.Search.get_search_props()
        props.filter_items.clear()

        containers: dict[str, int] = {}
        containers.setdefault("None", 0)
        for obj in context.selected_objects:
            assert (element := tool.Ifc.get_entity(obj))
            container = tool.Spatial.get_container(element)
            if not container:
                containers["None"] += 1
                continue
            containers.setdefault(container.Name, 0)
            containers[container.Name] += 1

        for name, total in dict(sorted(containers.items())).items():
            new = props.filter_items.add()
            new.name = name
            new.total = total

        props.filter_type = "CONTAINER"

        return context.window_manager.invoke_props_dialog(self, width=250)


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


class SelectSimilar(Operator):
    bl_idname = "bim.select_similar"
    bl_label = "Select Similar"
    bl_options = {"REGISTER", "UNDO"}

    key: bpy.props.StringProperty()
    calculate_sum: bpy.props.BoolProperty(
        name="Calculate Sum of Selected Objects", default=False, options={"SKIP_SAVE"}
    )
    calculated_sum: bpy.props.FloatProperty(name="Calculated Sum", default=0.0)
    remove_from_selection: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    @classmethod
    def description(cls, context, properties):
        base = "Select objects with a similar value\n\n" "SHIFT+CLICK remove from selection set."

        key = getattr(properties, "key", None)
        active = context.active_object
        if not active or not key:
            return base

        element = tool.Ifc.get_entity(active)
        if not element:
            return base

        value = ifcopenshell.util.selector.get_element_value(element, key)
        if isinstance(value, (int, float)):
            return base + ("\nCTRL+CLICK display the sum of all selected objects")
        else:
            return base

    @classmethod
    def poll(cls, context):
        if context.selected_objects or context.active_object:
            return True
        cls.poll_message_set("No selected or active object found.")
        return False

    def invoke(self, context, event):
        self.calculate_sum = event.ctrl and event.type == "LEFTMOUSE"
        self.remove_from_selection = event.shift and event.type == "LEFTMOUSE"
        return self.execute(context)

    def execute(self, context):
        self.calculated_sum = 0  # reset if run before
        key = "predefined_type" if self.key == "PredefinedType" else self.key
        prefs = tool.Blender.get_addon_preferences()
        tolerance = prefs.doc.tolerance
        formatted_tolerance = f"{tolerance:.{max(0, -int(f'{tolerance:.1e}'.split('e')[-1])) if tolerance < 1 else 1}f}"

        if self.calculate_sum:
            self._calculate_sum(context, key)
        else:
            reference_values = self._get_reference_values(context, key)
            if not reference_values:
                self.report({"WARNING"}, "No valid reference values found.")
                return {"CANCELLED"}

            matched_count = self._select_objects(context, key, reference_values, tolerance)
            verb = "Deselected" if self.remove_from_selection else "Selected"

            if all(isinstance(v, (int, float)) for v in reference_values):
                self.report(
                    {"INFO"},
                    f"{verb} all objects that share the same ({self.key}) value(s) within a ({formatted_tolerance}) tolerance.",
                )
            else:
                self.report(
                    {"INFO"},
                    f"{verb} all objects that share the same ({self.key}) value(s) from {len(reference_values)} reference object(s).",
                )

            self._generate_clipboard_query(reference_values[0] if reference_values else None, key)

        return {"FINISHED"}

    def _get_value(self, obj, key):
        element = tool.Ifc.get_entity(obj)
        if not element:
            return None
        return ifcopenshell.util.selector.get_element_value(element, key)

    def _get_reference_values(self, context, key):
        objects = (
            [context.active_object]
            if self.remove_from_selection
            else (context.selected_objects or [context.active_object])
        )
        values = [self._get_value(obj, key) for obj in objects]
        return [v for v in values if v is not None]

    def _compare_values(self, val1, val2, tolerance):
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return abs(val1 - val2) <= tolerance
        return val1 == val2

    def _select_objects(self, context, key, reference_values, tolerance):
        count = 0
        for obj in context.visible_objects:
            obj_value = self._get_value(obj, key)
            if obj_value is None:
                continue
            if any(self._compare_values(obj_value, ref_value, tolerance) for ref_value in reference_values):
                obj.select_set(not self.remove_from_selection)
                count += 1
        return count

    def _calculate_sum(self, context, key):
        total = 0
        for obj in context.selected_objects:
            value = self._get_value(obj, key)
            if isinstance(value, (int, float)):
                total += value
        self.calculated_sum = total
        bpy.context.window_manager.clipboard = str(total)
        self.report({"INFO"}, f"({total}) was copied to the clipboard.")

    def _generate_clipboard_query(self, value, key):
        key = "PredefinedType" if key == "predefined_type" else key
        if value is True:
            value = "TRUE"
        elif value is False:
            value = "FALSE"

        if isinstance(value, list) and value:
            result = ", ".join(f'{key} = "{item}"' for item in value)
        else:
            result = f'{key} = "{value}"'

        bpy.context.window_manager.clipboard = result
        self.report({"INFO"}, f"({result}) was copied to the clipboard.")
