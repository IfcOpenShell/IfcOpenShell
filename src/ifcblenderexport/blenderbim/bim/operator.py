from itertools import chain
import os
import bpy
import uuid
import time
import json
import logging
import webbrowser
import subprocess
import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.geolocation
import ifcopenshell.util.element
import ifcopenshell.util.schema
import tempfile
import numpy as np
from . import export_ifc
from . import import_ifc
from . import qto
from . import cut_ifc
from . import svgwriter
from . import sheeter
from . import scheduler
from . import schema
from . import ifc
from . import annotation
from . import helper
from bpy_extras.io_utils import ImportHelper
from itertools import cycle
from mathutils import Vector, Matrix, Euler, geometry
import bmesh
from math import radians, degrees, atan, tan, cos, sin
from pathlib import Path
from bpy.app.handlers import persistent

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


@persistent
def depsgraph_update_pre_handler(scene):
    set_active_camera_resolution(scene)


def set_active_camera_resolution(scene):
    if not scene.camera or "/" not in scene.camera.name or not scene.DocProperties.drawings:
        return
    if (
        scene.render.resolution_x != scene.camera.data.BIMCameraProperties.raster_x
        or scene.render.resolution_y != scene.camera.data.BIMCameraProperties.raster_y
    ):
        scene.render.resolution_x = scene.camera.data.BIMCameraProperties.raster_x
        scene.render.resolution_y = scene.camera.data.BIMCameraProperties.raster_y
    current_drawing = scene.DocProperties.drawings[scene.DocProperties.current_drawing_index]
    if scene.camera != current_drawing.camera:
        scene.DocProperties.current_drawing_index = scene.DocProperties.drawings.find(scene.camera.name.split("/")[1])
        bpy.ops.bim.activate_view(drawing_index=scene.DocProperties.current_drawing_index)


def open_with_user_command(user_command, path):
    if user_command:
        commands = eval(user_command)
        for command in commands:
            subprocess.run(command)
    else:
        webbrowser.open("file://" + path)


class ExportIFC(bpy.types.Operator):
    bl_idname = "export_ifc.bim"
    bl_label = "Export IFC"
    filename_ext = ".ifc"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".ifc")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        start = time.time()
        logger = logging.getLogger("ExportIFC")
        logging.basicConfig(
            filename=context.scene.BIMProperties.data_dir + "process.log", filemode="a", level=logging.DEBUG
        )
        extension = self.filepath.split(".")[-1]
        if extension == "ifczip":
            output_file = bpy.path.ensure_ext(self.filepath, ".ifczip")
        elif extension == "ifcjson":
            output_file = bpy.path.ensure_ext(self.filepath, ".ifcjson")
        else:
            output_file = bpy.path.ensure_ext(self.filepath, ".ifc")
        ifc_export_settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        qto_calculator = qto.QtoCalculator()
        ifc_parser = export_ifc.IfcParser(ifc_export_settings, qto_calculator)
        ifc_exporter = export_ifc.IfcExporter(ifc_export_settings, ifc_parser)
        ifc_export_settings.logger.info("Starting export")
        ifc_exporter.export(context.selected_objects)
        ifc_export_settings.logger.info("Export finished in {:.2f} seconds".format(time.time() - start))
        if not bpy.context.scene.DocProperties.ifc_files:
            new = bpy.context.scene.DocProperties.ifc_files.add()
            new.name = output_file
        if not bpy.context.scene.BIMProperties.ifc_file:
            bpy.context.scene.BIMProperties.ifc_file = output_file
        return {"FINISHED"}


class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import_ifc.bim"
    bl_label = "Import IFC"
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})

    def execute(self, context):
        start = time.time()
        logger = logging.getLogger("ImportIFC")
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + "process.log", filemode="a", level=logging.DEBUG
        )
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, self.filepath, logger)
        ifc_import_settings.logger.info("Starting import")
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.execute()
        ifc_import_settings.logger.info("Import finished in {:.2f} seconds".format(time.time() - start))
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class SelectGlobalId(bpy.types.Operator):
    bl_idname = "bim.select_global_id"
    bl_label = "Select GlobalId"

    def execute(self, context):
        for obj in bpy.context.visible_objects:
            index = obj.BIMObjectProperties.attributes.find("GlobalId")
            if (
                index != -1
                and obj.BIMObjectProperties.attributes[index].string_value == bpy.context.scene.BIMProperties.global_id
            ):
                obj.select_set(True)
                break
        return {"FINISHED"}


class SelectAttribute(bpy.types.Operator):
    bl_idname = "bim.select_attribute"
    bl_label = "Select Attribute"

    def execute(self, context):
        import re

        search_value = bpy.context.scene.BIMProperties.search_attribute_value
        for object in bpy.context.visible_objects:
            index = object.BIMObjectProperties.attributes.find(bpy.context.scene.BIMProperties.search_attribute_name)
            if index == -1:
                continue
            value = object.BIMObjectProperties.attributes[index].string_value
            if (
                bpy.context.scene.BIMProperties.search_regex
                and bpy.context.scene.BIMProperties.search_ignorecase
                and re.search(search_value, value, flags=re.IGNORECASE)
            ):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_regex and re.search(search_value, value):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_ignorecase and value.lower() == search_value.lower():
                object.select_set(True)
            elif value == search_value:
                object.select_set(True)
        return {"FINISHED"}


class SelectPset(bpy.types.Operator):
    bl_idname = "bim.select_pset"
    bl_label = "Select Pset"

    def execute(self, context):
        import re

        search_pset_name = bpy.context.scene.BIMProperties.search_pset_name
        search_prop_name = bpy.context.scene.BIMProperties.search_prop_name
        search_value = bpy.context.scene.BIMProperties.search_pset_value
        for object in bpy.context.visible_objects:
            pset_index = object.BIMObjectProperties.psets.find(search_pset_name)
            if pset_index == -1:
                continue
            prop_index = object.BIMObjectProperties.psets[pset_index].properties.find(search_prop_name)
            if prop_index == -1:
                continue
            value = object.BIMObjectProperties.psets[pset_index].properties[prop_index].string_value
            if (
                bpy.context.scene.BIMProperties.search_regex
                and bpy.context.scene.BIMProperties.search_ignorecase
                and re.search(search_value, value, flags=re.IGNORECASE)
            ):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_regex and re.search(search_value, value):
                object.select_set(True)
            elif bpy.context.scene.BIMProperties.search_ignorecase and value.lower() == search_value.lower():
                object.select_set(True)
            elif value == search_value:
                object.select_set(True)
        return {"FINISHED"}


class SelectClass(bpy.types.Operator):
    bl_idname = "bim.select_class"
    bl_label = "Select IFC Class"

    def execute(self, context):
        for object in bpy.context.visible_objects:
            if (
                "/" in object.name
                and object.name[0:3] == "Ifc"
                and object.name.split("/")[0] == bpy.context.scene.BIMProperties.ifc_class
            ):
                object.select_set(True)
        return {"FINISHED"}


class SelectType(bpy.types.Operator):
    bl_idname = "bim.select_type"
    bl_label = "Select IFC Type"

    def execute(self, context):
        for object in bpy.context.visible_objects:
            if (
                "/" in object.name
                and object.name[0:3] == "Ifc"
                and object.name.split("/")[0] == bpy.context.scene.BIMProperties.ifc_class
                and "PredefinedType" in object.BIMObjectProperties.attributes
                and object.BIMObjectProperties.attributes["PredefinedType"].string_value
                == bpy.context.scene.BIMProperties.ifc_predefined_type
            ):
                if bpy.context.scene.BIMProperties.ifc_predefined_type != "USERDEFINED":
                    object.select_set(True)
                elif (
                    "ObjectType" in object.BIMObjectProperties.attributes
                    and object.BIMObjectProperties.attributes["ObjectType"].string_value
                    == bpy.context.scene.BIMProperties.ifc_userdefined_type
                ):
                    object.select_set(True)
        return {"FINISHED"}


class ColourByClass(bpy.types.Operator):
    bl_idname = "bim.colour_by_class"
    bl_label = "Colour by Class"

    def execute(self, context):
        colours = cycle(colour_list)
        ifc_classes = {}
        for obj in bpy.context.visible_objects:
            if "/" not in obj.name:
                continue
            ifc_class = obj.name.split("/")[0]
            if ifc_class not in ifc_classes:
                ifc_classes[ifc_class] = next(colours)
            obj.color = ifc_classes[ifc_class]
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class ColourByAttribute(bpy.types.Operator):
    bl_idname = "bim.colour_by_attribute"
    bl_label = "Colour by Attribute"

    def execute(self, context):
        colours = cycle(colour_list)
        values = {}
        attribute_name = bpy.context.scene.BIMProperties.search_attribute_name
        for obj in bpy.context.visible_objects:
            index = obj.BIMObjectProperties.attributes.find(attribute_name)
            if index == -1:
                continue
            value = obj.BIMObjectProperties.attributes[index].string_value
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class ColourByPset(bpy.types.Operator):
    bl_idname = "bim.colour_by_pset"
    bl_label = "Colour by Pset"

    def execute(self, context):
        colours = cycle(colour_list)
        values = {}
        search_pset_name = bpy.context.scene.BIMProperties.search_pset_name
        search_prop_name = bpy.context.scene.BIMProperties.search_prop_name
        for obj in bpy.context.visible_objects:
            pset_index = obj.BIMObjectProperties.psets.find(search_pset_name)
            if pset_index == -1:
                continue
            prop_index = obj.BIMObjectProperties.psets[pset_index].properties.find(search_prop_name)
            if prop_index == -1:
                continue
            value = obj.BIMObjectProperties.psets[pset_index].properties[prop_index].string_value
            if value not in values:
                values[value] = next(colours)
            obj.color = values[value]
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class ResetObjectColours(bpy.types.Operator):
    bl_idname = "bim.reset_object_colours"
    bl_label = "Reset Colours"

    def execute(self, context):
        for object in bpy.context.selected_objects:
            object.color = (1, 1, 1, 1)
        return {"FINISHED"}


class QAHelper:
    @classmethod
    def append_to_scenario(cls, lines):
        filename = os.path.join(
            bpy.context.scene.BIMProperties.features_dir, bpy.context.scene.BIMProperties.features_file + ".feature"
        )
        if os.path.exists(filename + "~"):
            os.remove(filename + "~")
        os.rename(filename, filename + "~")
        with open(filename, "w") as destination:
            with open(filename + "~", "r") as source:
                is_in_scenario = False
                for source_line in source:
                    if (
                        "Scenario: " in source_line
                        and bpy.context.scene.BIMProperties.scenario == source_line.strip()[len("Scenario: ") :]
                    ):
                        is_in_scenario = True
                    elif is_in_scenario:
                        for line in lines:
                            destination.write(line + "\n")
                        is_in_scenario = False
                    destination.write(source_line)
        os.remove(filename + "~")


class ApproveClass(bpy.types.Operator):
    bl_idname = "bim.approve_class"
    bl_label = "Approve Class"

    def execute(self, context):
        lines = []
        for object in bpy.context.selected_objects:
            index = object.BIMObjectProperties.attributes.find("GlobalId")
            if index != -1:
                lines.append(
                    " * The element {} is an {}".format(
                        object.BIMObjectProperties.attributes[index].string_value, object.name.split("/")[0]
                    )
                )
        QAHelper.append_to_scenario(lines)
        return {"FINISHED"}


class RejectClass(bpy.types.Operator):
    bl_idname = "bim.reject_class"
    bl_label = "Reject Class"

    def execute(self, context):
        lines = []
        for object in bpy.context.selected_objects:
            lines.append(
                " * The element {} is an {}".format(
                    object.BIMObjectProperties.attributes[
                        object.BIMObjectProperties.attributes.find("GlobalId")
                    ].string_value,
                    bpy.context.scene.BIMProperties.audit_ifc_class,
                )
            )
        QAHelper.append_to_scenario(lines)
        return {"FINISHED"}


class RejectElement(bpy.types.Operator):
    bl_idname = "bim.reject_element"
    bl_label = "Reject Element"

    def execute(self, context):
        lines = []
        for object in bpy.context.selected_objects:
            lines.append(
                " * The element {} should not exist because {}".format(
                    object.BIMObjectProperties.attributes[
                        object.BIMObjectProperties.attributes.find("GlobalId")
                    ].string_value,
                    bpy.context.scene.BIMProperties.qa_reject_element_reason,
                )
            )
        QAHelper.append_to_scenario(lines)
        return {"FINISHED"}


class OpenUri(bpy.types.Operator):
    bl_idname = "bim.open_uri"
    bl_label = "Open URI"
    uri: bpy.props.StringProperty()

    def execute(self, context):
        webbrowser.open(self.uri)
        return {"FINISHED"}


class SelectAudited(bpy.types.Operator):
    bl_idname = "bim.select_audited"
    bl_label = "Select Audited"

    def execute(self, context):
        audited_global_ids = []
        for filename in Path(bpy.context.scene.BIMProperties.features_dir).glob("*.feature"):
            with open(filename, "r") as feature_file:
                lines = feature_file.readlines()
                for line in lines:
                    words = line.strip().split()
                    for word in words:
                        if self.is_a_global_id(word):
                            audited_global_ids.append(word)
        for object in bpy.context.visible_objects:
            index = object.BIMObjectProperties.attributes.find("GlobalId")
            if index != -1 and object.BIMObjectProperties.attributes[index].string_value in audited_global_ids:
                object.select_set(True)
        return {"FINISHED"}

    def is_a_global_id(self, word):
        return word[0] in ["0", "1", "2", "3"] and len(word) == 22


class AddQto(bpy.types.Operator):
    bl_idname = "bim.add_qto"
    bl_label = "Add Qto"

    def execute(self, context):
        name = bpy.context.active_object.BIMObjectProperties.qto_name
        qto_template = schema.ifc.psetqto.get_by_name(name)
        if not qto_template:
            return {"FINISHED"}
        for obj in bpy.context.selected_objects:
            if "/" not in obj.name or obj.BIMObjectProperties.qtos.find(name) != -1:
                continue
            applicable_qtos = schema.ifc.psetqto.get_applicable_names(obj.name.split("/")[0], qto_only=True)
            if name not in applicable_qtos:
                continue
            qto = obj.BIMObjectProperties.qtos.add()
            qto.name = name
            for prop_name in (p.Name for p in qto_template.HasPropertyTemplates):
                prop = qto.properties.add()
                prop.name = prop_name
        return {"FINISHED"}


class RemoveQto(bpy.types.Operator):
    bl_idname = "bim.remove_qto"
    bl_label = "Remove Qto"
    index: bpy.props.IntProperty()

    def execute(self, context):
        name = bpy.context.active_object.BIMObjectProperties.qtos[self.index].name
        for obj in bpy.context.selected_objects:
            if "/" not in obj.name:
                continue
            index = obj.BIMObjectProperties.qtos.find(name)
            if index != -1:
                obj.BIMObjectProperties.qtos.remove(index)
        return {"FINISHED"}


class AddMaterialPset(bpy.types.Operator):
    bl_idname = "bim.add_material_pset"
    bl_label = "Add Material Pset"

    def execute(self, context):
        material = bpy.context.active_object.active_material
        name = material.BIMMaterialProperties.pset_name
        pset_template = schema.ifc.psetqto.get_by_name(name)
        if not pset_template:
            return {"FINISHED"}
        if material.BIMMaterialProperties.psets.find(name) != -1:
            return {"FINISHED"}
        pset = material.BIMMaterialProperties.psets.add()
        pset.name = name
        for prop_name in (p.Name for p in pset_template.HasPropertyTemplates):
            prop = pset.properties.add()
            prop.name = prop_name
        return {"FINISHED"}


class RemoveMaterialPset(bpy.types.Operator):
    bl_idname = "bim.remove_material_pset"
    bl_label = "Remove Pset"
    pset_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.active_material.BIMMaterialProperties.psets.remove(self.pset_index)
        return {"FINISHED"}


