# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import re
import bpy
import mathutils
import webbrowser
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell.util.representation
import blenderbim.bim.module.drawing.sheeter as sheeter
import blenderbim.bim.module.drawing.annotation as annotation


class Drawing(blenderbim.core.tool.Drawing):
    @classmethod
    def create_annotation_object(cls, object_type):
        data_type = {
            "DIMENSION": "curve",
            "EQUAL_DIMENSION": "curve",
            "TEXT": "empty",
            "TEXT_LEADER": "curve",
            "STAIR_ARROW": "curve",
            "HIDDEN_LINE": "mesh",
            "PLAN_LEVEL": "curve",
            "SECTION_LEVEL": "curve",
            "BREAKLINE": "mesh",
            "MISC": "mesh",
        }[object_type]
        obj = annotation.Annotator.get_annotation_obj(object_type, data_type)
        if object_type == "BREAKLINE":
            obj = annotation.Annotator.add_plane_to_annotation(obj)
        elif object_type != "TEXT":
            obj = annotation.Annotator.add_line_to_annotation(obj)
        return obj

    @classmethod
    def create_camera(cls, name, matrix):
        camera = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        camera.location = (0, 0, 1.5)  # The view shall be 1.5m above the origin
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 50  # The default of 6m is too small
        camera.data.clip_end = 10  # A slightly more reasonable default
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            camera.data.BIMCameraProperties.diagram_scale = '1/8"=1\'-0"|1/96'
        else:
            camera.data.BIMCameraProperties.diagram_scale = "1:100|1/100"
        camera.matrix_world = matrix
        bpy.context.scene.collection.objects.link(camera)
        return camera

    @classmethod
    def create_svg_sheet(cls, document, titleblock):
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.create(cls.get_sheet_filename(document), titleblock)

    @classmethod
    def delete_collection(cls, collection):
        bpy.data.collections.remove(collection, do_unlink=True)

    @classmethod
    def delete_drawing_elements(cls, elements):
        for element in elements:
            tool.Ifc.delete(element)
            obj = tool.Ifc.get_object(element)
            if obj:
                bpy.data.objects.remove(obj)

    @classmethod
    def disable_editing_drawings(cls):
        bpy.context.scene.DocProperties.is_editing_drawings = False

    @classmethod
    def disable_editing_sheets(cls):
        bpy.context.scene.DocProperties.is_editing_sheets = False

    @classmethod
    def disable_editing_text(cls, obj):
        obj.BIMTextProperties.is_editing = False

    @classmethod
    def disable_editing_text_product(cls, obj):
        obj.BIMTextProperties.is_editing_product = False

    @classmethod
    def enable_editing(cls, obj):
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if obj.data:
            bpy.ops.object.mode_set(mode="EDIT")

    @classmethod
    def enable_editing_drawings(cls):
        bpy.context.scene.DocProperties.is_editing_drawings = True

    @classmethod
    def enable_editing_sheets(cls):
        bpy.context.scene.DocProperties.is_editing_sheets = True

    @classmethod
    def enable_editing_text(cls, obj):
        obj.BIMTextProperties.is_editing = True

    @classmethod
    def enable_editing_text_product(cls, obj):
        obj.BIMTextProperties.is_editing_product = True

    @classmethod
    def ensure_unique_drawing_name(cls, name):
        names = [e.Name for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        while name in names:
            name += "-X"
        return name

    @classmethod
    def ensure_unique_identification(cls, identification):
        if tool.Ifc.get_schema() == "IFC2X3":
            ids = [d.DocumentId for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"]
        else:
            ids = [
                d.Identification for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"
            ]
        while identification in ids:
            identification += "-X"
        return identification

    @classmethod
    def export_text_literal_attributes(cls, obj):
        return blenderbim.bim.helper.export_attributes(obj.BIMTextProperties.attributes)

    @classmethod
    def get_annotation_context(cls, target_view):
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Plan", "Annotation", target_view)

    @classmethod
    def get_body_context(cls):
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_drawing_collection(cls, drawing):
        obj = tool.Ifc.get_object(drawing)
        return obj.users_collection[0]

    @classmethod
    def get_drawing_group(cls, drawing):
        for rel in drawing.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToGroup"):
                return rel.RelatingGroup

    @classmethod
    def get_drawing_target_view(cls, drawing):
        return ifcopenshell.util.element.get_psets(drawing)["EPset_Drawing"]["TargetView"]

    @classmethod
    def get_group_elements(cls, group):
        for rel in group.IsGroupedBy or []:
            return rel.RelatedObjects

    @classmethod
    def get_ifc_representation_class(cls, object_type):
        if object_type == "TEXT":
            return "IfcTextLiteral"
        elif object_type == "TEXT_LEADER":
            return "IfcGeometricCurveSet/IfcTextLiteral"
        return ""

    @classmethod
    def get_name(cls, element):
        return element.Name

    @classmethod
    def get_sheet_filename(cls, document):
        if hasattr(document, "Identification"):
            name = document.Identification or "X"
        else:
            name = document.DocumentId or "X"
        name += " - " + document.Name or "Unnamed"
        return name

    @classmethod
    def generate_drawing_matrix(cls, target_view, location_hint):
        x = 0 if location_hint == 0 else bpy.context.scene.cursor.matrix[0][3]
        y = 0 if location_hint == 0 else bpy.context.scene.cursor.matrix[1][3]
        z = 0 if location_hint == 0 else bpy.context.scene.cursor.matrix[2][3]
        if target_view == "PLAN_VIEW":
            if location_hint:
                z = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint)).matrix_world[2][3]
                return mathutils.Matrix(((1, 0, 0, x), (0, 1, 0, y), (0, 0, 1, z + 1.6), (0, 0, 0, 1)))
        elif target_view == "REFLECTED_PLAN_VIEW":
            if location_hint:
                z = tool.Ifc.get_object(tool.Ifc.get().by_id(location_hint)).matrix_world[2][3]
                return mathutils.Matrix(((-1, 0, 0, x), (0, 1, 0, y), (0, 0, -1, z + 1.6), (0, 0, 0, 1)))
            return mathutils.Matrix(((-1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))
        elif target_view == "ELEVATION_VIEW":
            if location_hint == "NORTH":
                return mathutils.Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "SOUTH":
                return mathutils.Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "EAST":
                return mathutils.Matrix(((0, 0, 1, x), (1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "WEST":
                return mathutils.Matrix(((0, 0, -1, x), (-1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
        elif target_view == "SECTION_VIEW":
            if location_hint == "NORTH":
                return mathutils.Matrix(((1, 0, 0, x), (0, 0, -1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "SOUTH":
                return mathutils.Matrix(((-1, 0, 0, x), (0, 0, 1, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "EAST":
                return mathutils.Matrix(((0, 0, -1, x), (-1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
            elif location_hint == "WEST":
                return mathutils.Matrix(((0, 0, 1, x), (1, 0, 0, y), (0, 1, 0, z), (0, 0, 0, 1)))
        return mathutils.Matrix()

    @classmethod
    def generate_sheet_identification(cls):
        number = len([d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"])
        return "A" + str(number).zfill(2)

    @classmethod
    def get_text_literal(cls, obj):
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        rep = ifcopenshell.util.representation.get_representation(element, "Plan", "Annotation")
        if not rep:
            return
        items = [i for i in rep.Items if i.is_a("IfcTextLiteral")]
        if items:
            return items[0]

    @classmethod
    def get_text_product(cls, element):
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                return rel.RelatingProduct

    @classmethod
    def import_drawings(cls):
        bpy.context.scene.DocProperties.drawings.clear()
        drawings = [e for e in tool.Ifc.get().by_type("IfcAnnotation") if e.ObjectType == "DRAWING"]
        for drawing in drawings:
            new = bpy.context.scene.DocProperties.drawings.add()
            new.ifc_definition_id = drawing.id()
            new.name = drawing.Name or "Unnamed"

    @classmethod
    def import_sheets(cls):
        bpy.context.scene.DocProperties.sheets.clear()
        sheets = [d for d in tool.Ifc.get().by_type("IfcDocumentInformation") if d.Scope == "DOCUMENTATION"]
        for sheet in sheets:
            new = bpy.context.scene.DocProperties.sheets.add()
            new.ifc_definition_id = sheet.id()
            if tool.Ifc.get_schema() == "IFC2X3":
                new.identification = sheet.DocumentId
            else:
                new.identification = sheet.Identification
            new.name = sheet.Name

    @classmethod
    def import_text_attributes(cls, obj):
        props = obj.BIMTextProperties
        props.attributes.clear()
        text = cls.get_text_literal(obj)
        blenderbim.bim.helper.import_attributes2(text, props.attributes)

    @classmethod
    def import_text_product(cls, obj):
        element = tool.Ifc.get_entity(obj)
        product = cls.get_text_product(element)
        if product:
            obj.BIMTextProperties.relating_product = tool.Ifc.get_object(product)
        else:
            obj.BIMTextProperties.relating_product = None

    @classmethod
    def open_with_user_command(cls, user_command, path):
        if user_command:
            commands = eval(user_command)
            for command in commands:
                subprocess.run(command)
        else:
            webbrowser.open("file://" + path)

    @classmethod
    def open_svg(cls, filename):
        cls.open_with_user_command(
            bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
            os.path.join(bpy.context.scene.BIMProperties.data_dir, "sheets", filename + ".svg"),
        )

    @classmethod
    def run_root_assign_class(
        cls,
        obj=None,
        ifc_class=None,
        predefined_type=None,
        should_add_representation=True,
        context=None,
        ifc_representation_class=None,
    ):
        return blenderbim.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            should_add_representation=should_add_representation,
            context=context,
            ifc_representation_class=ifc_representation_class,
        )

    @classmethod
    def set_drawing_collection_name(cls, group, collection):
        collection.name = f"IfcGroup/{group.Name}"

    @classmethod
    def show_decorations(cls):
        bpy.context.scene.DocProperties.should_draw_decorations = True

    @classmethod
    def update_text_value(cls, obj):
        element = cls.get_text_literal(obj)
        if not element:
            return
        value = element.Literal
        product = cls.get_text_product(tool.Ifc.get_entity(obj))
        if product:
            selector = ifcopenshell.util.selector.Selector()
            variables = {}
            for variable in re.findall("{{.*?}}", value):
                value = value.replace(variable, selector.get_element_value(product, variable[2:-2]) or "")
        obj.BIMTextProperties.value = value
