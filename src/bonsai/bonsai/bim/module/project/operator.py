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

import os
import bpy
import time
import json
import logging
import tempfile
import traceback
import subprocess
import datetime
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.project
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.file
import ifcopenshell.util.selector
import ifcopenshell.util.geolocation
import ifcopenshell.util.representation
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import bonsai.bim.handler
import bonsai.bim.schema
import bonsai.tool as tool
import bonsai.core.project as core
from bonsai.bim.ifc import IfcStore
from bonsai.bim.ui import IFCFileSelector
from bonsai.bim import import_ifc
from bonsai.bim import export_ifc
from collections import defaultdict
from math import radians
from pathlib import Path
from mathutils import Vector, Matrix
from bpy.app.handlers import persistent
from ifcopenshell.geom import ShapeElementType
from bonsai.bim.module.project.data import LinksData
from bonsai.bim.module.project.decorator import ProjectDecorator, ClippingPlaneDecorator, MeasureDecorator
from bonsai.bim.module.model.decorator import PolylineDecorator
from bonsai.bim.module.model.polyline import PolylineOperator
from typing import Union, TYPE_CHECKING


class NewProject(bpy.types.Operator):
    bl_idname = "bim.new_project"
    bl_label = "New Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Start a new IFC project in a fresh session"
    preset: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.wm.read_homefile()

        if self.preset == "metric_m":
            bpy.context.scene.BIMProjectProperties.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "METRIC"
            bpy.context.scene.unit_settings.length_unit = "METERS"
            bpy.context.scene.BIMProperties.area_unit = "SQUARE_METRE"
            bpy.context.scene.BIMProperties.volume_unit = "CUBIC_METRE"
            bpy.context.scene.BIMProjectProperties.template_file = "0"
        elif self.preset == "metric_mm":
            bpy.context.scene.BIMProjectProperties.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "METRIC"
            bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
            bpy.context.scene.BIMProperties.area_unit = "SQUARE_METRE"
            bpy.context.scene.BIMProperties.volume_unit = "CUBIC_METRE"
            bpy.context.scene.BIMProjectProperties.template_file = "0"
        elif self.preset == "imperial_ft":
            bpy.context.scene.BIMProjectProperties.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "IMPERIAL"
            bpy.context.scene.unit_settings.length_unit = "FEET"
            bpy.context.scene.BIMProperties.area_unit = "square foot"
            bpy.context.scene.BIMProperties.volume_unit = "cubic foot"
            bpy.context.scene.BIMProjectProperties.template_file = "0"
        elif self.preset == "demo":
            bpy.context.scene.BIMProjectProperties.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "METRIC"
            bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
            bpy.context.scene.BIMProperties.area_unit = "SQUARE_METRE"
            bpy.context.scene.BIMProperties.volume_unit = "CUBIC_METRE"
            bpy.context.scene.BIMProjectProperties.template_file = "IFC4 Demo Template.ifc"

        if self.preset != "wizard":
            bpy.ops.bim.create_project()
        return {"FINISHED"}


class CreateProject(bpy.types.Operator):
    bl_idname = "bim.create_project"
    bl_label = "Create Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create a new IFC project"

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.add_transaction_operation(self, rollback=self.rollback, commit=lambda data: True)
        self._execute(context)
        self.transaction_data = {"file": tool.Ifc.get()}
        IfcStore.add_transaction_operation(self, rollback=lambda data: True, commit=self.commit)
        IfcStore.end_transaction(self)
        return {"FINISHED"}

    def _execute(self, context):
        props = context.scene.BIMProjectProperties
        template = None if props.template_file == "0" else props.template_file
        if tool.Blender.is_default_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)
            for mesh in bpy.data.meshes:
                bpy.data.meshes.remove(mesh)
            for mat in bpy.data.materials:
                bpy.data.materials.remove(mat)
        core.create_project(
            tool.Ifc, tool.Georeference, tool.Project, tool.Spatial, schema=props.export_schema, template=template
        )
        bonsai.bim.schema.reload(tool.Ifc.get().schema_identifier)
        tool.Blender.register_toolbar()

    def rollback(self, data):
        IfcStore.file = None

    def commit(self, data):
        IfcStore.file = data["file"]


class SelectLibraryFile(bpy.types.Operator, IFCFileSelector):
    bl_idname = "bim.select_library_file"
    bl_label = "Select Library File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select an IFC file that can be used as a library"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    append_all: bpy.props.BoolProperty(default=False)
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    def execute(self, context):
        IfcStore.begin_transaction(self)
        old_filepath = IfcStore.library_path
        result = self._execute(context)
        self.transaction_data = {"old_filepath": old_filepath, "filepath": self.get_filepath()}
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        filepath = self.get_filepath()
        ifc_file = tool.Ifc.get()
        library_file = ifcopenshell.open(filepath)
        if library_file.schema_identifier != ifc_file.schema_identifier:
            self.report(
                {"ERROR"},
                f"Schema of library file ({library_file.schema_identifier}) is not compatible with the current IFC file ({ifc_file.schema_identifier}).",
            )
            return {"CANCELLED"}

        IfcStore.library_path = filepath
        IfcStore.library_file = library_file
        bpy.ops.bim.refresh_library()
        if context.area:
            context.area.tag_redraw()
        if self.append_all:
            bpy.ops.bim.append_entire_library()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def rollback(self, data):
        if data["old_filepath"]:
            IfcStore.library_path = data["old_filepath"]
            IfcStore.library_file = ifcopenshell.open(data["old_filepath"])
        else:
            IfcStore.library_path = ""
            IfcStore.library_file = None

    def commit(self, data):
        IfcStore.library_path = data["filepath"]
        IfcStore.library_file = ifcopenshell.open(data["filepath"])

    def draw(self, context):
        self.layout.prop(self, "append_all", text="Append Entire Library")
        IFCFileSelector.draw(self, context)


class RefreshLibrary(bpy.types.Operator):
    bl_idname = "bim.refresh_library"
    bl_label = "Refresh Library"

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties

        self.props.library_elements.clear()
        self.props.library_breadcrumb.clear()

        self.props.active_library_element = ""

        for importable_type in sorted(tool.Project.get_appendable_asset_types()):
            if IfcStore.library_file.by_type(importable_type):
                new = self.props.library_elements.add()
                new.name = importable_type
        return {"FINISHED"}


class ChangeLibraryElement(bpy.types.Operator):
    bl_idname = "bim.change_library_element"
    bl_label = "Change Library Element"
    bl_options = {"REGISTER", "UNDO"}
    element_name: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties
        self.file = IfcStore.get_file()
        self.library_file = IfcStore.library_file
        ifc_classes = set()
        self.props.active_library_element = self.element_name

        crumb = self.props.library_breadcrumb.add()
        crumb.name = self.element_name

        elements = self.library_file.by_type(self.element_name)
        [ifc_classes.add(e.is_a()) for e in elements]

        self.props.library_elements.clear()

        if len(ifc_classes) == 1 and list(ifc_classes)[0] == self.element_name:
            for name, ifc_definition_id in sorted([(self.get_name(e), e.id()) for e in elements]):
                self.add_library_asset(name, ifc_definition_id)
        else:
            for ifc_class in sorted(ifc_classes):
                if ifc_class == self.element_name:
                    continue
                new = self.props.library_elements.add()
                new.name = ifc_class
            for name, ifc_definition_id, ifc_class in sorted([(self.get_name(e), e.id(), e.is_a()) for e in elements]):
                if ifc_class == self.element_name:
                    self.add_library_asset(name, ifc_definition_id)
        return {"FINISHED"}

    def get_name(self, element: ifcopenshell.entity_instance) -> str:
        if element.is_a("IfcProfileDef"):
            return element.ProfileName or "Unnamed"
        return element.Name or "Unnamed"

    def add_library_asset(self, name: str, ifc_definition_id: int) -> None:
        new = self.props.library_elements.add()
        new.name = name
        new.ifc_definition_id = ifc_definition_id
        element = self.library_file.by_id(ifc_definition_id)
        if self.library_file.schema == "IFC2X3" or not self.library_file.by_type("IfcProjectLibrary"):
            new.is_declared = False
        elif getattr(element, "HasContext", None) and element.HasContext[0].RelatingContext.is_a("IfcProjectLibrary"):
            new.is_declared = True
        try:
            if element.is_a("IfcMaterial"):
                next(e for e in self.file.by_type("IfcMaterial") if e.Name == name)
            elif element.is_a("IfcProfileDef"):
                next(e for e in self.file.by_type("IfcProfileDef") if e.ProfileName == name)
            else:
                self.file.by_guid(element.GlobalId)
            new.is_appended = True
        except (AttributeError, RuntimeError, StopIteration):
            new.is_appended = False


class RewindLibrary(bpy.types.Operator):
    bl_idname = "bim.rewind_library"
    bl_label = "Rewind Library"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties
        total_breadcrumbs = len(self.props.library_breadcrumb)
        if total_breadcrumbs < 2:
            bpy.ops.bim.refresh_library()
            return {"FINISHED"}
        element_name = self.props.library_breadcrumb[total_breadcrumbs - 2].name
        self.props.library_breadcrumb.remove(total_breadcrumbs - 1)
        self.props.library_breadcrumb.remove(total_breadcrumbs - 2)
        bpy.ops.bim.change_library_element(element_name=element_name)
        return {"FINISHED"}


class AssignLibraryDeclaration(bpy.types.Operator):
    bl_idname = "bim.assign_library_declaration"
    bl_label = "Assign Library Declaration"
    bl_options = {"REGISTER", "UNDO"}
    definition: bpy.props.IntProperty()

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.library_file.begin_transaction()
        result = self._execute(context)
        IfcStore.library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.props = context.scene.BIMProjectProperties
        self.file = IfcStore.library_file
        ifcopenshell.api.run(
            "project.assign_declaration",
            self.file,
            definitions=[self.file.by_id(self.definition)],
            relating_context=self.file.by_type("IfcProjectLibrary")[0],
        )
        element_name = self.props.active_library_element
        bpy.ops.bim.rewind_library()
        bpy.ops.bim.change_library_element(element_name=element_name)
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.library_file.undo()

    def commit(self, data):
        IfcStore.library_file.redo()