class AddConstraint(bpy.types.Operator):
    bl_idname = "bim.add_constraint"
    bl_label = "Add Constraint"

    def execute(self, context):
        constraint = bpy.context.scene.BIMProperties.constraints.add()
        constraint.name = "New Constraint"
        return {"FINISHED"}


class RemoveConstraint(bpy.types.Operator):
    bl_idname = "bim.remove_constraint"
    bl_label = "Remove Constraint"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.constraints.remove(self.index)
        return {"FINISHED"}


class AssignConstraint(bpy.types.Operator):
    bl_idname = "bim.assign_constraint"
    bl_label = "Assign Constraint"

    def execute(self, context):
        identification = bpy.context.scene.BIMProperties.constraints[
            bpy.context.scene.BIMProperties.active_constraint_index
        ].name
        for obj in bpy.context.selected_objects:
            if obj.BIMObjectProperties.constraints.get(identification):
                continue
            constraint = obj.BIMObjectProperties.constraints.add()
            constraint.name = identification
        return {"FINISHED"}


class UnassignConstraint(bpy.types.Operator):
    bl_idname = "bim.unassign_constraint"
    bl_label = "Unassign Constraint"

    def execute(self, context):
        identification = bpy.context.scene.BIMProperties.constraints[
            bpy.context.scene.BIMProperties.active_constraint_index
        ].name
        for obj in bpy.context.selected_objects:
            index = obj.BIMObjectProperties.constraints.find(identification)
            if index >= 0:
                obj.BIMObjectProperties.constraints.remove(index)
        return {"FINISHED"}


class RemoveObjectConstraint(bpy.types.Operator):
    bl_idname = "bim.remove_object_constraint"
    bl_label = "Remove Object Constraint"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.constraints.remove(self.index)
        return {"FINISHED"}


class AddDocumentInformation(bpy.types.Operator):
    bl_idname = "bim.add_document_information"
    bl_label = "Add Document Information"

    def execute(self, context):
        info = bpy.context.scene.BIMProperties.document_information.add()
        info.name = "New Document ID"
        return {"FINISHED"}


class RemoveDocumentInformation(bpy.types.Operator):
    bl_idname = "bim.remove_document_information"
    bl_label = "Remove Document Information"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.document_information.remove(self.index)
        return {"FINISHED"}


class AssignDocumentInformation(bpy.types.Operator):
    bl_idname = "bim.assign_document_information"
    bl_label = "Assign Document Information"
    index: bpy.props.IntProperty()

    def execute(self, context):
        reference = bpy.context.scene.BIMProperties.document_references[self.index]
        index = bpy.context.scene.BIMProperties.active_document_information_index
        info = bpy.context.scene.BIMProperties.document_information
        if index < len(info):
            reference.referenced_document = info[index].name
        return {"FINISHED"}


class AddDocumentReference(bpy.types.Operator):
    bl_idname = "bim.add_document_reference"
    bl_label = "Add Document Reference"

    def execute(self, context):
        document = bpy.context.scene.BIMProperties.document_references.add()
        document.name = "New Document Reference ID"
        return {"FINISHED"}


class RemoveDocumentReference(bpy.types.Operator):
    bl_idname = "bim.remove_document_reference"
    bl_label = "Remove Document Reference"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.document_references.remove(self.index)
        return {"FINISHED"}


class RemoveObjectDocumentReference(bpy.types.Operator):
    bl_idname = "bim.remove_object_document_reference"
    bl_label = "Remove Object Document Reference"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.document_references.remove(self.index)
        return {"FINISHED"}


class AssignDocumentReference(bpy.types.Operator):
    bl_idname = "bim.assign_document_reference"
    bl_label = "Assign Document Reference"

    def execute(self, context):
        identification = bpy.context.scene.BIMProperties.document_references[
            bpy.context.scene.BIMProperties.active_document_reference_index
        ].name
        for obj in bpy.context.selected_objects:
            if obj.BIMObjectProperties.document_references.get(identification):
                continue
            reference = obj.BIMObjectProperties.document_references.add()
            reference.name = identification
        return {"FINISHED"}


class UnassignDocumentReference(bpy.types.Operator):
    bl_idname = "bim.unassign_document_reference"
    bl_label = "Unassign Document Reference"

    def execute(self, context):
        identification = bpy.context.scene.BIMProperties.document_references[
            bpy.context.scene.BIMProperties.active_document_reference_index
        ].name
        for obj in bpy.context.selected_objects:
            index = obj.BIMObjectProperties.document_references.find(identification)
            if index >= 0:
                obj.BIMObjectProperties.document_references.remove(index)
        return {"FINISHED"}


class RemoveObjectDocumentReference(bpy.types.Operator):
    bl_idname = "bim.remove_object_document_reference"
    bl_label = "Remove Object Document Reference"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.document_references.remove(self.index)
        return {"FINISHED"}


class GenerateGlobalId(bpy.types.Operator):
    bl_idname = "bim.generate_global_id"
    bl_label = "Regenerate GlobalId"

    def execute(self, context):
        index = bpy.context.active_object.BIMObjectProperties.attributes.find("GlobalId")
        if index >= 0:
            global_id = bpy.context.active_object.BIMObjectProperties.attributes[index]
        else:
            global_id = bpy.context.active_object.BIMObjectProperties.attributes.add()
        global_id.name = "GlobalId"
        global_id.data_type = "string"
        global_id.string_value = ifcopenshell.guid.new()
        return {"FINISHED"}


class AddMaterialAttribute(bpy.types.Operator):
    bl_idname = "bim.add_material_attribute"
    bl_label = "Add Material Attribute"

    def execute(self, context):
        if bpy.context.active_object.active_material.BIMMaterialProperties.applicable_attributes:
            attribute = bpy.context.active_object.active_material.BIMMaterialProperties.attributes.add()
            attribute.name = bpy.context.active_object.active_material.BIMMaterialProperties.applicable_attributes
        return {"FINISHED"}


class RemoveMaterialAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_material_attribute"
    bl_label = "Remove Material Attribute"
    attribute_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.active_material.BIMMaterialProperties.attributes.remove(self.attribute_index)
        return {"FINISHED"}


class AddSweptSolid(bpy.types.Operator):
    bl_idname = "bim.add_swept_solid"
    bl_label = "Add Swept Solid"

    def execute(self, context):
        swept_solids = bpy.context.active_object.data.BIMMeshProperties.swept_solids
        swept_solid = swept_solids.add()
        swept_solid.name = "Swept Solid {}".format(len(swept_solids))
        return {"FINISHED"}


class RemoveSweptSolid(bpy.types.Operator):
    bl_idname = "bim.remove_swept_solid"
    bl_label = "Remove Swept Solid"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.data.BIMMeshProperties.swept_solids.remove(self.index)
        return {"FINISHED"}


class AssignSweptSolidOuterCurve(bpy.types.Operator):
    bl_idname = "bim.assign_swept_solid_outer_curve"
    bl_label = "Assign Outer Curve"
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != "EDIT_MESH":
            return {"FINISHED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        vertices = [v.index for v in bpy.context.active_object.data.vertices if v.select == True]
        bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].outer_curve = json.dumps(vertices)
        return {"FINISHED"}


