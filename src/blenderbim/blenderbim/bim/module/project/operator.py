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

import os
import bpy
import time
import logging
import tempfile
import subprocess
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.selector
import ifcopenshell.util.geolocation
import ifcopenshell.util.representation
import ifcopenshell.util.element
import blenderbim.bim.handler
import blenderbim.bim.schema
import blenderbim.tool as tool
import blenderbim.core.project as core
import blenderbim.core.context
import blenderbim.core.owner
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.ui import IFCFileSelector
from blenderbim.bim import import_ifc
from blenderbim.bim import export_ifc
from math import radians
from pathlib import Path
from mathutils import Vector, Matrix
from bpy.app.handlers import persistent
from blenderbim.bim.module.project.data import LinksData
from blenderbim.bim.module.project.decorator import ProjectDecorator, ClippingPlaneDecorator


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
        blenderbim.bim.schema.reload(props.export_schema)
        if tool.Blender.is_default_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)
        core.create_project(tool.Ifc, tool.Project, schema=props.export_schema, template=template)
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
        IfcStore.library_path = filepath
        IfcStore.library_file = ifcopenshell.open(filepath)
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


class RefreshLibrary(bpy.types.Operator):
    bl_idname = "bim.refresh_library"
    bl_label = "Refresh Library"

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties

        self.props.library_elements.clear()
        self.props.library_breadcrumb.clear()

        self.props.active_library_element = ""

        types = IfcStore.library_file.wrapped_data.types_with_super()

        element_classes = ["IfcTypeProduct", "IfcMaterial", "IfcCostSchedule", "IfcProfileDef"]
        if self.props.library_display_elements:
            element_classes += ["IfcElement"]
        for importable_type in sorted(element_classes):
            if importable_type in types:
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

    def get_name(self, element):
        if element.is_a("IfcProfileDef"):
            return element.ProfileName or "Unnamed"
        return element.Name or "Unnamed"

    def add_library_asset(self, name, ifc_definition_id):
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
            definition=self.file.by_id(self.definition),
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
            definition=self.file.by_id(self.definition),
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


class AppendEntireLibrary(bpy.types.Operator):
    bl_idname = "bim.append_entire_library"
    bl_label = "Append Entire Library"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        self.library = IfcStore.library_file

        lib_elements = ifcopenshell.util.selector.filter_elements(
            self.library, "IfcTypeProduct, IfcMaterial, IfcCostSchedule, IfcProfileDef"
        )
        for element in lib_elements:
            bpy.ops.bim.append_library_element(definition=element.id())
        return {"FINISHED"}


class AppendLibraryElementByQuery(bpy.types.Operator):
    bl_idname = "bim.append_library_element_by_query"
    bl_label = "Append Library Element By Query"
    query: bpy.props.StringProperty(name="Query")

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

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


