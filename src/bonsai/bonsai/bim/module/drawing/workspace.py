# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 @Andrej730
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


import os
import bpy
import bonsai.core.type
import bonsai.tool as tool
from bonsai.bim.module.drawing.data import DecoratorData, AnnotationData
from bonsai.bim.helper import prop_with_search
from bpy.types import WorkSpaceTool


class LaunchAnnotationTypeManager(bpy.types.Operator):
    bl_idname = "bim.launch_annotation_type_manager"
    bl_label = "Launch Annotation Type Manager"
    bl_options = {"REGISTER"}
    bl_description = "Manage annotation types and templates"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=550)

    def draw(self, context):
        if not AnnotationData.is_loaded:
            AnnotationData.load()

        props = context.scene.BIMAnnotationProperties

        columns = self.layout.column_flow(columns=3)
        row = columns.row()
        row.alignment = "LEFT"
        row.label(text=f"{len(AnnotationData.data['relating_types'])} Types", icon="FILE_VOLUME")

        row = columns.row(align=True)
        row.alignment = "CENTER"
        # In case you want something here in the future

        row = columns.row(align=True)
        row.alignment = "RIGHT"
        # In case you want something here in the future

        if props.is_adding_type:
            row = self.layout.row()
            box = row.box()
            row = box.row()
            row.prop(props, "type_name")
            row = box.row()
            row.prop(props, "create_representation_for_type", text="Geometric Type")
            row = box.row(align=True)
            row.operator("bim.add_annotation_type", icon="CHECKMARK", text="Save New Type")
            row.operator("bim.disable_add_annotation_type", icon="CANCEL", text="")
        else:
            row = self.layout.row()
            row.operator("bim.enable_add_annotation_type", icon="ADD", text="Create New Type")

        flow = self.layout.grid_flow(row_major=True, columns=3, even_columns=True, even_rows=True, align=True)

        for relating_type in AnnotationData.data["relating_types"]:
            outer_col = flow.column()
            box = outer_col.box()

            row = box.row()
            row.alignment = "CENTER"
            row.label(text=relating_type["name"], icon="FILE_3D")

            row = box.row()
            row.alignment = "CENTER"
            row.label(text=relating_type["description"])

            row = box.row(align=True)

            op = row.operator("bim.select_type", icon="OBJECT_DATA")
            op.relating_type = relating_type["id"]
            op = row.operator("bim.rename_type", icon="GREASEPENCIL", text="")
            op.element = relating_type["id"]
            op = row.operator("bim.duplicate_type", icon="DUPLICATE", text="")
            op.element = relating_type["id"]
            op = row.operator("bim.remove_type", icon="X", text="")
            op.element = relating_type["id"]


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
def create_annotation_occurrence(context):
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

    bonsai.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=relating_type)

    tool.Ifc.run("group.assign_group", group=tool.Drawing.get_drawing_group(drawing), products=[element])
    tool.Collector.assign(obj)
    tool.Blender.select_and_activate_single_object(context, obj)

    if relating_type_repr is None and props.object_type == "IMAGE":
        bpy.ops.bim.add_reference_image("INVOKE_DEFAULT", use_existing_object_by_name=obj.name)


def create_annotation():
    props = bpy.context.scene.BIMAnnotationProperties
    if props.relating_type_id != "0":
        create_annotation_occurrence(bpy.context)
    else:
        object_type = props.object_type
        if not bpy.ops.bim.add_annotation.poll():
            return
        bpy.ops.bim.add_annotation(
            object_type=object_type, data_type=tool.Drawing.ANNOTATION_TYPES_DATA[object_type][-1]
        )
        if props.object_type == "IMAGE":
            bpy.ops.bim.add_reference_image(
                "INVOKE_DEFAULT", use_existing_object_by_name=bpy.context.active_object.name
            )


class AnnotationToolUI:
    @classmethod
    def draw(cls, context, layout):
        cls.layout = layout
        cls.props = context.scene.BIMAnnotationProperties

        row = cls.layout.row(align=True)
        if not tool.Ifc.get():
            row.label(text="No IFC Project", icon="ERROR")
            return

        drawing = tool.Ifc.get_entity(context.scene.camera)
        if not drawing:
            row.label(text="No Active Drawing", icon="ERROR")
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
        row.prop(bpy.context.scene.DocProperties, "should_draw_decorations", text="Viewport Annotations")

    @classmethod
    def draw_edit_object_interface(cls, context):
        if DecoratorData.get_ifc_text_data(bpy.context.active_object):
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
        row.operator("bim.launch_annotation_type_manager", icon=tool.Blender.TYPE_MANAGER_ICON, text="")

        add_layout_hotkey_operator(cls.layout, "Add", "S_A", "Create a new annotation")

        if object_type in tool.Drawing.ANNOTATION_TYPES_SUPPORT_SETUP:
            add_layout_hotkey_operator(
                cls.layout,
                "Bulk Tag",
                "S_T",
                "Create new annotations and automatically adjust them to the selected objects",
            )
            add_layout_hotkey_operator(
                cls.layout, "Readjust", "S_G", "Readjust tags based on the products they are assigned to"
            )


class Hotkey(bpy.types.Operator, tool.Ifc.Operator):
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
        if not (camera := context.scene.camera) or not tool.Ifc.get_entity(camera):
            self.report({"ERROR"}, "No drawing active for annotation hotkeys.")
            return {"CANCELLED"}

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
        annotation_type = props.object_type

        if annotation_type not in tool.Drawing.ANNOTATION_TYPES_SUPPORT_SETUP:
            self.report({"ERROR"}, f"Annotation type {annotation_type} is not supported for tagging.")
            return

        related_objects = bpy.context.selected_objects
        for related_object in related_objects:
            create_annotation()
            obj = bpy.context.active_object
            bpy.ops.object.mode_set(mode="OBJECT")
            tool.Drawing.setup_annotation_object(obj, annotation_type, related_object)

    def hotkey_S_A(self):
        create_annotation()

    def hotkey_S_E(self):
        if not bpy.context.active_object:
            return

        if DecoratorData.get_ifc_text_data(bpy.context.active_object):
            bpy.ops.bim.edit_text_popup()

    def hotkey_S_G(self):
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcAnnotation"):
                continue

            annotation_type = element.ObjectType
            if annotation_type not in tool.Drawing.ANNOTATION_TYPES_SUPPORT_SETUP:
                self.report({"ERROR"}, f"Annotation type {annotation_type} is not supported for readjustment.")
                continue

            related_product = tool.Drawing.get_assigned_product(element)
            if not related_product:
                self.report({"ERROR"}, "Selected annotation has no product assigned.")
                continue
            related_object = tool.Ifc.get_object(related_product)

            tool.Drawing.setup_annotation_object(obj, annotation_type, related_object)
