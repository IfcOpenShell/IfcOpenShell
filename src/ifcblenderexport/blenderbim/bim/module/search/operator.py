import re
import bpy
import ifcopenshell
import ifcopenshell.util.element
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


def does_keyword_exist(pattern, string):
    string = str(string)
    if (
        bpy.context.scene.BIMSearchProperties.should_use_regex
        and bpy.context.scene.BIMSearchProperties.should_ignorecase
        and re.search(pattern, string, flags=re.IGNORECASE)
    ):
        return True
    elif bpy.context.scene.BIMSearchProperties.should_use_regex and re.search(pattern, string):
        return True
    elif bpy.context.scene.BIMSearchProperties.should_ignorecase and string.lower() == pattern.lower():
        return True
    elif string == pattern:
        return True


class SelectGlobalId(bpy.types.Operator):
    bl_idname = "bim.select_global_id"
    bl_label = "Select GlobalId"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMSearchProperties
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if element.GlobalId == props.global_id:
                obj.select_set(True)
                break
        return {"FINISHED"}


class SelectIfcClass(bpy.types.Operator):
    bl_idname = "bim.select_ifc_class"
    bl_label = "Select IFC Class"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMSearchProperties
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if does_keyword_exist(props.ifc_class, element.is_a()):
                obj.select_set(True)
        return {"FINISHED"}


class SelectAttribute(bpy.types.Operator):
    bl_idname = "bim.select_attribute"
    bl_label = "Select Attribute"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMSearchProperties
        pattern = props.search_attribute_value
        attribute_name = props.search_attribute_name
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            if does_keyword_exist(pattern, getattr(element, attribute_name, None)):
                obj.select_set(True)
        return {"FINISHED"}


class SelectPset(bpy.types.Operator):
    bl_idname = "bim.select_pset"
    bl_label = "Select Pset"

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
            props = psets.get(search_pset_name, {})
            if does_keyword_exist(pattern, props.get(search_prop_name, None)):
                obj.select_set(True)
        return {"FINISHED"}


class ColourByAttribute(bpy.types.Operator):
    bl_idname = "bim.colour_by_attribute"
    bl_label = "Colour by Attribute"

    def execute(self, context):
        self.file = IfcStore.get_file()
        colours = cycle(colour_list)
        values = {}
        attribute_name = context.scene.BIMSearchProperties.search_attribute_name
        for obj in context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            value = getattr(element, attribute_name, None)
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class ColourByPset(bpy.types.Operator):
    bl_idname = "bim.colour_by_pset"
    bl_label = "Colour by Pset"

    def execute(self, context):
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
            props = psets.get(search_pset_name, {})
            value = str(props.get(search_prop_name, None))
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class ColourByClass(bpy.types.Operator):
    bl_idname = "bim.colour_by_class"
    bl_label = "Colour by Class"

    def execute(self, context):
        self.file = IfcStore.get_file()
        colours = cycle(colour_list)
        ifc_classes = {}
        for obj in bpy.context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            ifc_class = element.is_a()
            if ifc_class not in ifc_classes:
                ifc_classes[ifc_class] = next(colours)
            obj.color = ifc_classes[ifc_class]
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class ResetObjectColours(bpy.types.Operator):
    bl_idname = "bim.reset_object_colours"
    bl_label = "Reset Colours"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.color = (1, 1, 1, 1)
        return {"FINISHED"}