class SelectSweptSolidOuterCurve(bpy.types.Operator):
    bl_idname = "bim.select_swept_solid_outer_curve"
    bl_label = "Select Outer Curve"
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != "EDIT_MESH":
            return {"FINISHED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        outer_curve = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].outer_curve
        if not outer_curve:
            return {"FINISHED"}
        indices = json.loads(outer_curve)
        for index in indices:
            bpy.context.active_object.data.vertices[index].select = True
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class AddSweptSolidInnerCurve(bpy.types.Operator):
    bl_idname = "bim.add_swept_solid_inner_curve"
    bl_label = "Add Inner Curve"
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != "EDIT_MESH":
            return {"FINISHED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        vertices = [v.index for v in bpy.context.active_object.data.vertices if v.select == True]
        swept_solid = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index]
        if swept_solid.inner_curves:
            curves = json.loads(swept_solid.inner_curves)
        else:
            curves = []
        curves.append(vertices)
        swept_solid.inner_curves = json.dumps(curves)
        return {"FINISHED"}


class SelectSweptSolidInnerCurves(bpy.types.Operator):
    bl_idname = "bim.select_swept_solid_inner_curves"
    bl_label = "Select Inner Curves"
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != "EDIT_MESH":
            return {"FINISHED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        inner_curves = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].inner_curves
        if not inner_curves:
            return {"FINISHED"}
        curves = json.loads(inner_curves)
        for curve in curves:
            for index in curve:
                bpy.context.active_object.data.vertices[index].select = True
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class AssignSweptSolidExtrusion(bpy.types.Operator):
    bl_idname = "bim.assign_swept_solid_extrusion"
    bl_label = "Assign Extrusion"
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != "EDIT_MESH":
            return {"FINISHED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        vertices = [v.index for v in bpy.context.active_object.data.vertices if v.select == True]
        bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].extrusion = json.dumps(vertices)
        return {"FINISHED"}


class SelectSweptSolidExtrusion(bpy.types.Operator):
    bl_idname = "bim.select_swept_solid_extrusion"
    bl_label = "Select Extrusion"
    index: bpy.props.IntProperty()

    def execute(self, context):
        if bpy.context.mode != "EDIT_MESH":
            return {"FINISHED"}
        bpy.ops.object.mode_set(mode="OBJECT")
        extrusion = bpy.context.active_object.data.BIMMeshProperties.swept_solids[self.index].extrusion
        if not extrusion:
            return {"FINISHED"}
        indices = json.loads(extrusion)
        for index in indices:
            bpy.context.active_object.data.vertices[index].select = True
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class SelectExternalMaterialDir(bpy.types.Operator):
    bl_idname = "bim.select_external_material_dir"
    bl_label = "Select Material File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.active_object.active_material.BIMMaterialProperties.location = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcPatch(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_patch"
    bl_label = "Execute IFCPatch"
    file_format: bpy.props.StringProperty()

    def execute(self, context):
        import ifcpatch

        ifcpatch.execute(
            {
                "input": bpy.context.scene.BIMProperties.ifc_patch_input,
                "output": bpy.context.scene.BIMProperties.ifc_patch_output,
                "recipe": bpy.context.scene.BIMProperties.ifc_patch_recipes,
                "arguments": json.loads("[" + bpy.context.scene.BIMProperties.ifc_patch_args + "]"),
                "log": bpy.context.scene.BIMProperties.data_dir + "process.log",
            }
        )
        return {"FINISHED"}


class SelectDiffJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_json_file"
    bl_label = "Select Diff JSON File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.diff_json_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class VisualiseDiff(bpy.types.Operator):
    bl_idname = "bim.visualise_diff"
    bl_label = "Visualise Diff"

    def execute(self, context):
        with open(bpy.context.scene.BIMProperties.diff_json_file, "r") as file:
            diff = json.load(file)
        for obj in bpy.context.visible_objects:
            obj.color = (1.0, 1.0, 1.0, 0.2)
            global_id = obj.BIMObjectProperties.attributes.get("GlobalId")
            if not global_id:
                continue
            if global_id.string_value in diff["deleted"]:
                obj.color = (1.0, 0.0, 0.0, 0.2)
            elif global_id.string_value in diff["added"]:
                obj.color = (0.0, 1.0, 0.0, 0.2)
            elif global_id.string_value in diff["changed"]:
                obj.color = (0.0, 0.0, 1.0, 0.2)
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SelectDiffOldFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_old_file"
    bl_label = "Select Diff Old File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.diff_old_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectDiffNewFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_new_file"
    bl_label = "Select Diff New File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.diff_new_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcDiff(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_diff"
    bl_label = "Execute IFC Diff"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifcdiff

        ifc_diff = ifcdiff.IfcDiff(
            bpy.context.scene.BIMProperties.diff_old_file,
            bpy.context.scene.BIMProperties.diff_new_file,
            self.filepath,
            bpy.context.scene.BIMProperties.diff_relationships.split(),
        )
        ifc_diff.diff()
        ifc_diff.export()
        bpy.context.scene.BIMProperties.diff_json_file = self.filepath
        return {"FINISHED"}


class ExportClashSets(bpy.types.Operator):
    bl_idname = "bim.export_clash_sets"
    bl_label = "Export Clash Sets"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        self.filepath = bpy.path.ensure_ext(self.filepath, ".json")
        clash_sets = []
        for clash_set in bpy.context.scene.BIMProperties.clash_sets:
            self.a = []
            self.b = []
            for ab in ["a", "b"]:
                for data in getattr(clash_set, ab):
                    clash_source = {"file": data.name}
                    if data.selector:
                        clash_source["selector"] = data.selector
                        clash_source["mode"] = data.mode
                    getattr(self, ab).append(clash_source)
            clash_sets.append({"name": clash_set.name, "tolerance": clash_set.tolerance, "a": self.a, "b": self.b})
        with open(self.filepath, "w") as destination:
            destination.write(json.dumps(clash_sets, indent=4))
        return {"FINISHED"}


class ImportClashSets(bpy.types.Operator):
    bl_idname = "bim.import_clash_sets"
    bl_label = "Import Clash Sets"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        with open(self.filepath) as f:
            clash_sets = json.load(f)
        for clash_set in clash_sets:
            new = bpy.context.scene.BIMProperties.clash_sets.add()
            new.name = clash_set["name"]
            new.tolerance = clash_set["tolerance"]
            for clash_source in clash_set["a"]:
                new_source = new.a.add()
                new_source.name = clash_source["file"]
                if "selector" in clash_source:
                    new_source.selector = clash_source["selector"]
                    new_source.mode = clash_source["mode"]
            if clash_set["b"]:
                for clash_source in clash_set["b"]:
                    new_source = new.b.add()
                    new_source.name = clash_source["file"]
                    if "selector" in clash_source:
                        new_source.selector = clash_source["selector"]
                        new_source.mode = clash_source["mode"]
        return {"FINISHED"}


class AddClashSet(bpy.types.Operator):
    bl_idname = "bim.add_clash_set"
    bl_label = "Add Clash Set"

    def execute(self, context):
        new = bpy.context.scene.BIMProperties.clash_sets.add()
        new.name = "New Clash Set"
        new.tolerance = 0.01
        return {"FINISHED"}


class RemoveClashSet(bpy.types.Operator):
    bl_idname = "bim.remove_clash_set"
    bl_label = "Remove Clash Set"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.clash_sets.remove(self.index)
        return {"FINISHED"}


class AddClashSource(bpy.types.Operator):
    bl_idname = "bim.add_clash_source"
    bl_label = "Add Clash Source"
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = bpy.context.scene.BIMProperties.clash_sets[bpy.context.scene.BIMProperties.active_clash_set_index]
        source = getattr(clash_set, self.group).add()
        return {"FINISHED"}


class RemoveClashSource(bpy.types.Operator):
    bl_idname = "bim.remove_clash_source"
    bl_label = "Remove Clash Source"
    index: bpy.props.IntProperty()
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = bpy.context.scene.BIMProperties.clash_sets[bpy.context.scene.BIMProperties.active_clash_set_index]
        getattr(clash_set, self.group).remove(self.index)
        return {"FINISHED"}


class SelectClashSource(bpy.types.Operator):
    bl_idname = "bim.select_clash_source"
    bl_label = "Select Clash Source"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    index: bpy.props.IntProperty()
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = bpy.context.scene.BIMProperties.clash_sets[bpy.context.scene.BIMProperties.active_clash_set_index]
        getattr(clash_set, self.group)[self.index].name = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectClashResults(bpy.types.Operator):
    bl_idname = "bim.select_clash_results"
    bl_label = "Select Clash Results"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.clash_results_path = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectSmartGroupedClashesPath(bpy.types.Operator):
    bl_idname = "bim.select_smart_grouped_clashes_path"
    bl_label = "Select Smart-Grouped Clashes Path"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.smart_grouped_clashes_path = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcClash(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_clash"
    bl_label = "Execute IFC Clash"
    filename_ext = ".bcf"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        if ".json" not in bpy.data.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".bcf")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifcclash

        settings = ifcclash.IfcClashSettings()
        if ".json" not in self.filepath:
            self.filepath = bpy.path.ensure_ext(self.filepath, ".bcf")
        settings.output = self.filepath
        settings.logger = logging.getLogger("Clash")
        settings.logger.setLevel(logging.DEBUG)
        ifc_clasher = ifcclash.IfcClasher(settings)

        if bpy.context.scene.BIMProperties.should_create_clash_snapshots:

            def get_viewpoint_snapshot(self, viewpoint, mat):
                camera = bpy.data.objects.get("IFC Clash Camera")
                if not camera:
                    camera = bpy.data.objects.new("IFC Clash Camera", bpy.data.cameras.new("IFC Clash Camera"))
                    bpy.context.scene.collection.objects.link(camera)
                camera.matrix_world = Matrix(mat)
                bpy.context.scene.camera = camera
                camera.data.angle = radians(60)
                area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
                area.spaces[0].region_3d.view_perspective = "CAMERA"
                area.spaces[0].shading.show_xray = True
                bpy.context.scene.render.resolution_x = 480
                bpy.context.scene.render.resolution_y = 270
                bpy.context.scene.render.image_settings.file_format = "PNG"
                bpy.context.scene.render.filepath = os.path.join(
                    bpy.context.scene.BIMProperties.data_dir, "snapshot.png"
                )
                bpy.ops.render.opengl(write_still=True)
                return bpy.context.scene.render.filepath

            ifcclash.IfcClasher.get_viewpoint_snapshot = get_viewpoint_snapshot

        ifc_clasher.clash_sets = []
        for clash_set in bpy.context.scene.BIMProperties.clash_sets:
            self.a = []
            self.b = []
            for ab in ["a", "b"]:
                for data in getattr(clash_set, ab):
                    clash_source = {"file": data.name}
                    if data.selector:
                        clash_source["selector"] = data.selector
                        clash_source["mode"] = data.mode
                    getattr(self, ab).append(clash_source)
            ifc_clasher.clash_sets.append(
                {"name": clash_set.name, "tolerance": clash_set.tolerance, "a": self.a, "b": self.b}
            )
        ifc_clasher.clash()
        ifc_clasher.export()
        return {"FINISHED"}


class SelectIfcClashResults(bpy.types.Operator):
    bl_idname = "bim.select_ifc_clash_results"
    bl_label = "Select IFC Clash Results"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        self.filepath = bpy.path.ensure_ext(self.filepath, ".json")
        with open(self.filepath) as f:
            clash_sets = json.load(f)
        clash_set_name = bpy.context.scene.BIMProperties.clash_sets[
            bpy.context.scene.BIMProperties.active_clash_set_index
        ].name
        global_ids = []
        for clash_set in clash_sets:
            if clash_set["name"] != clash_set_name:
                continue
            if not "clashes" in clash_set.keys():
                self.report({"WARNING"}, "No clashes found for the selected Clash Set.")
                return {"CANCELLED"}
            for clash in clash_set["clashes"].values():
                global_ids.extend([clash["a_global_id"], clash["b_global_id"]])
        for obj in bpy.context.visible_objects:
            global_id = obj.BIMObjectProperties.attributes.get("GlobalId")
            if global_id and global_id.string_value in global_ids:
                obj.select_set(True)
        return {"FINISHED"}


class SmartClashGroup(bpy.types.Operator):
    bl_idname = "bim.smart_clash_group"
    bl_label = "Smart Group Clashes"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        import ifcclash

        settings = ifcclash.IfcClashSettings()
        self.filepath = bpy.path.ensure_ext(bpy.context.scene.BIMProperties.clash_results_path, ".json")
        settings.output = self.filepath
        settings.logger = logging.getLogger("Clash")
        settings.logger.setLevel(logging.DEBUG)
        ifc_clasher = ifcclash.IfcClasher(settings)

        with open(self.filepath) as f:
            clash_sets = json.load(f)

        # execute the smart grouping
        save_path = bpy.path.ensure_ext(bpy.context.scene.BIMProperties.smart_grouped_clashes_path, ".json")
        smart_grouped_clashes = ifc_clasher.smart_group_clashes(
            clash_sets, bpy.context.scene.BIMProperties.smart_clash_grouping_max_distance
        )

        # save smart_groups to json
        with open(save_path, "w") as f:
            f.write(json.dumps(smart_grouped_clashes))

        clash_set_name = bpy.context.scene.BIMProperties.clash_sets[
            bpy.context.scene.BIMProperties.active_clash_set_index
        ].name

        # Reset the list of smart_clash_groups for the UI
        bpy.context.scene.BIMProperties.smart_clash_groups.clear()

        for clash_set, smart_groups in smart_grouped_clashes.items():
            # Only select the clashes that correspond to the actively selected IFC Clash Set
            if clash_set != clash_set_name:
                continue
            else:
                for smart_group, global_id_pairs in smart_groups[0].items():
                    new_group = bpy.context.scene.BIMProperties.smart_clash_groups.add()
                    new_group.number = f"{smart_group}"

                    for pair in global_id_pairs:
                        for id in pair:
                            new_global_id = new_group.global_ids.add()
                            new_global_id.name = id

        return {"FINISHED"}


class LoadSmartGroupsForActiveClashSet(bpy.types.Operator):
    bl_idname = "bim.load_smart_groups_for_active_clash_set"
    bl_label = "Load Smart Groups for Active Clash Set"

    def execute(self, context):
        smart_groups_path = bpy.path.ensure_ext(bpy.context.scene.BIMProperties.smart_grouped_clashes_path, ".json")

        clash_set_name = bpy.context.scene.BIMProperties.clash_sets[
            bpy.context.scene.BIMProperties.active_clash_set_index
        ].name

        with open(smart_groups_path) as f:
            smart_grouped_clashes = json.load(f)

        # Reset the list of smart_clash_groups for the UI
        bpy.context.scene.BIMProperties.smart_clash_groups.clear()

        for clash_set, smart_groups in smart_grouped_clashes.items():
            # Only select the clashes that correspond to the actively selected IFC Clash Set
            if clash_set != clash_set_name:
                continue
            else:
                for smart_group, global_id_pairs in smart_groups[0].items():
                    new_group = bpy.context.scene.BIMProperties.smart_clash_groups.add()
                    new_group.number = f"{smart_group}"
                    for pair in global_id_pairs:
                        for id in pair:
                            new_global_id = new_group.global_ids.add()
                            new_global_id.name = id

        return {"FINISHED"}


class SelectSmartGroup(bpy.types.Operator):
    bl_idname = "bim.select_smart_group"
    bl_label = "Select Smart Group"

    def execute(self, context):
        # Select smart group in view
        selected_smart_group = bpy.context.scene.BIMProperties.smart_clash_groups[
            bpy.context.scene.BIMProperties.active_smart_group_index
        ]
        # print(selected_smart_group.number)

        for obj in bpy.context.visible_objects:
            global_id = obj.BIMObjectProperties.attributes.get("GlobalId")
            if global_id:
                for id in selected_smart_group.global_ids:
                    # print("Id: ", id)
                    # print("Global id: ", global_id.string_value)
                    if global_id.string_value in id.name:
                        # print("object match: ", global_id)
                        obj.select_set(True)

        return {"FINISHED"}


class SelectFeaturesDir(bpy.types.Operator):
    bl_idname = "bim.select_features_dir"
    bl_label = "Select Features Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.features_dir = (
            os.path.dirname(os.path.abspath(self.filepath)) if "." in self.filepath else self.filepath
        )
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_ifc_file"
    bl_label = "Select IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ValidateIfcFile(bpy.types.Operator):
    bl_idname = "bim.validate_ifc_file"
    bl_label = "Validate IFC File"

    def execute(self, context):
        import ifcopenshell.validate

        logger = logging.getLogger("validate")
        logger.setLevel(logging.DEBUG)
        ifcopenshell.validate.validate(ifc.IfcStore.get_file(), logger)
        return {"FINISHED"}


class SelectDataDir(bpy.types.Operator):
    bl_idname = "bim.select_data_dir"
    bl_label = "Select Data Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.data_dir = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectSchemaDir(bpy.types.Operator):
    bl_idname = "bim.select_schema_dir"
    bl_label = "Select Schema Directory"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.schema_dir = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class CreateAggregate(bpy.types.Operator):
    bl_idname = "bim.create_aggregate"
    bl_label = "Create Aggregate"

    def execute(self, context):
        spatial_container = None
        for obj in bpy.context.selected_objects:
            if obj.instance_collection:
                return {"FINISHED"}
            for collection in obj.users_collection:
                if "IfcRelAggregates" in collection.name:
                    return {"FINISHED"}
                elif collection.name[0:3] == "Ifc":
                    spatial_container = collection
        if not spatial_container:
            return {"FINISHED"}

        aggregate = bpy.data.collections.new(
            "IfcRelAggregates/{}".format(bpy.context.scene.BIMProperties.aggregate_class)
        )
        for project in [c for c in bpy.context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            if not [c for c in project.children if "Aggregates" in c.name]:
                aggregates = bpy.data.collections.new("Aggregates")
                project.collection.children.link(aggregates)
            for aggregate_collection in [c for c in project.children if "Aggregates" in c.name]:
                aggregate_collection.collection.children.link(aggregate)
                break
            break
        for obj in bpy.context.selected_objects:
            for collection in obj.users_collection:
                collection.objects.unlink(obj)
            aggregate.objects.link(obj)

        instance = bpy.data.objects.new(
            "{}/{}".format(
                bpy.context.scene.BIMProperties.aggregate_class, bpy.context.scene.BIMProperties.aggregate_name
            ),
            None,
        )
        instance.instance_type = "COLLECTION"
        instance.instance_collection = aggregate
        spatial_container.objects.link(instance)
        return {"FINISHED"}


class EditAggregate(bpy.types.Operator):
    bl_idname = "bim.edit_aggregate"
    bl_label = "Edit Aggregate"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj.instance_type != "COLLECTION" or "IfcRelAggregates" not in obj.instance_collection.name:
            return {"FINISHED"}
        bpy.context.view_layer.objects[obj.name].hide_viewport = True
        for project in [c for c in bpy.context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            for aggregate_collection in [c for c in project.children if "Aggregates" in c.name]:
                aggregate_collection.hide_viewport = False
        return {"FINISHED"}


class SaveAggregate(bpy.types.Operator):
    bl_idname = "bim.save_aggregate"
    bl_label = "Save Aggregate"

    def execute(self, context):
        obj = bpy.context.active_object
        aggregate = None
        names = [c.name for c in obj.users_collection]
        for project in [c for c in bpy.context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            for aggregate_collection in [c for c in project.children if "Aggregates" in c.name]:
                aggregate_collection.hide_viewport = True
                for collection in [c for c in aggregate_collection.children if c.name in names]:
                    aggregate = collection.collection
                    break
        if not aggregate:
            return {"FINISHED"}
        for obj in bpy.context.view_layer.objects:
            if obj.instance_collection == aggregate:
                obj.hide_viewport = False
        return {"FINISHED"}


class ExplodeAggregate(bpy.types.Operator):
    bl_idname = "bim.explode_aggregate"
    bl_label = "Explode Aggregate"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj.instance_type != "COLLECTION" or "IfcRelAggregates" not in obj.instance_collection.name:
            return {"FINISHED"}
        aggregate_collection = bpy.data.collections.get(obj.instance_collection.name)
        spatial_collection = obj.users_collection[0]
        for part in aggregate_collection.objects:
            spatial_collection.objects.link(part)
            aggregate_collection.objects.unlink(part)
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(aggregate_collection, do_unlink=True)
        return {"FINISHED"}


class LoadClassification(bpy.types.Operator):
    bl_idname = "bim.load_classification"
    bl_label = "Load Classification"
    is_file: bpy.props.BoolProperty()
    classification_index: bpy.props.IntProperty()

    def execute(self, context):
        from . import prop

        if self.is_file:
            prop.ClassificationView.raw_data = schema.ifc.load_classification(
                context.scene.BIMProperties.classification
            )
        else:
            prop.ClassificationView.raw_data = schema.ifc.load_classification(
                context.scene.BIMProperties.classifications[self.classification_index].name, self.classification_index
            )
        context.scene.BIMProperties.classification_references.root = ""
        return {"FINISHED"}


class AddClassification(bpy.types.Operator):
    bl_idname = "bim.add_classification"
    bl_label = "Add Classification"

    def execute(self, context):
        if context.scene.BIMProperties.classification not in schema.ifc.classifications:
            return {"FINISHED"}
        data = schema.ifc.classifications[context.scene.BIMProperties.classification]
        classification = context.scene.BIMProperties.classifications.add()
        data_map = {
            "name": "Name",
            "source": "Source",
            "edition": "Edition",
            "edition_date": "EditionDate",
            "description": "Description",
            "location": "Location",
            "reference_tokens": "ReferenceTokens",
        }
        for key, value in data_map.items():
            if hasattr(data, value) and getattr(data, value):
                setattr(classification, key, str(getattr(data, value)))
        classification.data = schema.ifc.classification_files[context.scene.BIMProperties.classification].to_string()
        return {"FINISHED"}


class RemoveClassification(bpy.types.Operator):
    bl_idname = "bim.remove_classification"
    bl_label = "Remove Classification"
    classification_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.classifications.remove(self.classification_index)
        return {"FINISHED"}


class AssignClassification(bpy.types.Operator):
    bl_idname = "bim.assign_classification"
    bl_label = "Assign Classification"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            classification = obj.BIMObjectProperties.classifications.add()
            refs = bpy.context.scene.BIMProperties.classification_references
            data = refs.root["children"][refs.children[refs.active_index].name]
            if data["identification"]:
                classification.name = data["identification"]
            if data["name"]:
                classification.human_name = data["name"]
            for key in ["location", "description"]:
                if data[key]:
                    setattr(classification, key, data[key])
            classification.referenced_source = bpy.context.scene.BIMProperties.active_classification_name
        return {"FINISHED"}


class UnassignClassification(bpy.types.Operator):
    bl_idname = "bim.unassign_classification"
    bl_label = "Unassign Classification"

    def execute(self, context):
        refs = bpy.context.scene.BIMProperties.classification_references
        key = refs.children[refs.active_index].name
        for obj in bpy.context.selected_objects:
            index = obj.BIMObjectProperties.classifications.find(key)
            if index != -1:
                obj.BIMObjectProperties.classifications.remove(index)
        return {"FINISHED"}


class RemoveClassificationReference(bpy.types.Operator):
    bl_idname = "bim.remove_classification_reference"
    bl_label = "Remove Classification Reference"
    classification_index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.classifications.remove(self.classification_index)
        return {"FINISHED"}


class FetchExternalMaterial(bpy.types.Operator):
    bl_idname = "bim.fetch_external_material"
    bl_label = "Fetch External Material"

    def execute(self, context):
        location = bpy.context.active_object.active_material.BIMMaterialProperties.location
        if location[-6:] != ".mpass":
            return {"FINISHED"}
        if not os.path.isabs(location):
            location = os.path.join(os.path.join(bpy.context.scene.BIMProperties.data_dir, location))
        with open(location) as f:
            self.material_pass = json.load(f)
        if bpy.context.scene.render.engine == "BLENDER_EEVEE" and "eevee" in self.material_pass:
            self.fetch_eevee_or_cycles("eevee")
        elif bpy.context.scene.render.engine == "CYCLES" and "cycles" in self.material_pass:
            self.fetch_eevee_or_cycles("cycles")
        return {"FINISHED"}

    def fetch_eevee_or_cycles(self, name):
        identification = bpy.context.active_object.active_material.BIMMaterialProperties.identification
        uri = self.material_pass[name]["uri"]
        if not os.path.isabs(uri):
            uri = os.path.join(os.path.join(bpy.context.scene.BIMProperties.data_dir, uri))
        bpy.ops.wm.link(filename=identification, directory=os.path.join(uri, "Material"))
        for material in bpy.data.materials:
            if material.name == identification and material.library:
                bpy.context.active_object.material_slots[0].material = material
                return


class FetchLibraryInformation(bpy.types.Operator):
    bl_idname = "bim.fetch_library_information"
    bl_label = "Fetch Library Information"

    def execute(self, context):
        # TODO
        return {"FINISHED"}


class FetchObjectPassport(bpy.types.Operator):
    bl_idname = "bim.fetch_object_passport"
    bl_label = "Fetch Object Passport"

    def execute(self, context):
        for reference in bpy.context.active_object.BIMObjectProperties.document_references:
            reference = bpy.context.scene.BIMProperties.document_references[reference.name]
            if reference.location[-6:] == ".blend":
                self.fetch_blender(reference)
        return {"FINISHED"}

    def fetch_blender(self, reference):
        bpy.ops.wm.link(filename=reference.name, directory=os.path.join(reference.location, "Mesh"))
        bpy.context.active_object.data = bpy.data.meshes[reference.name]


class OpenView(bpy.types.Operator):
    bl_idname = "bim.open_view"
    bl_label = "Open View"
    view: bpy.props.StringProperty()

    def execute(self, context):
        open_with_user_command(
            bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
            os.path.join(bpy.context.scene.BIMProperties.data_dir, "diagrams", self.view + ".svg"),
        )
        return {"FINISHED"}


class OpenViewCamera(bpy.types.Operator):
    bl_idname = "bim.open_view_camera"
    bl_label = "Open View Camera"
    view_name: bpy.props.StringProperty()

    def execute(self, context):
        new_drawing_index = bpy.context.scene.DocProperties.drawings.find(self.view_name)
        bpy.context.scene.DocProperties.active_drawing_index = new_drawing_index
        drawing = bpy.context.scene.DocProperties.drawings[new_drawing_index]
        bpy.context.view_layer.objects.active = drawing.camera
        bpy.ops.object.select_all(action="DESELECT")
        drawing.camera.select_set(True)
        for area in bpy.context.screen.areas:
            if area.ui_type == "PROPERTIES":
                for space in area.spaces:
                    space.context = "DATA"
        return {"FINISHED"}


class CutSection(bpy.types.Operator):
    bl_idname = "bim.cut_section"
    bl_label = "Cut Section"

    def execute(self, context):
        self.file = ifc.IfcStore.get_file()
        camera = bpy.context.scene.camera
        if not (camera.type == "CAMERA" and camera.data.type == "ORTHO"):
            return {"FINISHED"}
        if not bpy.context.scene.DocProperties.ifc_files and bpy.context.scene.BIMProperties.ifc_file:
            new = bpy.context.scene.DocProperties.ifc_files.add()
            new.name = bpy.context.scene.BIMProperties.ifc_file
        bpy.ops.bim.activate_view(
            drawing_index=bpy.context.scene.DocProperties.drawings.find(camera.name.split("/")[1])
        )
        drawing_style = bpy.context.scene.DocProperties.drawing_styles[
            camera.data.BIMCameraProperties.active_drawing_style_index
        ]
        self.diagram_name = camera.name.split("/")[1]
        bpy.context.scene.render.filepath = os.path.join(
            bpy.context.scene.BIMProperties.data_dir, "diagrams", "{}.png".format(self.diagram_name)
        )
        self.create_raster(camera, drawing_style)
        location = camera.location
        render = bpy.context.scene.render
        if self.is_landscape():
            width = camera.data.ortho_scale
            height = width / render.resolution_x * render.resolution_y
        else:
            height = camera.data.ortho_scale
            width = height / render.resolution_y * render.resolution_x
        depth = camera.data.clip_end
        projection = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        x_axis = camera.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        y_axis = camera.matrix_world.to_quaternion() @ Vector((0, -1, 0))
        top_left_corner = location - (width / 2 * x_axis) - (height / 2 * y_axis)
        ifc_cutter = cut_ifc.IfcCutter()

        ifc_cutter.ifc_filenames = [i.name for i in bpy.context.scene.DocProperties.ifc_files]
        ifc_cutter.data_dir = bpy.context.scene.BIMProperties.data_dir
        ifc_cutter.vector_style = drawing_style.vector_style
        ifc_cutter.diagram_name = self.diagram_name
        ifc_cutter.background_image = bpy.context.scene.render.filepath
        if camera.data.BIMCameraProperties.cut_objects == "CUSTOM":
            ifc_cutter.cut_objects = camera.data.BIMCameraProperties.cut_objects_custom
        else:
            ifc_cutter.cut_objects = camera.data.BIMCameraProperties.cut_objects
        ifc_cutter.leader_obj = None
        ifc_cutter.stair_obj = None
        ifc_cutter.dimension_objs = []
        ifc_cutter.break_obj = None
        ifc_cutter.equal_objs = []
        ifc_cutter.hidden_objs = []
        ifc_cutter.solid_objs = []
        ifc_cutter.plan_level_obj = None
        ifc_cutter.section_level_obj = None
        ifc_cutter.grid_objs = []
        ifc_cutter.text_objs = []
        ifc_cutter.misc_objs = []
        ifc_cutter.attributes = [a.name for a in drawing_style.attributes]
        for obj in camera.users_collection[0].objects:
            if "IfcGrid" in obj.name:
                ifc_cutter.grid_objs.append(obj)
            elif "IfcGroup" in obj.name and obj.type == "CAMERA":
                ifc_cutter.camera_obj = obj

            if "IfcAnnotation/" not in obj.name:
                continue

            if "Leader" in obj.name:
                ifc_cutter.leader_obj = (obj, obj.data)
            elif "Stair" in obj.name:
                ifc_cutter.stair_obj = obj
            elif "Equal" in obj.name:
                ifc_cutter.equal_objs.append(obj)
            elif "Dimension" in obj.name:
                ifc_cutter.dimension_objs.append(obj)
            elif "Break" in obj.name:
                ifc_cutter.break_obj = obj
            elif "Hidden" in obj.name:
                ifc_cutter.hidden_objs.append((obj, obj.data))
            elif "Solid" in obj.name:
                ifc_cutter.solid_objs.append((obj, obj.data))
            elif "Plan Level" in obj.name:
                ifc_cutter.plan_level_obj = obj
            elif "Section Level" in obj.name:
                ifc_cutter.section_level_obj = obj
            elif obj.type == "FONT":
                ifc_cutter.text_objs.append(obj)
            else:
                ifc_cutter.misc_objs.append(obj)

        ifc_cutter.section_box = {
            "projection": tuple(projection),
            "x_axis": tuple(x_axis),
            "y_axis": tuple(y_axis),
            "top_left_corner": tuple(top_left_corner),
            "x": width,
            "y": height,
            "z": depth,
            "shape": None,
            "face": None,
        }
        ifc_cutter.cut_pickle_file = os.path.join(ifc_cutter.data_dir, "{}-cut.pickle".format(self.diagram_name))
        ifc_cutter.text_pickle_file = os.path.join(ifc_cutter.data_dir, "{}-text.pickle".format(self.diagram_name))
        ifc_cutter.metadata_pickle_file = os.path.join(
            ifc_cutter.data_dir, "{}-metadata.pickle".format(self.diagram_name)
        )
        ifc_cutter.should_recut = bpy.context.scene.DocProperties.should_recut
        ifc_cutter.should_recut_selected = bpy.context.scene.DocProperties.should_recut_selected
        selected_global_ids = []
        for obj in bpy.context.selected_objects:
            if "Ifc" not in obj.name:
                continue
            for attribute in obj.BIMObjectProperties.attributes:
                if attribute.name == "GlobalId":
                    selected_global_ids.append(attribute.string_value)
                    break
        ifc_cutter.selected_global_ids = selected_global_ids
        ifc_cutter.should_extract = bpy.context.scene.DocProperties.should_extract
        svg_writer = svgwriter.SvgWriter(ifc_cutter)
        if camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            human_scale, fraction = camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            human_scale, fraction = camera.data.BIMCameraProperties.diagram_scale.split("|")
        numerator, denominator = fraction.split("/")
        if camera.data.BIMCameraProperties.is_nts:
            svg_writer.human_scale = "NTS"
        else:
            svg_writer.human_scale = human_scale
        svg_writer.scale = float(numerator) / float(denominator)
        ifc_cutter.cut()
        svg_writer.write()
        bpy.ops.bim.open_view(view=self.diagram_name)
        return {"FINISHED"}

    def create_raster(self, camera, drawing_style):
        if drawing_style.render_type == "NONE":
            return

        if drawing_style.render_type == "DEFAULT":
            return bpy.ops.render.render(write_still=True)

        previous_visibility = {}
        for obj in camera.users_collection[0].objects:
            previous_visibility[obj.name] = obj.hide_get()
            obj.hide_set(True)
        for obj in bpy.context.visible_objects:
            if (
                (not obj.data and not obj.instance_collection)
                or isinstance(obj.data, bpy.types.Camera)
                or "IfcGrid/" in obj.name
                or "IfcGridAxis/" in obj.name
                or "IfcOpeningElement/" in obj.name
                or self.does_obj_have_target_view_representation(obj, camera)
            ):
                previous_visibility[obj.name] = obj.hide_get()
                obj.hide_set(True)

        space = self.get_view_3d()
        previous_shading = space.shading.type
        previous_format = bpy.context.scene.render.image_settings.file_format
        space.shading.type = "RENDERED"
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.opengl(write_still=True)
        space.shading.type = previous_shading
        bpy.context.scene.render.image_settings.file_format = previous_format

        for name, value in previous_visibility.items():
            bpy.data.objects[name].hide_set(value)

    def does_obj_have_target_view_representation(self, obj, camera):
        for representation in obj.BIMObjectProperties.representations:
            element = self.file.by_id(representation.ifc_definition_id)
            if ifcopenshell.util.element.is_representation_of_context(
                element, "Plan", "Annotation", camera.data.BIMCameraProperties.target_view
            ):
                return True

    def is_landscape(self):
        return bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y

    def get_view_3d(self):
        for area in bpy.context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space


class AddSheet(bpy.types.Operator):
    bl_idname = "bim.add_sheet"
    bl_label = "Add Sheet"

    def execute(self, context):
        new = bpy.context.scene.DocProperties.sheets.add()
        new.name = "{} - SHEET".format(len(bpy.context.scene.DocProperties.sheets))
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.create(new.name, bpy.context.scene.DocProperties.titleblock)
        return {"FINISHED"}


class OpenSheet(bpy.types.Operator):
    bl_idname = "bim.open_sheet"
    bl_label = "Open Sheet"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        open_with_user_command(
            bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
            os.path.join(
                bpy.context.scene.BIMProperties.data_dir, "sheets", props.sheets[props.active_sheet_index].name + ".svg"
            ),
        )
        return {"FINISHED"}


class AddDrawingToSheet(bpy.types.Operator):
    bl_idname = "bim.add_drawing_to_sheet"
    bl_label = "Add Drawing To Sheet"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        try:
            sheet_builder.add_drawing(
                props.drawings[props.active_drawing_index].name, props.sheets[props.active_sheet_index].name
            )
        except:
            self.report({"ERROR"}, "Drawings need to be created before being added to a sheet")
        return {"FINISHED"}


class CreateSheets(bpy.types.Operator):
    bl_idname = "bim.create_sheets"
    bl_label = "Create Sheets"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        name = props.sheets[props.active_sheet_index].name
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.build(name)

        svg2pdf_command = bpy.context.preferences.addons["blenderbim"].preferences.svg2pdf_command
        svg2dxf_command = bpy.context.preferences.addons["blenderbim"].preferences.svg2dxf_command

        if svg2pdf_command:
            path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", name)
            svg = os.path.join(path, name + ".svg")
            pdf = os.path.join(path, name + ".pdf")
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', pdf]]
            commands = eval(svg2pdf_command)
            for command in commands:
                subprocess.run(command)

        if svg2dxf_command:
            path = os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", name)
            svg = os.path.join(path, name + ".svg")
            eps = os.path.join(path, name + ".eps")
            dxf = os.path.join(path, name + ".dxf")
            base = os.path.join(path, name)
            # With great power comes great responsibility. Example:
            # [['inkscape', svg, '-o', eps], ['pstoedit', '-dt', '-f', 'dxf:-polyaslines -mm', eps, dxf, '-psarg', '-dNOSAFER']]
            commands = eval(svg2dxf_command)
            for command in commands:
                subprocess.run(command)

        if svg2pdf_command:
            open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.pdf_command, pdf)
        else:
            open_with_user_command(
                bpy.context.preferences.addons["blenderbim"].preferences.svg_command,
                os.path.join(bpy.context.scene.BIMProperties.data_dir, "build", name, name + ".svg"),
            )
        return {"FINISHED"}


class ActivateView(bpy.types.Operator):
    bl_idname = "bim.activate_view"
    bl_label = "Activate View"
    drawing_index: bpy.props.IntProperty()

    def execute(self, context):
        camera = bpy.context.scene.DocProperties.drawings[self.drawing_index].camera
        if not camera:
            return {"FINISHED"}
        bpy.context.scene.camera = camera
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].region_3d.view_perspective = "CAMERA"
        views_collection = bpy.data.collections.get("Views")
        for collection in views_collection.children:
            # We assume the project collection is at the top level
            for project_collection in bpy.context.view_layer.layer_collection.children:
                # We assume a convention that the 'Views' collection is directly
                # in the project collection
                if (
                    "Views" in project_collection.children
                    and collection.name in project_collection.children["Views"].children
                ):
                    project_collection.children["Views"].children[collection.name].hide_viewport = True
                    bpy.data.collections.get(collection.name).hide_render = True
        bpy.context.view_layer.layer_collection.children["Views"].children[
            camera.users_collection[0].name
        ].hide_viewport = False
        bpy.data.collections.get(camera.users_collection[0].name).hide_render = False
        bpy.ops.bim.activate_drawing_style()
        return {"FINISHED"}


class OpenUpstream(bpy.types.Operator):
    bl_idname = "bim.open_upstream"
    bl_label = "Open Upstream Reference"
    page: bpy.props.StringProperty()

    def execute(self, context):
        if self.page == "home":
            webbrowser.open("https://blenderbim.org/")
        elif self.page == "docs":
            webbrowser.open("https://blenderbim.org/docs/")
        elif self.page == "wiki":
            webbrowser.open("https://wiki.osarch.org/index.php?title=Category:BlenderBIM_Add-on")
        elif self.page == "community":
            webbrowser.open("https://community.osarch.org/")
        return {"FINISHED"}


class CopyPropertyToSelection(bpy.types.Operator):
    bl_idname = "bim.copy_property_to_selection"
    bl_label = "Copy Property To Selection"
    pset_name: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()
    prop_value: bpy.props.StringProperty()

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if "/" not in obj.name:
                continue
            pset = obj.BIMObjectProperties.psets.get(self.pset_name)
            if not pset:
                applicable_psets = schema.ifc.psetqto.get_applicable(obj.name.split("/")[0], pset_only=True)
                for pset_template in applicable_psets:
                    if pset_template.Name == self.pset_name:
                        break
                else:
                    continue
                pset = obj.BIMObjectProperties.psets.add()
                pset.name = self.pset_name
                for template_prop_name in (p.Name for p in pset_template.HasPropertyTemplates):
                    prop = pset.properties.add()
                    prop.name = template_prop_name
            prop = pset.properties.get(self.prop_name)
            if prop:
                prop.string_value = self.prop_value
        return {"FINISHED"}


class CopyAttributeToSelection(bpy.types.Operator):
    bl_idname = "bim.copy_attribute_to_selection"
    bl_label = "Copy Attribute To Selection"
    attribute_name: bpy.props.StringProperty()
    attribute_value: bpy.props.StringProperty()

    def execute(self, context):
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(bpy.context.scene.BIMProperties.export_schema)
        self.applicable_attributes_cache = {}
        for obj in bpy.context.selected_objects:
            if "/" not in obj.name:
                continue
            attribute = obj.BIMObjectProperties.attributes.get(self.attribute_name)
            if not attribute:
                applicable_attributes = self.get_applicable_attributes(obj.name.split("/")[0])
                if self.attribute_name not in applicable_attributes:
                    continue
                attribute = obj.BIMObjectProperties.attributes.add()
                attribute.name = self.attribute_name
            attribute.string_value = self.attribute_value
        return {"FINISHED"}

    def get_applicable_attributes(self, ifc_class):
        if ifc_class not in self.applicable_attributes_cache:
            self.applicable_attributes_cache[ifc_class] = [
                a.name() for a in self.schema.declaration_by_name(ifc_class).all_attributes()
            ]
        return self.applicable_attributes_cache[ifc_class]


class BIM_OT_ChangeClassificationLevel(bpy.types.Operator):
    bl_idname = "bim.change_classification_level"
    bl_label = "Change Classification Level"

    # string representing the id-data (e.g. the scene).
    path_sid: bpy.props.StringProperty()
    # path from the id-data to the classification view object
    path_lst: bpy.props.StringProperty()
    # name of child entity to enter (empty = go up one level)
    path_itm: bpy.props.StringProperty()

    def invoke(self, context, event):
        id_data = eval(self.path_sid)
        lst = id_data.path_resolve(self.path_lst)
        if self.path_itm:
            lst.root = self.path_itm
        else:
            lst.root = ""
        return {"FINISHED"}


class AddPropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.add_property_set_template"
    bl_label = "Add Property Set Template"

    def execute(self, context):
        context.scene.BIMProperties.active_property_set_template.global_id = ""
        context.scene.BIMProperties.active_property_set_template.name = "New_Pset"
        context.scene.BIMProperties.active_property_set_template.description = ""
        context.scene.BIMProperties.active_property_set_template.template_type = "PSET_TYPEDRIVENONLY"
        context.scene.BIMProperties.active_property_set_template.applicable_entity = "IfcTypeObject"
        while len(bpy.context.scene.BIMProperties.property_templates) > 0:
            bpy.context.scene.BIMProperties.property_templates.remove(0)
        return {"FINISHED"}


class RemovePropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.remove_property_set_template"
    bl_label = "Remove Property Set Template"

    def execute(self, context):
        template = ifc.IfcStore.pset_template_file.by_guid(context.scene.BIMProperties.property_set_templates)
        ifc.IfcStore.pset_template_file.remove(template)
        ifc.IfcStore.pset_template_file.write(ifc.IfcStore.pset_template_path)
        from . import prop

        prop.refreshPropertySetTemplates(self, context)
        return {"FINISHED"}


class EditPropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.edit_property_set_template"
    bl_label = "Edit Property Set Template"

    def execute(self, context):
        template = ifc.IfcStore.pset_template_file.by_guid(context.scene.BIMProperties.property_set_templates)
        context.scene.BIMProperties.active_property_set_template.global_id = template.GlobalId
        context.scene.BIMProperties.active_property_set_template.name = template.Name
        context.scene.BIMProperties.active_property_set_template.description = template.Description
        context.scene.BIMProperties.active_property_set_template.template_type = template.TemplateType
        context.scene.BIMProperties.active_property_set_template.applicable_entity = template.ApplicableEntity

        while len(bpy.context.scene.BIMProperties.property_templates) > 0:
            bpy.context.scene.BIMProperties.property_templates.remove(0)

        if template.HasPropertyTemplates:
            for property_template in template.HasPropertyTemplates:
                if not property_template.is_a("IfcSimplePropertyTemplate"):
                    continue
                new = context.scene.BIMProperties.property_templates.add()
                new.global_id = property_template.GlobalId
                new.name = property_template.Name
                new.description = property_template.Description
                new.primary_measure_type = property_template.PrimaryMeasureType
        return {"FINISHED"}


class SavePropertySetTemplate(bpy.types.Operator):
    bl_idname = "bim.save_property_set_template"
    bl_label = "Save Property Set Template"

    def execute(self, context):
        blender_property_set_template = context.scene.BIMProperties.active_property_set_template
        if blender_property_set_template.global_id:
            template = ifc.IfcStore.pset_template_file.by_guid(blender_property_set_template.global_id)
        else:
            template = ifc.IfcStore.pset_template_file.createIfcPropertySetTemplate()
            template.GlobalId = ifcopenshell.guid.new()
        template.Name = blender_property_set_template.name
        template.Description = blender_property_set_template.description
        template.TemplateType = blender_property_set_template.template_type
        template.ApplicableEntity = blender_property_set_template.applicable_entity

        saved_global_ids = []

        for blender_property_template in context.scene.BIMProperties.property_templates:
            if blender_property_template.global_id:
                property_template = ifc.IfcStore.pset_template_file.by_guid(blender_property_template.global_id)
            else:
                property_template = ifc.IfcStore.pset_template_file.createIfcSimplePropertyTemplate()
                property_template.GlobalId = ifcopenshell.guid.new()
                if template.HasPropertyTemplates:
                    has_property_templates = list(template.HasPropertyTemplates)
                else:
                    has_property_templates = []
                has_property_templates.append(property_template)
                template.HasPropertyTemplates = has_property_templates
            property_template.Name = blender_property_template.name
            property_template.Description = blender_property_template.description
            property_template.PrimaryMeasureType = blender_property_template.primary_measure_type
            property_template.TemplateType = "P_SINGLEVALUE"
            property_template.AccessState = "READWRITE"
            saved_global_ids.append(property_template.GlobalId)

        for element in template.HasPropertyTemplates:
            if element.GlobalId not in saved_global_ids:
                ifc.IfcStore.pset_template_file.remove(element)

        ifc.IfcStore.pset_template_file.write(ifc.IfcStore.pset_template_path)
        from . import prop

        prop.refreshPropertySetTemplates(self, context)
        return {"FINISHED"}


class AddPropertyTemplate(bpy.types.Operator):
    bl_idname = "bim.add_property_template"
    bl_label = "Add Property Template"

    def execute(self, context):
        context.scene.BIMProperties.property_templates.add()
        return {"FINISHED"}


class RemovePropertyTemplate(bpy.types.Operator):
    bl_idname = "bim.remove_property_template"
    bl_label = "Remove Property Template"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.property_templates.remove(self.index)
        return {"FINISHED"}


class AddSectionPlane(bpy.types.Operator):
    bl_idname = "bim.add_section_plane"
    bl_label = "Add Temporary Section Cutaway"

    def execute(self, context):
        obj = self.create_section_obj()
        if not self.has_section_override_node():
            self.create_section_compare_node()
            self.create_section_override_node(obj)
        else:
            self.append_obj_to_section_override_node(obj)
        self.add_default_material_if_none_exists()
        self.override_materials()
        return {"FINISHED"}

    def create_section_obj(self):
        section = bpy.data.objects.new("Section", None)
        section.empty_display_type = "SINGLE_ARROW"
        section.empty_display_size = 5
        section.show_in_front = True
        if (
            bpy.context.active_object
            and bpy.context.active_object.select_get()
            and isinstance(bpy.context.active_object.data, bpy.types.Camera)
        ):
            section.matrix_world = (
                bpy.context.active_object.matrix_world @ Euler((radians(180.0), 0.0, 0.0), "XYZ").to_matrix().to_4x4()
            )
        else:
            section.rotation_euler = Euler((radians(180.0), 0.0, 0.0), "XYZ")
            section.location = bpy.context.scene.cursor.location
        collection = bpy.data.collections.get("Sections")
        if not collection:
            collection = bpy.data.collections.new("Sections")
            bpy.context.scene.collection.children.link(collection)
        collection.objects.link(section)
        return section

    def has_section_override_node(self):
        return bpy.data.node_groups.get("Section Override")

    def create_section_compare_node(self):
        group = bpy.data.node_groups.new("Section Compare", type="ShaderNodeTree")
        group_input = group.nodes.new(type="NodeGroupInput")
        group_output = group.nodes.new(type="NodeGroupOutput")
        separate_xyz_a = group.nodes.new(type="ShaderNodeSeparateXYZ")
        separate_xyz_b = group.nodes.new(type="ShaderNodeSeparateXYZ")
        gt_a = group.nodes.new(type="ShaderNodeMath")
        gt_a.operation = "GREATER_THAN"
        gt_a.inputs[1].default_value = 0
        gt_b = group.nodes.new(type="ShaderNodeMath")
        gt_b.operation = "GREATER_THAN"
        gt_b.inputs[1].default_value = 0
        add = group.nodes.new(type="ShaderNodeMath")
        compare = group.nodes.new(type="ShaderNodeMath")
        compare.operation = "COMPARE"
        compare.inputs[1].default_value = 2
        group.links.new(group_input.outputs[""], separate_xyz_a.inputs[0])
        group.links.new(group_input.outputs[""], separate_xyz_b.inputs[0])
        group.links.new(separate_xyz_a.outputs[2], gt_a.inputs[0])
        group.links.new(separate_xyz_b.outputs[2], gt_b.inputs[0])
        group.links.new(gt_a.outputs[0], add.inputs[0])
        group.links.new(gt_b.outputs[0], add.inputs[1])
        group.links.new(add.outputs[0], compare.inputs[0])
        group.links.new(compare.outputs[0], group_output.inputs[""])

    def create_section_override_node(self, obj):
        group = bpy.data.node_groups.new("Section Override", type="ShaderNodeTree")

        group_input = group.nodes.new(type="NodeGroupInput")
        group_output = group.nodes.new(type="NodeGroupOutput")

        backfacing = group.nodes.new(type="ShaderNodeNewGeometry")
        backfacing_mix = group.nodes.new(type="ShaderNodeMixShader")
        emission = group.nodes.new(type="ShaderNodeEmission")
        emission.inputs[0].default_value = list(bpy.context.scene.BIMProperties.section_plane_colour) + [1]

        group.links.new(backfacing.outputs["Backfacing"], backfacing_mix.inputs[0])
        group.links.new(group_input.outputs[""], backfacing_mix.inputs[1])
        group.links.new(emission.outputs["Emission"], backfacing_mix.inputs[2])

        transparent = group.nodes.new(type="ShaderNodeBsdfTransparent")
        section_mix = group.nodes.new(type="ShaderNodeMixShader")
        section_mix.name = "Section Mix"

        group.links.new(transparent.outputs["BSDF"], section_mix.inputs[1])
        group.links.new(backfacing_mix.outputs["Shader"], section_mix.inputs[2])

        group.links.new(section_mix.outputs["Shader"], group_output.inputs[""])

        cut_obj = group.nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        section_compare = group.nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")
        section_compare.name = "Last Section Compare"
        value = group.nodes.new(type="ShaderNodeValue")
        value.name = "Mock Section"
        group.links.new(cut_obj.outputs["Object"], section_compare.inputs[0])
        group.links.new(value.outputs[0], section_compare.inputs[1])
        group.links.new(section_compare.outputs[0], section_mix.inputs[0])

    def append_obj_to_section_override_node(self, obj):
        group = bpy.data.node_groups.get("Section Override")
        cut_obj = group.nodes.new(type="ShaderNodeTexCoord")
        cut_obj.object = obj
        section_compare = group.nodes.new(type="ShaderNodeGroup")
        section_compare.node_tree = bpy.data.node_groups.get("Section Compare")

        last_compare = group.nodes.get("Last Section Compare")
        last_compare.name = "Section Compare"
        mock_section = group.nodes.get("Mock Section")
        section_mix = group.nodes.get("Section Mix")

        group.links.new(last_compare.outputs[0], section_compare.inputs[0])
        group.links.new(mock_section.outputs[0], section_compare.inputs[1])
        group.links.new(cut_obj.outputs["Object"], last_compare.inputs[1])
        group.links.new(section_compare.outputs[0], section_mix.inputs[0])

        section_compare.name = "Last Section Compare"

    def add_default_material_if_none_exists(self):
        material = bpy.data.materials.get("Section Override")
        if not material:
            material = bpy.data.materials.new("Section Override")
            material.use_nodes = True

        if bpy.context.scene.BIMProperties.should_section_selected_objects:
            objects = list(bpy.context.selected_objects)
        else:
            objects = list(bpy.context.visible_objects)

        for obj in objects:
            aggregate = obj.instance_collection
            if aggregate and "IfcRelAggregates/" in aggregate.name:
                for part in aggregate.objects:
                    objects.append(part)
            if not (obj.data and hasattr(obj.data, "materials") and obj.data.materials and obj.data.materials[0]):
                if obj.data and hasattr(obj.data, "materials"):
                    if len(obj.material_slots):
                        obj.material_slots[0].material = material
                    else:
                        obj.data.materials.append(material)

    def override_materials(self):
        override = bpy.data.node_groups.get("Section Override")
        for material in bpy.data.materials:
            material.use_nodes = True
            if material.node_tree.nodes.get("Section Override"):
                continue
            material.blend_method = "HASHED"
            material.shadow_method = "HASHED"
            material_output = self.get_node(material.node_tree.nodes, "OUTPUT_MATERIAL")
            if not material_output:
                continue
            from_socket = material_output.inputs[0].links[0].from_socket
            section_override = material.node_tree.nodes.new(type="ShaderNodeGroup")
            section_override.name = "Section Override"
            section_override.node_tree = override
            material.node_tree.links.new(from_socket, section_override.inputs[0])
            material.node_tree.links.new(section_override.outputs[0], material_output.inputs[0])

    def get_node(self, nodes, node_type):
        for node in nodes:
            if node.type == node_type:
                return node


class RemoveSectionPlane(bpy.types.Operator):
    bl_idname = "bim.remove_section_plane"
    bl_label = "Remove Temporary Section Cutaway"

    def execute(self, context):
        name = bpy.context.active_object.name
        section_override = bpy.data.node_groups.get("Section Override")
        if not section_override:
            return {"FINISHED"}
        for node in section_override.nodes:
            if node.type != "TEX_COORD" or node.object.name != name:
                continue
            section_compare = node.outputs["Object"].links[0].to_node
            # If the tex coord links to section_compare.inputs[1], it is called 'Input_3'
            if node.outputs["Object"].links[0].to_socket.identifier == "Input_3":
                section_override.links.new(
                    section_compare.inputs[0].links[0].from_socket, section_compare.outputs[0].links[0].to_socket
                )
            else:  # If it links to section_compare.inputs[0]
                if section_compare.inputs[1].links[0].from_node.name == "Mock Section":
                    # Then it is the very last section. Purge everything.
                    self.purge_all_section_data()
                    return {"FINISHED"}
                section_override.links.new(
                    section_compare.inputs[1].links[0].from_socket, section_compare.outputs[0].links[0].to_socket
                )
            section_override.nodes.remove(section_compare)
            section_override.nodes.remove(node)

            old_last_compare = section_override.nodes.get("Last Section Compare")
            old_last_compare.name = "Section Compare"
            section_mix = section_override.nodes.get("Section Mix")
            new_last_compare = section_mix.inputs[0].links[0].from_node
            new_last_compare.name = "Last Section Compare"
        bpy.ops.object.delete({"selected_objects": [bpy.context.active_object]})
        return {"FINISHED"}

    def purge_all_section_data(self):
        bpy.data.materials.remove(bpy.data.materials.get("Section Override"))
        for material in bpy.data.materials:
            if not material.node_tree:
                continue
            override = material.node_tree.nodes.get("Section Override")
            if not override:
                continue
            material.node_tree.links.new(
                override.inputs[0].links[0].from_socket, override.outputs[0].links[0].to_socket
            )
            material.node_tree.nodes.remove(override)
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Override"))
        bpy.data.node_groups.remove(bpy.data.node_groups.get("Section Compare"))
        bpy.ops.object.delete({"selected_objects": [bpy.context.active_object]})


class AddCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.add_csv_attribute"
    bl_label = "Add CSV Attribute"

    def execute(self, context):
        attribute = bpy.context.scene.BIMProperties.csv_attributes.add()
        return {"FINISHED"}


class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_csv_attribute"
    bl_label = "Remove CSV Attribute"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.csv_attributes.remove(self.index)
        return {"FINISHED"}


class ExportIfcCsv(bpy.types.Operator):
    bl_idname = "bim.export_ifccsv"
    bl_label = "Export IFC to CSV"
    filename_ext = ".csv"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".csv")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifccsv

        self.filepath = bpy.path.ensure_ext(self.filepath, ".csv")
        ifc_file = ifcopenshell.open(bpy.context.scene.BIMProperties.ifc_file)
        selector = ifcopenshell.util.selector.Selector()
        results = selector.parse(ifc_file, bpy.context.scene.BIMProperties.ifc_selector)
        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.attributes = [a.name for a in bpy.context.scene.BIMProperties.csv_attributes]
        ifc_csv.selector = selector
        if bpy.context.scene.BIMProperties.csv_delimiter == "CUSTOM":
            ifc_csv.delimiter = bpy.context.scene.BIMProperties.csv_custom_delimiter
        else:
            ifc_csv.delimiter = bpy.context.scene.BIMProperties.csv_delimiter
        ifc_csv.export(ifc_file, results)
        return {"FINISHED"}


class ImportIfcCsv(bpy.types.Operator):
    bl_idname = "bim.import_ifccsv"
    bl_label = "Import CSV to IFC"
    filename_ext = ".csv"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".csv")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifccsv

        ifc_csv = ifccsv.IfcCsv()
        ifc_csv.output = self.filepath
        ifc_csv.Import(bpy.context.scene.BIMProperties.ifc_file)
        return {"FINISHED"}