class AppendLibraryElement(bpy.types.Operator):
    bl_idname = "bim.append_library_element"
    bl_label = "Append Library Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Append element to the current project"
    definition: bpy.props.IntProperty()
    prop_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        poll = bool(IfcStore.get_file())
        if bpy.app.version > (3, 0, 0) and not poll:
            cls.poll_message_set("Please create or load a project first.")
        return poll

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        element = ifcopenshell.api.run(
            "project.append_asset",
            self.file,
            library=IfcStore.library_file,
            element=IfcStore.library_file.by_id(self.definition),
        )
        if not element:
            return {"FINISHED"}
        if element.is_a("IfcTypeProduct"):
            self.import_type_from_ifc(element, context)
        elif element.is_a("IfcProduct"):
            self.import_product_from_ifc(element, context)
            element_type = ifcopenshell.util.element.get_type(element)
            obj = tool.Ifc.get_object(element_type)
            if obj is None:
                self.import_type_from_ifc(element_type, context)

        elif element.is_a("IfcMaterial"):
            self.import_material_from_ifc(element, context)
        try:
            context.scene.BIMProjectProperties.library_elements[self.prop_index].is_appended = True
        except:
            # TODO Remove this terrible code when I refactor this into the core
            pass
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def import_material_from_ifc(self, element, context):
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        blender_material = ifc_importer.create_material(element)
        self.import_material_styles(blender_material, element, ifc_importer)

    def import_product_from_ifc(self, element, context):
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

    def import_type_from_ifc(self, element, context):
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)

        type_collection = bpy.data.collections.get("Types")
        if not type_collection:
            type_collection = bpy.data.collections.new("Types")
            for collection in bpy.context.view_layer.layer_collection.children:
                collection_obj = collection.collection.BIMCollectionProperties.obj
                if collection_obj and tool.Ifc.get_entity(collection_obj).is_a("IfcProject"):
                    collection.collection.children.link(type_collection)
                    collection.children["Types"].hide_viewport = True
                    break

        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.type_collection = type_collection
        ifc_importer.process_context_filter()
        ifc_importer.material_creator.load_existing_materials()
        self.import_materials(element, ifc_importer)
        self.import_styles(element, ifc_importer)
        ifc_importer.create_element_type(element)
        ifc_importer.place_objects_in_collections()

    def import_materials(self, element, ifc_importer):
        for material in ifcopenshell.util.element.get_materials(element):
            if IfcStore.get_element(material.id()):
                continue
            blender_material = ifc_importer.create_material(material)
            self.import_material_styles(blender_material, material, ifc_importer)

    def import_styles(self, element, ifc_importer):
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

    def import_material_styles(self, blender_material, material, ifc_importer):
        if not material.HasRepresentation:
            return
        for element in self.file.traverse(material.HasRepresentation[0]):
            if element.is_a("IfcSurfaceStyle") and not IfcStore.get_element(element.id()):
                ifc_importer.create_style(element, blender_material)


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
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcsqlite", options={"HIDDEN"})
    is_advanced: bpy.props.BoolProperty(name="Enable Advanced Mode", default=False)
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)
    should_start_fresh_session: bpy.props.BoolProperty(name="Should Start Fresh Session", default=True)

    def execute(self, context):
        @persistent
        def load_handler(*args):
            bpy.app.handlers.load_post.remove(load_handler)
            self.finish_loading_project(context)

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
        if not self.is_existing_ifc_file():
            return {"FINISHED"}

        if tool.Blender.is_default_scene():
            for obj in bpy.data.objects:
                bpy.data.objects.remove(obj)

        context.scene.BIMProperties.ifc_file = self.get_filepath()
        context.scene.BIMProjectProperties.is_loading = True
        context.scene.BIMProjectProperties.total_elements = len(tool.Ifc.get().by_type("IfcElement"))
        tool.Blender.register_toolbar()
        if not self.is_advanced:
            bpy.ops.bim.load_project_elements()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        self.layout.prop(self, "is_advanced")
        IFCFileSelector.draw(self, context)


class UnloadProject(bpy.types.Operator):
    bl_idname = "bim.unload_project"
    bl_label = "Unload Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unload the IFC project"

    def execute(self, context):
        IfcStore.purge()
        context.scene.BIMProperties.ifc_file = ""
        context.scene.BIMProjectProperties.is_loading = False
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
        blenderbim.bim.schema.reload(self.file.schema)
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
    false_origin: bpy.props.StringProperty(name="False Origin", default="0,0,0")

    def execute(self, context):
        start = time.time()
        files = [f.name.replace("\\", "/") for f in self.files] if self.files else [self.filepath.replace("\\", "/")]
        for filename in files:
            filepath = os.path.join(self.directory, filename).replace("\\", "/")
            if bpy.data.filepath and Path(filepath).samefile(bpy.data.filepath):
                self.report({"INFO"}, "Can't link the current .blend file")
                continue
            new = context.scene.BIMProjectProperties.links.add()
            if self.use_relative_path:
                filepath = os.path.relpath(filepath, bpy.path.abspath("//")).replace("\\", "/")
            new.name = filepath
            bpy.ops.bim.load_link(filepath=filepath, false_origin=self.false_origin)
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
        self.filepath = self.filepath.replace("\\", "/")
        bpy.ops.bim.unload_link(filepath=self.filepath)
        index = context.scene.BIMProjectProperties.links.find(self.filepath)
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
        self.filepath = self.filepath.replace("\\", "/")
        filepath = self.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), filepath)).replace("\\", "/")
        for collection in context.scene.collection.children:
            if collection.library and collection.library.filepath.replace("\\", "/") == filepath:
                context.scene.collection.children.unlink(collection)
        for scene in bpy.data.scenes:
            if scene.library and scene.library.filepath.replace("\\", "/") == filepath:
                bpy.data.scenes.remove(scene)
        link = context.scene.BIMProjectProperties.links.get(self.filepath)
        link.is_loaded = False
        return {"FINISHED"}