class UnassignLibraryDeclaration(bpy.types.Operator):
    bl_idname = "bim.unassign_library_declaration"
    bl_label = "Unassign Library Declaration"
    bl_options = {"REGISTER", "UNDO"}
    definition: bpy.props.IntProperty()

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.library_file.begin_transaction()
        result = self._execute(context)
        IfcStore.library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.props = context.scene.BIMProjectProperties
        self.file = IfcStore.library_file
        ifcopenshell.api.run(
            "project.unassign_declaration",
            self.file,
            definitions=[self.file.by_id(self.definition)],
            relating_context=self.file.by_type("IfcProjectLibrary")[0],
        )
        element_name = self.props.active_library_element
        bpy.ops.bim.rewind_library()
        bpy.ops.bim.change_library_element(element_name=element_name)
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.library_file.undo()

    def commit(self, data):
        IfcStore.library_file.redo()


class SaveLibraryFile(bpy.types.Operator):
    bl_idname = "bim.save_library_file"
    bl_label = "Save Library File"

    def execute(self, context):
        IfcStore.library_file.write(IfcStore.library_path)
        return {"FINISHED"}


class AppendEntireLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.append_entire_library"
    bl_label = "Append Entire Library"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        self.library = IfcStore.library_file

        query = ", ".join(tool.Project.get_appendable_asset_types())
        lib_elements = ifcopenshell.util.selector.filter_elements(self.library, query)
        for element in lib_elements:
            bpy.ops.bim.append_library_element(definition=element.id())
        return {"FINISHED"}


class AppendLibraryElementByQuery(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.append_library_element_by_query"
    bl_label = "Append Library Element By Query"
    query: bpy.props.StringProperty(name="Query")

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        self.library = IfcStore.library_file

        for element in ifcopenshell.util.selector.filter_elements(self.library, self.query):
            bpy.ops.bim.append_library_element(definition=element.id())
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "query")


class AppendLibraryElement(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.append_library_element"
    bl_label = "Append Library Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Append element to the current project.\n\n"
        "ALT+CLICK to skip reusing materials, profiles, styles based on their name (may result in duplicates)"
    )
    definition: bpy.props.IntProperty()
    prop_index: bpy.props.IntProperty()
    assume_unique_by_name: bpy.props.BoolProperty(name="Assume Unique By Name", default=True, options={"SKIP_SAVE"})

    file: ifcopenshell.file

    @classmethod
    def poll(cls, context):
        poll = bool(IfcStore.get_file())
        if bpy.app.version > (3, 0, 0) and not poll:
            cls.poll_message_set("Please create or load a project first.")
        return poll

    def invoke(self, context, event):
        if event.type == "LEFTMOUSE" and event.alt:
            self.assume_unique_by_name = False
        return self.execute(context)

    def _execute(self, context):
        self.file = tool.Ifc.get()
        library_file = IfcStore.library_file
        assert library_file
        element = ifcopenshell.api.project.append_asset(
            self.file,
            library=library_file,
            element=library_file.by_id(self.definition),
            assume_asset_uniqueness_by_name=self.assume_unique_by_name,
        )
        if not element:
            return {"FINISHED"}
        if element.is_a("IfcTypeProduct"):
            self.import_type_from_ifc(element, context)
        elif element.is_a("IfcProduct"):
            # NOTE: not used as UI doesn't allow appending non-types
            self.import_product_from_ifc(element, context)
            element_type = ifcopenshell.util.element.get_type(element)
            obj = tool.Ifc.get_object(element_type)
            if obj is None:
                self.import_type_from_ifc(element_type, context)
        elif element.is_a("IfcMaterial"):
            self.import_material_from_ifc(element, context)
        elif element.is_a("IfcPresentationStyle"):
            self.import_presentation_style_from_ifc(element, context)

        try:
            context.scene.BIMProjectProperties.library_elements[self.prop_index].is_appended = True
        except:
            # TODO Remove this terrible code when I refactor this into the core
            pass
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def import_material_from_ifc(self, element: ifcopenshell.entity_instance, context: bpy.types.Context) -> None:
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        self.import_material_styles(element, ifc_importer)

    def import_presentation_style_from_ifc(
        self, style: ifcopenshell.entity_instance, context: bpy.types.Context
    ) -> None:
        self.file = tool.Ifc.get()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, tool.Ifc.get_path(), logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.create_style(style)

    def import_product_from_ifc(self, element: ifcopenshell.entity_instance, context: bpy.types.Context) -> None:
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        self.import_materials(element, ifc_importer)
        self.import_styles(element, ifc_importer)
        ifc_importer.create_generic_elements({element})
        ifc_importer.place_objects_in_collections()

    def import_type_from_ifc(self, element: ifcopenshell.entity_instance, context: bpy.types.Context) -> None:
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)

        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        self.import_materials(element, ifc_importer)
        self.import_styles(element, ifc_importer)
        ifc_importer.create_element_type(element)
        ifc_importer.place_objects_in_collections()

    def import_materials(self, element: ifcopenshell.entity_instance, ifc_importer: import_ifc.IfcImporter) -> None:
        for material in ifcopenshell.util.element.get_materials(element):
            if IfcStore.get_element(material.id()):
                continue
            self.import_material_styles(material, ifc_importer)

    def import_styles(self, element: ifcopenshell.entity_instance, ifc_importer: import_ifc.IfcImporter) -> None:
        if element.is_a("IfcTypeProduct"):
            representations = element.RepresentationMaps or []
        elif element.is_a("IfcProduct"):
            representations = [element.Representation] if element.Representation else []
        for representation in representations or []:
            for element in self.file.traverse(representation):
                if not element.is_a("IfcRepresentationItem") or not element.StyledByItem:
                    continue
                for element2 in self.file.traverse(element.StyledByItem[0]):
                    if element2.is_a("IfcSurfaceStyle") and not IfcStore.get_element(element2.id()):
                        ifc_importer.create_style(element2)

    def import_material_styles(
        self,
        material: ifcopenshell.entity_instance,
        ifc_importer: import_ifc.IfcImporter,
    ) -> None:
        if not material.HasRepresentation:
            return
        for element in self.file.traverse(material.HasRepresentation[0]):
            if element.is_a("IfcSurfaceStyle") and not IfcStore.get_element(element.id()):
                ifc_importer.create_style(element)


class EnableEditingHeader(bpy.types.Operator):
    bl_idname = "bim.enable_editing_header"
    bl_label = "Enable Editing Header"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Edit the IFC header file such as Author, Organization, ..."

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMProjectProperties
        props.is_editing = True

        mvd = "".join(IfcStore.get_file().wrapped_data.header.file_description.description)
        if "[" in mvd:
            props.mvd = mvd.split("[")[1][0:-1]
        else:
            props.mvd = ""

        author = self.file.wrapped_data.header.file_name.author
        if author:
            props.author_name = author[0]
            if len(author) > 1:
                props.author_email = author[1]

        organisation = self.file.wrapped_data.header.file_name.organization
        if organisation:
            props.organisation_name = organisation[0]
            if len(organisation) > 1:
                props.organisation_email = organisation[1]

        props.authorisation = self.file.wrapped_data.header.file_name.authorization
        return {"FINISHED"}


class EditHeader(bpy.types.Operator):
    bl_idname = "bim.edit_header"
    bl_label = "Edit Header"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Save header information"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        IfcStore.begin_transaction(self)
        self.transaction_data = {}
        self.transaction_data["old"] = self.record_state()
        result = self._execute(context)
        self.transaction_data["new"] = self.record_state()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMProjectProperties
        props.is_editing = True

        self.file.wrapped_data.header.file_description.description = (f"ViewDefinition[{props.mvd}]",)
        self.file.wrapped_data.header.file_name.author = (props.author_name, props.author_email)
        self.file.wrapped_data.header.file_name.organization = (props.organisation_name, props.organisation_email)
        self.file.wrapped_data.header.file_name.authorization = props.authorisation
        bpy.ops.bim.disable_editing_header()
        return {"FINISHED"}

    def record_state(self):
        self.file = IfcStore.get_file()
        return {
            "description": self.file.wrapped_data.header.file_description.description,
            "author": self.file.wrapped_data.header.file_name.author,
            "organisation": self.file.wrapped_data.header.file_name.organization,
            "authorisation": self.file.wrapped_data.header.file_name.authorization,
        }

    def rollback(self, data):
        file = IfcStore.get_file()
        file.wrapped_data.header.file_description.description = data["old"]["description"]
        file.wrapped_data.header.file_name.author = data["old"]["author"]
        file.wrapped_data.header.file_name.organization = data["old"]["organisation"]
        file.wrapped_data.header.file_name.authorization = data["old"]["authorisation"]

    def commit(self, data):
        file = IfcStore.get_file()
        file.wrapped_data.header.file_description.description = data["new"]["description"]
        file.wrapped_data.header.file_name.author = data["new"]["author"]
        file.wrapped_data.header.file_name.organization = data["new"]["organisation"]
        file.wrapped_data.header.file_name.authorization = data["new"]["authorisation"]


class DisableEditingHeader(bpy.types.Operator):
    bl_idname = "bim.disable_editing_header"
    bl_label = "Disable Editing Header"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Cancel unsaved header information"

    def execute(self, context):
        context.scene.BIMProjectProperties.is_editing = False
        return {"FINISHED"}