class EyedropIfcCsv(bpy.types.Operator):
    bl_idname = "bim.eyedrop_ifccsv"
    bl_label = "Query Selected Items"

    def execute(self, context):
        global_ids = []
        for obj in bpy.context.selected_objects:
            if hasattr(obj, "BIMObjectProperties") and obj.BIMObjectProperties.attributes.get("GlobalId"):
                global_ids.append("#" + obj.BIMObjectProperties.attributes.get("GlobalId").string_value)
        bpy.context.scene.BIMProperties.ifc_selector = "|".join(global_ids)
        return {"FINISHED"}


class ReloadIfcFile(bpy.types.Operator):
    bl_idname = "bim.reload_ifc_file"
    bl_label = "Reload IFC File"

    def execute(self, context):
        self.diff_ifc()
        self.reimport_ifc(context)
        return {"FINISHED"}

    def diff_ifc(self):
        import ifcdiff

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        ifc_diff = ifcdiff.IfcDiff(
            bpy.context.scene.BIMProperties.ifc_cache, bpy.context.scene.BIMProperties.ifc_file, temp_file.name
        )
        ifc_diff.diff()
        ifc_diff.export()
        bpy.context.scene.BIMProperties.diff_json_file = temp_file.name

    def reimport_ifc(self, context):
        logger = logging.getLogger("ImportIFC")
        logging.basicConfig(
            filename=bpy.context.scene.BIMProperties.data_dir + "process.log", filemode="a", level=logging.DEBUG
        )
        ifc_import_settings = import_ifc.IfcImportSettings.factory(
            context, bpy.context.scene.BIMProperties.ifc_file, logger
        )
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.execute()


