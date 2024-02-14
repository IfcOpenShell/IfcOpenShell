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
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.selector
import ifcopenshell.util.representation
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
from pathlib import Path
from bpy.app.handlers import persistent
import numpy as np


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
            bpy.context.scene.BIMProjectProperties.template_file = "IFC4 Demo Library.ifc"

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
        for importable_type in sorted(["IfcTypeProduct", "IfcMaterial", "IfcCostSchedule", "IfcProfileDef"]):
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
    bl_label = "Link Blend/IFC File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "This will link the Blender file that is synced with the IFC file"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    files: bpy.props.CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_glob: bpy.props.StringProperty(default="*.blend;*.blend1", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    def execute(self, context):
        files = [f.name for f in self.files] if self.files else [self.filepath]
        for filename in files:
            filepath = os.path.join(self.directory, filename)
            if bpy.data.filepath and Path(filepath).samefile(bpy.data.filepath):
                self.report({"INFO"}, "Can't link the current .blend file")
                continue
            new = context.scene.BIMProjectProperties.links.add()
            if self.use_relative_path:
                filepath = os.path.relpath(filepath, bpy.path.abspath("//"))
            new.name = filepath
            bpy.ops.bim.load_link(filepath=filepath)
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
        filepath = self.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), filepath))
        for collection in context.scene.collection.children:
            if collection.library and collection.library.filepath == filepath:
                context.scene.collection.children.unlink(collection)
        for scene in bpy.data.scenes:
            if scene.library and scene.library.filepath == filepath:
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

    def execute(self, context):
        filepath = self.filepath
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), filepath))
        with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
        for scene in bpy.data.scenes:
            if not scene.library or scene.library.filepath != filepath:
                continue
            for child in scene.collection.children:
                if "IfcProject" not in child.name:
                    continue
                bpy.data.scenes[0].collection.children.link(child)
        link = context.scene.BIMProjectProperties.links.get(self.filepath)
        link.is_loaded = True
        return {"FINISHED"}


class ReloadLink(bpy.types.Operator):
    bl_idname = "bim.reload_link"
    bl_label = "Reload Link"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Reload the selected file"
    filepath: bpy.props.StringProperty()

    def execute(self, context):
        def get_linked_ifcs():
            selected_filename = os.path.basename(self.filepath)
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
            self.filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), self.filepath))
        for collection in self.get_linked_collections():
            collection.hide_select = not collection.hide_select
            link.is_selectable = not collection.hide_select
        return {"FINISHED"}

    def get_linked_collections(self):
        return [
            c
            for c in bpy.data.collections
            if "IfcProject" in c.name and c.library and c.library.filepath == self.filepath
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
            self.filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), self.filepath))
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
            if "IfcProject" in c.name and c.library and c.library.filepath == self.filepath
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


class xxx(bpy.types.Operator):
    bl_idname = "bim.xxx"
    bl_label = "xxx"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import time
        import multiprocessing
        import ifcopenshell
        import ifcopenshell.geom
        import numpy as np
        from mathutils import Matrix
        import resource
        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        start = time.time()

        collection = bpy.data.collections.new("Project")
        # ifc_file = ifcopenshell.open('/home/dion/test.ifc')
        ifc_file = ifcopenshell.open('/home/dion/drive/ifcs/racbasicsampleproject.ifc')
        # ifc_file = ifcopenshell.open('/home/dion/drive/ifcs/TXG_sample_project-fixed-IFC4.ifc')

        settings = ifcopenshell.geom.settings()
        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
        meshes = {}
        blender_mats = {}
        if iterator.initialize():
            while True:
                shape = iterator.get()
                element = ifc_file.by_id(shape.id)
                matrix = shape.transformation.matrix.data
                faces = shape.geometry.faces
                verts = shape.geometry.verts
                materials = shape.geometry.materials
                material_ids = shape.geometry.material_ids

                m = shape.transformation.matrix.data
                mat = np.array(
                    ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
                )

                mesh = meshes.get(shape.geometry.id, None)
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
                        blender_mat = blender_mats.get(material_name, None)
                        if not blender_mat:
                            blender_mat = bpy.data.materials.new(material_name)
                            blender_mat.diffuse_color = diffuse
                            blender_mats[material_name] = blender_mat
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

                obj = bpy.data.objects.new(tool.Loader.get_name(element), mesh)
                obj.matrix_world = Matrix(mat.tolist())
                collection.objects.link(obj)

                if not iterator.next():
                    break

        bpy.context.scene.collection.children.link(collection)
        print('Finished', time.time() - start)
        newmem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        print("Mem", newmem-mem)
        return {"FINISHED"}