class LoadLink(bpy.types.Operator):
    bl_idname = "bim.load_link"
    bl_label = "Load Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Load the selected file"
    filepath: bpy.props.StringProperty()
    false_origin: bpy.props.StringProperty(name="False Origin", default="0,0,0")

    def execute(self, context):
        self.filepath = self.filepath.replace("\\", "/")
        filepath = self.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), filepath)).replace("\\", "/")
        if self.filepath.lower().endswith(".blend"):
            self.link_blend(filepath)
        elif self.filepath.lower().endswith(".ifc"):
            self.link_ifc()
        return {"FINISHED"}

    def link_blend(self, filepath):
        with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
        for scene in bpy.data.scenes:
            if not scene.library or scene.library.filepath.replace("\\", "/") != filepath:
                continue
            for child in scene.collection.children:
                if "IfcProject" not in child.name:
                    continue
                bpy.data.scenes[0].collection.children.link(child)
        link = bpy.context.scene.BIMProjectProperties.links.get(self.filepath)
        link.is_loaded = True

    def link_ifc(self):
        blend_filepath = self.filepath + ".cache.blend"
        h5_filepath = self.filepath + ".cache.h5"

        if not os.path.exists(blend_filepath):
            code = f"""
import bpy

def run():
    bpy.ops.bim.load_linked_project(filepath="{self.filepath}", false_origin="{self.false_origin}")
    bpy.ops.wm.save_as_mainfile(filepath="{blend_filepath}")

try:
    run()
except Exception as e:
    import traceback
    traceback.print_exc()
    exit(1)
            """

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
                temp_file.write(code)
            run = subprocess.run([bpy.app.binary_path, "-b", "--python", temp_file.name, "--python-exit-code", "1"])
            if run.returncode == 1:
                print("An error occurred while processing your IFC.")

        self.link_blend(blend_filepath)


class ReloadLink(bpy.types.Operator):
    bl_idname = "bim.reload_link"
    bl_label = "Reload Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reload the selected file"
    filepath: bpy.props.StringProperty()

    def execute(self, context):
        def get_linked_ifcs():
            selected_filename = os.path.basename(self.filepath.replace("\\", "/"))
            return [
                c.library
                for c in bpy.data.collections
                if "IfcProject" in c.name and c.library and os.path.basename(c.library.filepath) == selected_filename
            ]

        for library in get_linked_ifcs() or []:
            library.reload()
        return {"FINISHED"}


class ToggleLinkSelectability(bpy.types.Operator):
    bl_idname = "bim.toggle_link_selectability"
    bl_label = "Toggle Link Selectability"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle selectability"
    link: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMProjectProperties
        link = props.links.get(self.link)
        self.filepath = self.link
        if not os.path.isabs(self.filepath):
            self.filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), self.filepath)).replace("\\", "/")
        for collection in self.get_linked_collections():
            collection.hide_select = not collection.hide_select
            link.is_selectable = not collection.hide_select
        return {"FINISHED"}

    def get_linked_collections(self):
        return [
            c
            for c in bpy.data.collections
            if "IfcProject" in c.name and c.library and c.library.filepath.replace("\\", "/") == self.filepath
        ]


class ToggleLinkVisibility(bpy.types.Operator):
    bl_idname = "bim.toggle_link_visibility"
    bl_label = "Toggle Link Visibility"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Toggle visibility between SOLID and WIREFRAME"
    link: bpy.props.StringProperty()
    mode: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMProjectProperties
        link = props.links.get(self.link)
        self.filepath = self.link
        if not os.path.isabs(self.filepath):
            self.filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), self.filepath)).replace("\\", "/")
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
        queue = [bpy.context.view_layer.layer_collection]
        layer_collection = None

        while queue:
            layer = queue.pop()
            if layer.collection in linked_collections:
                layer_collection = layer
                break
            queue.extend(list(layer.children))

        if layer_collection:
            layer_collection.exclude = not layer_collection.exclude
            link.is_hidden = layer_collection.exclude

    def get_linked_collections(self):
        return [
            c
            for c in bpy.data.collections
            if "IfcProject" in c.name and c.library and c.library.filepath.replace("\\", "/") == self.filepath
        ]