class AddIfcFile(bpy.types.Operator):
    bl_idname = "bim.add_ifc_file"
    bl_label = "Add IFC File"

    def execute(self, context):
        bpy.context.scene.DocProperties.ifc_files.add()
        return {"FINISHED"}


class RemoveIfcFile(bpy.types.Operator):
    bl_idname = "bim.remove_ifc_file"
    bl_label = "Remove IFC File"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.ifc_files.remove(self.index)
        return {"FINISHED"}


class SelectDocIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_doc_ifc_file"
    bl_label = "Select Documentation IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.ifc_files[self.index].name = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class AddAnnotation(bpy.types.Operator):
    bl_idname = "bim.add_annotation"
    bl_label = "Add Annotation"
    obj_name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        if not bpy.context.scene.camera:
            return {"FINISHED"}
        if self.data_type == "text":
            if bpy.context.selected_objects:
                for selected_object in bpy.context.selected_objects:
                    obj = annotation.Annotator.add_text(related_element=selected_object)
            else:
                obj = annotation.Annotator.add_text()
        else:
            obj = annotation.Annotator.get_annotation_obj(self.obj_name, self.data_type)
            if self.obj_name == "Break":
                obj = annotation.Annotator.add_plane_to_annotation(obj)
            else:
                obj = annotation.Annotator.add_line_to_annotation(obj)
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class GenerateReferences(bpy.types.Operator):
    bl_idname = "bim.generate_references"
    bl_label = "Generate References"

    def execute(self, context):
        self.camera = bpy.context.scene.camera
        self.filter_potential_references()
        if self.camera.data.BIMCameraProperties.target_view == "PLAN_VIEW":
            self.generate_grids()
        if self.camera.data.BIMCameraProperties.target_view == "ELEVATION_VIEW":
            self.generate_grids()
            self.generate_levels()
        if self.camera.data.BIMCameraProperties.target_view == "SECTION_VIEW":
            self.generate_grids()
            self.generate_levels()
        return {"FINISHED"}

    def filter_potential_references(self):
        for name in ["grids", "levels"]:
            setattr(self, name, [])
        for obj in bpy.data.objects:
            if "IfcGridAxis/" in obj.name:
                self.grids.append(obj)
            if "IfcBuildingStorey/" in obj.name:
                self.levels.append(obj)

    def generate_grids(self):
        # TODO
        pass

    def generate_levels(self):
        if self.camera.data.BIMCameraProperties.raster_x > self.camera.data.BIMCameraProperties.raster_y:
            width = self.camera.data.ortho_scale
            height = (
                width / self.camera.data.BIMCameraProperties.raster_x * self.camera.data.BIMCameraProperties.raster_y
            )
        else:
            height = self.camera.data.ortho_scale
            width = (
                height / self.camera.data.BIMCameraProperties.raster_y * self.camera.data.BIMCameraProperties.raster_x
            )
        level_obj = annotation.Annotator.get_annotation_obj("Section Level", "curve")

        width_in_mm = width * 1000
        if self.camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            human_scale, fraction = self.camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            human_scale, fraction = self.camera.data.BIMCameraProperties.diagram_scale.split("|")
        numerator, denominator = fraction.split("/")
        scale = float(numerator) / float(denominator)
        real_world_width_in_mm = width_in_mm * scale
        offset_in_mm = 20
        offset_percentage = offset_in_mm / real_world_width_in_mm

        for obj in self.levels:
            projection = self.project_point_onto_camera(obj.location)
            co1 = self.camera.matrix_world @ Vector((width / 2 - (offset_percentage * width), projection[1], -1))
            co2 = self.camera.matrix_world @ Vector((-(width / 2), projection[1], -1))
            annotation.Annotator.add_line_to_annotation(level_obj, co1, co2)

    def project_point_onto_camera(self, point):
        projection = self.camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        return self.camera.matrix_world.inverted() @ geometry.intersect_line_plane(
            point.xyz, point.xyz - projection, self.camera.location, projection
        )