class LoadProject(bpy.types.Operator, IFCFileSelector):
    bl_idname = "bim.load_project"
    bl_label = "Load Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Load an existing IFC project"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE"})
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcsqlite", options={"HIDDEN"})
    is_advanced: bpy.props.BoolProperty(
        name="Enable Advanced Mode",
        description="Load IFC file with advanced settings. Checking this option will skip loading IFC file and will open advanced load settings",
        default=False,
    )
    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path",
        description="Store the IFC project path relative to the .blend file. Requires .blend file to be saved",
        default=False,
    )
    should_start_fresh_session: bpy.props.BoolProperty(
        name="Should Start Fresh Session",
        description="Clear current Blender session before loading IFC. Not supported with 'Use Relative Path' option",
        default=True,
    )
    import_without_ifc_data: bpy.props.BoolProperty(
        name="Import Without IFC Data",
        description=(
            "Import IFC objects as Blender objects without any IFC metadata and authoring capabilities."
            "Can be useful for work with purely IFC geometry"
        ),
        default=False,
    )
    use_detailed_tooltip: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        tooltip = cls.bl_description
        if not properties.use_detailed_tooltip:
            return tooltip

        filepath = properties.filepath
        if not filepath:
            return tooltip
        filepath = Path(filepath)
        tooltip += f".\n"
        if not filepath.exists():
            tooltip += "\nFile does not exist"
            return tooltip

        def get_modified_date(st_mtime: float) -> str:
            mod_time = datetime.datetime.fromtimestamp(st_mtime)

            today = datetime.date.today()
            if mod_time.date() == today:
                return f"Today {mod_time.strftime('%I:%M %p')}"
            elif mod_time.date() == today - datetime.timedelta(days=1):
                return f"Yesterday {mod_time.strftime('%I:%M %p')}"
            return mod_time.strftime("%d %b %Y")

        def get_file_size(size_bytes: float) -> str:
            if size_bytes < 1024 * 1024:  # Less than 1 MiB
                size = size_bytes / 1024
                return f"{size:.0f} KiB"
            else:
                size = size_bytes / (1024 * 1024)
                return f"{size:.1f} MiB"

        extractor = ifcopenshell.util.file.IfcHeaderExtractor(str(filepath))
        header_metadata = extractor.extract()
        if schema := header_metadata.get("schema_name"):
            tooltip += f"\nSchema: {schema}"

        file_stat = filepath.stat()
        tooltip += f"\nModified: {get_modified_date(file_stat.st_mtime)}"
        tooltip += f"\nSize: {get_file_size(file_stat.st_size)}"

        return tooltip

    def execute(self, context):
        @persistent
        def load_handler(*args):
            bpy.app.handlers.load_post.remove(load_handler)
            self.finish_loading_project(context)

        if self.use_relative_path:
            self.should_start_fresh_session = False

        if self.should_start_fresh_session:
            # WARNING: wm.read_homefile clears context which could lead to some
            # operators to fail:
            # https://blender.stackexchange.com/a/282558/135166
            # So we continue using the load_post handler thats triggered when
            # context is already restored
            bpy.app.handlers.load_post.append(load_handler)
            bpy.ops.wm.read_homefile()
            return {"FINISHED"}
        else:
            return self.finish_loading_project(context)

    def finish_loading_project(self, context):
        try:
            filepath = self.get_filepath()
            if not self.is_existing_ifc_file():
                self.report({"ERROR"}, f"Couldn't find IFC file: '{filepath}'.")
                return {"FINISHED"}

            if self.should_start_fresh_session and tool.Blender.is_default_scene():
                for obj in bpy.data.objects:
                    bpy.data.objects.remove(obj)

            # To be safe from any accidental IFC data in the previous session.
            if not self.is_advanced and not self.should_start_fresh_session:
                bpy.ops.bim.convert_to_blender()

            context.scene.BIMProperties.ifc_file = filepath
            if not (ifc_file := tool.Ifc.get()):
                self.report(
                    {"ERROR"},
                    f"Error loading IFC file from filepath '{filepath}'. See logs above in the system console for the details.",
                )
                return {"CANCELLED"}
            context.scene.BIMProjectProperties.is_loading = True
            context.scene.BIMProjectProperties.total_elements = len(tool.Ifc.get().by_type("IfcElement"))
            context.scene.BIMProjectProperties.use_relative_project_path = self.use_relative_path
            tool.Blender.register_toolbar()
            tool.Project.add_recent_ifc_project(self.get_filepath_abs())

            if self.is_advanced:
                pass
            elif len(tool.Ifc.get().by_type("IfcElement")) > 30000:
                self.report({"WARNING"}, "Warning: large model. Please review advanced settings to continue.")
            else:
                bpy.ops.bim.load_project_elements()
                if self.import_without_ifc_data:
                    bpy.ops.bim.convert_to_blender()
        except:
            bonsai.last_error = traceback.format_exc()
            raise
        return {"FINISHED"}

    def invoke(self, context, event):
        if self.filepath:
            return self.execute(context)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        if self.use_relative_path:
            self.should_start_fresh_session = False
        self.layout.prop(self, "is_advanced")
        self.layout.prop(self, "should_start_fresh_session")
        self.layout.prop(self, "import_without_ifc_data")
        IFCFileSelector.draw(self, context)


class ClearRecentIFCProjects(bpy.types.Operator):
    bl_idname = "bim.clear_recent_ifc_projects"
    bl_label = "Clear Recent IFC Projects List"
    bl_options = {"REGISTER"}

    def execute(self, context):
        tool.Project.clear_recent_ifc_projects()
        return {"FINISHED"}


class RevertProject(bpy.types.Operator, IFCFileSelector):
    bl_idname = "bim.revert_project"
    bl_label = "Revert IFC Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Revert to a fresh session discarding all unsaved changes"

    @classmethod
    def poll(cls, context):
        if not context.scene.BIMProperties.ifc_file:
            cls.poll_message_set("IFC project need to be loaded and saved on the disk.")
            return False
        return True

    def execute(self, context):
        bpy.ops.bim.load_project(should_start_fresh_session=True, filepath=context.scene.BIMProperties.ifc_file)
        return {"FINISHED"}


class LoadProjectElements(bpy.types.Operator):
    bl_idname = "bim.load_project_elements"
    bl_label = "Load Project Elements"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties
        self.file = IfcStore.get_file()
        bonsai.bim.schema.reload(self.file.schema_identifier)
        start = time.time()
        logger = logging.getLogger("ImportIFC")
        path_log = os.path.join(context.scene.BIMProperties.data_dir, "process.log")
        if not os.access(context.scene.BIMProperties.data_dir, os.W_OK):
            path_log = os.path.join(tempfile.mkdtemp(), "process.log")
        logging.basicConfig(
            filename=path_log,
            filemode="a",
            level=logging.DEBUG,
        )
        settings = import_ifc.IfcImportSettings.factory(context, context.scene.BIMProperties.ifc_file, logger)
        settings.has_filter = self.props.filter_mode != "NONE"
        settings.should_filter_spatial_elements = self.props.should_filter_spatial_elements
        if self.props.filter_mode == "DECOMPOSITION":
            settings.elements = self.get_decomposition_elements()
        elif self.props.filter_mode == "IFC_CLASS":
            settings.elements = self.get_ifc_class_elements()
        elif self.props.filter_mode == "IFC_TYPE":
            settings.elements = self.get_ifc_type_elements()
        elif self.props.filter_mode == "WHITELIST":
            settings.elements = self.get_whitelist_elements()
        elif self.props.filter_mode == "BLACKLIST":
            settings.elements = self.get_blacklist_elements()
        settings.logger.info("Starting import")
        ifc_importer = import_ifc.IfcImporter(settings)
        ifc_importer.execute()
        settings.logger.info("Import finished in {:.2f} seconds".format(time.time() - start))
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        context.scene.BIMProjectProperties.is_loading = False

        tool.Project.load_pset_templates()
        tool.Project.load_default_thumbnails()
        tool.Project.set_default_context()
        tool.Project.set_default_modeling_dimensions()
        tool.Root.reload_grid_decorator()
        return {"FINISHED"}

    def get_decomposition_elements(self):
        containers = set()
        for filter_category in self.props.filter_categories:
            if not filter_category.is_selected:
                continue
            container = self.file.by_id(filter_category.ifc_definition_id)
            while container:
                containers.add(container)
                container = ifcopenshell.util.element.get_aggregate(container)
                if self.file.schema == "IFC2X3" and container.is_a("IfcProject"):
                    container = None
                elif self.file.schema != "IFC2X3" and container.is_a("IfcContext"):
                    container = None
        elements = set()
        for container in containers:
            for rel in container.ContainsElements:
                elements.update(rel.RelatedElements)
        self.append_decomposed_elements(elements)
        return elements

    def append_decomposed_elements(self, elements):
        decomposed_elements = set()
        for element in elements:
            if element.IsDecomposedBy:
                for subelement in element.IsDecomposedBy[0].RelatedObjects:
                    decomposed_elements.add(subelement)
        if decomposed_elements:
            self.append_decomposed_elements(decomposed_elements)
        elements.update(decomposed_elements)

    def get_ifc_class_elements(self):
        elements = set()
        for filter_category in self.props.filter_categories:
            if not filter_category.is_selected:
                continue
            elements.update(self.file.by_type(filter_category.name, include_subtypes=False))
        return elements

    def get_ifc_type_elements(self):
        elements = set()
        for filter_category in self.props.filter_categories:
            if not filter_category.is_selected:
                continue
            elements.update(ifcopenshell.util.element.get_types(self.file.by_id(filter_category.ifc_definition_id)))
        return elements

    def get_whitelist_elements(self):
        return set(ifcopenshell.util.selector.filter_elements(self.file, self.props.filter_query))

    def get_blacklist_elements(self):
        return set(self.file.by_type("IfcElement")) - set(
            ifcopenshell.util.selector.filter_elements(self.file, self.props.filter_query)
        )


class ToggleFilterCategories(bpy.types.Operator):
    bl_idname = "bim.toggle_filter_categories"
    bl_label = "Toggle Filter Categories"
    bl_options = {"REGISTER", "UNDO"}
    should_select: bpy.props.BoolProperty(name="Should Select", default=True)

    def execute(self, context):
        for filter_category in context.scene.BIMProjectProperties.filter_categories:
            filter_category.is_selected = self.should_select
        return {"FINISHED"}


class LinkIfc(bpy.types.Operator):
    bl_idname = "bim.link_ifc"
    bl_label = "Link IFC"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reference in a read-only IFC model in the background"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    files: bpy.props.CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)
    use_cache: bpy.props.BoolProperty(name="Use Cache", default=True)

    if TYPE_CHECKING:
        filepath: str
        files: list[bpy.types.OperatorFileListElement]
        directory: str

    def draw(self, context):
        pprops = context.scene.BIMProjectProperties
        row = self.layout.row()
        row.prop(self, "use_relative_path")
        row = self.layout.row()
        row.prop(self, "use_cache")
        row = self.layout.row()
        row.prop(pprops, "false_origin_mode")
        if pprops.false_origin_mode == "MANUAL":
            row = self.layout.row()
            row.prop(pprops, "false_origin")
            row = self.layout.row()
            row.prop(pprops, "project_north")

    def execute(self, context):
        start = time.time()
        files = [f.name for f in self.files] if self.files else [self.filepath]
        for filename in files:
            filepath = Path(self.directory) / filename
            if bpy.data.filepath and filepath.samefile(bpy.data.filepath):
                self.report({"INFO"}, "Can't link the current .blend file")
                continue
            new = context.scene.BIMProjectProperties.links.add()
            if self.use_relative_path:
                try:
                    filepath = filepath.relative_to(bpy.path.abspath("//"))
                except:
                    pass  # Perhaps on another drive or something
            new.name = filepath.as_posix()
            status = bpy.ops.bim.load_link(filepath=filepath.as_posix(), use_cache=self.use_cache)
            if status == {"CANCELLED"}:
                error_msg = (
                    f'Error processing IFC file "{filepath.as_posix()}" '
                    "was critical and blend file either wasn't saved or wasn't updated. "
                    "See logs above in system console for details."
                )
                print(error_msg)
                self.report({"ERROR"}, error_msg)
                return {"FINISHED"}
        print(f"Finished linking {len(files)} IFCs", time.time() - start)
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class UnlinkIfc(bpy.types.Operator):
    bl_idname = "bim.unlink_ifc"
    bl_label = "UnLink IFC"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the selected file from the link list"
    filepath: bpy.props.StringProperty()

    def execute(self, context):
        filepath = Path(self.filepath).as_posix()
        bpy.ops.bim.unload_link(filepath=filepath)
        index = context.scene.BIMProjectProperties.links.find(filepath)
        if index != -1:
            context.scene.BIMProjectProperties.links.remove(index)
        return {"FINISHED"}