class ExportIFC(bpy.types.Operator):
    bl_idname = "export_ifc.bim"
    bl_label = "Save IFC"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcjson", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    json_version: bpy.props.EnumProperty(items=[("4", "4", ""), ("5a", "5a", "")], name="IFC JSON Version")
    json_compact: bpy.props.BoolProperty(name="Export Compact IFCJSON", default=False)
    should_save_as: bpy.props.BoolProperty(name="Should Save As", default=False, options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)
    save_as_invoked: bpy.props.BoolProperty(name="Save As Dialog Was Invoked", default=False, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "json_version")
        layout.prop(self, "json_compact")
        if bpy.data.is_saved:
            layout.prop(self, "use_relative_path")

    def invoke(self, context, event):
        if not tool.Ifc.get():
            bpy.ops.wm.save_mainfile("INVOKE_DEFAULT")
            return {"FINISHED"}

        self.save_as_invoked = False
        if context.scene.BIMProperties.ifc_file and not self.should_save_as:
            self.filepath = context.scene.BIMProperties.ifc_file
            if not os.path.isabs(self.filepath):
                self.filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), self.filepath))
            return self.execute(context)
        if not self.filepath:
            if bpy.data.is_saved:
                self.filepath = Path(bpy.data.filepath).with_suffix(".ifc").__str__()
            else:
                self.filepath = "untitled.ifc"

        self.save_as_invoked = True
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        project_props = context.scene.BIMProjectProperties
        if self.save_as_invoked:
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
        blenderbim.bim.handler.refresh_ui_data()
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


class ImportIFC(bpy.types.Operator):
    bl_idname = "import_ifc.bim"
    bl_label = "Import IFC"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.bim.load_project("INVOKE_DEFAULT")
        return {"FINISHED"}