class ResizeText(bpy.types.Operator):
    bl_idname = "bim.resize_text"
    bl_label = "Resize Text"

    def execute(self, context):
        for obj in bpy.context.scene.camera.users_collection[0].objects:
            if isinstance(obj.data, bpy.types.TextCurve):
                annotation.Annotator.resize_text(obj)
        return {"FINISHED"}


class AddVariable(bpy.types.Operator):
    bl_idname = "bim.add_variable"
    bl_label = "Add Variable"

    def execute(self, context):
        bpy.context.active_object.data.BIMTextProperties.variables.add()
        return {"FINISHED"}


class RemoveVariable(bpy.types.Operator):
    bl_idname = "bim.remove_variable"
    bl_label = "Remove Variable"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.data.BIMTextProperties.variables.remove(self.index)
        return {"FINISHED"}


class PropagateTextData(bpy.types.Operator):
    bl_idname = "bim.propagate_text_data"
    bl_label = "Propagate Text Data"

    def execute(self, context):
        source = bpy.context.active_object
        for obj in bpy.context.selected_objects:
            if obj == source:
                continue
            obj.data.body = source.data.body
            obj.data.align_x = source.data.align_x
            obj.data.align_y = source.data.align_y
            obj.data.BIMTextProperties.font_size = source.data.BIMTextProperties.font_size
            obj.data.BIMTextProperties.symbol = source.data.BIMTextProperties.symbol
            while len(obj.data.BIMTextProperties.variables) > 0:
                obj.data.BIMTextProperties.variables.remove(0)
            for variable in source.data.BIMTextProperties.variables:
                new_variable = obj.data.BIMTextProperties.variables.add()
                new_variable.name = variable.name
                new_variable.prop_key = variable.prop_key
        return {"FINISHED"}


class ConvertLocalToGlobal(bpy.types.Operator):
    bl_idname = "bim.convert_local_to_global"
    bl_label = "Convert Local To Global"

    def execute(self, context):
        if bpy.context.scene.MapConversion.scale:
            scale = float(bpy.context.scene.MapConversion.scale)
        else:
            scale = 1.0
        results = ifcopenshell.util.geolocation.xyz2enh(
            bpy.context.scene.cursor.location[0],
            bpy.context.scene.cursor.location[1],
            bpy.context.scene.cursor.location[2],
            float(bpy.context.scene.MapConversion.eastings),
            float(bpy.context.scene.MapConversion.northings),
            float(bpy.context.scene.MapConversion.orthogonal_height),
            float(bpy.context.scene.MapConversion.x_axis_abscissa),
            float(bpy.context.scene.MapConversion.x_axis_ordinate),
            scale,
        )
        print("Coordinates:", results)
        bpy.context.scene.cursor.location = results
        return {"FINISHED"}


class ConvertGlobalToLocal(bpy.types.Operator):
    bl_idname = "bim.convert_global_to_local"
    bl_label = "Convert Global To Local"

    def execute(self, context):
        if bpy.context.scene.MapConversion.scale:
            scale = float(bpy.context.scene.MapConversion.scale)
        else:
            scale = 1.0
        results = ifcopenshell.util.geolocation.enh2xyz(
            float(bpy.context.scene.BIMProperties.eastings),
            float(bpy.context.scene.BIMProperties.northings),
            float(bpy.context.scene.BIMProperties.orthogonal_height),
            float(bpy.context.scene.MapConversion.eastings),
            float(bpy.context.scene.MapConversion.northings),
            float(bpy.context.scene.MapConversion.orthogonal_height),
            float(bpy.context.scene.MapConversion.x_axis_abscissa),
            float(bpy.context.scene.MapConversion.x_axis_ordinate),
            scale,
        )
        print("Coordinates:", results)
        bpy.context.scene.cursor.location = results
        return {"FINISHED"}


class GuessQuantity(bpy.types.Operator):
    bl_idname = "bim.guess_quantity"
    bl_label = "Guess Quantity"
    qto_index: bpy.props.IntProperty()
    prop_index: bpy.props.IntProperty()

    def execute(self, context):
        self.qto_calculator = qto.QtoCalculator()
        source_qto = bpy.context.active_object.BIMObjectProperties.qtos[self.qto_index]
        props = source_qto.properties
        prop = props[self.prop_index]
        for obj in bpy.context.selected_objects:
            dest_qto = obj.BIMObjectProperties.qtos.get(source_qto.name)
            if not dest_qto:
                if source_qto.name not in obj.BIMObjectProperties.qto_name:
                    continue
                dest_qto = self.add_qto(obj, source_qto.name)
            prop = dest_qto.properties.get(prop.name)
            self.guess_quantity(obj, prop, props)
        return {"FINISHED"}

    def guess_quantity(self, obj, prop, props):
        quantity = self.qto_calculator.guess_quantity(prop.name, [p.name for p in props], obj)
        if "area" in prop.name.lower():
            if bpy.context.scene.BIMProperties.area_unit:
                prefix, name = self.get_prefix_name(bpy.context.scene.BIMProperties.area_unit)
                quantity = helper.SIUnitHelper.convert(quantity, None, "SQUARE_METRE", prefix, name)
        elif "volume" in prop.name.lower():
            if bpy.context.scene.BIMProperties.volume_unit:
                prefix, name = self.get_prefix_name(bpy.context.scene.BIMProperties.volume_unit)
                quantity = helper.SIUnitHelper.convert(quantity, None, "CUBIC_METRE", prefix, name)
        else:
            prefix, name = self.get_blender_prefix_name()
            quantity = helper.SIUnitHelper.convert(quantity, None, "METRE", prefix, name)
        prop.string_value = str(round(quantity, 3))

    def add_qto(self, obj, name):
        qto_template = schema.ifc.psetqto.get_by_name(name)
        if not qto_template:
            return
        qto = obj.BIMObjectProperties.qtos.add()
        qto.name = name
        for prop_name in (p.Name for p in qto_template.HasPropertyTemplates):
            prop = qto.properties.add()
            prop.name = prop_name
        return qto

    def get_prefix_name(self, value):
        if "/" in value:
            return value.split("/")
        return None, value

    def get_blender_prefix_name(self):
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            if bpy.context.scene.unit_settings.length_unit == "INCHES":
                return None, "inch"
            elif bpy.context.scene.unit_settings.length_unit == "FEET":
                return None, "foot"
        elif bpy.context.scene.unit_settings.system == "METRIC":
            if bpy.context.scene.unit_settings.length_unit == "METERS":
                return None, "METRE"
            return bpy.context.scene.unit_settings.length_unit[0 : -len("METERS")], "METRE"


class ExecuteBIMTester(bpy.types.Operator):
    bl_idname = "bim.execute_bim_tester"
    bl_label = "Execute BIMTester"

    def execute(self, context):
        import bimtester
        import bimtester.run
        import bimtester.reports

        filename = os.path.join(
            bpy.context.scene.BIMProperties.features_dir, bpy.context.scene.BIMProperties.features_file + ".feature"
        )
        cwd = os.getcwd()
        os.chdir(bpy.context.scene.BIMProperties.features_dir)
        bimtester.run.run_tests({"feature": filename, "advanced_arguments": None, "console": False})
        bimtester.reports.generate_report()
        webbrowser.open(
            "file://"
            + os.path.join(
                bpy.context.scene.BIMProperties.features_dir,
                "report",
                bpy.context.scene.BIMProperties.features_file + ".feature.html",
            )
        )
        os.chdir(cwd)
        return {"FINISHED"}


class BIMTesterPurge(bpy.types.Operator):
    bl_idname = "bim.bim_tester_purge"
    bl_label = "Purge Tests"

    def execute(self, context):
        import bimtester
        import bimtester.clean

        filename = os.path.join(
            bpy.context.scene.BIMProperties.features_dir, bpy.context.scene.BIMProperties.features_file + ".feature"
        )
        cwd = os.getcwd()
        os.chdir(bpy.context.scene.BIMProperties.features_dir)
        bimtester.clean.TestPurger().purge()
        os.chdir(cwd)
        return {"FINISHED"}


