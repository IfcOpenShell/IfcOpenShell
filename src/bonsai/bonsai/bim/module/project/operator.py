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
#
# This file was modified with the assistance of an AI coding tool.

import datetime
import json
import logging
import os
import subprocess
import tempfile
import time
import traceback
from collections import defaultdict
from math import radians
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Union, get_args

import bpy
import ifcopenshell
import ifcopenshell.api.attribute
import ifcopenshell.api.document
import ifcopenshell.api.nest
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.element
import ifcopenshell.util.file
import ifcopenshell.util.geolocation
import ifcopenshell.util.representation
import ifcopenshell.util.selector
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import numpy as np
from bpy.app.handlers import persistent
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy_extras.view3d_utils import (
    region_2d_to_origin_3d,
    region_2d_to_vector_3d,
)
from mathutils import Vector

import bonsai.bim.handler
import bonsai.bim.helper
import bonsai.core.project as core
import bonsai.tool as tool
from bonsai.bim import export_ifc, import_ifc
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.model import preview_base
from bonsai.bim.module.model.decorator import FaceAreaDecorator, PolylineDecorator
from bonsai.bim.module.model.polyline import PolylineOperator
from bonsai.bim.module.project.data import LinksData, ProjectLibraryData
from bonsai.bim.module.project.decorator import (
    ClippingPlaneDecorator,
    MeasureDecorator,
    ProjectDecorator,
)
from bonsai.bim.module.project.prop import BreadcrumbType
from bonsai.bim.ui import IFCFileSelector

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums

    from bonsai.bim.module.project.prop import Link


PresetType = Literal["metric_m", "metric_mm", "imperial_ft", "demo", "wizard"]


class NewProject(bpy.types.Operator):
    bl_idname = "bim.new_project"
    bl_label = "New Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Start a new IFC project in a fresh session"
    preset: bpy.props.EnumProperty(items=[(i, i, "") for i in get_args(PresetType)])

    if TYPE_CHECKING:
        preset: PresetType

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        bpy.ops.wm.read_homefile()
        pprops = tool.Project.get_project_props()
        bim_props = tool.Blender.get_bim_props()

        assert bpy.context.scene
        if self.preset == "metric_m":
            pprops.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "METRIC"
            bpy.context.scene.unit_settings.length_unit = "METERS"
            bim_props.area_unit = "SQUARE_METRE"
            bim_props.volume_unit = "CUBIC_METRE"
            pprops.template_file = "0"
        elif self.preset == "metric_mm":
            pprops.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "METRIC"
            bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
            bim_props.area_unit = "SQUARE_METRE"
            bim_props.volume_unit = "CUBIC_METRE"
            pprops.template_file = "0"
        elif self.preset == "imperial_ft":
            pprops.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "IMPERIAL"
            bpy.context.scene.unit_settings.length_unit = "FEET"
            bim_props.area_unit = "square foot"
            bim_props.volume_unit = "cubic foot"
            pprops.template_file = "0"
        elif self.preset == "demo":
            pprops.export_schema = "IFC4"
            bpy.context.scene.unit_settings.system = "METRIC"
            bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
            bim_props.area_unit = "SQUARE_METRE"
            bim_props.volume_unit = "CUBIC_METRE"
            pprops.template_file = "IFC4 Demo Template.ifc"

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
        props = tool.Project.get_project_props()
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
        tool.Blender.register_toolbar()
        tool.Loader.set_unit_scale(ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get()))

    def rollback(self, data):
        IfcStore.file = None

    def commit(self, data):
        IfcStore.file = data["file"]


class SelectLibraryFile(bpy.types.Operator, IFCFileSelector, ImportHelper):
    bl_idname = "bim.select_library_file"
    bl_label = "Select Library File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Select an IFC file that can be used as a library.\n\nALT+click to reload the current loaded library file."
    )
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    append_all: bpy.props.BoolProperty(default=False)
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    if TYPE_CHECKING:
        filter_glob: str
        append_all: bool
        use_relative_path: bool

    reload_previous_file = False

    def invoke(self, context, event):
        if event.alt:
            old_filepath = IfcStore.library_path
            if not old_filepath:
                self.report({"ERROR"}, "No library file loaded to reload.")
                return {"CANCELLED"}
            self.filepath = old_filepath
            self.reload_previous_file = True
            return self.execute(context)

        return ImportHelper.invoke(self, context, event)

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
        library_file: ifcopenshell.file
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
        ProjectLibraryData.load()
        self.report({"INFO"}, f"Loaded library from {filepath}.")
        return {"FINISHED"}

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
    bl_description = "Refresh the library browser"
    bl_options = {"UNDO"}

    def execute(self, context):
        self.props = tool.Project.get_project_props()

        self.props.library_elements.clear()
        self.props.library_breadcrumb.clear()

        library_file = IfcStore.library_file
        assert library_file

        if not self.props.show_library_tree:
            for appendable_type in sorted(tool.Project.get_appendable_asset_types()):
                elements = library_file.by_type(appendable_type)
                self.props.add_library_asset_class(appendable_type, len(elements))
            return {"FINISHED"}

        # Library tree.
        # Add entry for unassigned elements.
        elements = set()
        for importable_type in sorted(tool.Project.get_appendable_asset_types()):
            elements.update(library_file.by_type(importable_type))
        rels = tool.Project.get_project_library_rels(library_file)
        elements = {e for e in elements if not tool.Project.is_element_assigned_to_project_library(e, rels)}
        self.props.add_library_project_library("Unassigned", len(elements), 0, False)

        root_context = tool.Project.get_root_context(library_file)
        hierarchy = tool.Project.get_project_hierarchy(library_file)
        tool.Project.load_project_libraries_to_ui(root_context, hierarchy)
        return {"FINISHED"}


class ChangeLibraryElement(bpy.types.Operator):
    bl_idname = "bim.change_library_element"
    bl_label = "Change Library Element"
    bl_options = {"REGISTER", "UNDO"}
    element_name: bpy.props.StringProperty()
    breadcrumb_type: bpy.props.EnumProperty(items=[(i, i, "") for i in get_args(BreadcrumbType)])
    library_id: bpy.props.IntProperty()

    if TYPE_CHECKING:
        element_name: str
        breadcrumb_type: BreadcrumbType
        library_id: int

    def execute(self, context):
        self.props = tool.Project.get_project_props()
        self.file = tool.Ifc.get()
        library_file = IfcStore.library_file
        assert library_file
        self.library_file = library_file

        crumb = self.props.library_breadcrumb.add()
        crumb.name = self.element_name
        crumb.breadcrumb_type = self.breadcrumb_type
        if self.breadcrumb_type == "LIBRARY":
            crumb.library_id = self.library_id

        active_project_library = None
        library_elements = None
        project_library_rels = None
        # Reverse to get last library in hierarchy.
        for entry in reversed(self.props.library_breadcrumb):
            if entry.breadcrumb_type == "LIBRARY":
                if entry.library_id == 0:
                    # For unassigned elements.
                    active_project_library = "NO_LIBRARY"
                    project_library_rels = tool.Project.get_project_library_rels(library_file)
                else:
                    active_project_library = library_file.by_id(entry.library_id)
                    library_elements = tool.Project.get_project_library_elements(active_project_library)
                break

        def filter_elements(elements: list[ifcopenshell.entity_instance]) -> list[ifcopenshell.entity_instance]:
            if active_project_library is None:
                return elements
            elif active_project_library == "NO_LIBRARY":
                assert project_library_rels is not None
                return [
                    element
                    for element in elements
                    if not tool.Project.is_element_assigned_to_project_library(element, project_library_rels)
                ]
            else:
                assert library_elements is not None
                return [e for e in elements if e in library_elements]

        self.props.library_elements.clear()

        if self.breadcrumb_type == "LIBRARY":
            hierarchy = tool.Project.get_project_hierarchy(library_file)
            assert active_project_library is not None
            if active_project_library != "NO_LIBRARY" and hierarchy[active_project_library]:
                tool.Project.load_project_libraries_to_ui(active_project_library, hierarchy)

            for appendable_type in sorted(tool.Project.get_appendable_asset_types()):
                elements = library_file.by_type(appendable_type)
                if elements := filter_elements(elements):
                    self.props.add_library_asset_class(appendable_type, len(elements))

        else:  # breadcrumb_type CLASS.
            elements = self.library_file.by_type(self.element_name)
            elements = list(filter_elements(elements))
            ifc_classes_elements: dict[str, list[ifcopenshell.entity_instance]] = defaultdict(list)
            for element in elements:
                ifc_classes_elements[element.is_a()].append(element)

            if len(ifc_classes_elements) == 1 and next(iter(ifc_classes_elements)) == self.element_name:
                for name, ifc_definition_id in sorted(
                    [(self.get_name(e), e.id()) for e in ifc_classes_elements[self.element_name]]
                ):
                    self.add_library_asset(name, ifc_definition_id)
            else:
                for ifc_class in sorted(ifc_classes_elements):
                    if ifc_class == self.element_name:
                        continue
                    self.props.add_library_asset_class(ifc_class, len(ifc_classes_elements[ifc_class]))
                elements_ = ifc_classes_elements[self.element_name]
                for name, ifc_definition_id, ifc_class in sorted(
                    [(self.get_name(e), e.id(), e.is_a()) for e in elements_]
                ):
                    self.add_library_asset(name, ifc_definition_id)

        # Could occur if all elements were assigned to a different library.
        if len(self.props.library_elements) == 0:
            bpy.ops.bim.rewind_library()

        return {"FINISHED"}

    def get_name(self, element: ifcopenshell.entity_instance) -> str:
        attr_name = tool.Project.get_library_element_attr_name(element)
        return getattr(element, attr_name) or "Unnamed"

    def add_library_asset(self, name: str, ifc_definition_id: int) -> None:
        new = self.props.library_elements.add()
        new["name"] = name
        new.ifc_definition_id = ifc_definition_id
        element = self.library_file.by_id(ifc_definition_id)

        # is_declarable.
        project_libraries_exist = bool(
            self.library_file.schema != "IFC2X3" and self.library_file.by_type("IfcProjectLibrary")
        )
        is_declarable = project_libraries_exist and element.is_a("IfcObjectDefinition")
        new.is_declarable = is_declarable

        selected_library = self.props.selected_project_library
        # is_declared.
        if not is_declarable:
            new.is_declared = False
        elif has_context := element.HasContext:
            relating_context: ifcopenshell.entity_instance
            relating_context = has_context[0].RelatingContext
            new.is_declared = relating_context == self.library_file.by_id(int(selected_library))

        # is_appended.
        try:
            if element.is_a("IfcMaterial"):
                next(e for e in self.file.by_type("IfcMaterial") if e.Name == name)
            elif element.is_a("IfcProfileDef"):
                next(e for e in self.file.by_type("IfcProfileDef") if e.ProfileName == name)
            elif element.is_a("IfcPresentationStyle"):
                next(e for e in self.file.by_type(element.is_a()) if e.Name == name)
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
        self.props = tool.Project.get_project_props()
        total_breadcrumbs = len(self.props.library_breadcrumb)
        if total_breadcrumbs < 2:
            bpy.ops.bim.refresh_library()
            return {"FINISHED"}
        current_element = self.props.library_breadcrumb[total_breadcrumbs - 2]
        element_name = current_element.name
        breadcrumb_type = current_element.breadcrumb_type
        library_id = current_element.library_id
        self.props.library_breadcrumb.remove(total_breadcrumbs - 1)
        self.props.library_breadcrumb.remove(total_breadcrumbs - 2)
        bpy.ops.bim.change_library_element(
            element_name=element_name,
            breadcrumb_type=breadcrumb_type,
            library_id=library_id,
        )
        return {"FINISHED"}