class LoadLinkedProject(bpy.types.Operator):
    bl_idname = "bim.load_linked_project"
    bl_label = "Load a project for viewing only."
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty()
    false_origin: bpy.props.StringProperty(name="False Origin", default="0,0,0")

    def execute(self, context):
        import ifcpatch
        import multiprocessing
        import ifcopenshell.geom

        start = time.time()

        self.filepath = self.filepath.replace("\\", "/")
        print("Processing", self.filepath)

        self.collection = bpy.data.collections.new("IfcProject/" + os.path.basename(self.filepath))
        self.file = ifcopenshell.open(self.filepath)
        print("Finished opening")

        self.db_filepath = self.filepath + ".cache.sqlite"
        db = ifcpatch.execute(
            {"input": self.filepath, "file": self.file, "recipe": "ExtractPropertiesToSQLite", "arguments": []}
        )
        ifcpatch.write(db, self.db_filepath)
        print("Finished writing property database")

        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.process_context_filter()

        self.elements = set(self.file.by_type("IfcElement"))
        if self.file.schema in ("IFC2X3", "IFC4"):
            self.elements |= set(self.file.by_type("IfcProxy"))
        self.elements |= set(self.file.by_type("IfcSite"))
        self.elements -= set(self.file.by_type("IfcFeatureElement"))
        self.elements = list(self.elements)

        model_origin = np.array(ifcopenshell.util.geolocation.auto_xyz2enh(self.file, 0, 0, 0))
        false_origin = np.array([float(o.strip()) for o in self.false_origin.split(",")])
        model_offset = model_origin - false_origin
        zero_origin = np.array((0, 0, 0))
        has_model_offset = not np.allclose(model_offset, zero_origin)

        for settings in ifc_importer.context_settings:
            settings = ifcopenshell.geom.settings()

            if has_model_offset:
                offset = ifcopenshell.ifcopenshell_wrapper.float_array_3()
                offset[0], offset[1], offset[2] = model_offset
                settings.offset = offset

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
            max_slot_index = 0
            chunk_size = 10000
            r4 = np.array([[0, 0, 0, 1]])
            offset = 0

            ci = 0
            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    if len(shape.geometry.faces) > 1000 and self.is_local(shape):  # 333 tris
                        self.process_occurrence(shape)
                        if not iterator.next():
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
                        continue

                    ci += 1
                    if ci % 50 == 0:
                        print("Doing chunk", ci)

                    has_processed_chunk = False

                    ms = np.vstack([default_mat, np.frombuffer(shape.geometry.colors_buffer).reshape((-1, 4))])
                    mi = np.frombuffer(shape.geometry.material_ids_buffer, dtype=np.int32)
                    chunked_materials.append(ms)
                    chunked_material_ids.append(mi + material_offset + 1)
                    material_offset += len(ms)

                    M4 = np.frombuffer(shape.transformation_buffer).reshape((4, 3))
                    M4 = np.concatenate((M4.T, r4))
                    vs = np.frombuffer(shape.geometry.verts_buffer).reshape((-1, 3))
                    vs = np.hstack((vs, np.ones((len(vs), 1))))
                    vs = (np.asmatrix(M4) * np.asmatrix(vs).T).T.A
                    vs = vs[:, :3].flatten()
                    fs = np.frombuffer(shape.geometry.faces_buffer, dtype=np.int32)
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
                        max_slot_index = 0
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

            bpy.context.scene.collection.children.link(self.collection)
            print("Finished", time.time() - start)
            break
        return {"FINISHED"}

    def is_local(self, shape):
        m = shape.transformation.matrix.data
        if max([abs(co) for co in (m[9], m[10], m[11])]) > 1000:
            return False
        elif max([abs(co) for co in shape.geometry.verts[0:3]]) > 1000:
            return False
        return True

    def process_occurrence(self, shape):
        element = self.file.by_id(shape.id)
        matrix = shape.transformation.matrix.data
        faces = shape.geometry.faces
        verts = shape.geometry.verts
        materials = shape.geometry.materials
        material_ids = shape.geometry.material_ids

        m = shape.transformation.matrix.data
        mat = np.array(([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1]))

        mesh = self.meshes.get(shape.geometry.id, None)
        if not mesh:
            mesh = bpy.data.meshes.new("Mesh")

            material_to_slot = {}
            max_slot_index = 0

            for i, material in enumerate(materials):
                alpha = 1.0
                if material.has_transparency and material.transparency > 0:
                    alpha = 1.0 - material.transparency
                diffuse = material.diffuse + (alpha,)
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
        obj.matrix_world = Matrix(mat.tolist())

        obj["guids"] = [shape.guid]
        obj["guid_ids"] = [len(mesh.polygons)]
        obj["db"] = self.db_filepath

        self.collection.objects.link(obj)

    def create_object(self, verts, faces, materials, material_ids, guids, guid_ids):
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

        if material_ids.size > 0:
            mesh.polygons.foreach_set("material_index", material_ids)

        mesh.update()

        obj = bpy.data.objects.new("Chunk", mesh)
        obj["guids"] = list(guids)
        obj["guid_ids"] = list(guid_ids)
        obj["db"] = self.db_filepath

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
        bpy.context.scene.BIMProjectProperties.queried_obj = None

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
        hit, location, normal, face_index, obj, matrix = self.ray_cast(context, origin, direction)
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
                bpy.context.scene.BIMProjectProperties.queried_obj = obj

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

    def ray_cast(self, context, origin, direction):
        depsgraph = context.evaluated_depsgraph_get()
        result = context.scene.ray_cast(depsgraph, origin, direction)
        return result

    def invoke(self, context, event):
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y
        return self.execute(context)


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
                    print("doing", obj)

                    bm = bmesh.new()
                    bm.from_mesh(obj.data)

                    world_matrix = obj.matrix_world

                    bm.faces.ensure_lookup_table()
                    face = bm.faces[0]
                    center = world_matrix @ face.calc_center_median()
                    print("center", center)
                    normal = world_matrix.to_3x3() @ face.normal * -1
                    center += normal * -0.01
                    print("normal", normal)
                    print("new center", center)

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

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

        # Clean up deleted planes

        if len(bpy.context.scene.BIMProjectProperties.clipping_planes) > 5:
            self.report({"INFO"}, "Maximum of six clipping planes allowed.")
            return {"FINISHED"}

        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

        region = context.region
        rv3d = context.region_data
        coord = (self.mouse_x, self.mouse_y)
        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)
        hit, location, normal, face_index, obj, matrix = self.ray_cast(context, origin, direction)
        if not hit:
            self.report({"INFO"}, "No object found.")
            return {"FINISHED"}

        vertices = [(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)]

        faces = [(0, 1, 2, 3)]

        mesh = bpy.data.meshes.new(name="ClippingPlane")
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        plane_obj = bpy.data.objects.new("ClippingPlane", mesh)
        bpy.context.collection.objects.link(plane_obj)
        z_axis = Vector((0, 0, 1))
        rotation_matrix = z_axis.rotation_difference(normal).to_matrix().to_4x4()
        plane_obj.matrix_world = rotation_matrix
        plane_obj.matrix_world.translation = location

        bpy.context.scene.cursor.location = location

        new = bpy.context.scene.BIMProjectProperties.clipping_planes.add()
        new.obj = plane_obj

        tool.Blender.set_active_object(plane_obj)

        ClippingPlaneDecorator.install(bpy.context)
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
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj in [cp.obj for cp in bpy.context.scene.BIMProjectProperties.clipping_planes]:
            obj.rotation_euler[0] += radians(180)
            bpy.context.view_layer.update()
        return {"FINISHED"}