class SelectIfcPatchInput(bpy.types.Operator):
    bl_idname = "bim.select_ifc_patch_input"
    bl_label = "Select IFC Patch Input"
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.ifc_patch_input = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectIfcPatchOutput(bpy.types.Operator):
    bl_idname = "bim.select_ifc_patch_output"
    bl_label = "Select IFC Patch Output"
    filename_ext = ".ifc"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.BIMProperties.ifc_patch_output = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class CalculateEdgeLengths(bpy.types.Operator):
    bl_idname = "bim.calculate_edge_lengths"
    bl_label = "Calculate Edge Lengths"

    def execute(self, context):
        result = 0
        for obj in bpy.context.selected_objects:
            if not obj.data or not obj.data.edges:
                continue
            for edge in obj.data.edges:
                if edge.select:
                    result += (obj.data.vertices[edge.vertices[1]].co - obj.data.vertices[edge.vertices[0]].co).length
        bpy.context.scene.BIMProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateFaceAreas(bpy.types.Operator):
    bl_idname = "bim.calculate_face_areas"
    bl_label = "Calculate Face Areas"

    def execute(self, context):
        result = 0
        for obj in bpy.context.selected_objects:
            if not obj.data or not obj.data.polygons:
                continue
            for polygon in obj.data.polygons:
                if polygon.select:
                    result += polygon.area
        bpy.context.scene.BIMProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateObjectVolumes(bpy.types.Operator):
    bl_idname = "bim.calculate_object_volumes"
    bl_label = "Calculate Object Volumes"

    def execute(self, context):
        qto_calculator = qto.QtoCalculator()
        result = 0
        for obj in bpy.context.selected_objects:
            if not obj.data:
                continue
            result += qto_calculator.get_volume(obj)
        bpy.context.scene.BIMProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class AddOpening(bpy.types.Operator):
    bl_idname = "bim.add_opening"
    bl_label = "Add Opening"

    def execute(self, context):
        if context.active_object.children and "IfcOpeningElement/" in context.active_object.children[0].name:
            opening = context.active_object.children[0]
        else:
            opening = context.active_object
        if context.selected_objects[0] != context.active_object:
            obj = context.selected_objects[0]
        else:
            obj = context.selected_objects[1]
        modifier = obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.object = opening
        return {"FINISHED"}


class SetOverrideColour(bpy.types.Operator):
    bl_idname = "bim.set_override_colour"
    bl_label = "Set Override Colour"

    def execute(self, context):
        result = 0
        for obj in bpy.context.selected_objects:
            obj.color = bpy.context.scene.BIMProperties.override_colour
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class AddDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.add_drawing_style"
    bl_label = "Add Drawing Style"

    def execute(self, context):
        new = bpy.context.scene.DocProperties.drawing_styles.add()
        new.name = "New Drawing Style"
        return {"FINISHED"}


class RemoveDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_style"
    bl_label = "Remove Drawing Style"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.DocProperties.drawing_styles.remove(self.index)
        return {"FINISHED"}


class SaveDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.save_drawing_style"
    bl_label = "Save Drawing Style"
    index: bpy.props.StringProperty()

    def execute(self, context):
        space = self.get_view_3d()
        style = {
            "bpy.data.worlds[0].color": tuple(bpy.data.worlds[0].color),
            "bpy.context.scene.render.engine": bpy.context.scene.render.engine,
            "bpy.context.scene.render.film_transparent": bpy.context.scene.render.film_transparent,
            "bpy.context.scene.display.shading.show_object_outline": bpy.context.scene.display.shading.show_object_outline,
            "bpy.context.scene.display.shading.show_cavity": bpy.context.scene.display.shading.show_cavity,
            "bpy.context.scene.display.shading.cavity_type": bpy.context.scene.display.shading.cavity_type,
            "bpy.context.scene.display.shading.curvature_ridge_factor": bpy.context.scene.display.shading.curvature_ridge_factor,
            "bpy.context.scene.display.shading.curvature_valley_factor": bpy.context.scene.display.shading.curvature_valley_factor,
            "bpy.context.scene.view_settings.view_transform": bpy.context.scene.view_settings.view_transform,
            "bpy.context.scene.display.shading.light": bpy.context.scene.display.shading.light,
            "bpy.context.scene.display.shading.color_type": bpy.context.scene.display.shading.color_type,
            "bpy.context.scene.display.shading.single_color": tuple(bpy.context.scene.display.shading.single_color),
            "bpy.context.scene.display.shading.show_shadows": bpy.context.scene.display.shading.show_shadows,
            "bpy.context.scene.display.shading.shadow_intensity": bpy.context.scene.display.shading.shadow_intensity,
            "bpy.context.scene.display.light_direction": tuple(bpy.context.scene.display.light_direction),
            "bpy.context.scene.view_settings.use_curve_mapping": bpy.context.scene.view_settings.use_curve_mapping,
            "space.overlay.show_wireframes": space.overlay.show_wireframes,
            "space.overlay.wireframe_threshold": space.overlay.wireframe_threshold,
            "space.overlay.show_floor": space.overlay.show_floor,
            "space.overlay.show_axis_x": space.overlay.show_axis_x,
            "space.overlay.show_axis_y": space.overlay.show_axis_y,
            "space.overlay.show_axis_z": space.overlay.show_axis_z,
            "space.overlay.show_object_origins": space.overlay.show_object_origins,
            "space.overlay.show_relationship_lines": space.overlay.show_relationship_lines,
        }
        if self.index:
            index = int(self.index)
        else:
            index = bpy.context.active_object.data.BIMCameraProperties.active_drawing_style_index
        bpy.context.scene.DocProperties.drawing_styles[index].raster_style = json.dumps(style)
        return {"FINISHED"}

    def get_view_3d(self):
        for area in bpy.context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space


class ActivateDrawingStyle(bpy.types.Operator):
    bl_idname = "bim.activate_drawing_style"
    bl_label = "Activate Drawing Style"

    def execute(self, context):
        if context.scene.camera.data.BIMCameraProperties.active_drawing_style_index < len(
            bpy.context.scene.DocProperties.drawing_styles
        ):
            self.drawing_style = bpy.context.scene.DocProperties.drawing_styles[
                context.scene.camera.data.BIMCameraProperties.active_drawing_style_index
            ]
            self.set_raster_style()
            self.set_query()
        return {"FINISHED"}

    def set_raster_style(self):
        space = self.get_view_3d()
        style = json.loads(self.drawing_style.raster_style)
        bpy.data.worlds[0].color = style["bpy.data.worlds[0].color"]
        bpy.context.scene.render.engine = style["bpy.context.scene.render.engine"]
        bpy.context.scene.render.film_transparent = style["bpy.context.scene.render.film_transparent"]
        bpy.context.scene.display.shading.show_object_outline = style[
            "bpy.context.scene.display.shading.show_object_outline"
        ]
        bpy.context.scene.display.shading.show_cavity = style["bpy.context.scene.display.shading.show_cavity"]
        bpy.context.scene.display.shading.cavity_type = style["bpy.context.scene.display.shading.cavity_type"]
        bpy.context.scene.display.shading.curvature_ridge_factor = style[
            "bpy.context.scene.display.shading.curvature_ridge_factor"
        ]
        bpy.context.scene.display.shading.curvature_valley_factor = style[
            "bpy.context.scene.display.shading.curvature_valley_factor"
        ]
        bpy.context.scene.view_settings.view_transform = style["bpy.context.scene.view_settings.view_transform"]
        bpy.context.scene.display.shading.light = style["bpy.context.scene.display.shading.light"]
        bpy.context.scene.display.shading.color_type = style["bpy.context.scene.display.shading.color_type"]
        bpy.context.scene.display.shading.single_color = style["bpy.context.scene.display.shading.single_color"]
        bpy.context.scene.display.shading.show_shadows = style["bpy.context.scene.display.shading.show_shadows"]
        bpy.context.scene.display.shading.shadow_intensity = style["bpy.context.scene.display.shading.shadow_intensity"]
        bpy.context.scene.display.light_direction = style["bpy.context.scene.display.light_direction"]

        bpy.context.scene.view_settings.use_curve_mapping = style["bpy.context.scene.view_settings.use_curve_mapping"]
        space.overlay.show_wireframes = style["space.overlay.show_wireframes"]
        space.overlay.wireframe_threshold = style["space.overlay.wireframe_threshold"]
        space.overlay.show_floor = style["space.overlay.show_floor"]
        space.overlay.show_axis_x = style["space.overlay.show_axis_x"]
        space.overlay.show_axis_y = style["space.overlay.show_axis_y"]
        space.overlay.show_axis_z = style["space.overlay.show_axis_z"]
        space.overlay.show_object_origins = style["space.overlay.show_object_origins"]
        space.overlay.show_relationship_lines = style["space.overlay.show_relationship_lines"]

    def set_query(self):
        self.selector = ifcopenshell.util.selector.Selector()
        self.include_global_ids = []
        self.exclude_global_ids = []
        for ifc_file in bpy.context.scene.DocProperties.ifc_files:
            try:
                ifc = ifcopenshell.open(ifc_file.name)
            except:
                continue
            if self.drawing_style.include_query:
                results = self.selector.parse(ifc, self.drawing_style.include_query)
                self.include_global_ids.extend([e.GlobalId for e in results])
            if self.drawing_style.exclude_query:
                results = self.selector.parse(ifc, self.drawing_style.exclude_query)
                self.exclude_global_ids.extend([e.GlobalId for e in results])
        if self.drawing_style.include_query:
            self.parse_filter_query("INCLUDE")
        if self.drawing_style.exclude_query:
            self.parse_filter_query("EXCLUDE")

    def parse_filter_query(self, mode):
        if mode == "INCLUDE":
            objects = bpy.context.scene.objects
        elif mode == "EXCLUDE":
            objects = bpy.context.visible_objects
        for obj in objects:
            if mode == "INCLUDE":
                obj.hide_viewport = False  # Note: this breaks alt-H
            global_id = obj.BIMObjectProperties.attributes.get("GlobalId")
            if not global_id:
                continue
            global_id = global_id.string_value
            if mode == "INCLUDE":
                if global_id not in self.include_global_ids:
                    obj.hide_viewport = True  # Note: this breaks alt-H
            elif mode == "EXCLUDE":
                if global_id in self.exclude_global_ids:
                    obj.hide_viewport = True  # Note: this breaks alt-H

    def get_view_3d(self):
        for area in bpy.context.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type != "VIEW_3D":
                    continue
                return space


class AddDrawing(bpy.types.Operator):
    bl_idname = "bim.add_drawing"
    bl_label = "Add Drawing"

    def execute(self, context):
        new = bpy.context.scene.DocProperties.drawings.add()
        new.name = "DRAWING {}".format(len(bpy.context.scene.DocProperties.drawings))
        if not bpy.data.collections.get("Views"):
            bpy.context.scene.collection.children.link(bpy.data.collections.new("Views"))
        views_collection = bpy.data.collections.get("Views")
        view_collection = bpy.data.collections.new("IfcGroup/" + new.name)
        views_collection.children.link(view_collection)
        camera = bpy.data.objects.new("IfcGroup/" + new.name, bpy.data.cameras.new("IfcGroup/" + new.name))
        camera.location = (0, 0, 1.7)  # The view shall be 1.7m above the origin
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 50  # The default of 6m is too small
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            camera.data.BIMCameraProperties.diagram_scale = '1/8"=1\'-0"|1/96'
        else:
            camera.data.BIMCameraProperties.diagram_scale = "1:100|1/100"
        bpy.context.scene.camera = camera
        view_collection.objects.link(camera)
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].region_3d.view_perspective = "CAMERA"
        new.camera = camera
        bpy.ops.bim.activate_drawing_style()
        return {"FINISHED"}


class RemoveDrawing(bpy.types.Operator):
    bl_idname = "bim.remove_drawing"
    bl_label = "Remove Drawing"
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        camera = props.drawings[self.index].camera
        collection = camera.users_collection[0]
        for obj in collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(collection, do_unlink=True)
        props.drawings.remove(self.index)
        return {"FINISHED"}


class EditVectorStyle(bpy.types.Operator):
    bl_idname = "bim.edit_vector_style"
    bl_label = "Edit Vector Style"

    def execute(self, context):
        camera = context.scene.camera
        vector_style = context.scene.DocProperties.drawing_styles[
            camera.data.BIMCameraProperties.active_drawing_style_index
        ].vector_style
        bpy.data.texts.load(os.path.join(context.scene.BIMProperties.data_dir, "styles", vector_style + ".css"))
        return {"FINISHED"}


class RemoveSheet(bpy.types.Operator):
    bl_idname = "bim.remove_sheet"
    bl_label = "Remove Sheet"
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        props.sheets.remove(self.index)
        return {"FINISHED"}


class AddSchedule(bpy.types.Operator):
    bl_idname = "bim.add_schedule"
    bl_label = "Add Schedule"

    def execute(self, context):
        new = bpy.context.scene.DocProperties.schedules.add()
        new.name = "SCHEDULE {}".format(len(bpy.context.scene.DocProperties.schedules))
        return {"FINISHED"}


class RemoveSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_schedule"
    bl_label = "Remove Schedule"
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        props.schedules.remove(self.index)
        return {"FINISHED"}


class AddMaterialLayer(bpy.types.Operator):
    bl_idname = "bim.add_material_layer"
    bl_label = "Add Material Layer"

    def execute(self, context):
        new = bpy.context.active_object.BIMObjectProperties.material_set.material_layers.add()
        new.material = bpy.data.materials[0]
        new.name = "Material Layer"
        return {"FINISHED"}


class RemoveMaterialLayer(bpy.types.Operator):
    bl_idname = "bim.remove_material_layer"
    bl_label = "Remove Material Layer"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.material_set.material_layers.remove(self.index)
        return {"FINISHED"}


class MoveMaterialLayer(bpy.types.Operator):
    bl_idname = "bim.move_material_layer"
    bl_label = "Move Material Layer"
    direction: bpy.props.StringProperty()

    def execute(self, context):
        props = bpy.context.active_object.BIMObjectProperties.material_set
        index = props.active_material_layer_index
        if self.direction == "UP" and index - 1 >= 0:
            props.material_layers.move(index, index - 1)
            props.active_material_layer_index = index - 1
        elif self.direction == "DOWN" and index + 1 < len(props.material_layers):
            props.material_layers.move(index, index + 1)
            props.active_material_layer_index = index + 1
        return {"FINISHED"}


class AddMaterialConstituent(bpy.types.Operator):
    bl_idname = "bim.add_material_constituent"
    bl_label = "Add Material Constituent"

    def execute(self, context):
        new = bpy.context.active_object.BIMObjectProperties.material_set.material_constituents.add()
        new.material = bpy.data.materials[0]
        new.name = "Material Constituent"
        return {"FINISHED"}


class RemoveMaterialConstituent(bpy.types.Operator):
    bl_idname = "bim.remove_material_constituent"
    bl_label = "Remove Material Constituent"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.material_set.material_constituents.remove(self.index)
        return {"FINISHED"}


class MoveMaterialConstituent(bpy.types.Operator):
    bl_idname = "bim.move_material_constituent"
    bl_label = "Move Material Constituent"
    direction: bpy.props.StringProperty()

    def execute(self, context):
        props = bpy.context.active_object.BIMObjectProperties.material_set
        index = props.active_material_constituent_index
        if self.direction == "UP" and index - 1 >= 0:
            props.material_constituents.move(index, index - 1)
            props.active_material_constituent_index = index - 1
        elif self.direction == "DOWN" and index + 1 < len(props.material_constituents):
            props.material_constituents.move(index, index + 1)
            props.active_material_constituent_index = index + 1
        return {"FINISHED"}


class AddMaterialProfile(bpy.types.Operator):
    bl_idname = "bim.add_material_profile"
    bl_label = "Add Material Profile"

    def execute(self, context):
        new = bpy.context.active_object.BIMObjectProperties.material_set.material_profiles.add()
        new.material = bpy.data.materials[0]
        new.name = "Material Profile"
        return {"FINISHED"}


class RemoveMaterialProfile(bpy.types.Operator):
    bl_idname = "bim.remove_material_profile"
    bl_label = "Remove Material Profile"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.material_set.material_profiles.remove(self.index)
        return {"FINISHED"}


