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
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore
from itertools import cycle


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


class SelectGlobalId(bpy.types.Operator):
    """Click to select the objects that match with the given Global ID"""

    bl_idname = "bim.select_global_id"
    bl_label = "Select GlobalId"
    bl_options = {"REGISTER", "UNDO"}
    global_id: bpy.props.StringProperty()

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.BIMSearchProperties
        global_id = self.global_id or props.global_id
        entity = ifc_file.by_guid(global_id)
        obj = tool.Ifc.get_object(entity)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return {"FINISHED"}


class SelectIfcClass(bpy.types.Operator):
    """Click to select all objects that match with the given IFC class"""

    bl_idname = "bim.select_ifc_class"
    bl_label = "Select IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id or obj.is_library_indirect:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if does_keyword_exist(self.ifc_class, element.is_a(), context):
                obj.select_set(True)
        return {"FINISHED"}


class SelectAttribute(bpy.types.Operator):
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


class SelectPset(bpy.types.Operator):
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


class ColourByAttribute(bpy.types.Operator):
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


class ColourByPset(bpy.types.Operator):
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


class ColourByClass(bpy.types.Operator):
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


class ResetObjectColours(bpy.types.Operator):
    """Reset the colour of selected objects"""

    bl_idname = "bim.reset_object_colours"
    bl_label = "Reset Colours"

    def execute(self, context):
        for obj in context.selected_objects:
            obj.color = (1, 1, 1, 1)
        return {"FINISHED"}


class ToggleFilterSelection(bpy.types.Operator):
    "Click to select/deselect current selection"
    bl_idname = "bim.toggle_filter_selection"
    bl_label = "Toggle Filter Selection"
    action: bpy.props.EnumProperty(items=(("SELECT", "Select", ""), ("DESELECT", "Deselect", "")))

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


class ActivateIfcClassFilter(bpy.types.Operator):
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


class ActivateIfcBuildingStoreyFilter(bpy.types.Operator):
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