class zzz(bpy.types.Operator):
    bl_idname = "bim.zzz"
    bl_label = "zzz"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import uuid
        import h5py
        import multiprocessing
        import ifcopenshell
        import ifcopenshell.geom
        import numpy as np
        import time
        from mathutils import Matrix
        import resource
        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        start = time.time()

        collection = bpy.data.collections.new("Project")
        # model = h5py.File('/home/dion/test3.h5', 'r')
        model = h5py.File('/home/dion/test4.h5', 'r')

        materials = {}
        for i, rgb in enumerate(model["materials"]):
            blender_mat = bpy.data.materials.new(str(i))
            blender_mat.diffuse_color = rgb[()].tolist()
            materials[i] = blender_mat

        meshes = {}
        for shape_id, shape in model["shapes"].items():
            mesh = bpy.data.meshes.new(shape_id)
            meshes[int(shape_id)] = mesh

            for material in shape["materials"]:
                mesh.materials.append(materials[material])

            verts = shape["verts"][()].tolist()
            faces = shape["faces"][()].tolist()

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

            if "material_ids" in shape:
                mesh.polygons.foreach_set("material_index", shape["material_ids"][()].tolist())

            mesh.update()

        for i, global_id in enumerate(model["element_global_ids"]):
            global_id = str(uuid.UUID(bytes=bytes(global_id)))
            obj = bpy.data.objects.new(global_id, meshes[model["element_shape_ids"][i]])
            m = model["element_matrices"][i]
            mat = np.array(
                ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
            )
            obj.matrix_world = Matrix(mat.tolist())
            collection.objects.link(obj)

        bpy.context.scene.collection.children.link(collection)
        print('Finished', time.time() - start)
        newmem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        print("Mem", newmem-mem)
        return {"FINISHED"}


class zxc(bpy.types.Operator):
    bl_idname = "bim.zxc"
    bl_label = "zxc"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import uuid
        import h5py
        import multiprocessing
        import ifcopenshell
        import ifcopenshell.geom
        import time
        from mathutils import Matrix
        import resource
        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        start = time.time()

        self.collection = bpy.data.collections.new("Project")
        # model = h5py.File('/home/dion/test3.h5', 'r')
        model = h5py.File('/home/dion/test5.h5', 'r')
        print('Opened', time.time() - start)

        materials = {}
        for i, rgb in enumerate(model["materials"]):
            blender_mat = bpy.data.materials.new(str(i))
            blender_mat.diffuse_color = rgb[()].tolist()
            materials[i] = blender_mat

        print('Materials', time.time() - start)

        shapes = {}
        for shape_id, shape in model["shapes"].items():
            verts = np.array(shape["verts"][()].tolist())
            faces = shape["faces"][()].tolist()

            shapes[int(shape_id)] = {
                "verts": verts,
                "faces": faces,
                "materials": [materials[m] for m in shape["materials"]],
                "material_ids": shape["material_ids"][()].tolist() if "material_ids" in shape else None,
            }

        print('Shapes', time.time() - start)

        chunk_size = 10000

        offset = 0
        material_offset = 0
        chunked_verts = []
        chunked_faces = []
        chunked_materials = []
        chunked_material_ids = []

        for i, global_id in enumerate(model["element_global_ids"]):
            global_id = str(uuid.UUID(bytes=bytes(global_id)))
            m = model["element_matrices"][i]
            mat = np.array(
                ([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1])
            )

            shape = shapes[model["element_shape_ids"][i]]
            verts = self.apply_matrix_to_flat_list(shape["verts"], mat)
            faces = [f + offset for f in shape["faces"]]

            chunked_verts.extend(verts)
            chunked_faces.extend(faces)

            material_map = {}
            for material_index, material in enumerate(shape["materials"]):
                try:
                    chunked_index = chunked_materials.index(material)
                except:
                    chunked_index = len(chunked_materials)
                    chunked_materials.append(material)
                material_map[material_index] = chunked_index

            if shape["material_ids"] is None:
                chunked_material_ids.extend([list(material_map.values())[0]] * (len(faces) // 3))
            else:
                chunked_material_ids.extend([material_map[m] for m in shape["material_ids"]])

            offset += len(verts) // 3
            material_offset += len(shape["materials"])

            if offset > chunk_size:
                print("Chunk at", i)
                self.create_object(chunked_verts, chunked_faces, chunked_materials, chunked_material_ids)
                chunked_verts = []
                chunked_faces = []
                chunked_materials = []
                chunked_material_ids = []
                offset = 0
                material_offset = 0

        if offset:
            self.create_object(chunked_verts, chunked_faces, chunked_materials, chunked_material_ids)

        bpy.context.scene.collection.children.link(self.collection)
        print('Finished', time.time() - start)
        newmem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        print("Mem", newmem-mem)
        return {"FINISHED"}

    def apply_matrix_to_flat_list(self, flat_list, matrix):
        # Convert the flat list to a 2D array with 3 columns (x, y, z)
        vertices = np.array(flat_list).reshape(-1, 3)
        # Add a column of ones for homogeneous coordinates (x, y, z, 1)
        vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
        # Apply the matrix transformation
        transformed_vertices = np.dot(vertices, matrix.T)
        # Discard the homogeneous coordinate and flatten the array
        return transformed_vertices[:, :3].flatten()

    def create_object(self, verts, faces, materials, material_ids):
        num_vertices = len(verts) // 3
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

        if material_ids:
            mesh.polygons.foreach_set("material_index", material_ids)

        mesh.update()

        obj = bpy.data.objects.new("Blah", mesh)
        self.collection.objects.link(obj)
