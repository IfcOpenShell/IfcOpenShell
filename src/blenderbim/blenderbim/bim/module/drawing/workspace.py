# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import os
import bpy
import blenderbim.tool as tool
from blenderbim.bim.helper import prop_with_search
from bpy.types import WorkSpaceTool

# from blenderbim.bim.module.model.data import AuthoringData, RailingData, RoofData
from blenderbim.bim.module.drawing.prop import ANNOTATION_TYPES_DATA
from blenderbim.bim.module.drawing.data import DecoratorData, AnnotationData
from blenderbim.bim.ifc import IfcStore
import blenderbim.bim.handler


# declaring it here to avoid circular import problems
class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class AnnotationTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "OBJECT"

    bl_idname = "bim.annotation_tool"
    bl_label = "Annotation Tool"
    bl_description = "Gives you Annotation related superpowers"
    bl_icon = os.path.join(os.path.dirname(__file__), "ops.authoring.annotation")
    bl_widget = None
    bl_keymap = tool.Blender.get_default_selection_keypmap() + (
        ("bim.annotation_hotkey", {"type": "A", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_A")]}),
        ("bim.annotation_hotkey", {"type": "C", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_C")]}),
        ("bim.annotation_hotkey", {"type": "E", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_E")]}),
        ("bim.annotation_hotkey", {"type": "F", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_F")]}),
        ("bim.annotation_hotkey", {"type": "G", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_G")]}),
        ("bim.annotation_hotkey", {"type": "K", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_K")]}),
        ("bim.annotation_hotkey", {"type": "M", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_M")]}),
        ("bim.annotation_hotkey", {"type": "O", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_O")]}),
        ("bim.annotation_hotkey", {"type": "Q", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Q")]}),
        ("bim.annotation_hotkey", {"type": "R", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_R")]}),
        ("bim.annotation_hotkey", {"type": "T", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_T")]}),
        ("bim.annotation_hotkey", {"type": "V", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_V")]}),
        ("bim.annotation_hotkey", {"type": "X", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_X")]}),
        ("bim.annotation_hotkey", {"type": "Y", "value": "PRESS", "shift": True}, {"properties": [("hotkey", "S_Y")]}),
        ("bim.annotation_hotkey", {"type": "D", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_D")]}),
        ("bim.annotation_hotkey", {"type": "E", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_E")]}),
        ("bim.annotation_hotkey", {"type": "O", "value": "PRESS", "alt": True}, {"properties": [("hotkey", "A_O")]}),
    )

    def draw_settings(context, layout, ws_tool):
        # Unlike operators, Blender doesn't treat workspace tools as a class, so we'll create our own.
        AnnotationToolUI.draw(context, layout)


def add_layout_hotkey_operator(layout, text, hotkey, description):
    modifiers = {
        "A": "EVENT_ALT",
        "S": "EVENT_SHIFT",
    }
    modifier, key = hotkey.split("_")

    row = layout.row(align=True)
    row.label(text="", icon=modifiers[modifier])
    row.label(text="", icon=f"EVENT_{key}")

    op = row.operator("bim.annotation_hotkey", text=text)
    op.hotkey = hotkey
    op.description = description
    return op, row


# TODO: move to operator
def create_annotation_type(context):
    # just empty to store parameters
    props = context.scene.BIMAnnotationProperties
    object_type = props.object_type
    create_representation = props.create_representation_for_type
    drawing = tool.Ifc.get_entity(bpy.context.scene.camera)

    if props.create_representation_for_type:
        obj = tool.Drawing.create_annotation_object(drawing, object_type)
    else:
        obj = bpy.data.objects.new(object_type, None)

    obj.name = f"{object_type}_TYPE"
    obj.location = context.scene.cursor.location
    tool.Drawing.ensure_annotation_in_drawing_plane(obj)

    drawing = tool.Ifc.get_entity(context.scene.camera)
    ifc_context = tool.Drawing.get_annotation_context(tool.Drawing.get_drawing_target_view(drawing), object_type)

    element = tool.Drawing.run_root_assign_class(
        obj=obj,
        ifc_class="IfcTypeProduct",
        predefined_type=object_type,
        should_add_representation=create_representation,
        context=ifc_context,
        ifc_representation_class=tool.Drawing.get_ifc_representation_class(object_type),
    )
    element.ApplicableOccurrence = f"IfcAnnotation/{object_type}"

    tool.Blender.select_and_activate_single_object(context, obj)


# TODO: move to operator
def create_annotation_occurence(context):
    # object_type = context.scene.BIMAnnotationProperties.object_type
    props = context.scene.BIMAnnotationProperties
    relating_type = tool.Ifc.get().by_id(int(props.relating_type_id))
    object_type = props.object_type

    drawing = tool.Ifc.get_entity(context.scene.camera)
    obj = tool.Drawing.create_annotation_object(drawing, object_type)
    obj.name = relating_type.Name
    ifc_context = tool.Drawing.get_annotation_context(tool.Drawing.get_drawing_target_view(drawing), object_type)
    relating_type_repr = tool.Drawing.get_annotation_representation(relating_type)
    element = tool.Drawing.run_root_assign_class(
        obj=obj,
        ifc_class="IfcAnnotation",
        predefined_type=object_type,
        should_add_representation=not bool(relating_type_repr),
        context=ifc_context,
        ifc_representation_class=tool.Drawing.get_ifc_representation_class(object_type),
    )

    blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)

    tool.Ifc.run("group.assign_group", group=tool.Drawing.get_drawing_group(drawing), products=[element])
    tool.Collector.assign(obj)
    tool.Blender.select_and_activate_single_object(context, obj)


def create_annotation():
    props = bpy.context.scene.BIMAnnotationProperties
    create_type_occurence = props.relating_type_id != "0"
    if create_type_occurence:
        create_annotation_occurence(bpy.context)
    else:
        object_type = props.object_type
        bpy.ops.bim.add_annotation(object_type=object_type, data_type=ANNOTATION_TYPES_DATA[object_type][-1])


class AnnotationToolUI:
    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        cls.props = context.scene.BIMAnnotationProperties

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        if not AnnotationData.is_loaded:
            AnnotationData.load()

        cls.draw_type_selection_interface()

        if context.active_object and context.selected_objects:
            cls.draw_edit_object_interface(context)
        cls.draw_create_object_interface()

    @classmethod
    def draw_create_object_interface(cls):
        row = cls.layout.row(align=True)
        op, row = add_layout_hotkey_operator(cls.layout, "Add Type", "S_C", "Create a new annotation type")
        selected_icon = "CHECKBOX_HLT" if cls.props.create_representation_for_type else "CHECKBOX_DEHLT"
        row.prop(cls.props, "create_representation_for_type", text="", icon=selected_icon)

        row = cls.layout.row(align=True)
        row.prop(bpy.context.scene.DocProperties, "should_draw_decorations", text="Viewport Annotations")

    @classmethod
    def draw_edit_object_interface(cls, context):
        if DecoratorData.get_ifc_text_data(bpy.context.object):
            add_layout_hotkey_operator(cls.layout, "Edit Text", "S_E", "")

    @classmethod
    def draw_type_selection_interface(cls):
        # shared by both sidebar and header
        object_type = cls.props.object_type

        row = cls.layout.row(align=True)
        row.label(text="", icon="FILE_VOLUME")
        prop_with_search(row, cls.props, "object_type", text="")

        row = cls.layout.row(align=True)
        row.label(text="", icon="FILE_3D")
        prop_with_search(row, cls.props, "relating_type_id", text="")

        create_type_occurence = cls.props.relating_type_id != "0"
        label = "Add Type Occurence" if create_type_occurence else "Add Annotation"
        add_layout_hotkey_operator(cls.layout, label, "S_A", "Create a new annotation")

        if object_type in ("TEXT", "STAIR_ARROW"):
            add_layout_hotkey_operator(
                cls.layout,
                "Bulk Tag",
                "S_T",
                "Create new annotations and automatically adjust them to the selected objects",
            )
        add_layout_hotkey_operator(
            cls.layout, "Readjust", "S_G", "Readjust tags based on the products they are assigned to"
        )


class Hotkey(bpy.types.Operator, Operator):
    bl_idname = "bim.annotation_hotkey"
    bl_label = "Hotkey"
    bl_options = {"REGISTER", "UNDO"}
    hotkey: bpy.props.StringProperty()
    description: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    @classmethod
    def description(cls, context, operator):
        return operator.description or ""

    def _execute(self, context):
        self.props = context.scene.BIMAnnotationProperties
        getattr(self, f"hotkey_{self.hotkey}")()

    def invoke(self, context, event):
        # https://blender.stackexchange.com/questions/276035/how-do-i-make-operators-remember-their-property-values-when-called-from-a-hotkey
        self.props = context.scene.BIMAnnotationProperties
        return self.execute(context)

    def draw(self, context):
        pass

    def hotkey_S_T(self):
        props = bpy.context.scene.BIMAnnotationProperties
        object_type = props.object_type

        related_objects = bpy.context.selected_objects
        for related_object in related_objects:
            create_annotation()
            obj = bpy.context.active_object
            bpy.ops.object.mode_set(mode="OBJECT")
            tool.Drawing.setup_annotation_object(obj, object_type, related_object)

    def hotkey_S_A(self):
        create_annotation()

    def hotkey_S_E(self):
        if not bpy.context.object:
            return

        if DecoratorData.get_ifc_text_data(bpy.context.object):
            bpy.ops.bim.edit_text_popup()

    def hotkey_S_G(self):
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcAnnotation"):
                continue

            related_product = tool.Drawing.get_assigned_product(element)
            if not related_product:
                continue
            related_object = tool.Ifc.get_object(related_product)

            tool.Drawing.setup_annotation_object(obj, element.ObjectType, related_object)

    def hotkey_S_C(self):
        create_annotation_type(bpy.context)