class AssignLibraryDeclaration(bpy.types.Operator):
    bl_idname = "bim.assign_library_declaration"
    bl_label = "Assign Library Declaration"
    bl_description = "Assign element to the active library. If no specific library selected, will assign it to the first library in the file."
    bl_options = {"REGISTER", "UNDO"}
    definition: bpy.props.IntProperty()

    if TYPE_CHECKING:
        definition: int

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.library_file.begin_transaction()
        result = self._execute(context)
        IfcStore.library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = tool.Project.get_project_props()
        library_file = IfcStore.library_file
        assert library_file

        project_library = library_file.by_id(int(props.selected_project_library))

        ifcopenshell.api.project.assign_declaration(
            library_file,
            definitions=[library_file.by_id(self.definition)],
            relating_context=project_library,
        )

        tool.Project.update_current_library_page()
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

    if TYPE_CHECKING:
        definition: int

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.library_file.begin_transaction()
        result = self._execute(context)
        IfcStore.library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = tool.Project.get_project_props()
        library_file = IfcStore.library_file
        assert library_file

        element = library_file.by_id(self.definition)
        ifcopenshell.api.project.unassign_declaration(
            library_file,
            definitions=[library_file.by_id(self.definition)],
            relating_context=element.HasContext[0].RelatingContext,
        )

        tool.Project.update_current_library_page()
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
        self.report({"INFO"}, f"Library saved to {IfcStore.library_path}")
        return {"FINISHED"}


class AppendEntireLibrary(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.append_entire_library"
    bl_label = "Append Entire Library"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def _execute(self, context):
        self.file = tool.Ifc.get()
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

    if TYPE_CHECKING:
        query: str

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def _execute(self, context):
        self.file = tool.Ifc.get()
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

    if TYPE_CHECKING:
        definition: int
        prop_index: int
        assume_unique_by_name: bool

    file: ifcopenshell.file

    @classmethod
    def poll(cls, context):
        poll = bool(tool.Ifc.get())
        if not poll:
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
            # NOTE: Non-types are not exposed in UI directly
            # but the code is still used when appending products by query.
            self.import_product_from_ifc(element, context)
            element_type = ifcopenshell.util.element.get_type(element)
            if element_type is not None and tool.Ifc.get_object(element_type) is None:
                self.import_type_from_ifc(element_type, context)
        elif element.is_a("IfcMaterial"):
            self.import_material_from_ifc(element, context)
        elif element.is_a("IfcSurfaceStyle"):
            self.import_presentation_style_from_ifc(element, context)
        else:
            # E.g. other IfcPresentationStyles.
            pass

        try:
            props = tool.Project.get_project_props()
            props.library_elements[self.prop_index].is_appended = True
        except:
            # TODO Remove this terrible code when I refactor this into the core
            pass
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def import_material_from_ifc(self, element: ifcopenshell.entity_instance, context: bpy.types.Context) -> None:
        self.file = tool.Ifc.get()
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
        self.file = tool.Ifc.get()
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
        self.file = tool.Ifc.get()
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
            if tool.Ifc.get_object_by_identifier(material.id()):
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
                    if element2.is_a("IfcSurfaceStyle") and not tool.Ifc.get_object_by_identifier(element2.id()):
                        ifc_importer.create_style(element2)

    def import_material_styles(
        self,
        material: ifcopenshell.entity_instance,
        ifc_importer: import_ifc.IfcImporter,
    ) -> None:
        if not material.HasRepresentation:
            return
        for element in self.file.traverse(material.HasRepresentation[0]):
            if element.is_a("IfcSurfaceStyle") and not tool.Ifc.get_object_by_identifier(element.id()):
                ifc_importer.create_style(element)


class EditProjectLibrary(bpy.types.Operator):
    bl_idname = "bim.edit_project_library"
    bl_label = "Edit Project Library"
    bl_description = "Apply changes for currently edited library."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        library_file = IfcStore.library_file
        assert library_file
        library_file.begin_transaction()
        result = self._execute(context)
        library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = tool.Project.get_project_props()
        library_file = IfcStore.library_file
        assert library_file
        project_library = library_file.by_id(props.editing_project_library_id)
        attributes = bonsai.bim.helper.export_attributes(props.project_library_attributes)
        ifcopenshell.api.attribute.edit_attributes(library_file, project_library, attributes)

        # Update parent library.
        previous_parent_library = tool.Project.get_parent_library(project_library)
        new_parent_library = library_file.by_id(int(props.parent_library))
        if previous_parent_library != new_parent_library:
            if previous_parent_library is None:
                # Edited library was a root in a library-only file; nest it under the new parent.
                ifcopenshell.api.nest.assign_object(library_file, [project_library], new_parent_library)
            elif previous_parent_library.is_a("IfcProject"):
                # Then new one is IfcProjectLibrary.
                ifcopenshell.api.nest.assign_object(library_file, [project_library], new_parent_library)
            else:  # Previous is IfcProjectLibrary.
                ifcopenshell.api.nest.unassign_object(library_file, [project_library])
                # If new one is IfcProject, then it's already assigned by default.
                if new_parent_library.is_a("IfcProjectLibrary"):
                    ifcopenshell.api.nest.assign_object(library_file, [project_library], new_parent_library)

        props.is_editing_project_library = False
        bpy.ops.bim.refresh_library()
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.library_file.undo()

    def commit(self, data):
        IfcStore.library_file.redo()


class AddProjectLibrary(bpy.types.Operator):
    bl_idname = "bim.add_project_library"
    bl_label = "Add Project Library"
    bl_description = "Add new IfcProjectLibrary to the currently selected library."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        library_file = IfcStore.library_file
        assert library_file
        library_file.begin_transaction()
        result = self._execute(context)
        library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = tool.Project.get_project_props()
        library_file = IfcStore.library_file
        assert library_file
        root_context = tool.Project.get_root_context(library_file)
        project_library = ifcopenshell.api.root.create_entity(library_file, "IfcProjectLibrary")
        if root_context.is_a("IfcProject"):
            ifcopenshell.api.project.assign_declaration(library_file, [project_library], root_context)
        else:
            ifcopenshell.api.nest.assign_object(library_file, [project_library], root_context)
        ProjectLibraryData.load()  # Update enum.
        props.selected_project_library = str(project_library.id())
        props.is_editing_project_library = True
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.library_file.undo()

    def commit(self, data):
        IfcStore.library_file.redo()


class RemoveProjectLibrary(bpy.types.Operator):
    bl_idname = "bim.remove_project_library"
    bl_label = "Remove Project Library"
    bl_description = "Remove the currently selected IfcProjectLibrary."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        library_file = IfcStore.library_file
        assert library_file
        library_file.begin_transaction()
        result = self._execute(context)
        library_file.end_transaction()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        props = tool.Project.get_project_props()
        library_file = IfcStore.library_file
        assert library_file

        project_library = library_file.by_id(int(props.selected_project_library))
        tool.Project.remove_project_library(project_library)

        ProjectLibraryData.load()  # Update enum.
        enum_len = len(ProjectLibraryData.data["project_libraries_enum"])
        if props.is_property_set("selected_project_library"):
            props["selected_project_library"] = min(enum_len - 1, props["selected_project_library"])
        bpy.ops.bim.refresh_library()
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.library_file.undo()

    def commit(self, data):
        IfcStore.library_file.redo()


class EnableEditingHeader(bpy.types.Operator):
    bl_idname = "bim.enable_editing_header"
    bl_label = "Enable Editing Header"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Edit the IFC header file such as Author, Organization, ..."

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Project.get_project_props()
        props.is_editing = True
        header_data = tool.Project.get_header_data()
        props.load_header_data(header_data)
        return {"FINISHED"}


class EditHeader(bpy.types.Operator):
    bl_idname = "bim.edit_header"
    bl_label = "Edit Header"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Save header information"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def execute(self, context):
        # NOTE: Though header entities are now generic `entity_instance`
        # we still have a special undo system in place for this operator
        # since general undo system tracks only elements with ids != 0.
        IfcStore.begin_transaction(self)
        self.transaction_data = {}
        self.transaction_data["old"] = self.record_state()
        result = self._execute(context)
        self.transaction_data["new"] = self.record_state()
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        bonsai.bim.handler.refresh_ui_data()
        return result

    def _execute(self, context):
        self.file = tool.Ifc.get()
        props = tool.Project.get_project_props()
        props.is_editing = True

        self.file.header.file_description.description = (f"ViewDefinition[{props.mvd}]",)
        self.file.header.file_name.author = (props.author_name, props.author_email)
        self.file.header.file_name.organization = (props.organisation_name, props.organisation_email)
        self.file.header.file_name.authorization = props.authorisation
        bpy.ops.bim.disable_editing_header()
        return {"FINISHED"}

    def record_state(self):
        self.file = tool.Ifc.get()
        return {
            "description": self.file.header.file_description.description,
            "author": self.file.header.file_name.author,
            "organisation": self.file.header.file_name.organization,
            "authorisation": self.file.header.file_name.authorization,
        }

    def rollback(self, data):
        file = tool.Ifc.get()
        file.header.file_description.description = data["old"]["description"]
        file.header.file_name.author = data["old"]["author"]
        file.header.file_name.organization = data["old"]["organisation"]
        file.header.file_name.authorization = data["old"]["authorisation"]

    def commit(self, data):
        file = tool.Ifc.get()
        file.header.file_description.description = data["new"]["description"]
        file.header.file_name.author = data["new"]["author"]
        file.header.file_name.organization = data["new"]["organisation"]
        file.header.file_name.authorization = data["new"]["authorisation"]


class DisableEditingHeader(bpy.types.Operator):
    bl_idname = "bim.disable_editing_header"
    bl_label = "Disable Editing Header"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Cancel unsaved header information"

    def execute(self, context):
        props = tool.Project.get_project_props()
        props.is_editing = False
        return {"FINISHED"}


class LoadProject(bpy.types.Operator, IFCFileSelector, ImportHelper):
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
    skip_autosave_recovery: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})
    use_detailed_tooltip: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    filename_ext = ".ifc"
    skip_recent: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    if TYPE_CHECKING:
        filepath: str
        filter_glob: str
        is_advanced: bool
        use_relative_path: bool
        should_start_fresh_session: bool
        import_without_ifc_data: bool
        skip_autosave_recovery: bool
        use_detailed_tooltip: bool

    @classmethod
    def description(cls, context, properties):
        tooltip = cls.bl_description
        if not properties.use_detailed_tooltip:
            return tooltip

        filepath = properties.filepath
        if not filepath:
            return tooltip
        filepath = Path(filepath)
        tooltip += ".\n"
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

    def check_autosave_recovery(self, context: bpy.types.Context) -> bool:
        if self.skip_autosave_recovery:
            return False
        autosaved_filepath = tool.Autosave.get_newer_autosaved_path(self.get_filepath_abs())
        if not autosaved_filepath:
            return False
        # Fire-and-forget: don't propagate this popup's own RUNNING_MODAL
        # return value up as if *this* operator were running modally too -
        # we never call modal_handler_add() on ourselves, so the window
        # manager would be left tracking a modal operator with no handler,
        # corrupting its operator bookkeeping until it crashes later when
        # the (real) popup modal handler is closed.
        bpy.ops.bim.load_autosaved_recovery_popup(
            "INVOKE_DEFAULT",
            original_filepath=str(self.get_filepath_abs()),
            autosaved_filepath=autosaved_filepath,
            is_advanced=self.is_advanced,
            use_relative_path=self.use_relative_path,
            should_start_fresh_session=self.should_start_fresh_session,
            import_without_ifc_data=self.import_without_ifc_data,
        )
        return True

    def execute(self, context):
        if self.check_autosave_recovery(context):
            return {"FINISHED"}

        if (
            tool.Blender.get_addon_preferences().save_metadata_blend_file
            and self.should_start_fresh_session
            and not self.is_advanced
        ):
            filepath = self.get_filepath()

            # First, load the IFC file temporarily to check for metadata document
            temp_ifc = None
            has_metadata_doc = False
            try:
                temp_ifc = ifcopenshell.open(str(filepath))
                for doc in temp_ifc.by_type("IfcDocumentInformation"):
                    if getattr(doc, "Scope", None) == "BLEND_METADATA":
                        has_metadata_doc = True
                        break
            except:
                pass
            finally:
                temp_ifc = None

            if has_metadata_doc:
                suffix = tool.Blender.get_addon_preferences().metadata_blend_file_suffix
                if str(filepath).lower().endswith(".ifc"):
                    metadata_path = Path(str(filepath)[:-4] + suffix)
                else:
                    metadata_path = Path(str(filepath) + suffix)
                if metadata_path.exists() and metadata_path.is_file():
                    try:
                        bpy.ops.bim.load_blend_metadata_and_ifc(filepath=filepath)
                        self.report({"INFO"}, f"Loaded metadata file: {metadata_path.name}")
                        return {"FINISHED"}
                    except Exception as e:
                        self.report({"WARNING"}, f"Failed to load metadata file, using regular load: {e}")

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

    def finish_loading_project(self, context: bpy.types.Context) -> set["rna_enums.OperatorReturnItems"]:
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

            tool.Ifc.set_path(filepath)
            if not tool.Ifc.get():
                self.report(
                    {"ERROR"},
                    f"Error loading IFC file from filepath '{filepath}'. See logs above in the system console for the details.",
                )
                return {"CANCELLED"}
            if not tool.Ifc.get().by_type("IfcProject"):
                self.report(
                    {"ERROR"},
                    "This file contains no IfcProject. It is likely an IFC project library — "
                    "load it via Project Setup → Project Library → Select Library File instead.",
                )
                IfcStore.purge()
                return {"CANCELLED"}
            props = tool.Project.get_project_props()
            props.is_loading = True
            props.total_elements = len(tool.Ifc.get().by_type("IfcElement"))
            props.use_relative_project_path = self.use_relative_path

            metadata_doc = tool.Project.get_metadata_document_information()
            props.should_save_metadata_for_this_file = metadata_doc is not None

            tool.Blender.register_toolbar()
            if not self.skip_recent:
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
        tool.Autosave.reset_timer()
        return {"FINISHED"}

    def invoke(self, context, event):
        if self.filepath:
            if self.check_autosave_recovery(context):
                return {"FINISHED"}
            return self.execute(context)
        return ImportHelper.invoke(self, context, event)

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
        props = tool.Blender.get_bim_props()
        if not props.ifc_file:
            cls.poll_message_set("IFC project need to be loaded and saved on the disk.")
            return False
        return True

    def execute(self, context):
        props = tool.Blender.get_bim_props()
        bpy.ops.bim.load_project(should_start_fresh_session=True, filepath=props.ifc_file)
        return {"FINISHED"}