class MoveMaterialProfile(bpy.types.Operator):
    bl_idname = "bim.move_material_profile"
    bl_label = "Move Material Profile"
    direction: bpy.props.StringProperty()

    def execute(self, context):
        props = bpy.context.active_object.BIMObjectProperties.material_set
        index = props.active_material_profile_index
        if self.direction == "UP" and index - 1 >= 0:
            props.material_profiles.move(index, index - 1)
            props.active_material_profile_index = index - 1
        elif self.direction == "DOWN" and index + 1 < len(props.material_profiles):
            props.material_profiles.move(index, index + 1)
            props.active_material_profile_index = index + 1
        return {"FINISHED"}


class SelectScheduleFile(bpy.types.Operator):
    bl_idname = "bim.select_schedule_file"
    bl_label = "Select Documentation IFC File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ods", options={"HIDDEN"})
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        props.schedules[props.active_schedule_index].file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class BuildSchedule(bpy.types.Operator):
    bl_idname = "bim.build_schedule"
    bl_label = "Build Schedule"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        schedule = props.schedules[props.active_schedule_index]
        schedule_creator = scheduler.Scheduler()
        outfile = os.path.join(bpy.context.scene.BIMProperties.data_dir, "schedules", schedule.name + ".svg")
        schedule_creator.schedule(schedule.file, outfile)
        open_with_user_command(bpy.context.preferences.addons["blenderbim"].preferences.svg_command, outfile)
        return {"FINISHED"}


class AddScheduleToSheet(bpy.types.Operator):
    bl_idname = "bim.add_schedule_to_sheet"
    bl_label = "Add Schedule To Sheet"

    def execute(self, context):
        props = bpy.context.scene.DocProperties
        sheet_builder = sheeter.SheetBuilder()
        sheet_builder.data_dir = bpy.context.scene.BIMProperties.data_dir
        sheet_builder.add_schedule(
            props.schedules[props.active_schedule_index].name, props.sheets[props.active_sheet_index].name
        )
        return {"FINISHED"}


class SetViewportShadowFromSun(bpy.types.Operator):
    bl_idname = "bim.set_viewport_shadow_from_sun"
    bl_label = "Set Viewport Shadow from Sun"

    def execute(self, context):
        # The vector used for the light direction is a bit funny
        mat = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, 0, 1.0, 0.0), (-0.0, -1.0, 0, 0.0), (0.0, 0.0, 0.0, 1.0)))
        context.scene.display.light_direction = mat.inverted() @ (
            context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        )
        return {"FINISHED"}


class SetNorthOffset(bpy.types.Operator):
    bl_idname = "bim.set_north_offset"
    bl_label = "Set North Offset"

    def execute(self, context):
        context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.xy2angle(
                float(bpy.context.scene.MapConversion.x_axis_abscissa),
                float(bpy.context.scene.MapConversion.x_axis_ordinate),
            )
        )
        return {"FINISHED"}


class GetNorthOffset(bpy.types.Operator):
    bl_idname = "bim.get_north_offset"
    bl_label = "Get North Offset"

    def execute(self, context):
        x_angle = -context.scene.sun_pos_properties.north_offset
        bpy.context.scene.MapConversion.x_axis_abscissa = str(cos(x_angle))
        bpy.context.scene.MapConversion.x_axis_ordinate = str(sin(x_angle))
        return {"FINISHED"}


class AssignPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.assign_presentation_layer"
    bl_label = "Assign Presentation Layer"
    index: bpy.props.IntProperty()

    def execute(self, context):
        layer = bpy.context.scene.BIMProperties.presentation_layers[self.index]
        for obj in bpy.context.selected_objects:
            if not obj.data or not hasattr(obj.data, "BIMMeshProperties"):
                continue
            obj.data.BIMMeshProperties.presentation_layer_index = self.index
            obj.hide_set(not layer.layer_on)
        return {"FINISHED"}


class UnassignPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.unassign_presentation_layer"
    bl_label = "Unassign Presentation Layer"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if not obj.data or not hasattr(obj.data, "BIMMeshProperties"):
                continue
            obj.data.BIMMeshProperties.presentation_layer_index = -1
        return {"FINISHED"}


class AddPresentationLayer(bpy.types.Operator):
    bl_idname = "bim.add_presentation_layer"
    bl_label = "Add Presentation Layer"

    def execute(self, context):
        new = bpy.context.scene.BIMProperties.presentation_layers.add()
        new.name = "New Presentation Layer"
        new.layer_on = True
        new.layer_frozen = False
        new.layer_blocked = False
        return {"FINISHED"}


class RemovePresentationLayer(bpy.types.Operator):
    bl_idname = "bim.remove_presentation_layer"
    bl_label = "Remove Presentation Layer"
    index: bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.scene.BIMProperties.presentation_layers.remove(self.index)
        return {"FINISHED"}


class UpdatePresentationLayer(bpy.types.Operator):
    bl_idname = "bim.update_presentation_layer"
    bl_label = "Hide/Show selected Presentation Layer"
    index: bpy.props.IntProperty()

    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if not obj.data or not hasattr(obj.data, "BIMMeshProperties"):
                continue
            if obj.data.BIMMeshProperties.presentation_layer_index == self.index:
                set_status = obj.hide_get()
                obj.hide_set(not obj.hide_get())
        return {"FINISHED"}


class AddDrawingStyleAttribute(bpy.types.Operator):
    bl_idname = "bim.add_drawing_style_attribute"
    bl_label = "Add Drawing Style Attribute"

    def execute(self, context):
        props = bpy.context.scene.camera.data.BIMCameraProperties
        context.scene.DocProperties.drawing_styles[props.active_drawing_style_index].attributes.add()
        return {"FINISHED"}


class RemoveDrawingStyleAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_drawing_style_attribute"
    bl_label = "Remove Drawing Style Attribute"
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = bpy.context.scene.camera.data.BIMCameraProperties
        context.scene.DocProperties.drawing_styles[props.active_drawing_style_index].attributes.remove(self.index)
        return {"FINISHED"}


class RefreshDrawingList(bpy.types.Operator):
    bl_idname = "bim.refresh_drawing_list"
    bl_label = "Refresh Drawing List"

    def execute(self, context):
        while len(bpy.context.scene.DocProperties.drawings) > 0:
            bpy.context.scene.DocProperties.drawings.remove(0)
        for obj in bpy.context.scene.objects:
            if not isinstance(obj.data, bpy.types.Camera):
                continue
            if "IfcGroup/" in obj.name and obj.users_collection[0].name == obj.name:
                new = bpy.context.scene.DocProperties.drawings.add()
                new.name = obj.name.split("/")[1]
                new.camera = obj
        return {"FINISHED"}


class BlenderClasher:
    def process_clash_set(self):
        import collision

        a_cm = collision.CollisionManager()
        b_cm = collision.CollisionManager()
        self.add_to_cm(a_cm, bpy.context.scene.BIMProperties.blender_clash_set_a)
        self.add_to_cm(b_cm, bpy.context.scene.BIMProperties.blender_clash_set_b)
        results = a_cm.in_collision_other(b_cm, return_data=True)
        if not results[0]:
            print("No clashes")
            return
        for contact in results[1]:
            if contact.raw.penetration_depth < 0.01:
                continue
            print("-----")
            print(contact.names)
            print(contact.raw.normal)
            print(contact.raw.pos)

    def add_to_cm(self, cm, object_names):
        import numpy as np
        import ifcclash

        for object_name in object_names:
            name = object_name.name
            obj = bpy.data.objects[name]
            triangulated_mesh = self.triangulate_mesh(obj)
            mesh = ifcclash.Mesh()
            mesh.vertices = np.array([tuple(obj.matrix_world @ v.co) for v in triangulated_mesh.vertices])
            mesh.faces = np.array([tuple(p.vertices) for p in triangulated_mesh.polygons])
            cm.add_object(name, mesh)

    def triangulate_mesh(self, obj):
        import bmesh

        mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
        del bm
        return mesh


class SetBlenderClashSetA(bpy.types.Operator):
    bl_idname = "bim.set_blender_clash_set_a"
    bl_label = "Set Blender Clash Set A"

    def execute(self, context):
        while len(bpy.context.scene.BIMProperties.blender_clash_set_a) > 0:
            bpy.context.scene.BIMProperties.blender_clash_set_a.remove(0)
        for obj in bpy.context.selected_objects:
            new = bpy.context.scene.BIMProperties.blender_clash_set_a.add()
            new.name = obj.name
        return {"FINISHED"}


class SetBlenderClashSetB(bpy.types.Operator):
    bl_idname = "bim.set_blender_clash_set_b"
    bl_label = "Set Blender Clash Set B"

    def execute(self, context):
        while len(bpy.context.scene.BIMProperties.blender_clash_set_b) > 0:
            bpy.context.scene.BIMProperties.blender_clash_set_b.remove(0)
        for obj in bpy.context.selected_objects:
            new = bpy.context.scene.BIMProperties.blender_clash_set_b.add()
            new.name = obj.name
        return {"FINISHED"}


class ExecuteBlenderClash(bpy.types.Operator):
    bl_idname = "bim.execute_blender_clash"
    bl_label = "Execute Blender Clash"

    def execute(self, context):
        blender_clasher = BlenderClasher()
        blender_clasher.process_clash_set()
        return {"FINISHED"}


class CleanWireframes(bpy.types.Operator):
    bl_idname = "bim.clean_wireframes"
    bl_label = "Clean Wireframes"

    def execute(self, context):
        objects = bpy.data.objects
        if bpy.context.selected_objects:
            objects = bpy.context.selected_objects
        for obj in objects:
            if not isinstance(obj.data, bpy.types.Mesh):
                continue
            # TODO: probably breaks i18n
            if not obj.modifiers.get("EdgeSplit"):
                obj.modifiers.new("EdgeSplit", "EDGE_SPLIT")
        return {"FINISHED"}


class LinkIfc(bpy.types.Operator):
    bl_idname = "bim.link_ifc"
    bl_label = "Link IFC"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # bpy.context.active_object.active_material.BIMMaterialProperties.location = self.filepath
        # coll_name = "MyCollection"

        with bpy.data.libraries.load(self.filepath, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes

        for scene in bpy.data.scenes:
            if not scene.library or scene.library.filepath != self.filepath:
                continue
            for child in scene.collection.children:
                if "IfcProject" not in child.name:
                    continue
                bpy.data.scenes[0].collection.children.link(child)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SnapSpacesTogether(bpy.types.Operator):
    bl_idname = "bim.snap_spaces_together"
    bl_label = "Snap Spaces Together"

    def execute(self, context):
        threshold = 0.5
        processed_polygons = set()
        for obj in bpy.context.selected_objects:
            if obj.type != "MESH":
                continue
            for polygon in obj.data.polygons:
                center = obj.matrix_world @ polygon.center
                distance = None
                for obj2 in bpy.context.selected_objects:
                    if obj2 == obj or obj.type != "MESH":
                        continue
                    result = obj2.ray_cast(obj2.matrix_world.inverted() @ center, polygon.normal, distance=threshold)
                    if not result[0]:
                        continue
                    hit = obj2.matrix_world @ result[1]
                    distance = (hit - center).length / 2
                    if distance < 0.01:
                        distance = None
                        break

                    if (obj2.name, result[3]) in processed_polygons:
                        distance *= 2
                        continue

                    offset = polygon.normal * distance * -1
                    processed_polygons.add((obj2.name, result[3]))
                    for v in obj2.data.polygons[result[3]].vertices:
                        obj2.data.vertices[v].co += offset
                    break
                if distance:
                    offset = polygon.normal * distance
                    processed_polygons.add((obj.name, polygon.index))
                    for v in polygon.vertices:
                        obj.data.vertices[v].co += offset
        return {"FINISHED"}


class CopyGrid(bpy.types.Operator):
    bl_idname = "bim.add_grid"
    bl_label = "Add Grid"
    bl_options = {"UNDO"}

    def execute(self, context):
        proj_coll = helper.get_project_collection(context.scene)
        view_coll, camera = helper.get_active_drawing(context.scene)
        if view_coll is None:
            return {'CANCELLED'}
        is_ortho = camera.data.type == "ORTHO"
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None
        clipping = is_ortho and camera.data.BIMCameraProperties.target_view in ('PLAN_VIEW', 'REFLECTED_PLAN_VIEW')
        elevating = is_ortho and camera.data.BIMCameraProperties.target_view in ('ELEVATION_VIEW', 'SECTION_VIEW')

        def grep(coll):
            return [obj for obj in coll.all_objects if obj.name.startswith("IfcGridAxis")]

        def clone(src):
            dst = src.copy()
            dst.data = dst.data.copy()
            return dst

        def disassemble(obj):
            mesh = bmesh.new()
            mesh.verts.ensure_lookup_table()
            mesh.from_mesh(obj.data)
            return obj, mesh

        def assemble(obj, mesh):
            mesh.to_mesh(obj.data)
            return obj

        def localize(obj, mesh):
            # convert to camera coords
            mesh.transform(camera.matrix_world.inverted() @ obj.matrix_world)
            obj.matrix_world = camera.matrix_world
            return obj, mesh

        def clip(mesh):
            # clip segment against camera view bounds
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        def elev(mesh):
            # put camera-perpendicular segments vertically
            mesh.verts.ensure_lookup_table()
            points = [v.co for v in mesh.verts[0:2]]
            points = helper.elevate_segment(bounds, points)
            if points is None:
                return None
            points = helper.clip_segment(bounds, points)
            if points is None:
                return None
            mesh.verts[0].co = points[0]
            mesh.verts[1].co = points[1]
            return mesh

        for obj in grep(view_coll):
            view_coll.objects.unlink(obj)

        grid = [localize(*disassemble(clone(obj))) for obj in grep(proj_coll)]

        if clipping:
            grid = [(obj, clip(mesh)) for obj, mesh in grid]
        elif elevating:
            grid = [(obj, elev(mesh)) for obj, mesh in grid]

        for obj, mesh in grid:
            if mesh is not None:
                view_coll.objects.link(assemble(obj, mesh))

        return {"FINISHED"}


class AddSectionsAnnotations(bpy.types.Operator):
    bl_idname = "bim.add_sections_annotations"
    bl_label = "Add Sections"
    bl_options = {"UNDO"}

    def execute(self, context):
        scene = context.scene
        view_coll, camera = helper.get_active_drawing(scene)
        is_ortho = camera.data.type == "ORTHO"
        if not is_ortho:
            return {'CANCELLED'}
        bounds = helper.ortho_view_frame(camera.data) if is_ortho else None

        drawings = [d
                    for d in scene.DocProperties.drawings
                    if (d.camera is not camera and
                        d.camera.data.type == "ORTHO" and
                        d.camera.data.BIMCameraProperties.target_view == 'SECTION_VIEW')]

        def sideview(cam):
            # leftmost and righmost points of camera view area, local coords
            xmin, xmax, _, _, _, _ = helper.ortho_view_frame(cam.data, margin=0)
            proj = camera.matrix_world.inverted() @ cam.matrix_world
            p_l = proj @ Vector((xmin, 0, 0))
            p_r = proj @ Vector((xmax, 0, 0))
            return helper.clip_segment(bounds, (p_l, p_r))

        def annotation(drawing, points):
            # object with path geometry
            name = drawing.name
            curve = bpy.data.curves.new(f"Section/{name}", 'CURVE')
            spline = curve.splines.new('POLY')  # has 1 initial point
            spline.points.add(1)
            p1, p2 = points
            z = bounds[4] - 1e-5  # zmin
            spline.points[0].co = (p1.x, p1.y, z, 1)
            spline.points[1].co = (p2.x, p2.y, z, 1)
            obj = bpy.data.objects.new(f"IfcAnnotation/Section/{name}", curve)
            obj.matrix_world = camera.matrix_world
            return obj

        for d in drawings:
            points = sideview(d.camera)
            if points is None:
                continue
            obj = annotation(d, points)
            view_coll.objects.link(obj)

        return {'FINISHED'}