class UnloadLink(bpy.types.Operator):
    bl_idname = "bim.unload_link"
    bl_label = "Unload Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unload the selected linked file"
    filepath: bpy.props.StringProperty()

    def execute(self, context):
        filepath = tool.Blender.ensure_blender_path_is_abs(Path(self.filepath))
        if filepath.suffix.lower() == ".ifc":
            filepath = filepath.with_suffix(".ifc.cache.blend")

        for collection in context.scene.collection.children[:]:
            if collection.library and Path(collection.library.filepath) == filepath:
                bpy.data.collections.remove(collection)

        for scene in bpy.data.scenes[:]:
            if scene.library and Path(scene.library.filepath) == filepath:
                bpy.data.scenes.remove(scene)

        links = context.scene.BIMProjectProperties.links
        link = links.get(self.filepath)
        # Let's assume that user might delete it.
        if empty_handle := link.empty_handle:
            bpy.data.objects.remove(empty_handle)
        link.is_loaded = False

        if not any([l.is_loaded for l in links]):
            ProjectDecorator.uninstall()
        # we make sure we don't draw queried object from the file that was just unlinked
        elif queried_obj := context.scene.BIMProjectProperties.queried_obj:
            queried_filepath = Path(queried_obj["ifc_filepath"])
            if queried_filepath == filepath:
                ProjectDecorator.uninstall()

        return {"FINISHED"}