class LoadProjectElements(bpy.types.Operator):
    bl_idname = "bim.load_project_elements"
    bl_label = "Load Project Elements"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = tool.Project.get_project_props()
        self.file = tool.Ifc.get()
        start = time.time()
        logger = logging.getLogger("ImportIFC")
        path_log = tool.Blender.get_data_dir_path("process.log")
        if not os.access(path_log.parent, os.W_OK):
            path_log = os.path.join(
                tempfile.mkdtemp(dir=tool.Blender.get_addon_preferences().tmp_dir or None), "process.log"
            )
        logging.basicConfig(
            filename=path_log,
            filemode="a",
            level=logging.DEBUG,
        )
        props = tool.Blender.get_bim_props()
        settings = import_ifc.IfcImportSettings.factory(context, props.ifc_file, logger)
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
        props = tool.Project.get_project_props()
        props.is_loading = False

        # Stash elements the kernel skipped opening cuts on (HasOpenings > void_limit).
        # The Project panel banner offers the user a one-click recut.
        props.pending_opening_recut.clear()
        if ifc_importer.gross_elements:
            for element in ifc_importer.gross_elements:
                item = props.pending_opening_recut.add()
                item.ifc_definition_id = element.id()
            self.report(
                {"WARNING"},
                f"{len(ifc_importer.gross_elements)} element(s) had too many openings and were loaded without cuts. "
                f"Apply manually from the Project panel.",
            )

        props.pending_array_repair.clear()
        if ifc_importer.broken_arrays:
            for element in ifc_importer.broken_arrays:
                item = props.pending_array_repair.add()
                item.ifc_definition_id = element.id()
            self.report(
                {"WARNING"},
                f"{len(ifc_importer.broken_arrays)} array parent(s) reference missing child GUIDs. "
                f"Inspect from the Project panel.",
            )

        tool.Project.load_default_thumbnails()
        tool.Project.set_default_context()
        tool.Project.set_default_modeling_dimensions()
        tool.Root.reload_grid_decorator()
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def get_decomposition_elements(self) -> set[ifcopenshell.entity_instance]:
        containers: set[ifcopenshell.entity_instance] = set()
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
        elements: set[ifcopenshell.entity_instance] = set()
        for container in containers:
            for rel in container.ContainsElements:
                elements.update(rel.RelatedElements)
        self.append_decomposed_elements(elements)
        return elements

    def append_decomposed_elements(self, elements: set[ifcopenshell.entity_instance]) -> None:
        decomposed_elements: set[ifcopenshell.entity_instance] = set()
        for element in elements:
            if element.IsDecomposedBy:
                for subelement in element.IsDecomposedBy[0].RelatedObjects:
                    decomposed_elements.add(subelement)
            # IfcSurfaceFeature (e.g. road markings) adhere to a host element
            # via IfcRelAdheresToElement, a [1:1] hierarchical relationship in
            # the same family as aggregation, containment and nesting (IFC4.3).
            for rel in getattr(element, "HasSurfaceFeatures", ()):
                decomposed_elements.update(rel.RelatedSurfaceFeatures)
        if decomposed_elements:
            self.append_decomposed_elements(decomposed_elements)
        elements.update(decomposed_elements)

    def get_ifc_class_elements(self) -> set[ifcopenshell.entity_instance]:
        elements: set[ifcopenshell.entity_instance] = set()
        for filter_category in self.props.filter_categories:
            if not filter_category.is_selected:
                continue
            elements.update(self.file.by_type(filter_category.name, include_subtypes=False))
        return elements

    def get_ifc_type_elements(self) -> set[ifcopenshell.entity_instance]:
        elements: set[ifcopenshell.entity_instance] = set()
        for filter_category in self.props.filter_categories:
            if not filter_category.is_selected:
                continue
            elements.update(ifcopenshell.util.element.get_types(self.file.by_id(filter_category.ifc_definition_id)))
        return elements

    def get_whitelist_elements(self) -> set[ifcopenshell.entity_instance]:
        return set(ifcopenshell.util.selector.filter_elements(self.file, self.props.filter_query))

    def get_blacklist_elements(self) -> set[ifcopenshell.entity_instance]:
        return set(self.file.by_type("IfcElement")) - set(
            ifcopenshell.util.selector.filter_elements(self.file, self.props.filter_query)
        )


class ToggleFilterCategories(bpy.types.Operator):
    bl_idname = "bim.toggle_filter_categories"
    bl_label = "Toggle Filter Categories"
    bl_options = {"REGISTER", "UNDO"}
    should_select: bpy.props.BoolProperty(name="Should Select", default=True)

    if TYPE_CHECKING:
        should_select: bool

    def execute(self, context):
        props = tool.Project.get_project_props()
        for filter_category in props.filter_categories:
            filter_category.is_selected = self.should_select
        return {"FINISHED"}


class LinkIfc(bpy.types.Operator, ImportHelper, tool.Ifc.Operator):
    bl_idname = "bim.link_ifc"
    bl_label = "Link IFC"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reference in a read-only IFC model in the background"

    files: bpy.props.CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path",
        description="Whether to store linked model path relative to the currently opened IFC file.",
        default=False,
    )
    use_cache: bpy.props.BoolProperty(name="Use Cache", default=True)
    query: bpy.props.StringProperty(
        name="Query",
        description=(
            "Custom selector query to use to load element from a linked model. E.g. 'IfcElement'.\n\n"
            "Default query - IfcElement, but excluding IfcProxy, IfcSpatialStructureElement, IfcSpatialElement, IfcFeatureElement."
        ),
    )

    filename_ext = ".ifc"

    if TYPE_CHECKING:
        filepath: str
        files: list[bpy.types.OperatorFileListElement]
        directory: str
        filter_glob: str
        use_relative_path: bool
        use_cache: bool
        query: str

    def draw(self, context):
        assert self.layout
        pprops = tool.Project.get_project_props()
        row = self.layout.row()
        row.prop(self, "use_relative_path")
        row = self.layout.row()
        row.prop(self, "use_cache")
        row = self.layout.row()
        row.label(text="False Origin Mode:")
        row = self.layout.row()
        row.prop(pprops, "false_origin_mode", text="")
        if pprops.false_origin_mode == "MANUAL":
            row = self.layout.row()
            row.prop(pprops, "false_origin")
            row = self.layout.row()
            row.prop(pprops, "project_north")
        self.layout.prop(self, "query", placeholder="IfcElement")

    def _execute(self, context):
        start = time.time()
        files = [f.name for f in self.files] if self.files else [self.filepath]

        if not files or all(not f or not f.strip() for f in files):
            self.report({"ERROR"}, "No file selected")
            return {"CANCELLED"}

        existing_links = tool.Project.get_linked_models_documents() if tool.Ifc.get() else {}
        for filename in files:
            if not filename or not filename.strip():
                continue
            filepath = Path(self.directory) / filename
            if bpy.data.filepath and filepath.samefile(bpy.data.filepath):
                self.report({"INFO"}, "Can't link the current .blend file")
                continue
            props = tool.Project.get_project_props()
            filepath = tool.Ifc.get_uri(filepath, use_relative_path=self.use_relative_path)

            new = props.links.add()
            if tool.Ifc.get():
                if not (document := existing_links.get(filepath)):
                    document = ifcopenshell.api.document.add_information(tool.Ifc.get())
                    document.Name = Path(filepath).name
                    document.Scope = "LINKED_MODEL"
                reference = ifcopenshell.api.document.add_reference(tool.Ifc.get(), information=document)
                reference[1] = ",".join([str(o) for o in np.eye(4).flatten().tolist()])
                reference.Location = filepath.replace("\\", "/")
                new.ifc_definition_id = reference.id()
            new.name = filepath
            new.filepath = filepath
            new.query = self.query
            bpy.ops.bim.load_link(link_index=-1, use_cache=self.use_cache, query=self.query)


class UnlinkIfc(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unlink_ifc"
    bl_label = "Unlink IFC"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the selected file from the link list"

    link_index: bpy.props.IntProperty(name="Link Index")

    if TYPE_CHECKING:
        link_index: int

    def _execute(self, context):
        props = tool.Project.get_project_props()
        link = props.links[self.link_index]
        bpy.ops.bim.unload_link(link_index=self.link_index)
        if tool.Ifc.get():
            reference = tool.Ifc.get().by_id(link.ifc_definition_id)
            document = tool.Document.get_reference_document(reference)
            ifcopenshell.api.document.remove_reference(tool.Ifc.get(), reference)
            if document and not tool.Document.get_document_references(document):
                ifcopenshell.api.document.remove_information(tool.Ifc.get(), document)
        props.links.remove(self.link_index)


class UnloadLink(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unload_link"
    bl_label = "Unload Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unload the selected linked file"

    link_index: bpy.props.IntProperty(name="Link Index")

    if TYPE_CHECKING:
        link_index: int

    def _execute(self, context):
        link = tool.Project.get_project_props().links[self.link_index]
        if obj := tool.Project.get_link_empty_handle(link):
            collection = obj.instance_collection
            library = collection.library
            tool.Ifc.unlink(obj=obj)
            bpy.data.objects.remove(obj)
            if collection.users == 0:
                bpy.data.collections.remove(collection)
            if not len([c for c in bpy.data.collections if c.library == library]):
                bpy.data.libraries.remove(library)
        link.is_loaded = False
        ProjectDecorator.uninstall()


class LoadLink(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_link"
    bl_label = "Load Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Load the selected file"

    link_index: bpy.props.IntProperty(name="Link Index")
    use_cache: bpy.props.BoolProperty(name="Use Cache", default=True)
    query: bpy.props.StringProperty()

    if TYPE_CHECKING:
        link_index: int
        use_cache: bool
        query: str

    def _execute(self, context):
        self.link = tool.Project.get_project_props().links[self.link_index]
        # Fall back to the Link's stored query so callers that omit it
        # still replay the filter the link was created with.
        if not self.query and self.link.query:
            self.query = self.link.query
        filepath = Path(tool.Ifc.resolve_uri(self.link.filepath))
        if not filepath.exists():
            self.report({"ERROR"}, f"File does not exist: '{filepath}'")
            return {"CANCELLED"}
        self.filepath_ = filepath
        if filepath.suffix.lower().endswith(".ifc"):
            return self.link_ifc()

    def link_blend(self, filepath: Path) -> None:
        with bpy.data.libraries.load(str(filepath), link=True) as (data_from, data_to):
            data_to.collections = [c for c in data_from.collections if "IfcProject" in c]

        # Find the linked collection
        for collection in bpy.data.collections:
            if not collection.library or Path(collection.library.filepath) != filepath:
                continue
            # Create unique empty instance for this link
            empty_name = collection.name
            empty = bpy.data.objects.new(empty_name, None)
            empty.instance_type = "COLLECTION"
            empty.instance_collection = collection
            empty.matrix_world = tool.Project.calculate_link_matrix(self.link)

            tool.Project.set_link_empty_handle(self.link, empty)
            assert bpy.context.scene
            bpy.context.scene.collection.objects.link(empty)
            self.link.is_loaded = True
            if tool.Ifc.get():  # For non-IFC projects, locking has no meaning
                tool.Geometry.lock_object(empty)
            tool.Blender.select_and_activate_single_object(bpy.context, empty)
            break
        else:
            print(f"WARNING: No IfcProject collection found in {filepath}")
            self.link.is_loaded = False

    def link_ifc(self) -> Union[set[str], None]:
        blend_filepath = self.filepath_.with_suffix(".ifc.cache.blend")
        h5_filepath = self.filepath_.with_suffix(".ifc.cache.h5")
        json_filepath = self.filepath_.with_suffix(".ifc.cache.json")

        def should_clear_cache() -> bool:
            if not self.use_cache:
                return True
            if not blend_filepath.exists():
                return False
            data = json.loads(json_filepath.read_text())
            # Empty 'query' - model loaded without custom query.
            # Missing 'query' - model was loaded before custom queries were introduced in Bonsai.
            query = data.get("query", "")
            return query != self.query

        if should_clear_cache():
            os.remove(blend_filepath)

        if not blend_filepath.exists():
            pprops = tool.Project.get_project_props()
            gprops = tool.Georeference.get_georeference_props()

            code = f"""
import bpy
import sys

def run():
    import bonsai.tool as tool
    gprops = tool.Georeference.get_georeference_props()
    # Our model origin becomes their host model origin
    gprops.has_blender_offset = {gprops.has_blender_offset}
    gprops.blender_offset_x = "{gprops.blender_offset_x}"
    gprops.blender_offset_y = "{gprops.blender_offset_y}"
    gprops.blender_offset_z = "{gprops.blender_offset_z}"
    gprops.blender_x_axis_abscissa = "{gprops.blender_x_axis_abscissa}"
    gprops.blender_x_axis_ordinate = "{gprops.blender_x_axis_ordinate}"
    pprops = tool.Project.get_project_props()
    pprops.distance_limit = {pprops.distance_limit}
    pprops.false_origin_mode = "{pprops.false_origin_mode}"
    pprops.false_origin = "{pprops.false_origin}"
    pprops.project_north = "{pprops.project_north}"
    # Use absolute path to be safe from cwd changes.
    try:
        bpy.ops.bim.load_linked_project(filepath=r"{str(self.filepath_)}", query={repr(self.query)})
    except RuntimeError as e:
        # Operator failed (returned CANCELLED with error report)
        print(f"Failed to load linked project: {{e}}")
        sys.exit(1)
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
            run = subprocess.run(
                [
                    bpy.app.binary_path,
                    "-b",
                    # Explicitly ask to enable Bonsai for this Blender instance
                    # as Bonsai may be just enabled and user preferences are not saved.
                    "--addons",
                    tool.Blender.get_blender_addon_package_name(),
                    "--python",
                    temp_file.name,
                    "--python-exit-code",
                    "1",
                ]
            )
            if run.returncode == 1:
                print("An error occurred while processing your IFC.")
                if not blend_filepath.exists() or blend_filepath.stat().st_mtime < t:
                    return {"CANCELLED"}

        self.set_model_origin_from_link()
        self.set_georeferencing_indicator()
        self.link_blend(blend_filepath)

    def set_model_origin_from_link(self) -> None:
        if tool.Ifc.get():
            return  # The current model's coordinates always take priority.

        if len(tool.Project.get_project_props().links) > 1:
            return  # Only the first link sets the origin

        json_filepath = self.filepath_.with_suffix(".ifc.cache.json")
        if not json_filepath.exists():
            return

        with open(json_filepath, "r") as f:
            data = json.load(f)

        gprops = tool.Georeference.get_georeference_props()
        for prop in ("model_origin", "model_origin_si", "model_project_north"):
            if (value := data.get(prop, None)) is not None:
                setattr(gprops, prop, value)

    def set_georeferencing_indicator(self) -> None:
        if not tool.Ifc.get():
            self.link.georeferenced = "NONE"
            return
        if not (crs_name := (ifcopenshell.util.geolocation.get_crs(tool.Ifc.get()) or {}).get("Name", "")):
            self.link.georeferenced = "NONE"
            return
        reference = tool.Ifc.get().by_id(self.link.ifc_definition_id)
        json_filepath = Path(reference.Location).with_suffix(".ifc.cache.json")
        if not json_filepath.exists():
            self.link.georeferenced = "NONE"
            return
        with open(json_filepath, "r") as f:
            data = json.load(f)
        if not data["model_is_georeferenced"]:
            self.link.georeferenced = "NONE"
        else:
            self.link.georeferenced = "FULL_COMPATIBLE" if crs_name == data["model_crs"] else "NOT_COMPATIBLE"


class ReloadLink(bpy.types.Operator):
    bl_idname = "bim.reload_link"
    bl_label = "Reload Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reload the selected file"

    link_index: bpy.props.IntProperty(name="Link Index")
    query: bpy.props.StringProperty(
        name="Query",
        description=(
            "Custom selector query to use to load element from a linked model. E.g. 'IfcElement'.\n\n"
            "Default query - IfcElement, but excluding IfcProxy, IfcSpatialStructureElement, IfcSpatialElement, IfcFeatureElement."
        ),
    )

    if TYPE_CHECKING:
        link_index: int
        query: str

    def invoke(self, context, event):
        link = tool.Project.get_project_props().links[self.link_index]
        self.query = link.query
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        assert self.layout
        self.layout.prop(self, "query", placeholder="IfcElement")

    def execute(self, context):
        link = tool.Project.get_project_props().links[self.link_index]
        # An unset query means the operator was called without the dialog
        # (e.g. from a script) - preserve the link's stored query instead
        # of overwriting it with the empty default.
        if self.properties.is_property_set("query"):
            link.query = self.query
        bpy.ops.bim.unload_link(link_index=self.link_index)
        return bpy.ops.bim.load_link(link_index=self.link_index, use_cache=False, query=link.query) or {"FINISHED"}


class ToggleLinkSelectability(bpy.types.Operator):
    bl_idname = "bim.toggle_link_selectability"
    bl_label = "Toggle Link Selectability"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle selectability"

    link_index: bpy.props.IntProperty(name="Link Index")

    if TYPE_CHECKING:
        link_index: int

    def execute(self, context):
        props = tool.Project.get_project_props()
        link = props.links[self.link_index]
        self.library_filepath = tool.Blender.ensure_blender_path_is_abs(
            Path(link.filepath).with_suffix(".ifc.cache.blend")
        )
        link.is_selectable = (is_selectable := not link.is_selectable)
        for collection in self.get_linked_collections():
            collection.hide_select = not is_selectable
        if handle := tool.Project.get_link_empty_handle(link):
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

    link_index: bpy.props.IntProperty(name="Link Index")
    mode: bpy.props.EnumProperty(
        name="Visibility Mode",
        items=((i, i, "") for i in ("WIREFRAME", "VISIBLE")),
    )

    if TYPE_CHECKING:
        link_index: int
        mode: Literal["WIREFRAME", "VISIBLE"]

    def execute(self, context):
        props = tool.Project.get_project_props()
        link = props.links[self.link_index]
        self.library_filepath = tool.Blender.ensure_blender_path_is_abs(
            Path(link.filepath).with_suffix(".ifc.cache.blend")
        )
        if self.mode == "WIREFRAME":
            self.toggle_wireframe(link)
        elif self.mode == "VISIBLE":
            self.toggle_visibility(link)
        return {"FINISHED"}

    def toggle_wireframe(self, link: "Link") -> None:
        linked_collections = self.get_linked_collections()

        link.is_wireframe = not link.is_wireframe
        display_type = "WIRE" if link.is_wireframe else "TEXTURED"
        for collection in linked_collections:
            objs = filter(lambda obj: "IfcOpeningElement" not in obj.name, collection.all_objects)
            for obj in objs:
                obj.display_type = display_type
        if handle := tool.Project.get_link_empty_handle(link):
            handle.display_type = display_type

    def toggle_visibility(self, link: "Link") -> None:
        linked_collections = self.get_linked_collections()

        link.is_hidden = (is_hidden := not link.is_hidden)
        layer_collections = tool.Blender.get_layer_collections_mapping(linked_collections)
        for layer_collection in layer_collections.values():
            layer_collection.exclude = is_hidden
        if handle := tool.Project.get_link_empty_handle(link):
            handle.hide_set(is_hidden)

    def get_linked_collections(self) -> list[bpy.types.Collection]:
        return [
            c
            for c in bpy.data.collections
            if "IfcProject" in c.name and c.library and Path(c.library.filepath) == self.library_filepath
        ]


class EnableEditingLink(bpy.types.Operator):
    bl_idname = "bim.enable_editing_link"
    bl_label = "Enable Editing Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing link location"

    def execute(self, context):
        link = tool.Project.get_project_props().active_link
        assert link
        link.is_editing = True
        obj = tool.Project.get_link_empty_handle(link)
        assert obj
        tool.Geometry.unlock_object(obj)
        return {"FINISHED"}


class DisableEditingLink(bpy.types.Operator):
    bl_idname = "bim.disable_editing_link"
    bl_label = "Disable Editing Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Disable editing link and restore to previously saved location"

    def execute(self, context):
        link = tool.Project.get_project_props().active_link
        assert link
        link.is_editing = False
        obj = tool.Project.get_link_empty_handle(link)
        assert obj
        obj.matrix_world = tool.Project.calculate_link_matrix(link)
        tool.Geometry.lock_object(obj)
        return {"FINISHED"}


class EditLink(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_link"
    bl_label = "Edit Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Disable editing link and restore to previously saved location"

    def _execute(self, context):
        link = tool.Project.get_project_props().active_link
        assert link
        link.is_editing = False
        obj = tool.Project.get_link_empty_handle(link)
        assert obj
        new_obj_matrix = obj.matrix_world

        filepath = Path(tool.Ifc.resolve_uri(link.filepath))
        with open(filepath.with_suffix(".ifc.cache.json"), "r") as f:
            metadata = json.load(f)

        rot = ifcopenshell.util.shape_builder.np_rotation_matrix(
            radians(-float(metadata["model_project_north"])), 4, "Z"
        )
        global_matrix = rot @ np.eye(4)
        global_matrix[:, 3][:3] = [float(o) for o in metadata["model_origin_si"].split(",")]

        gprops = tool.Georeference.get_georeference_props()
        rot = ifcopenshell.util.shape_builder.np_rotation_matrix(radians(-float(gprops.model_project_north)), 4, "Z")
        local_matrix = rot @ np.eye(4)
        local_matrix[:, 3][:3] = [float(o) for o in gprops.model_origin_si.split(",")]

        # obj_matrix is typically calculated as:
        # obj_matrix = np.linalg.inv(local_matrix) @ transformation @ global_matrix
        identity_blender_matrix = np.linalg.inv(local_matrix) @ global_matrix
        if np.allclose(np.array(new_obj_matrix), identity_blender_matrix, atol=1e-5):
            link.has_transformation = False
            transformation = ",".join(map(str, np.eye(4).reshape(-1)))
        else:
            transformed_global_matrix = local_matrix @ np.array(new_obj_matrix)
            transformation = transformed_global_matrix @ np.linalg.inv(global_matrix)
            link.has_transformation = True
            transformation = ",".join(map(str, transformation.reshape(-1)))

        if tool.Ifc.get():
            reference = tool.Ifc.get().by_id(link.ifc_definition_id)
            reference[1] = transformation
        else:
            link.transformation = transformation

        obj.matrix_world = tool.Project.calculate_link_matrix(link)
        tool.Geometry.lock_object(obj)


class SelectLinkHandle(bpy.types.Operator):
    bl_idname = "bim.select_link_handle"
    bl_label = "Select Link Handle"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select link empty object handle"

    link_index: bpy.props.IntProperty(name="Link Index")

    if TYPE_CHECKING:
        link_index: int

    def execute(self, context):
        props = tool.Project.get_project_props()
        link = props.links[self.link_index]
        handle = tool.Project.get_link_empty_handle(link)
        if not handle:
            self.report({"ERROR"}, "Link has no empty handle (probably it was deleted).")
            return {"CANCELLED"}
        tool.Blender.select_and_activate_single_object(context, handle)
        return {"FINISHED"}


class SelectLinkedModelElement(bpy.types.Operator):
    bl_idname = "bim.select_linked_model_element"
    bl_label = "Select Linked Model Element"
    bl_options = {"REGISTER"}
    bl_description = "Select an element in the currently selected linked model by providing GlobalId."

    guid: bpy.props.StringProperty(name="GlobalId")

    if TYPE_CHECKING:
        guid: str

    def invoke(self, context, event):
        assert context.window_manager
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        guid = self.guid.strip()
        if not guid:
            self.report({"ERROR"}, "GlobalId is not provided.")
            return {"CANCELLED"}

        props = tool.Project.get_project_props()
        active_link = props.active_link
        assert active_link is not None
        assert active_link.is_loaded

        guid_obj = tool.Project.Link.get_obj_by_guid(active_link, guid)
        if not guid_obj:
            filepath = active_link.filepath
            self.report({"INFO"}, f"Element with GlobalId '{guid}' not found in the linked model at '{filepath}'.")
            return {"CANCELLED"}

        tool.Project.Link.select_linked_element(context, guid_obj, guid)
        self.report({"INFO"}, f"Element with GlobalId '{guid}' is selected.")
        return {"FINISHED"}


class ExportIFC(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.save_project"
    bl_label = "Save IFC"
    # Prevents crash on Blender 4.4.0.
    bl_description = "Save active IFC file by the provided filepath."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    supported_filexts = (".ifc", ".ifczip", ".ifcjson")
    filter_glob: bpy.props.StringProperty(default=";".join(f"*{ext}" for ext in supported_filexts), options={"HIDDEN"})
    json_version: bpy.props.EnumProperty(items=[("4", "4", ""), ("5a", "5a", "")], name="IFC JSON Version")
    json_compact: bpy.props.BoolProperty(name="Export Compact IFCJSON", default=False)
    should_save_as: bpy.props.BoolProperty(name="Should Save As", default=False, options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)
    skip_recent: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    if TYPE_CHECKING:
        filter_glob: str
        json_version: str
        json_compact: bool
        should_save_as: bool
        use_relative_path: bool

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
        layout.label(text=",".join(self.supported_filexts))

    def invoke(self, context, event):
        if not tool.Ifc.get():
            bpy.ops.wm.save_mainfile("INVOKE_DEFAULT")
            return {"FINISHED"}

        self.use_relative_path = tool.Project.get_project_props().use_relative_project_path
        props = tool.Blender.get_bim_props()
        filepath = props.ifc_file
        if not filepath or self.should_save_as:
            return ExportHelper.invoke(self, context, event)
        self.filepath = str(tool.Blender.ensure_blender_path_is_abs(Path(filepath)))
        return self.execute(context)

    def check(self, context):
        # ExportHelper is automatically adjusting suffix to `filename_ext`.
        filepath = Path(self.filepath)
        suffix = filepath.suffix.lower()
        if suffix != self.filename_ext and suffix in self.supported_filexts:
            self.filename_ext = suffix
        return ExportHelper.check(self, context)

    def execute(self, context):
        project_props = tool.Project.get_project_props()
        prefs = tool.Blender.get_addon_preferences()
        project_props.use_relative_project_path = self.use_relative_path
        if prefs.should_disable_undo_on_save:
            old_history_size = tool.Ifc.get().history_size
            old_undo_steps = context.preferences.edit.undo_steps
            tool.Ifc.get().history_size = 0
            context.preferences.edit.undo_steps = 0
        IfcStore.execute_ifc_operator(self, context)
        if prefs.should_disable_undo_on_save:
            tool.Ifc.get().history_size = old_history_size
            context.preferences.edit.undo_steps = old_undo_steps
        return {"FINISHED"}

    def _execute(self, context):
        project_props = tool.Project.get_project_props()
        project_props.use_relative_project_path = self.use_relative_path

        # Fallback if filepath is not set
        if not getattr(self, "filepath", None) or self.filepath.strip() in ("", ".ifc"):
            props = tool.Blender.get_bim_props()
            if props.ifc_file:
                self.filepath = str(tool.Blender.ensure_blender_path_is_abs(Path(props.ifc_file)))
            else:
                self.report({"ERROR"}, "No filepath available for saving.")
                return {"CANCELLED"}

        committed, failed_commits = tool.Parametric.commit_pending_edits()
        # Previews are session-transient — discard rather than commit. Sibling
        # gizmo polls gate on each preview's is_active flag, and a stuck flag
        # persisted through the save would silently hide them on reload.
        preview_base.discard_pending_previews(context.scene)
        # Suffix is appended to the IFC save-success report below so the auto-commit
        # info isn't immediately overwritten by the success message in Blender's
        # status bar (only the latest self.report({"INFO"}, ...) sticks).
        commit_suffix = f" (auto-committed {committed} pending parametric edit(s))" if committed else ""
        if failed_commits:
            names = ", ".join(o.name for o in failed_commits)
            msg = f"Auto-commit failed for {len(failed_commits)} object(s): {names}"
            print(f"Bonsai: {msg} (their drafts are NOT saved to the IFC file).")
            self.report({"ERROR"}, msg)
        start = time.time()
        logger = logging.getLogger("ExportIFC")
        path_log = tool.Blender.get_data_dir_path("process.log")
        if not os.access(path_log.parent, os.W_OK):
            path_log = os.path.join(
                tempfile.mkdtemp(dir=tool.Blender.get_addon_preferences().tmp_dir or None), "process.log"
            )
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
        output_file = Path(output_file).as_posix().replace("\\", "/")

        settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        settings.json_version = self.json_version
        settings.json_compact = self.json_compact

        pprops = tool.Project.get_project_props()
        if tool.Blender.get_addon_preferences().save_metadata_blend_file and pprops.should_save_metadata_for_this_file:
            suffix = tool.Blender.get_addon_preferences().metadata_blend_file_suffix
            if output_file.lower().endswith(".ifc"):
                metadata_filename = os.path.basename(output_file)[:-4] + suffix
            else:
                metadata_filename = os.path.basename(output_file) + suffix

            if not tool.Project.get_metadata_document_information():
                tool.Project.create_metadata_document_information(metadata_filename)
            else:
                tool.Project.update_metadata_document_information(metadata_filename)
        else:
            if not pprops.should_save_metadata_for_this_file:
                tool.Project.remove_metadata_document_information()

        ifc_exporter = export_ifc.IfcExporter(settings)
        print("Starting export")
        settings.logger.info("Starting export")
        ifc_exporter.export()
        settings.logger.info("Export finished in {:.2f} seconds".format(time.time() - start))
        print("Export finished in {:.2f} seconds".format(time.time() - start))
        # New project created in Bonsai should be in recent projects too.
        if not self.skip_recent:
            tool.Project.add_recent_ifc_project(Path(output_file))
        props = tool.Project.get_project_props()
        if props.use_relative_project_path and bpy.data.is_saved:
            output_file = os.path.relpath(output_file, bpy.path.abspath("//"))
        bim_props = tool.Blender.get_bim_props()
        if bim_props.ifc_file != output_file and extension not in ("ifczip", "ifcjson"):
            tool.Ifc.set_path(output_file)
        bim_props.is_dirty = False

        pprops = tool.Project.get_project_props()
        if tool.Blender.get_addon_preferences().save_metadata_blend_file and pprops.should_save_metadata_for_this_file:
            try:
                bpy.ops.bim.save_blend_metadata_file()
                suffix = tool.Blender.get_addon_preferences().metadata_blend_file_suffix
                if output_file.lower().endswith(".ifc"):
                    blendmetadata_path = output_file[:-4] + suffix
                else:
                    blendmetadata_path = output_file + suffix
                self.report(
                    {"INFO"},
                    f'IFC Project "{os.path.basename(output_file)}" And Metadata File Saved to: {os.path.basename(blendmetadata_path)}{commit_suffix}',
                )
            except Exception as e:
                self.report({"ERROR"}, f"Failed to save blend metadata file: {e}")
        else:
            save_blend_file = bool(bpy.data.is_saved and bpy.data.is_dirty and bpy.data.filepath)
            if save_blend_file:
                bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
            self.report(
                {"INFO"},
                f'IFC Project "{os.path.basename(output_file)}" {"" if not save_blend_file else "And Current Blend File Are"} Saved{commit_suffix}',
            )

        bonsai.bim.handler.refresh_ui_data()
        tool.Autosave.reset_timer()

    @classmethod
    def description(cls, context, properties):
        if properties.should_save_as:
            return "Save the IFC file under a new name, or relocate file"
        return "Save the IFC file.  Will save both .IFC/.BLEND files if synced together"


class LoadAutosavedRecoveryPopup(bpy.types.Operator):
    bl_idname = "bim.load_autosaved_recovery_popup"
    bl_label = "Recover Autosaved File"
    bl_options = {"REGISTER", "UNDO"}

    original_filepath: bpy.props.StringProperty(options={"SKIP_SAVE"})
    autosaved_filepath: bpy.props.StringProperty(options={"SKIP_SAVE"})
    is_advanced: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})
    use_relative_path: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})
    should_start_fresh_session: bpy.props.BoolProperty(default=True, options={"SKIP_SAVE"})
    import_without_ifc_data: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.label(text="A newer autosaved copy was found:", icon="INFO")
        layout.label(text=os.path.basename(self.autosaved_filepath))
        layout.separator()
        layout.label(text="Do you want to load the autosaved version instead?")
        layout.label(text="(Cancel will load the original)")

    def invoke(self, context, event):
        # invoke_props_dialog is modal - unlike invoke_popup/popup_menu, it
        # isn't dismissed by the mouse simply leaving its bounds. It always
        # renders both a fixed "Cancel" button and this confirm_text one, so
        # the question is framed as Yes/Cancel rather than adding separate
        # Load buttons on top.
        return context.window_manager.invoke_props_dialog(
            self, width=420, title="Recover Autosaved File", confirm_text="Yes"
        )

    def _load_kwargs(self, filepath: str, skip_recent: bool) -> dict:
        return dict(
            filepath=filepath,
            skip_autosave_recovery=True,  # Prevent infinite loop
            is_advanced=self.is_advanced,
            use_relative_path=self.use_relative_path,
            should_start_fresh_session=self.should_start_fresh_session,
            import_without_ifc_data=self.import_without_ifc_data,
            skip_recent=skip_recent,
        )

    @staticmethod
    def _defer(callback) -> None:
        def on_timer() -> None:
            callback()
            return None

        # bim.load_project (with should_start_fresh_session, our default)
        # calls wm.read_homefile(), which tears down the window
        # manager/screens/regions. Calling that synchronously from this
        # dialog's execute()/cancel() - themselves invoked from deep inside
        # Blender's modal handling for this popup's button click - frees
        # data that the still-on-stack caller dereferences once we return,
        # segfaulting Blender. Deferring by one timer tick runs the reload
        # after the popup's own modal handling has fully unwound. The
        # callback only closes over plain values (not `self`), since the
        # operator instance itself may no longer be valid by the time the
        # timer fires.
        bpy.app.timers.register(on_timer, first_interval=0.0)

    def execute(self, context):
        kwargs = self._load_kwargs(self.autosaved_filepath, skip_recent=True)
        original_filepath = self.original_filepath

        def load_and_repoint() -> None:
            bpy.ops.bim.load_project(**kwargs)
            # Re-point tracking at the original path so future saves write
            # back to it, not "_autosaved.ifc".
            tool.Ifc.set_path(original_filepath)

        self._defer(load_and_repoint)
        return {"FINISHED"}

    def cancel(self, context):
        # Also reached via Escape or a click outside the dialog, not just Cancel.
        kwargs = self._load_kwargs(self.original_filepath, skip_recent=False)
        self._defer(lambda: bpy.ops.bim.load_project(**kwargs))


class AutosavePrompt(bpy.types.Operator):
    bl_idname = "bim.autosave_prompt"
    bl_label = "Autosave Reminder"
    bl_options = set()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(
            self, width=400, confirm_text="Save", title="Autosave Reminder"
        )

    def draw(self, context):
        layout = self.layout
        layout.label(text="The autosave timer has expired.", icon="INFO")
        layout.label(text="Would you like to save your IFC project now?")

    def execute(self, context):
        # Get current IFC path
        props = tool.Blender.get_bim_props()
        current_ifc_path = props.ifc_file

        if not current_ifc_path:
            self.report({"WARNING"}, "No IFC file path set. Please save manually.")
            tool.Autosave.reset_timer()
            return {"CANCELLED"}

        # Call save_project with explicit filepath using EXEC_DEFAULT
        result = bpy.ops.bim.save_project(
            "EXEC_DEFAULT", filepath=current_ifc_path, should_save_as=False, skip_recent=True
        )

        tool.Autosave.reset_timer()
        return result

    def cancel(self, context):
        tool.Autosave.reset_timer()
        return {"CANCELLED"}


class LoadLinkedProject(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.load_linked_project"
    bl_label = "Load Project For Viewing Only"
    bl_description = "Operator is used to load a project .cache.blend to then link it to the IFC file."
    bl_options = {"REGISTER", "UNDO"}

    query: bpy.props.StringProperty()
    """See ``bim.link_ifc``."""

    if TYPE_CHECKING:
        query: str

    file: ifcopenshell.file
    meshes: dict[str, bpy.types.Mesh]
    # Material names is derived from diffuse as in 'r-g-b-a'.
    blender_mats: dict[str, bpy.types.Material]

    def invoke(self, context, event):
        # Invoke is for debugging purposes, users are not intended to use this method really.
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        import multiprocessing

        import ifcpatch

        start = time.time()

        pprops = tool.Project.get_project_props()
        gprops = tool.Georeference.get_georeference_props()

        self.filepath = Path(self.filepath).as_posix()
        print("Processing", self.filepath)

        self.collection = bpy.data.collections.new("IfcProject/" + os.path.basename(self.filepath))

        try:
            self.file = ifcopenshell.open(self.filepath)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to open IFC file: {str(e)}")
            bpy.data.collections.remove(self.collection)
            return {"CANCELLED"}

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

        if self.query:
            self.elements = ifcopenshell.util.selector.filter_elements(self.file, self.query)
        else:
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
            tool.Loader.guess_false_origin(self.file)

        tool.Georeference.set_model_origin()
        self.json_filepath = self.filepath + ".cache.json"
        data = {
            "model_is_georeferenced": gprops.model_is_georeferenced,
            "model_crs": gprops.model_crs,
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
            "query": self.query,
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
            blender_mats: dict[tuple[float, float, float, float], bpy.types.Material] = {}

            default_mat = np.array([[1, 1, 1, 1]], dtype=np.float32)
            chunked_guids: list[str] = []
            chunked_guid_ids: list[int] = []
            chunked_verts: list[np.ndarray] = []
            chunked_faces: list[np.ndarray] = []
            # List of material colors.
            chunked_materials: list[np.ndarray] = []
            # List of material indices for each face.
            chunked_material_ids: list[np.ndarray] = []
            material_offset = 0
            chunk_size = 10000
            # Vertex offset.
            offset = 0

            ci = 0

            def process_chunk() -> None:
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

                # Create object for current chunk.
                self.create_object(
                    np.concatenate(chunked_verts),
                    np.concatenate(chunked_faces),
                    mat_results,
                    midx,
                    chunked_guids,
                    chunked_guid_ids,
                )

            if iterator.initialize():
                while True:  # Main loop.
                    shape = iterator.get()
                    assert isinstance(shape, W.TriangulationElement)
                    results.add(self.file.by_id(shape.id))
                    geometry = shape.geometry

                    # Elements with a lot of geometry benefit from instancing to save memory
                    if ifcopenshell.util.shape.get_faces(geometry).shape[0] > 333:  # 333 tris
                        self.process_occurrence(shape)
                        if not iterator.next():
                            if not chunked_verts:
                                break
                            process_chunk()
                            break  # Break from main loop.
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
                    vs = vs[:, :3].ravel()
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
                        process_chunk()
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
                            process_chunk()
                        break  # Break main loop.
            self.elements -= results

        bpy.context.scene.collection.children.link(self.collection)
        print("Finished", time.time() - start)
        return {"FINISHED"}

    def process_occurrence(self, shape: W.TriangulationElement) -> None:
        element = self.file.by_id(shape.id)

        mat = ifcopenshell.util.shape.get_shape_matrix(shape)

        geometry = shape.geometry
        mesh = self.meshes.get(geometry.id, None)
        if not mesh:
            verts = ifcopenshell.util.shape.get_vertices(geometry)
            material_ids = geometry.material_ids
            mesh = tool.Loader.create_mesh_from_shape(geometry, mesh)

            gprops = tool.Georeference.get_georeference_props()
            if gprops.has_blender_offset and verts.size and tool.Loader.is_point_far_away(verts[0], is_meters=True):
                vert: np.ndarray = verts[0]
                # Shift geometry close to the origin based off that first vert it found
                offset = ifcopenshell.util.shape_builder.np_translation_matrix(-vert)
                mat = offset @ mat

                mesh["has_cartesian_point_offset"] = True
                mesh["cartesian_point_offset"] = ",".join(vert.astype(str))
            else:
                mesh["has_cartesian_point_offset"] = False

            material_to_slot: dict[int, int] = {}
            max_slot_index = 0

            for i, material in enumerate(geometry.materials):
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

            material_index = np.array([(material_to_slot[i] if i != -1 else 0) for i in material_ids], dtype="I")

            mesh.polygons.foreach_set("material_index", material_index)
            mesh.update()

            self.meshes[geometry.id] = mesh

        obj = bpy.data.objects.new(tool.Loader.get_name(element), mesh)
        obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(obj, mat)

        obj["guids"] = [shape.guid]
        obj["guid_ids"] = [len(mesh.polygons)]
        obj["db"] = self.db_filepath
        obj["ifc_filepath"] = self.filepath

        self.collection.objects.link(obj)

    def create_object(
        self,
        verts: np.ndarray,
        faces: np.ndarray,
        materials: list[bpy.types.Material],
        material_ids: np.ndarray,
        guids: list[str],
        guid_ids: list[int],
    ) -> None:
        num_vertices = len(verts) // 3
        if not num_vertices:
            return

        mesh = tool.Loader.create_mesh_from_shape(verts=verts.reshape(-1, 3), faces=faces.reshape(-1, 3))

        for material in materials:
            mesh.materials.append(material)
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
        assert context.area
        return context.area.type == "VIEW_3D"

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        LinksData.linked_data = {}
        props = tool.Project.get_project_props()
        props.queried_obj = None

        assert context.screen
        for area in context.screen.areas:
            if area.type == "PROPERTIES":
                for region in area.regions:
                    if region.type == "WINDOW":
                        region.tag_redraw()
            elif area.type == "VIEW_3D":
                area.tag_redraw()

        assert context.region and context.region_data
        region = context.region
        rv3d = context.region_data
        coord = (self.mouse_x, self.mouse_y)
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        hit, location, normal, face_index, obj, instance_matrix = tool.Blender.ray_cast_scene(
            context, origin, direction
        )
        if not hit:
            self.report({"INFO"}, "No object found.")
            return {"FINISHED"}

        if not tool.Project.Link.is_linked_element(obj):
            self.report({"INFO"}, "Object is not a linked IFC element.")
            return {"FINISHED"}

        guid = tool.Project.Link.get_guid_by_face_index(obj, face_index)
        assert guid is not None
        tool.Project.Link.select_linked_element(context, obj, guid)

        self.report({"INFO"}, f"Loaded data for {guid}")
        ProjectDecorator.install(bpy.context)
        return {"FINISHED"}

    def invoke(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        return self.execute(context)


class HideQueriedLinkedElement(bpy.types.Operator):
    bl_idname = "bim.hide_queried_linked_element"
    bl_label = "Hide Queried Linked Element"
    bl_description = (
        "Hide geometry for currently queried linked element.\n\n"
        "SHIFT+Click (or SHIFT+H in Explore Tool) to hide everything "
        "in the currently selected model, but the queried element.\n"
        "ALT+Click (or ALT+H in Explore Tool) to unhide all geometry for currently selected linked model.\n\n"
        "Known limitation: doesn't work with UNDO."
    )
    bl_options = {"REGISTER", "UNDO"}

    unhide_all: bpy.props.BoolProperty(options={"SKIP_SAVE"})
    hide_all_except: bpy.props.BoolProperty(options={"SKIP_SAVE"})

    if TYPE_CHECKING:
        unhide_all: bool
        hide_all_except: bool

    def invoke(self, context, event):
        self.unhide_all = event.alt
        self.hide_all_except = event.shift
        return self.execute(context)

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Project.get_project_props()

        if self.unhide_all:
            return self.run_unhide_all()

        if self.hide_all_except:
            return self.run_hide_all_except()

        obj = props.queried_obj
        if not obj:
            self.report({"INFO"}, "No object is queried to hide.")
            return {"FINISHED"}
        guid = props.queried_guid
        tool.Project.Link.hide_linked_element(obj, guid)
        tool.Project.Link.deselect_queried_linked_element()

        self.report({"INFO"}, "Queried object is now hidden.")
        return {"FINISHED"}

    def run_unhide_all(self) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Project.get_project_props()
        link = props.active_link
        if not link:
            self.report({"INFO"}, "No linked model is currently selected.")
            return {"FINISHED"}
        tool.Project.Link.unhide_all_elements(link)
        self.report({"INFO"}, "All linked model geometry is unhidden.")
        return {"FINISHED"}

    def run_hide_all_except(self) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Project.get_project_props()
        obj = props.queried_obj
        if not obj:
            self.report({"INFO"}, "No object is queried.")
            return {"FINISHED"}
        link = props.active_link
        if not link:
            self.report({"INFO"}, "No linked model is currently selected.")
            return {"FINISHED"}
        guid = props.queried_guid
        tool.Project.Link.hide_all_elements_except(link, obj, guid)
        self.report({"INFO"}, "All other linked model geometry is now hidden.")
        return {"FINISHED"}


class AppendInspectedLinkedElement(AppendLibraryElement):
    bl_idname = "bim.append_inspected_linked_element"
    bl_label = "Append Inspected Linked Element"
    bl_description = "Append inspected linked element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        from bonsai.bim.module.project.data import LinksData

        props = tool.Project.get_project_props()
        if not LinksData.linked_data:
            self.report({"INFO"}, "No linked element found.")
            return {"CANCELLED"}

        guid = LinksData.linked_data["attributes"].get("GlobalId")
        if guid is None:
            self.report({"INFO"}, "Cannot find Global Id for element.")
            return {"CANCELLED"}

        queried_obj = props.queried_obj
        assert queried_obj

        ifc_file = tool.Ifc.get()
        linked_ifc_file: ifcopenshell.file
        linked_ifc_file = ifcopenshell.open(queried_obj["ifc_filepath"])
        if ifc_file.schema_identifier != linked_ifc_file.schema_identifier:
            self.report(
                {"ERROR"},
                f"Schema of linked file ({linked_ifc_file.schema_identifier}) is not compatible with the current IFC file ({ifc_file.schema_identifier}).",
            )
            return {"CANCELLED"}

        element_to_append = linked_ifc_file.by_guid(guid)
        element = ifcopenshell.api.project.append_asset(
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_view_corners = None
        self.total_mousemoves = 0
        self.cullable_objects = []

    def modal(self, context, event) -> set["rna_enums.OperatorReturnItems"]:
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

    def is_view_changed(self, context: bpy.types.Context) -> bool:
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

    def is_object_in_view(self, obj: bpy.types.Object, context: bpy.types.Context, camera_position: Vector) -> bool:
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

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set["rna_enums.OperatorReturnItems"]:
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_planes = 0
        self.camera = None

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        should_refresh = False
        props = tool.Project.get_project_props()

        self.clean_deleted_planes(context)

        for clipping_plane in props.clipping_planes:
            if clipping_plane.obj and tool.Ifc.is_moved(clipping_plane.obj, ifc_only=False):
                should_refresh = True
                break

        if (camera := context.scene.camera) and camera.visible_get() and tool.Ifc.get_entity(camera):
            camera = context.scene.camera
        else:
            camera = None

        if self.camera != camera:
            should_refresh = True
        elif self.camera and tool.Ifc.is_moved(self.camera, ifc_only=False):
            should_refresh = True

        total_planes = len(props.clipping_planes)
        if should_refresh or total_planes != self.total_planes:
            self.camera = camera
            self.refresh_clipping_planes(context)
            for clipping_plane in props.clipping_planes:
                if clipping_plane.obj:
                    tool.Geometry.record_object_position(clipping_plane.obj)
            self.total_planes = total_planes
        return {"PASS_THROUGH"}

    def clean_deleted_planes(self, context: bpy.types.Context) -> None:
        props = tool.Project.get_project_props()
        while True:
            for i, clipping_plane in enumerate(props.clipping_planes):
                if clipping_plane.obj:
                    try:
                        clipping_plane.obj.name
                    except:
                        props.clipping_planes.remove(i)
                        break
                else:
                    props.clipping_planes.remove(i)
                    break
            else:
                break

    def refresh_clipping_planes(self, context):
        from itertools import cycle

        import bmesh

        area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
        region = next(r for r in area.regions if r.type == "WINDOW")
        data = region.data

        props = tool.Project.get_project_props()
        # See 6452 and 6478.
        # if not len(props.clipping_planes) and not self.camera:
        if not len(props.clipping_planes):
            data.use_clip_planes = False
        else:
            with bpy.context.temp_override(area=area, region=region):
                bpy.ops.view3d.clip_border()

                clip_planes = []
                for clipping_plane in tool.Project.get_project_props().clipping_planes:
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

                # See 6452 and 6478.
                # if self.camera:
                #     normal = self.camera.matrix_world.col[2].to_3d()
                #     normal *= -1
                #     center = self.camera.matrix_world.translation
                #     distance = -center.dot(normal)
                #     clip_plane = (normal.x, normal.y, normal.z, distance)
                #     clip_planes.append(clip_plane)

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
        # Clean up deleted planes
        props = tool.Project.get_project_props()
        if len(props.clipping_planes) > 5:
            self.report({"INFO"}, "Maximum of six clipping planes allowed.")
            return {"FINISHED"}

        tool.Blender.update_all_viewports(context)

        assert context.region and context.region_data
        region = context.region
        rv3d = context.region_data
        if rv3d:  # Called from a 3D viewport
            coord = (self.mouse_x, self.mouse_y)
            origin = region_2d_to_origin_3d(region, rv3d, coord)
            direction = region_2d_to_vector_3d(region, rv3d, coord)
            hit, location, normal, face_index, obj, matrix = tool.Blender.ray_cast_scene(context, origin, direction)
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

        new = tool.Project.get_project_props().clipping_planes.add()
        new.obj = plane_obj

        tool.Blender.set_active_object(plane_obj)

        ClippingPlaneDecorator.install(context)
        bpy.ops.bim.refresh_clipping_planes("INVOKE_DEFAULT")
        return {"FINISHED"}

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
        if obj in tool.Project.get_project_props().clipping_planes_objs:
            obj.rotation_euler[0] += radians(180)
            obj.rotation_euler[0] %= radians(360)
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
            return tool.Project.get_project_props().clipping_planes
        cls.poll_message_set("Please Save The IFC File")

    def execute(self, context):
        clipping_planes_to_serialize = defaultdict(dict)
        clipping_planes = tool.Project.get_project_props().clipping_planes
        for clipping_plane in clipping_planes:
            obj = clipping_plane.obj
            assert obj
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
        props = tool.Project.get_project_props()
        bpy.data.batch_remove(props.clipping_planes_objs)
        props.clipping_planes.clear()
        with open(Path(IfcStore.path).with_name(CLIPPING_PLANES_FILE_NAME), "r") as file:
            clipping_planes_dict = json.load(file)
        for name, values in clipping_planes_dict.items():
            bpy.ops.bim.create_clipping_plane()
            obj = props.clipping_planes_objs[-1]
            obj.name = name
            obj.location = values["location"]
            obj.rotation_euler = values["rotation"]
        return {"FINISHED"}


class IFCFileHandlerOperator(bpy.types.Operator):
    bl_idname = "bim.load_project_file_handler"
    bl_label = "Import .ifc file"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    directory: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE", "HIDDEN"})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={"SKIP_SAVE", "HIDDEN"})

    if TYPE_CHECKING:
        directory: str
        files: list[bpy.types.OperatorFileListElement]

    def invoke(self, context, event):
        # Keeping code in .invoke() as we'll probably add some
        # popup windows later.

        def clean_up_path(path: str) -> str:
            # In Blender 4.5.6 there was a bug producing unncesseary double slash prefix
            # breaking the paths. Issue is not present in 5.0+ and is fixed in 4.5.7.
            # https://projects.blender.org/blender/blender/issues/153822
            if bpy.app.version == (4, 5, 6):
                blender_prefix = "//"
                if path.startswith(blender_prefix):
                    return path.removeprefix(blender_prefix)
            return path

        # `files` contain only .ifc files.
        filepath = Path(self.directory)
        # If user is just drag'n'dropping a single file -> load it as a new project,
        # if they're holding ALT -> link the file/files to the current project.
        if event.alt:
            # Passing self.files directly results in TypeError.
            serialized_files = [{"name": clean_up_path(f.name)} for f in self.files]
            return bpy.ops.bim.link_ifc(directory=self.directory, files=serialized_files)
        else:
            if len(self.files) == 1:
                return bpy.ops.bim.load_project(filepath=(filepath / clean_up_path(self.files[0].name)).as_posix())
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

    if TYPE_CHECKING:
        measure_type: str

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self.input_options = ["D", "A", "X", "Y", "Z"]
        self.input_ui = tool.Polyline.create_input_ui(input_options=self.input_options)

    def modal(self, context, event):
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        custom_instructions = {
            "Choose Axis": {"icons": True, "keys": ["EVENT_X", "EVENT_Y", "EVENT_Z"]},
            "Choose Plane": {"icons": True, "keys": ["EVENT_SHIFT", "EVENT_X", "EVENT_Y", "EVENT_Z"]},
        }
        self.handle_instructions(context, custom_instructions)

        self.handle_mouse_move(context, event)

        self.choose_axis(event, z=True)

        self.choose_plane(event)

        self.handle_snap_selection(context, event)

        single_mode = False
        polyline_props = tool.Model.get_polyline_props()
        if (
            self.measure_type == "SINGLE"
            and polyline_props.insertion_polyline
            and len(polyline_props.insertion_polyline[0].polyline_points) >= 2
        ):
            single_mode = True

        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ) or single_mode:
            context.workspace.status_text_set(text=None)
            self.tool_state.plane_method = None
            PolylineDecorator.uninstall()
            tool.Polyline.move_polyline_to_measure(context, self.input_ui)
            tool.Polyline.clear_polyline()
            MeasureDecorator.install(context)
            tool.Blender.update_viewport()
            return {"FINISHED"}

        self.handle_keyboard_input(context, event)

        self.handle_inserting_polyline(context, event)

        # Add measurement type to the insertion polyline
        polyline_data = polyline_props.insertion_polyline
        if not polyline_data:
            pass
        else:
            polyline_data = polyline_props.insertion_polyline[0]
            measurement_type = tool.Project.get_measure_tool_settings().measurement_type
            if not polyline_data.measurement_type:
                polyline_data.measurement_type = measurement_type

        tool.Polyline.calculate_area(context, self.input_ui)

        if event.type == "E":
            polyline_props.measurement_polyline.clear()
            MeasureDecorator.uninstall()
            tool.Blender.update_viewport()

        result = self.handle_cancelation(context, event)
        if result is not None:
            return result

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        super().invoke(context, event)
        return {"RUNNING_MODAL"}


class MeasureFaceAreaTool(bpy.types.Operator, PolylineOperator):
    bl_idname = "bim.measure_face_area_tool"
    bl_label = "Measure Face Area Tool"
    bl_options = {"REGISTER", "UNDO"}

    measure_type: bpy.props.StringProperty()

    if TYPE_CHECKING:
        measure_type: str

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self.input_options = ["AREA"]
        self.input_ui = tool.Polyline.create_input_ui(input_options=self.input_options)
        self.clicked_faces = []
        self.total_area = 0
        if tool.Ifc.get():
            self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        else:
            self.unit_scale = tool.Blender.get_unit_scale()

    def modal(self, context, event):
        def select_face(mouse_pos):
            objs_to_raycast = tool.Raycast.filter_objects_to_raycast(context, event, self.objs_2d_bbox)
            obj, _, face_index = tool.Raycast.cast_rays_and_get_best_object(
                context, event, objs_to_raycast, include_wireframes=False
            )
            if face_index is not None:
                return obj, face_index
            return None, None

        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        custom_instructions = {
            "Select Face": {"icons": True, "keys": ["MOUSE_LMB"]},
            "Deselect Face": {"icons": True, "keys": ["EVENT_SHIFT", "MOUSE_LMB"]},
        }
        custom_info = []
        self.handle_instructions(context, custom_instructions, custom_info, overwrite=True)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_mouse_move(context, event)
        polyline_props = tool.Model.get_polyline_props()

        if event.value == "PRESS" and event.type == "LEFTMOUSE":
            tool.Blender.update_viewport()
            mouse_pos = event.mouse_region_x, event.mouse_region_y
            obj, face_index = select_face(mouse_pos)
            if face_index is not None:
                if obj.data.polygons[face_index] not in self.clicked_faces:
                    self.clicked_faces.append(obj.data.polygons[face_index])
                    self.total_area += obj.data.polygons[face_index].area
                    self.input_ui.set_value("AREA", self.total_area)
                    polyline_data = polyline_props.insertion_polyline.add()
                    polyline_data.id = obj.name + str(face_index)
                    for v_id in obj.data.polygons[face_index].vertices:
                        vertex = obj.matrix_world @ obj.data.vertices[v_id].co
                        polyline_point = polyline_data.polyline_points.add()
                        polyline_point.x = vertex.x
                        polyline_point.y = vertex.y
                        polyline_point.z = vertex.z
            tool.Blender.update_viewport()

        if event.shift and (event.value == "PRESS" and event.type == "LEFTMOUSE"):
            mouse_pos = event.mouse_region_x, event.mouse_region_y
            obj, face_index = select_face(mouse_pos)
            if face_index:
                if obj.data.polygons[face_index] in self.clicked_faces:
                    self.clicked_faces.remove(obj.data.polygons[face_index])
                    self.total_area -= obj.data.polygons[face_index].area
                    self.input_ui.set_value("AREA", self.total_area)
                    polyline_data = polyline_props.insertion_polyline
                    for i, polyline in enumerate(polyline_data):
                        if polyline.id == obj.name + str(face_index):
                            polyline_data.remove(i)
            tool.Blender.update_viewport()

        if event.value == "RELEASE" and event.type in {"ESC", "RIGHTMOUSE"}:
            polyline_props.insertion_polyline.clear()
            context.workspace.status_text_set(text=None)
            PolylineDecorator.uninstall()
            FaceAreaDecorator.uninstall()
            tool.Blender.update_viewport()
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        super().invoke(context, event)
        PolylineDecorator.uninstall()
        PolylineDecorator.install(context, ui_only=True)
        FaceAreaDecorator.install(context)
        return {"RUNNING_MODAL"}


class ClearMeasurement(bpy.types.Operator):
    bl_idname = "bim.clear_measurement"
    bl_label = "Clear measurement from the screen"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        polyline_props = tool.Model.get_polyline_props()
        if len(polyline_props.measurement_polyline) > 0:
            return True
        cls.poll_message_set("No measurement to clear.")
        return False

    def execute(self, context):
        polyline_props = tool.Model.get_polyline_props()
        polyline_props.measurement_polyline.clear()
        MeasureDecorator.uninstall()
        tool.Blender.update_viewport()
        return {"FINISHED"}


class ImageScalingTool(bpy.types.Operator, PolylineOperator):
    bl_idname = "bim.image_scaling_tool"
    bl_label = "Image Scaling Tool"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == "VIEW_3D"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        self.input_options = ["DISTANCE"]
        self.input_ui = tool.Polyline.create_input_ui(input_options=self.input_options)
        self.selected_points = []
        self.target_object = None
        self.current_distance_value = ""
        self.is_typing_distance = False
        self.calculated_distance = 0.0

        if tool.Ifc.get():
            self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        else:
            self.unit_scale = tool.Blender.get_unit_scale()

    def modal(self, context, event):
        if not self.target_object or not context.active_object or context.active_object != self.target_object:
            self.report({"ERROR"}, "Image annotation was deselected. Tool cancelled.")
            return self.cancel_tool(context)

        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_custom_instructions(context)
        self.handle_mouse_move(context, event)
        self.choose_axis(event, z=True)
        self.choose_plane(event)
        self.handle_snap_selection(context, event)

        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            if len(self.selected_points) < 2:
                snapped_point = self.snapping_points[0]
                point_3d = snapped_point["point"].copy()
                self.selected_points.append(point_3d)

                if len(self.selected_points) == 2:
                    self.calculate_distance()
                    self.current_distance_value = f"{self.calculated_distance:.3f}"
                    self.is_typing_distance = False
                    self.input_ui.set_value("DISTANCE", self.calculated_distance)

        elif len(self.selected_points) == 2:
            if event.type in {"RET", "NUMPAD_ENTER"} and event.value == "PRESS":
                return self.apply_scaling(context)

            if event.unicode and event.unicode.isprintable() and event.value == "PRESS":
                if event.unicode.isdigit() or event.unicode == ".":
                    if not self.is_typing_distance:
                        self.current_distance_value = event.unicode
                        self.is_typing_distance = True
                    else:
                        self.current_distance_value += event.unicode

                    distance_value = float(self.current_distance_value)
                    self.input_ui.set_value("DISTANCE", distance_value)

            elif event.type in {"BACK_SPACE", "DEL"} and event.value == "PRESS":
                if len(self.current_distance_value) > 0:
                    self.current_distance_value = self.current_distance_value[:-1]
                    distance_value = (
                        float(self.current_distance_value) if self.current_distance_value else self.calculated_distance
                    )
                    self.input_ui.set_value("DISTANCE", distance_value)

        self.handle_keyboard_input(context, event)

        result = self.handle_cancelation(context, event)
        if result is not None:
            return result

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        active_obj = context.active_object
        self.target_object = active_obj
        super().invoke(context, event)
        return {"RUNNING_MODAL"}

    def cancel_tool(self, context: bpy.types.Context) -> set["rna_enums.OperatorReturnItems"]:
        context.workspace.status_text_set(text=None)
        if hasattr(self, "tool_state"):
            self.tool_state.plane_method = None
        PolylineDecorator.uninstall()
        tool.Blender.update_viewport()
        return {"CANCELLED"}

    def handle_custom_instructions(self, context: bpy.types.Context) -> None:
        if len(self.selected_points) == 0:
            instruction_text = "Click First Point on Image"
        elif len(self.selected_points) == 1:
            instruction_text = "Click Second Point on Image"
        elif len(self.selected_points) == 2:
            if self.is_typing_distance:
                instruction_text = f"Distance: {self.current_distance_value} - Press Enter to Apply"
            else:
                instruction_text = f"Measured: {self.calculated_distance:.3f} - Type New Distance or Press Enter"
        else:
            instruction_text = "Image Scaling Tool"

        context.workspace.status_text_set(text=instruction_text)

    def calculate_distance(self) -> None:
        if len(self.selected_points) == 2:
            point1 = self.selected_points[0]
            point2 = self.selected_points[1]
            distance_3d = (point2 - point1).length
            self.calculated_distance = distance_3d / self.unit_scale

    def apply_scaling(self, context: bpy.types.Context) -> set["rna_enums.OperatorReturnItems"]:
        if len(self.selected_points) != 2:
            self.report({"ERROR"}, "Two points must be selected")
            return {"CANCELLED"}

        target_distance = float(self.current_distance_value)

        if target_distance <= 0:
            self.report({"ERROR"}, "Distance must be positive")
            return {"CANCELLED"}

        if self.calculated_distance <= 0:
            self.report({"ERROR"}, "Selected points are too close together")
            return {"CANCELLED"}

        scale_factor = target_distance / self.calculated_distance

        if self.target_object:
            import bmesh

            mesh = self.target_object.data

            bm = bmesh.new()
            bm.from_mesh(mesh)

            bmesh.ops.scale(bm, vec=(scale_factor, scale_factor, 1.0), verts=bm.verts)

            bm.to_mesh(mesh)
            bm.free()
            tool.Loader.load_generated_uv_map(mesh)
            mesh.update()

            element = tool.Ifc.get_entity(self.target_object)
            if element and element.Representation:
                for representation in element.Representation.Representations:
                    for item in representation.Items:
                        if item.is_a("IfcPolygonalFaceSet") and item.Coordinates:
                            new_coords = []
                            for vertex in mesh.vertices:
                                co = self.target_object.matrix_world @ vertex.co
                                new_coords.append([co.x, co.y, co.z])

                            item.Coordinates.CoordList = new_coords

            self.report({"INFO"}, f"Applied scale factor: {scale_factor:.4f}")

        context.workspace.status_text_set(text=None)
        self.tool_state.plane_method = None
        PolylineDecorator.uninstall()
        tool.Blender.update_viewport()

        return {"FINISHED"}


class LoadBlendMetadataAndIFC(bpy.types.Operator):
    bl_idname = "bim.load_blend_metadata_and_ifc"
    bl_label = "Load Blend Metadata and IFC"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(name="IFC File Path", default="")

    if TYPE_CHECKING:
        filepath: str

    def execute(self, context):
        ifc_file = self.filepath
        if not ifc_file:
            props = tool.Blender.get_bim_props()
            ifc_file = getattr(props, "ifc_file", None)

        if not ifc_file:
            self.report({"WARNING"}, "No IFC file path set.")
            return {"CANCELLED"}

        suffix = tool.Blender.get_addon_preferences().metadata_blend_file_suffix
        if ifc_file.lower().endswith(".ifc"):
            metadata_path = ifc_file[:-4] + suffix
        else:
            metadata_path = ifc_file + suffix

        # Define a handler to load the IFC project after the blend file is loaded and context is restored
        @persistent
        def load_handler(*args):
            bpy.app.handlers.load_post.remove(load_handler)
            # After loading metadata, clear blend warning (no geometry loaded yet)
            props = tool.Blender.get_bim_props()
            props.has_blend_warning = False
            # Load the IFC file into the current session (preserve layout)
            bpy.ops.bim.load_project(filepath=ifc_file, should_start_fresh_session=False)
            # Disable editing styles
            bpy.ops.bim.disable_editing_styles()
            self.report({"INFO"}, f"Loaded metadata and IFC: {metadata_path}, {ifc_file}")

        bpy.app.handlers.load_post.append(load_handler)
        bpy.ops.wm.open_mainfile(filepath=metadata_path)
        return {"FINISHED"}


class GenerateUVMap(bpy.types.Operator):
    bl_idname = "bim.generate_uv_map"
    bl_label = "Generate UV Map"
    bl_description = "Generate UV map for selected mesh."
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        obj = context.active_object
        if not obj or not isinstance(obj.data, bpy.types.Mesh):
            self.report({"ERROR"}, "No valid mesh selected.")
            return {"CANCELLED"}
        tool.Loader.load_generated_uv_map(obj.data)
        self.report({"INFO"}, "Generated UV map for selected mesh.")
        return {"FINISHED"}


class BIM_OT_apply_pending_opening_cuts(bpy.types.Operator, tool.Ifc.Operator):
    """Recompute the wall mesh including opening subtractions for every host
    that the load-time ``void_limit`` filter skipped. Clears the deferred
    list on completion so the panel banner disappears."""

    bl_idname = "bim.apply_pending_opening_cuts"
    bl_label = "Apply Pending Opening Cuts"
    bl_description = (
        "Recompute meshes for elements whose openings were skipped at load because they had too many openings"
    )
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context: bpy.types.Context) -> set[str]:
        pending = tool.Project.get_project_props().pending_opening_recut
        applied = 0
        skipped = 0
        failed = 0
        for item in pending:
            try:
                element = tool.Ifc.get().by_id(item.ifc_definition_id)
            except RuntimeError:
                skipped += 1
                continue
            obj = tool.Ifc.get_object(element)
            if obj is None:
                skipped += 1
                continue
            body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
            if body is None:
                skipped += 1
                continue
            try:
                tool.Geometry.reimport_element_representations(obj, body, apply_openings=True)
                applied += 1
            except (RuntimeError, OSError, AttributeError) as exc:
                # Programmer errors (TypeError, ValueError, etc.) must surface — don't swallow them.
                failed += 1
                print(f"apply_pending_opening_cuts: failed to recompute {element} ({exc})")

        pending.clear()
        message = f"Applied opening cuts to {applied} element(s)."
        if skipped:
            message += f" {skipped} entry/entries skipped (entity or object no longer available)."
        if failed:
            message += f" {failed} entry/entries failed (see system console)."
            self.report({"WARNING"}, message)
        else:
            self.report({"INFO"}, message)
        return {"FINISHED"}


class BIM_OT_dismiss_pending_opening_cuts(bpy.types.Operator):
    bl_idname = "bim.dismiss_pending_opening_cuts"
    bl_label = "Dismiss Pending Opening Cuts"
    bl_description = "Clear the pending opening-cut list without applying it. Walls stay solid where openings would have been subtracted."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        tool.Project.get_project_props().pending_opening_recut.clear()
        return {"FINISHED"}


class BIM_OT_dismiss_multi_instance_warning(bpy.types.Operator):
    bl_idname = "bim.dismiss_multi_instance_warning"
    bl_label = "Dismiss Multi-Instance Warning"
    bl_description = (
        "Hide the warning that another Blender instance has this IFC file open. Sticky for the current session."
    )
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        from bonsai.bim.ifc import dismiss_multi_instance_warning

        dismiss_multi_instance_warning()
        return {"FINISHED"}


class BIM_OT_select_pending_opening_cuts(bpy.types.Operator):
    bl_idname = "bim.select_pending_opening_cuts"
    bl_label = "Select Elements With Skipped Opening Cuts"
    bl_description = "Select the Blender objects whose openings were skipped at load. Useful for locating which elements need attention."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            self.report({"INFO"}, "No IFC file loaded.")
            return {"CANCELLED"}
        objects: list[bpy.types.Object] = []
        for item in tool.Project.get_project_props().pending_opening_recut:
            try:
                element = ifc_file.by_id(item.ifc_definition_id)
            except RuntimeError:
                continue
            obj = tool.Ifc.get_object(element)
            if obj is not None:
                objects.append(obj)
        if not objects:
            self.report({"INFO"}, "No matching Blender objects found for the pending list.")
            return {"CANCELLED"}
        tool.Blender.set_objects_selection(context, active_object=objects[0], selected_objects=objects)
        self.report({"INFO"}, f"Selected {len(objects)} element(s).")
        return {"FINISHED"}


class BIM_OT_select_pending_array_repair(bpy.types.Operator):
    bl_idname = "bim.select_pending_array_repair"
    bl_label = "Select Array Parents With Missing Children"
    bl_description = "Select the Blender objects of array parents whose BBIM_Array.Data references children that don't resolve in the file."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            self.report({"INFO"}, "No IFC file loaded.")
            return {"CANCELLED"}
        objects: list[bpy.types.Object] = []
        for item in tool.Project.get_project_props().pending_array_repair:
            try:
                element = ifc_file.by_id(item.ifc_definition_id)
            except RuntimeError:
                continue
            obj = tool.Ifc.get_object(element)
            if obj is not None:
                objects.append(obj)
        if not objects:
            self.report({"INFO"}, "No matching Blender objects found for the pending list.")
            return {"CANCELLED"}
        tool.Blender.set_objects_selection(context, active_object=objects[0], selected_objects=objects)
        self.report({"INFO"}, f"Selected {len(objects)} array parent(s).")
        return {"FINISHED"}


class BIM_OT_dismiss_pending_array_repair(bpy.types.Operator):
    bl_idname = "bim.dismiss_pending_array_repair"
    bl_label = "Dismiss Pending Array Repair"
    bl_description = (
        "Clear the pending array-repair list without acting on it. The underlying BBIM_Array.Data stays unchanged."
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        tool.Project.get_project_props().pending_array_repair.clear()
        return {"FINISHED"}