class LoadLink(bpy.types.Operator):
    bl_idname = "bim.load_link"
    bl_label = "Load Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Load the selected file"
    filepath: bpy.props.StringProperty()
    use_cache: bpy.props.BoolProperty(name="Use Cache", default=True)

    filepath_: Path

    def execute(self, context):
        filepath = tool.Blender.ensure_blender_path_is_abs(Path(self.filepath))
        self.filepath_ = filepath
        if filepath.suffix.lower().endswith(".blend"):
            self.link_blend(filepath)
        elif filepath.suffix.lower().endswith(".ifc"):
            status = self.link_ifc()
            if status:
                return status
        return {"FINISHED"}

    def link_blend(self, filepath: Path) -> None:
        with bpy.data.libraries.load(str(filepath), link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
        link = bpy.context.scene.BIMProjectProperties.links.get(self.filepath_.as_posix())
        for scene in bpy.data.scenes:
            if not scene.library or Path(scene.library.filepath) != filepath:
                continue
            for child in scene.collection.children:
                if "IfcProject" not in child.name:
                    continue
                empty = bpy.data.objects.new(child.name, None)
                empty.instance_type = "COLLECTION"
                empty.instance_collection = child
                link.empty_handle = empty
                bpy.context.scene.collection.objects.link(empty)
                break
            break
        link.is_loaded = True
        tool.Blender.select_and_activate_single_object(bpy.context, empty)

    def link_ifc(self) -> Union[set[str], None]:
        blend_filepath = self.filepath_.with_suffix(".ifc.cache.blend")
        h5_filepath = self.filepath_.with_suffix(".ifc.cache.h5")

        if not self.use_cache and blend_filepath.exists():
            os.remove(blend_filepath)

        if not blend_filepath.exists():
            pprops = bpy.context.scene.BIMProjectProperties
            gprops = bpy.context.scene.BIMGeoreferenceProperties

            code = f"""
import bpy

def run():
    gprops = bpy.context.scene.BIMGeoreferenceProperties
    # Our model origin becomes their host model origin
    gprops.host_model_origin = "{gprops.model_origin}"
    gprops.host_model_origin_si = "{gprops.model_origin_si}"
    gprops.host_model_project_north = "{gprops.model_project_north}"
    gprops.has_blender_offset = {gprops.has_blender_offset}
    gprops.blender_offset_x = "{gprops.blender_offset_x}"
    gprops.blender_offset_y = "{gprops.blender_offset_y}"
    gprops.blender_offset_z = "{gprops.blender_offset_z}"
    gprops.blender_x_axis_abscissa = "{gprops.blender_x_axis_abscissa}"
    gprops.blender_x_axis_ordinate = "{gprops.blender_x_axis_ordinate}"
    pprops = bpy.context.scene.BIMProjectProperties
    pprops.distance_limit = {pprops.distance_limit}
    pprops.false_origin_mode = "{pprops.false_origin_mode}"
    pprops.false_origin = "{pprops.false_origin}"
    pprops.project_north = "{pprops.project_north}"
    bpy.ops.bim.load_linked_project(filepath="{self.filepath}")
    # Use str instead of as_posix to avoid issues with Windows shared paths.
    bpy.ops.wm.save_as_mainfile(filepath=r"{str(blend_filepath)}")

try:
    run()
except Exception as e:
    import traceback
    traceback.print_exc()
    exit(1)
            """

            t = time.time()
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(code)
            run = subprocess.run([bpy.app.binary_path, "-b", "--python", temp_file.name, "--python-exit-code", "1"])
            if run.returncode == 1:
                print("An error occurred while processing your IFC.")
                if not blend_filepath.exists() or blend_filepath.stat().st_mtime < t:
                    return {"CANCELLED"}

            self.set_model_origin_from_link()

        self.link_blend(blend_filepath)

    def set_model_origin_from_link(self) -> None:
        if tool.Ifc.get():
            return  # The current model's coordinates always take priority.

        json_filepath = self.filepath_.with_suffix(".ifc.cache.json")
        if not json_filepath.exists():
            return

        with open(json_filepath, "r") as f:
            data = json.load(f)

        gprops = bpy.context.scene.BIMGeoreferenceProperties
        for prop in ("model_origin", "model_origin_si", "model_project_north"):
            if (value := data.get(prop, None)) is not None:
                setattr(gprops, prop, value)


class ReloadLink(bpy.types.Operator):
    bl_idname = "bim.reload_link"
    bl_label = "Reload Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reload the selected file"
    filepath: bpy.props.StringProperty()

    def execute(self, context):
        filepath = Path(self.filepath)

        def get_linked_ifcs() -> set[bpy.types.Library]:
            return {
                c.library
                for c in bpy.data.collections
                if "IfcProject" in c.name and c.library and Path(c.library.filepath) == filepath
            }

        for library in get_linked_ifcs():
            library.reload()
        return {"FINISHED"}


class ToggleLinkSelectability(bpy.types.Operator):
    bl_idname = "bim.toggle_link_selectability"
    bl_label = "Toggle Link Selectability"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle selectability"
    link: bpy.props.StringProperty(name="Linked IFC Filepath")

    def execute(self, context):
        props = context.scene.BIMProjectProperties
        link = props.links.get(self.link)
        self.library_filepath = tool.Blender.ensure_blender_path_is_abs(Path(self.link).with_suffix(".ifc.cache.blend"))
        link.is_selectable = (is_selectable := not link.is_selectable)
        for collection in self.get_linked_collections():
            collection.hide_select = not is_selectable
        if handle := link.empty_handle:
            handle.hide_select = not is_selectable
        return {"FINISHED"}

    def get_linked_collections(self) -> list[bpy.types.Collection]:
        return [
            c
            for c in bpy.data.collections
            if "IfcProject" in c.name and c.library and Path(c.library.filepath) == self.library_filepath
        ]


class ToggleLinkVisibility(bpy.types.Operator):
    bl_idname = "bim.toggle_link_visibility"
    bl_label = "Toggle Link Visibility"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle visibility between SOLID and WIREFRAME"
    link: bpy.props.StringProperty(name="Linked IFC Filepath")
    mode: bpy.props.EnumProperty(name="Visibility Mode", items=((i, i, "") for i in ("WIREFRAME", "VISIBLE")))

    def execute(self, context):
        props = context.scene.BIMProjectProperties
        link = props.links.get(self.link)
        self.library_filepath = tool.Blender.ensure_blender_path_is_abs(Path(self.link).with_suffix(".ifc.cache.blend"))
        if self.mode == "WIREFRAME":
            self.toggle_wireframe(link)
        elif self.mode == "VISIBLE":
            self.toggle_visibility(link)
        return {"FINISHED"}

    def toggle_wireframe(self, link):
        for collection in self.get_linked_collections():
            objs = filter(lambda obj: "IfcOpeningElement" not in obj.name, collection.all_objects)
            for i, obj in enumerate(objs):
                if i == 0:
                    if obj.display_type == "WIRE":
                        display_type = "TEXTURED"
                    else:
                        display_type = "WIRE"
                obj.display_type = display_type
            link.is_wireframe = display_type == "WIRE"

    def toggle_visibility(self, link):
        linked_collections = self.get_linked_collections()

        link.is_hidden = (is_hidden := not link.is_hidden)
        layer_collections = tool.Blender.get_layer_collections_mapping(linked_collections)
        for layer_collection in layer_collections.values():
            layer_collection.exclude = is_hidden
        if handle := link.empty_handle:
            handle.hide_set(is_hidden)

    def get_linked_collections(self) -> list[bpy.types.Collection]:
        return [
            c
            for c in bpy.data.collections
            if "IfcProject" in c.name and c.library and Path(c.library.filepath) == self.library_filepath
        ]


class SelectLinkHandle(bpy.types.Operator):
    bl_idname = "bim.select_link_handle"
    bl_label = "Select Link Handle"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select link empty object handle"
    index: bpy.props.IntProperty(name="Link Index")

    def execute(self, context):
        props = context.scene.BIMProjectProperties
        link = props.links[self.index]
        handle = link.empty_handle
        if not handle:
            self.report({"ERROR"}, "Link has no empty handle (probably it was deleted).")
            return {"CANCELLED"}
        tool.Blender.select_and_activate_single_object(context, handle)
        return {"FINISHED"}


class ExportIFC(bpy.types.Operator):
    bl_idname = "bim.save_project"
    bl_label = "Save IFC"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcjson", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    json_version: bpy.props.EnumProperty(items=[("4", "4", ""), ("5a", "5a", "")], name="IFC JSON Version")
    json_compact: bpy.props.BoolProperty(name="Export Compact IFCJSON", default=False)
    should_save_as: bpy.props.BoolProperty(name="Should Save As", default=False, options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "json_version")
        layout.prop(self, "json_compact")
        if bpy.data.is_saved:
            layout.prop(self, "use_relative_path")

        layout.separator()
        layout.label(text="Supported formats for export:")
        layout.label(text=".ifc, .ifczip, .ifcjson")

    def invoke(self, context, event):
        if not tool.Ifc.get():
            bpy.ops.wm.save_mainfile("INVOKE_DEFAULT")
            return {"FINISHED"}

        self.use_relative_path = context.scene.BIMProjectProperties.use_relative_project_path
        if (filepath := context.scene.BIMProperties.ifc_file) and not self.should_save_as:
            self.filepath = str(tool.Blender.ensure_blender_path_is_abs(Path(filepath)))
            return self.execute(context)
        if not self.filepath:
            if bpy.data.is_saved:
                self.filepath = Path(bpy.data.filepath).with_suffix(".ifc").__str__()
            else:
                self.filepath = "untitled.ifc"

        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        project_props = context.scene.BIMProjectProperties
        project_props.use_relative_project_path = self.use_relative_path
        if project_props.should_disable_undo_on_save:
            old_history_size = tool.Ifc.get().history_size
            old_undo_steps = context.preferences.edit.undo_steps
            tool.Ifc.get().history_size = 0
            context.preferences.edit.undo_steps = 0
        IfcStore.execute_ifc_operator(self, context)
        if project_props.should_disable_undo_on_save:
            tool.Ifc.get().history_size = old_history_size
            context.preferences.edit.undo_steps = old_undo_steps
        return {"FINISHED"}

    def _execute(self, context):
        start = time.time()
        logger = logging.getLogger("ExportIFC")
        path_log = os.path.join(context.scene.BIMProperties.data_dir, "process.log")
        if not os.access(context.scene.BIMProperties.data_dir, os.W_OK):
            path_log = os.path.join(tempfile.mkdtemp(), "process.log")
        logging.basicConfig(
            filename=path_log,
            filemode="a",
            level=logging.DEBUG,
        )
        extension = self.filepath.split(".")[-1]
        if extension == "ifczip":
            output_file = bpy.path.ensure_ext(self.filepath, ".ifczip")
        elif extension == "ifcjson":
            output_file = bpy.path.ensure_ext(self.filepath, ".ifcjson")
        else:
            output_file = bpy.path.ensure_ext(self.filepath, ".ifc")

        settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        settings.json_version = self.json_version
        settings.json_compact = self.json_compact

        ifc_exporter = export_ifc.IfcExporter(settings)
        print("Starting export")
        settings.logger.info("Starting export")
        ifc_exporter.export()
        settings.logger.info("Export finished in {:.2f} seconds".format(time.time() - start))
        print("Export finished in {:.2f} seconds".format(time.time() - start))
        # New project created in Bonsai should be in recent projects too.
        tool.Project.add_recent_ifc_project(Path(output_file))
        scene = context.scene
        if not scene.DocProperties.ifc_files:
            new = scene.DocProperties.ifc_files.add()
            new.name = output_file
        if context.scene.BIMProjectProperties.use_relative_project_path and bpy.data.is_saved:
            output_file = os.path.relpath(output_file, bpy.path.abspath("//"))
        if scene.BIMProperties.ifc_file != output_file and extension not in ["ifczip", "ifcjson"]:
            scene.BIMProperties.ifc_file = output_file
        save_blend_file = bool(bpy.data.is_saved and bpy.data.is_dirty and bpy.data.filepath)
        if save_blend_file:
            bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
        bpy.context.scene.BIMProperties.is_dirty = False
        bonsai.bim.handler.refresh_ui_data()
        self.report(
            {"INFO"},
            f'IFC Project "{os.path.basename(output_file)}" {"" if not save_blend_file else "And Current Blend File Are"} Saved',
        )

        if bpy.data.is_saved:
            bpy.ops.wm.save_mainfile("INVOKE_DEFAULT")

    @classmethod
    def description(cls, context, properties):
        if properties.should_save_as:
            return "Save the IFC file under a new name, or relocate file"
        return "Save the IFC file.  Will save both .IFC/.BLEND files if synced together"


class LoadLinkedProject(bpy.types.Operator):
    bl_idname = "bim.load_linked_project"
    bl_label = "Load a project for viewing only."
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty()

    file: ifcopenshell.file
    meshes: dict[str, bpy.types.Mesh]
    # Material names is derived from diffuse as in 'r-g-b-a'.
    blender_mats: dict[str, bpy.types.Material]

    def execute(self, context):
        import ifcpatch
        import multiprocessing

        start = time.time()

        pprops = bpy.context.scene.BIMProjectProperties
        gprops = bpy.context.scene.BIMGeoreferenceProperties

        self.filepath = Path(self.filepath).as_posix()
        print("Processing", self.filepath)

        self.collection = bpy.data.collections.new("IfcProject/" + os.path.basename(self.filepath))
        self.file = ifcopenshell.open(self.filepath)
        tool.Ifc.set(self.file)
        print("Finished opening")

        self.db_filepath = self.filepath + ".cache.sqlite"
        db = ifcpatch.execute(
            {"input": self.filepath, "file": self.file, "recipe": "ExtractPropertiesToSQLite", "arguments": []}
        )
        ifcpatch.write(db, self.db_filepath)
        print("Finished writing property database")

        logger = logging.getLogger("ImportIFC")
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        tool.Loader.set_unit_scale(self.unit_scale)
        tool.Loader.set_settings(import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger))
        tool.Loader.settings.contexts = ifcopenshell.util.representation.get_prioritised_contexts(self.file)
        tool.Loader.settings.context_settings = tool.Loader.create_settings()
        tool.Loader.settings.gross_context_settings = tool.Loader.create_settings(is_gross=True)

        self.elements = set(self.file.by_type("IfcElement"))
        if self.file.schema in ("IFC2X3", "IFC4"):
            self.elements |= set(self.file.by_type("IfcProxy"))
        if self.file.schema == "IFC2X3":
            self.elements |= set(self.file.by_type("IfcSpatialStructureElement"))
        else:
            self.elements |= set(self.file.by_type("IfcSpatialElement"))
        self.elements -= set(self.file.by_type("IfcFeatureElement"))

        if tool.Loader.settings.false_origin_mode == "MANUAL" and tool.Loader.settings.false_origin:
            tool.Loader.set_manual_blender_offset(self.file)
        elif tool.Loader.settings.false_origin_mode == "AUTOMATIC":
            if host_model_origin_si := gprops.host_model_origin_si:
                host_model_origin_si = [float(o) / self.unit_scale for o in host_model_origin_si.split(",")]
                tool.Loader.settings.false_origin = host_model_origin_si
                tool.Loader.settings.project_north = float(gprops.host_model_project_north)
                tool.Loader.set_manual_blender_offset(self.file)
            else:
                tool.Loader.guess_false_origin(self.file)

        tool.Georeference.set_model_origin()
        self.json_filepath = self.filepath + ".cache.json"
        data = {
            "host_model_origin": gprops.host_model_origin,
            "host_model_origin_si": gprops.host_model_origin_si,
            "host_model_project_north": gprops.host_model_project_north,
            "model_origin": gprops.model_origin,
            "model_origin_si": gprops.model_origin_si,
            "model_project_north": gprops.model_project_north,
            "has_blender_offset": gprops.has_blender_offset,
            "blender_offset_x": gprops.blender_offset_x,
            "blender_offset_y": gprops.blender_offset_y,
            "blender_offset_z": gprops.blender_offset_z,
            "blender_x_axis_abscissa": gprops.blender_x_axis_abscissa,
            "blender_x_axis_ordinate": gprops.blender_x_axis_ordinate,
            "distance_limit": pprops.distance_limit,
            "false_origin_mode": pprops.false_origin_mode,
            "false_origin": pprops.false_origin,
            "project_north": pprops.project_north,
        }
        with open(self.json_filepath, "w") as f:
            json.dump(data, f)

        for settings in tool.Loader.settings.context_settings:
            if not self.elements:
                break

            results = set()
            iterator = ifcopenshell.geom.iterator(
                settings, self.file, multiprocessing.cpu_count(), include=self.elements
            )
            self.meshes = {}
            self.blender_mats = {}
            blender_mats = {}

            default_mat = np.array([[1, 1, 1, 1]], dtype=np.float32)
            chunked_guids = []
            chunked_guid_ids = []
            chunked_verts = []
            chunked_faces = []
            chunked_materials = []
            chunked_material_ids = []
            material_offset = 0
            chunk_size = 10000
            offset = 0

            ci = 0
            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    results.add(self.file.by_id(shape.id))

                    # Elements with a lot of geometry benefit from instancing to save memory
                    if len(shape.geometry.faces) > 1000:  # 333 tris
                        self.process_occurrence(shape)
                        if not iterator.next():
                            if not chunked_verts:
                                break
                            mats = np.concatenate(chunked_materials)
                            midx = np.concatenate(chunked_material_ids)
                            mats, mapping = np.unique(mats, axis=0, return_inverse=True)
                            midx = mapping[midx]

                            mat_results: list[bpy.types.Material] = []
                            for mat in mats:
                                mat = tuple(mat)
                                blender_mat = blender_mats.get(mat, None)
                                if not blender_mat:
                                    blender_mat = bpy.data.materials.new("Chunk")
                                    blender_mat.diffuse_color = mat
                                    blender_mats[mat] = blender_mat
                                mat_results.append(blender_mat)

                            # The left over chunk
                            self.create_object(
                                np.concatenate(chunked_verts),
                                np.concatenate(chunked_faces),
                                mat_results,
                                midx,
                                chunked_guids,
                                chunked_guid_ids,
                            )
                            break
                        continue

                    ci += 1
                    if ci % 50 == 0:
                        print("Doing chunk", ci)

                    has_processed_chunk = False

                    ms = np.vstack([default_mat, ifcopenshell.util.shape.get_material_colors(shape.geometry)])
                    mi = ifcopenshell.util.shape.get_faces_material_style_ids(shape.geometry)
                    for geom_material_idx, geom_material in enumerate(shape.geometry.materials):
                        if not geom_material.instance_id():
                            ms[geom_material_idx + 1] = (0.8, 0.8, 0.8, 1)
                    chunked_materials.append(ms)
                    chunked_material_ids.append(mi + material_offset + 1)
                    material_offset += len(ms)

                    matrix = np.frombuffer(shape.transformation_buffer).reshape((4, 4), order="F")
                    if gprops.has_blender_offset:
                        matrix = ifcopenshell.util.geolocation.global2local(
                            matrix,
                            float(gprops.blender_offset_x) * self.unit_scale,
                            float(gprops.blender_offset_y) * self.unit_scale,
                            float(gprops.blender_offset_z) * self.unit_scale,
                            float(gprops.blender_x_axis_abscissa),
                            float(gprops.blender_x_axis_ordinate),
                        )
                    vs = ifcopenshell.util.shape.get_vertices(shape.geometry)
                    vs = np.hstack((vs, np.ones((len(vs), 1))))
                    vs = (np.asmatrix(matrix) * np.asmatrix(vs).T).T.A
                    vs = vs[:, :3].flatten()
                    fs = ifcopenshell.util.shape.get_faces(shape.geometry).ravel()
                    chunked_verts.append(vs)
                    chunked_faces.append(fs + offset)
                    offset += len(vs) // 3

                    chunked_guids.append(shape.guid)
                    if chunked_guid_ids:
                        chunked_guid_ids.append((len(fs) // 3) + chunked_guid_ids[-1])
                    else:
                        chunked_guid_ids.append(len(fs) // 3)

                    if offset > chunk_size:
                        has_processed_chunk = True

                        mats = np.concatenate(chunked_materials)
                        midx = np.concatenate(chunked_material_ids)
                        mats, mapping = np.unique(mats, axis=0, return_inverse=True)
                        midx = mapping[midx]

                        mat_results = []
                        for mat in mats:
                            mat = tuple(mat)
                            blender_mat = blender_mats.get(mat, None)
                            if not blender_mat:
                                blender_mat = bpy.data.materials.new("Chunk")
                                blender_mat.diffuse_color = mat
                                blender_mats[mat] = blender_mat
                            mat_results.append(blender_mat)

                        self.create_object(
                            np.concatenate(chunked_verts),
                            np.concatenate(chunked_faces),
                            mat_results,
                            midx,
                            chunked_guids,
                            chunked_guid_ids,
                        )
                        chunked_guids = []
                        chunked_guid_ids = []
                        chunked_verts = []
                        chunked_faces = []
                        chunked_materials = []
                        chunked_material_ids = []
                        material_offset = 0
                        offset = 0

                    if not iterator.next():
                        if not has_processed_chunk:
                            mats = np.concatenate(chunked_materials)
                            midx = np.concatenate(chunked_material_ids)
                            mats, mapping = np.unique(mats, axis=0, return_inverse=True)
                            midx = mapping[midx]

                            mat_results = []
                            for mat in mats:
                                mat = tuple(mat)
                                blender_mat = blender_mats.get(mat, None)
                                if not blender_mat:
                                    blender_mat = bpy.data.materials.new("Chunk")
                                    blender_mat.diffuse_color = mat
                                    blender_mats[mat] = blender_mat
                                mat_results.append(blender_mat)

                            # The left over chunk
                            self.create_object(
                                np.concatenate(chunked_verts),
                                np.concatenate(chunked_faces),
                                mat_results,
                                midx,
                                chunked_guids,
                                chunked_guid_ids,
                            )
                        break
            self.elements -= results

        bpy.context.scene.collection.children.link(self.collection)
        print("Finished", time.time() - start)
        return {"FINISHED"}

    def process_occurrence(self, shape: ShapeElementType) -> None:
        element = self.file.by_id(shape.id)
        faces: tuple[int, ...] = shape.geometry.faces
        verts: tuple[float, ...] = shape.geometry.verts
        materials: tuple[W.style, ...] = shape.geometry.materials
        material_ids: tuple[int, ...] = shape.geometry.material_ids

        mat = ifcopenshell.util.shape.get_shape_matrix(shape)

        mesh = self.meshes.get(shape.geometry.id, None)
        if not mesh:
            mesh = bpy.data.meshes.new("Mesh")

            geometry = shape.geometry
            gprops = bpy.context.scene.BIMGeoreferenceProperties
            if (
                gprops.has_blender_offset
                and geometry.verts
                and tool.Loader.is_point_far_away(
                    (geometry.verts[0], geometry.verts[1], geometry.verts[2]), is_meters=True
                )
            ):
                # Shift geometry close to the origin based off that first vert it found
                verts_array = np.array(geometry.verts)
                offset = np.array([-geometry.verts[0], -geometry.verts[1], -geometry.verts[2]])
                offset_verts = verts_array + np.tile(offset, len(verts_array) // 3)
                verts = offset_verts.tolist()

                mesh["has_cartesian_point_offset"] = True
                mesh["cartesian_point_offset"] = f"{geometry.verts[0]},{geometry.verts[1]},{geometry.verts[2]}"
            else:
                verts = geometry.verts
                mesh["has_cartesian_point_offset"] = False

            material_to_slot = {}
            max_slot_index = 0

            for i, material in enumerate(materials):
                alpha = 1.0
                if material.has_transparency and material.transparency > 0:
                    alpha = 1.0 - material.transparency
                if material.instance_id():
                    diffuse = (material.diffuse.r(), material.diffuse.g(), material.diffuse.b(), alpha)
                else:
                    diffuse = (0.8, 0.8, 0.8, 1)  # Blender's default material
                material_name = f"{diffuse[0]}-{diffuse[1]}-{diffuse[2]}-{diffuse[3]}"
                blender_mat = self.blender_mats.get(material_name, None)
                if not blender_mat:
                    blender_mat = bpy.data.materials.new(material_name)
                    blender_mat.diffuse_color = diffuse
                    self.blender_mats[material_name] = blender_mat
                slot_index = mesh.materials.find(material.name)
                if slot_index == -1:
                    mesh.materials.append(blender_mat)
                    slot_index = max_slot_index
                    max_slot_index += 1
                material_to_slot[i] = slot_index

            material_index = [(material_to_slot[i] if i != -1 else 0) for i in material_ids]

            num_vertices = len(verts) // 3
            total_faces = len(faces)
            loop_start = range(0, total_faces, 3)
            num_loops = total_faces // 3
            loop_total = [3] * num_loops
            num_vertex_indices = len(faces)

            mesh.vertices.add(num_vertices)
            mesh.vertices.foreach_set("co", verts)
            mesh.loops.add(num_vertex_indices)
            mesh.loops.foreach_set("vertex_index", faces)
            mesh.polygons.add(num_loops)
            mesh.polygons.foreach_set("loop_start", loop_start)
            mesh.polygons.foreach_set("loop_total", loop_total)
            mesh.polygons.foreach_set("use_smooth", [0] * total_faces)
            mesh.polygons.foreach_set("material_index", material_index)
            mesh.update()

            self.meshes[shape.geometry.id] = mesh

        obj = bpy.data.objects.new(tool.Loader.get_name(element), mesh)
        obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(obj, mat)

        obj["guids"] = [shape.guid]
        obj["guid_ids"] = [len(mesh.polygons)]
        obj["db"] = self.db_filepath
        obj["ifc_filepath"] = self.filepath

        self.collection.objects.link(obj)

    def create_object(self, verts, faces, materials: list[bpy.types.Material], material_ids, guids, guid_ids):
        num_vertices = len(verts) // 3
        if not num_vertices:
            return
        total_faces = len(faces)
        loop_start = range(0, total_faces, 3)
        num_loops = total_faces // 3
        loop_total = [3] * num_loops
        num_vertex_indices = len(faces)

        mesh = bpy.data.meshes.new("Mesh")

        for material in materials:
            mesh.materials.append(material)

        mesh.vertices.add(num_vertices)
        mesh.vertices.foreach_set("co", verts)
        mesh.loops.add(num_vertex_indices)
        mesh.loops.foreach_set("vertex_index", faces)
        mesh.polygons.add(num_loops)
        mesh.polygons.foreach_set("loop_start", loop_start)
        mesh.polygons.foreach_set("loop_total", loop_total)
        mesh.polygons.foreach_set("use_smooth", [0] * total_faces)

        if material_ids.size > 0 and len(mesh.polygons) == len(material_ids):
            mesh.polygons.foreach_set("material_index", material_ids)

        mesh.update()

        obj = bpy.data.objects.new("Chunk", mesh)
        obj["guids"] = list(guids)
        obj["guid_ids"] = list(guid_ids)
        obj["db"] = self.db_filepath
        obj["ifc_filepath"] = self.filepath

        self.collection.objects.link(obj)


class QueryLinkedElement(bpy.types.Operator):
    bl_idname = "bim.query_linked_element"
    bl_label = "Query Linked Element"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        import sqlite3
        from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

        LinksData.linked_data = {}
        props = context.scene.BIMProjectProperties
        props.queried_obj = None
        props.quried_obj_root = None

        for area in bpy.context.screen.areas:
            if area.type == "PROPERTIES":
                for region in area.regions:
                    if region.type == "WINDOW":
                        region.tag_redraw()
            elif area.type == "VIEW_3D":
                area.tag_redraw()

        region = context.region
        rv3d = context.region_data
        coord = (self.mouse_x, self.mouse_y)
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        hit, location, normal, face_index, obj, instance_matrix = self.ray_cast(context, origin, direction)
        if not hit:
            self.report({"INFO"}, "No object found.")
            return {"FINISHED"}

        if "guids" not in obj:
            self.report({"INFO"}, "Object is not a linked IFC element.")
            return {"FINISHED"}

        guid = None
        guid_start_index = 0
        for i, guid_end_index in enumerate(obj["guid_ids"]):
            if face_index < guid_end_index:
                guid = obj["guids"][i]
                props.queried_obj = obj
                props.queried_obj_root = self.find_obj_root(obj, instance_matrix)

                selected_tris = []
                selected_edges = []
                vert_indices = set()
                for polygon in obj.data.polygons[guid_start_index:guid_end_index]:
                    vert_indices.update(polygon.vertices)
                vert_indices = list(vert_indices)
                vert_map = {k: v for v, k in enumerate(vert_indices)}
                selected_vertices = [tuple(obj.matrix_world @ obj.data.vertices[vi].co) for vi in vert_indices]
                for polygon in obj.data.polygons[guid_start_index:guid_end_index]:
                    selected_tris.append(tuple(vert_map[v] for v in polygon.vertices))
                    selected_edges.extend(tuple([vert_map[vi] for vi in e] for e in polygon.edge_keys))

                obj["selected_vertices"] = selected_vertices
                obj["selected_edges"] = selected_edges
                obj["selected_tris"] = selected_tris

                break
            guid_start_index = guid_end_index

        self.db = sqlite3.connect(obj["db"])
        self.c = self.db.cursor()

        self.c.execute(f"SELECT * FROM elements WHERE global_id = '{guid}' LIMIT 1")
        element = self.c.fetchone()

        attributes = {}
        for i, attr in enumerate(["GlobalId", "IFC Class", "Predefined Type", "Name", "Description"]):
            if element[i + 1] is not None:
                attributes[attr] = element[i + 1]

        self.c.execute("SELECT * FROM properties WHERE element_id = ?", (element[0],))
        rows = self.c.fetchall()

        properties = {}
        for row in rows:
            properties.setdefault(row[1], {})[row[2]] = row[3]

        self.c.execute("SELECT * FROM relationships WHERE from_id = ?", (element[0],))
        relationships = self.c.fetchall()

        relating_type_id = None

        for relationship in relationships:
            if relationship[1] == "IfcRelDefinesByType":
                relating_type_id = relationship[2]

        type_properties = {}
        if relating_type_id is not None:
            self.c.execute("SELECT * FROM properties WHERE element_id = ?", (relating_type_id,))
            rows = self.c.fetchall()
            for row in rows:
                type_properties.setdefault(row[1], {})[row[2]] = row[3]

        LinksData.linked_data = {
            "attributes": attributes,
            "properties": [(k, properties[k]) for k in sorted(properties.keys())],
            "type_properties": [(k, type_properties[k]) for k in sorted(type_properties.keys())],
        }
        self.db.close()

        for area in bpy.context.screen.areas:
            if area.type == "PROPERTIES":
                for region in area.regions:
                    if region.type == "WINDOW":
                        region.tag_redraw()
            elif area.type == "VIEW_3D":
                area.tag_redraw()

        self.report({"INFO"}, f"Loaded data for {guid}")
        ProjectDecorator.install(bpy.context)
        return {"FINISHED"}

    def ray_cast(self, context: bpy.types.Context, origin: Vector, direction: Vector):
        depsgraph = context.evaluated_depsgraph_get()
        result = context.scene.ray_cast(depsgraph, origin, direction)
        return result

    def find_obj_root(self, obj: bpy.types.Object, matrix: Matrix) -> Union[bpy.types.Object, None]:
        collections = set(obj.users_collection)
        for o in bpy.data.objects:
            if (
                o.type != "EMPTY"
                or o.instance_type != "COLLECTION"
                or o.instance_collection not in collections
                or not np.allclose(matrix, o.matrix_world, atol=1e-4)
            ):
                continue
            return o

    def invoke(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        return self.execute(context)


class AppendInspectedLinkedElement(AppendLibraryElement):
    bl_idname = "bim.append_inspected_linked_element"
    bl_label = "Append Inspected Linked Element"
    bl_description = "Append inspected linked element"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        from bonsai.bim.module.project.data import LinksData

        if not LinksData.linked_data:
            self.report({"INFO"}, "No linked element found.")
            return {"CANCELLED"}

        guid = LinksData.linked_data["attributes"].get("GlobalId")
        if guid is None:
            self.report({"INFO"}, "Cannot find Global Id for element.")
            return {"CANCELLED"}

        queried_obj = context.scene.BIMProjectProperties.queried_obj

        ifc_file = tool.Ifc.get()
        linked_ifc_file = ifcopenshell.open(queried_obj["ifc_filepath"])
        if ifc_file.schema_identifier != linked_ifc_file.schema_identifier:
            self.report(
                {"ERROR"},
                f"Schema of linked file ({linked_ifc_file.schema_identifier}) is not compatible with the current IFC file ({ifc_file.schema_identifier}).",
            )
            return {"CANCELLED"}

        element_to_append = linked_ifc_file.by_guid(guid)
        element = ifcopenshell.api.run(
            "project.append_asset",
            tool.Ifc.get(),
            library=linked_ifc_file,
            element=element_to_append,
        )
        self.import_product_from_ifc(element, context)
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type and tool.Ifc.get_object(element_type) is None:
            self.import_type_from_ifc(element_type, context)

        return {"FINISHED"}


class EnableCulling(bpy.types.Operator):
    bl_idname = "bim.enable_culling"
    bl_label = "Enable Culling"
    bl_options = {"REGISTER"}

    def __init__(self):
        self.last_view_corners = None
        self.total_mousemoves = 0
        self.cullable_objects = []

    def modal(self, context, event):
        if not LinksData.enable_culling:
            for obj in bpy.context.visible_objects:
                if obj.type == "MESH" and obj.name.startswith("Ifc"):
                    obj.display_type = "SOLID"
            self.cullable_objects = []
            return {"CANCELLED"}

        # Even if the view is changing, there are certain scenarios where we
        # don't want to apply culling. For example, if we scroll to zoom but
        # are simultaneously moving our mouse, or if we `Zoom to Selected`. A
        # dumb but seemingly effective way is to count MOUSEMOVE events. If at
        # least 3 consecutive events occur, you're probably not doing some
        # other navigational thing.
        if event.type == "MOUSEMOVE":
            self.total_mousemoves += 1
        else:
            self.total_mousemoves = 0

        if self.total_mousemoves > 2 and self.is_view_changed(context):
            self.total_mousemoves = 0
            camera_position = context.region_data.view_matrix.inverted().translation
            for obj in self.cullable_objects:
                if obj.type == "MESH" and obj.name.startswith("Ifc"):
                    if self.is_object_in_view(obj, context, camera_position):
                        obj.display_type = "SOLID"
                    elif obj.display_type != "BOUNDS":
                        obj.display_type = "BOUNDS"

        return {"PASS_THROUGH"}

    def is_view_changed(self, context):
        view_matrix = context.region_data.view_matrix
        projection_matrix = context.region_data.window_matrix
        vp_matrix = projection_matrix @ view_matrix

        # Get NDC coordinates of the viewport corners
        viewport_corners = [Vector((-1, -1, 0)), Vector((1, -1, 0)), Vector((1, 1, 0)), Vector((-1, 1, 0))]
        ndc_corners = [vp_matrix @ Vector((corner.x, corner.y, -1, 1)) for corner in viewport_corners]
        ndc_corners = [(corner / corner.w).xy for corner in ndc_corners]

        if self.last_view_corners != ndc_corners:
            self.last_view_corners = ndc_corners
            return True
        return False

    def is_object_in_view(self, obj, context, camera_position):
        # Get the view matrix and the projection matrix from the active viewport
        view_matrix = context.region_data.view_matrix
        projection_matrix = context.region_data.window_matrix
        # Calculate the combined view projection matrix
        vp_matrix = projection_matrix @ view_matrix
        obj_matrix_world = obj.matrix_world

        # Transform each corner of the bounding box using the view projection matrix
        # and check if it's inside the normalized device coordinates (NDC) space
        for corner in [obj_matrix_world @ Vector(corner) for corner in obj.bound_box]:
            ndc = vp_matrix @ corner.to_4d()
            ndc /= ndc.w
            if -1 <= ndc.x <= 1 and -1 <= ndc.y <= 1 and 0 <= ndc.z <= 1:
                # At least one corner is inside the view, so the object is visible
                break
        else:
            return False

        # Check if the object is too far away from the camera
        object_center = obj.matrix_world.translation
        distance_threshold = 900  # 30m squared
        if (camera_position - object_center).length_squared > distance_threshold:
            # The object is too far away, so consider it not visible
            return False
        return True

    def invoke(self, context, event):
        LinksData.enable_culling = True
        self.cullable_objects = []
        for obj in bpy.context.visible_objects:
            if obj.type == "MESH" and obj.name.startswith("Ifc") and max(obj.dimensions) < 0.6:
                self.cullable_objects.append(obj)
                camera_position = context.region_data.view_matrix.inverted().translation
                if not self.is_object_in_view(obj, context, camera_position):
                    obj.display_type = "BOUNDS"
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class DisableCulling(bpy.types.Operator):
    bl_idname = "bim.disable_culling"
    bl_label = "Disable Culling"
    bl_options = {"REGISTER"}

    def execute(self, context):
        LinksData.enable_culling = False
        return {"FINISHED"}


class RefreshClippingPlanes(bpy.types.Operator):
    bl_idname = "bim.refresh_clipping_planes"
    bl_label = "Refresh Clipping Planes"
    bl_options = {"REGISTER"}

    def __init__(self):
        self.total_planes = 0

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        should_refresh = False

        self.clean_deleted_planes(context)

        for clipping_plane in context.scene.BIMProjectProperties.clipping_planes:
            if clipping_plane.obj and self.is_moved(clipping_plane.obj):
                should_refresh = True
                break

        total_planes = len(context.scene.BIMProjectProperties.clipping_planes)
        if should_refresh or total_planes != self.total_planes:
            self.refresh_clipping_planes(context)
            for clipping_plane in context.scene.BIMProjectProperties.clipping_planes:
                if clipping_plane.obj:
                    tool.Geometry.record_object_position(clipping_plane.obj)
            self.total_planes = total_planes
        return {"PASS_THROUGH"}

    def clean_deleted_planes(self, context):
        while True:
            for i, clipping_plane in enumerate(context.scene.BIMProjectProperties.clipping_planes):
                if clipping_plane.obj:
                    try:
                        clipping_plane.obj.name
                    except:
                        context.scene.BIMProjectProperties.clipping_planes.remove(i)
                        break
                else:
                    context.scene.BIMProjectProperties.clipping_planes.remove(i)
                    break
            else:
                break

    def is_moved(self, obj):
        if not obj.BIMObjectProperties.location_checksum:
            return True  # Let's be conservative
        loc_check = np.frombuffer(eval(obj.BIMObjectProperties.location_checksum))
        rot_check = np.frombuffer(eval(obj.BIMObjectProperties.rotation_checksum))
        loc_real = np.array(obj.matrix_world.translation).flatten()
        rot_real = np.array(obj.matrix_world.to_3x3()).flatten()
        if np.allclose(loc_check, loc_real, atol=1e-4) and np.allclose(rot_check, rot_real, atol=1e-2):
            return False
        return True

    def refresh_clipping_planes(self, context):
        import bmesh
        from itertools import cycle

        area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
        region = next(r for r in area.regions if r.type == "WINDOW")
        data = region.data

        if not len(context.scene.BIMProjectProperties.clipping_planes):
            data.use_clip_planes = False
        else:
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.view3d.clip_border()

                clip_planes = []
                for clipping_plane in bpy.context.scene.BIMProjectProperties.clipping_planes:
                    obj = clipping_plane.obj
                    if not obj:
                        continue

                    bm = bmesh.new()
                    bm.from_mesh(obj.data)

                    world_matrix = obj.matrix_world

                    bm.faces.ensure_lookup_table()
                    face = bm.faces[0]
                    center = world_matrix @ face.calc_center_median()
                    normal = world_matrix.to_3x3() @ face.normal * -1
                    center += normal * -0.01

                    normal.normalize()
                    distance = -center.dot(normal)
                    clip_plane = (normal.x, normal.y, normal.z, distance)
                    clip_planes.append(clip_plane)
                    bm.free()

                clip_planes = cycle(clip_planes)
                data.clip_planes = [tuple(next(clip_planes)) for i in range(0, 6)]
        data.update()
        region.tag_redraw()
        [a.tag_redraw() for a in bpy.context.screen.areas]
        return {"FINISHED"}


class CreateClippingPlane(bpy.types.Operator):
    bl_idname = "bim.create_clipping_plane"
    bl_label = "Create Clipping Plane"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

        # Clean up deleted planes

        if len(context.scene.BIMProjectProperties.clipping_planes) > 5:
            self.report({"INFO"}, "Maximum of six clipping planes allowed.")
            return {"FINISHED"}

        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

        region = context.region
        rv3d = context.region_data
        if rv3d:  # Called from a 3D viewport
            coord = (self.mouse_x, self.mouse_y)
            origin = region_2d_to_origin_3d(region, rv3d, coord)
            direction = region_2d_to_vector_3d(region, rv3d, coord)
            hit, location, normal, face_index, obj, matrix = self.ray_cast(context, origin, direction)
            if not hit:
                self.report({"INFO"}, "No object found.")
                return {"FINISHED"}
        else:  # Not Called from a 3D viewport
            location = (0, 0, 1)
            normal = (0, 0, 1)

        vertices = [(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)]

        faces = [(0, 1, 2, 3)]

        mesh = bpy.data.meshes.new(name="ClippingPlane")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        plane_obj = bpy.data.objects.new("ClippingPlane", mesh)
        plane_obj.show_in_front = True
        context.collection.objects.link(plane_obj)
        z_axis = Vector((0, 0, 1))
        rotation_matrix = z_axis.rotation_difference(normal).to_matrix().to_4x4()
        plane_obj.matrix_world = rotation_matrix
        plane_obj.matrix_world.translation = location

        context.scene.cursor.location = location

        new = context.scene.BIMProjectProperties.clipping_planes.add()
        new.obj = plane_obj

        tool.Blender.set_active_object(plane_obj)

        ClippingPlaneDecorator.install(context)
        bpy.ops.bim.refresh_clipping_planes("INVOKE_DEFAULT")
        return {"FINISHED"}

    def ray_cast(self, context, origin, direction):
        depsgraph = context.evaluated_depsgraph_get()
        result = context.scene.ray_cast(depsgraph, origin, direction)
        return result

    def invoke(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        return self.execute(context)


class FlipClippingPlane(bpy.types.Operator):
    bl_idname = "bim.flip_clipping_plane"
    bl_label = "Flip Clipping Plane"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        if obj in context.scene.BIMProjectProperties.clipping_planes_objs:
            obj.rotation_euler[0] += radians(180)
            context.view_layer.update()
        return {"FINISHED"}


CLIPPING_PLANES_FILE_NAME = "ClippingPlanes.json"  # TODO un-hardcode :=


class BIM_OT_save_clipping_planes(bpy.types.Operator):
    bl_idname = "bim.save_clipping_planes"
    bl_label = "Save Clipping Planes"
    bl_description = "Save Clipping Planes to Disk"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if IfcStore.path:
            return context.scene.BIMProjectProperties.clipping_planes
        cls.poll_message_set("Please Save The IFC File")

    def execute(self, context):
        clipping_planes_to_serialize = defaultdict(dict)
        clipping_planes = context.scene.BIMProjectProperties.clipping_planes
        for clipping_plane in clipping_planes:
            obj = clipping_plane.obj
            name = obj.name
            clipping_planes_to_serialize[name]["location"] = obj.location[0:3]
            clipping_planes_to_serialize[name]["rotation"] = obj.rotation_euler[0:3]
        with open(Path(IfcStore.path).with_name(CLIPPING_PLANES_FILE_NAME), "w") as file:
            json.dump(clipping_planes_to_serialize, file, indent=4)
        return {"FINISHED"}


class BIM_OT_load_clipping_planes(bpy.types.Operator):
    bl_idname = "bim.load_clipping_planes"
    bl_label = "Load Clipping Planes"
    bl_description = "Load Clipping Planes from Disk"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if filepath := IfcStore.path:
            if Path(filepath).with_name(CLIPPING_PLANES_FILE_NAME).exists():
                return True
            else:
                cls.poll_message_set(f"No Clipping Planes File in Folder {filepath}")
        else:
            cls.poll_message_set("Please Save The IFC File")

    def execute(self, context):
        bpy.data.batch_remove(context.scene.BIMProjectProperties.clipping_planes_objs)
        context.scene.BIMProjectProperties.clipping_planes.clear()
        with open(Path(IfcStore.path).with_name(CLIPPING_PLANES_FILE_NAME), "r") as file:
            clipping_planes_dict = json.load(file)
        for name, values in clipping_planes_dict.items():
            bpy.ops.bim.create_clipping_plane()
            obj = context.scene.BIMProjectProperties.clipping_planes_objs[-1]
            obj.name = name
            obj.location = values["location"]
            obj.rotation_euler = values["rotation"]
        return {"FINISHED"}


if bpy.app.version >= (4, 1, 0):

    class IFCFileHandlerOperator(bpy.types.Operator):
        bl_idname = "bim.load_project_file_handler"
        bl_label = "Import .ifc file"
        bl_options = {"REGISTER", "UNDO", "INTERNAL"}

        directory: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE", "HIDDEN"})
        files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={"SKIP_SAVE", "HIDDEN"})

        def invoke(self, context, event):
            # Keeping code in .invoke() as we'll probably add some
            # popup windows later.

            # `files` contain only .ifc files.
            filepath = Path(self.directory)
            # If user is just drag'n'dropping a single file -> load it as a new project,
            # if they're holding ALT -> link the file/files to the current project.
            if event.alt:
                # Passing self.files directly results in TypeError.
                serialized_files = [{"name": f.name} for f in self.files]
                return bpy.ops.bim.link_ifc(directory=self.directory, files=serialized_files)
            else:
                if len(self.files) == 1:
                    return bpy.ops.bim.load_project(filepath=(filepath / self.files[0].name).as_posix())
                else:
                    self.report(
                        {"INFO"},
                        "To link multiple IFC files hold ALT while drag'n'dropping them.",
                    )
                    return {"FINISHED"}

    class BIM_FH_import_ifc(bpy.types.FileHandler):
        bl_label = "IFC File Handler"
        bl_import_operator = IFCFileHandlerOperator.bl_idname
        bl_file_extensions = ".ifc"

        # FileHandler won't work without poll_drop defined.
        @classmethod
        def poll_drop(cls, context):
            return True


class MeasureTool(bpy.types.Operator, PolylineOperator):
    bl_idname = "bim.measure_tool"
    bl_label = "Measure Tool"
    bl_options = {"REGISTER", "UNDO"}

    measure_type: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self):
        super().__init__()
        if self.measure_type == "AREA":
            self.input_ui = tool.Polyline.create_input_ui(init_z=True, init_area=True)
        else:
            self.input_ui = tool.Polyline.create_input_ui(init_z=True)
        self.input_options = ["D", "A", "X", "Y", "Z"]
        self.instructions = """TAB: Cycle Input
        D: Distance Input
        A: Angle Input
        M: Modify Snap Point
        C: Close Polyline
        E: Erase previous polylines
        BACKSPACE: Remove Point
        X, Y, Z: Choose Axis
        S-X, S-Y, S-Z: Choose Plane
        L: Lock axis
        """

    def modal(self, context, event):
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_instructions(context)

        self.handle_mouse_move(context, event)

        self.choose_axis(event, z=True)

        self.choose_plane(event)

        self.handle_snap_selection(context, event)

        single_mode = False

        if (
            self.measure_type == "SINGLE"
            and context.scene.BIMPolylineProperties.insertion_polyline
            and len(context.scene.BIMPolylineProperties.insertion_polyline[0].polyline_points) >= 2
        ):
            single_mode = True

        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ) or single_mode:
            context.workspace.status_text_set(text=None)
            PolylineDecorator.uninstall()
            tool.Polyline.move_polyline_to_measure(context, self.input_ui)
            tool.Polyline.clear_polyline()
            MeasureDecorator.install(context)
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)

        self.handle_inserting_polyline(context, event)

        # Add measurement type to the insertion polyline
        polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
        if not polyline_data:
            pass
        else:
            polyline_data = context.scene.BIMPolylineProperties.insertion_polyline[0]
            measurement_type = bpy.context.scene.MeasureToolSettings.measurement_type
            if not polyline_data.measurement_type:
                polyline_data.measurement_type = measurement_type

        tool.Polyline.calculate_area(context, self.input_ui)

        if event.type == "E":
            context.scene.BIMPolylineProperties.measurement_polyline.clear()
            MeasureDecorator.uninstall()
            tool.Blender.update_viewport()

        result = self.handle_cancelation(context, event)
        if result is not None:
            return result

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        super().invoke(context, event)
        return {"RUNNING_MODAL"}
