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
import blenderbim.tool as tool
import blenderbim.core.project as core
import blenderbim.core.context
import blenderbim.core.owner
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.ui import IFCFileSelector
from blenderbim.bim import import_ifc
from blenderbim.bim import export_ifc
from ifcopenshell.api.context.data import Data as ContextData


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
        core.create_project(tool.Ifc, tool.Project, schema=props.export_schema, template=template)

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

    def execute(self, context):
        IfcStore.begin_transaction(self)
        old_filepath = IfcStore.library_path
        result = self._execute(context)
        self.transaction_data = {"old_filepath": old_filepath, "filepath": self.filepath}
        IfcStore.add_transaction_operation(self)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        IfcStore.library_path = self.filepath
        IfcStore.library_file = ifcopenshell.open(self.filepath)
        bpy.ops.bim.refresh_library()
        if context.area:
            context.area.tag_redraw()
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


class AppendLibraryElement(bpy.types.Operator):
    bl_idname = "bim.append_library_element"
    bl_label = "Append Library Element"
    bl_options = {"REGISTER", "UNDO"}
    definition: bpy.props.IntProperty()
    prop_index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

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
        elif element.is_a("IfcMaterial"):
            self.import_material_from_ifc(element, context)
        try:
            context.scene.BIMProjectProperties.library_elements[self.prop_index].is_appended = True
        except:
            # TODO Remove this terrible code when I refactor this into the core
            pass
        blenderbim.bim.handler.purge_module_data()
        return {"FINISHED"}

    def import_material_from_ifc(self, element, context):
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        blender_material = ifc_importer.create_material(element)
        self.import_material_styles(blender_material, element, ifc_importer)

    def import_type_from_ifc(self, element, context):
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(context, IfcStore.path, logger)

        type_collection = bpy.data.collections.get("Types")
        if not type_collection:
            type_collection = bpy.data.collections.new("Types")
            for collection in bpy.context.view_layer.layer_collection.children:
                if "IfcProject/" in collection.name:
                    collection.collection.children.link(type_collection)
                    collection.children["Types"].hide_viewport = True
                    break

        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.type_collection = type_collection
        ifc_importer.material_creator.load_existing_materials()
        self.import_type_materials(element, ifc_importer)
        self.import_type_styles(element, ifc_importer)
        ifc_importer.create_type_product(element)
        ifc_importer.place_objects_in_collections()

    def import_type_materials(self, element, ifc_importer):
        for rel in element.HasAssociations:
            if not rel.is_a("IfcRelAssociatesMaterial"):
                continue
            for material in [e for e in self.file.traverse(rel) if e.is_a("IfcMaterial")]:
                if IfcStore.get_element(material.id()):
                    continue
                blender_material = ifc_importer.create_material(material)
                self.import_material_styles(blender_material, material, ifc_importer)

    def import_type_styles(self, element, ifc_importer):
        for representation_map in element.RepresentationMaps or []:
            for element in self.file.traverse(representation_map):
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
    bl_description = "Save header informations"

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
    bl_description = "Cancel unsaved header informations"

    def execute(self, context):
        context.scene.BIMProjectProperties.is_editing = False
        return {"FINISHED"}


class LoadProject(bpy.types.Operator, IFCFileSelector):
    bl_idname = "bim.load_project"
    bl_label = "Load Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Load an existing IFC project"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    is_advanced: bpy.props.BoolProperty(name="Enable Advanced Mode", default=False)

    def execute(self, context):
        if not self.is_existing_ifc_file():
            return {"FINISHED"}
        context.scene.BIMProperties.ifc_file = self.filepath
        context.scene.BIMProjectProperties.is_loading = True
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

    def execute(self, context):
        IfcStore.purge()
        context.scene.BIMProperties.ifc_file = ""
        context.scene.BIMProjectProperties.is_loading = False
        return {"FINISHED"}


class LoadProjectElements(bpy.types.Operator):
    bl_idname = "bim.load_project_elements"
    bl_label = "Load Project Elements"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties
        self.file = IfcStore.get_file()
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

    def get_whitelist_elements(self):
        selector = ifcopenshell.util.selector.Selector()
        return set(selector.parse(self.file, self.props.filter_query))

    def get_blacklist_elements(self):
        selector = ifcopenshell.util.selector.Selector()
        return set(self.file.by_type("IfcElement")) - set(selector.parse(self.file, self.props.filter_query))


class LinkIfc(bpy.types.Operator):
    bl_idname = "bim.link_ifc"
    bl_label = "Link IFC"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Link a Blender file"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.blend;*.blend1", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    def execute(self, context):
        new = context.scene.BIMProjectProperties.links.add()
        filepath = self.filepath
        if self.use_relative_path:
            filepath = os.path.relpath(filepath, bpy.path.abspath("//"))
        new.name = filepath
        bpy.ops.bim.load_link(filepath=self.filepath)
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
        link = context.scene.BIMProjectProperties.links.get(filepath)
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
        with bpy.data.libraries.load(self.filepath, link=True) as (data_from, data_to):
            data_to.scenes = data_from.scenes
        for scene in bpy.data.scenes:
            if not scene.library or scene.library.filepath != filepath:
                continue
            for child in scene.collection.children:
                if "IfcProject" not in child.name:
                    continue
                bpy.data.scenes[0].collection.children.link(child)
        link = context.scene.BIMProjectProperties.links.get(filepath)
        link.is_loaded = True
        return {"FINISHED"}


class ExportIFC(bpy.types.Operator):
    bl_idname = "export_ifc.bim"
    bl_label = "Export IFC"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml;*.ifcjson", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    json_version: bpy.props.EnumProperty(items=[("4", "4", ""), ("5a", "5a", "")], name="IFC JSON Version")
    json_compact: bpy.props.BoolProperty(name="Export Compact IFCJSON", default=False)
    should_save_as: bpy.props.BoolProperty(name="Should Save As", default=False)
    use_relative_path: bpy.props.BoolProperty(name="Use Relative Path", default=False)

    def invoke(self, context, event):
        if not IfcStore.get_file():
            self.report({"ERROR"}, "No IFC project is available for export - create or import a project first.")
            return {"FINISHED"}
        if context.scene.BIMProperties.ifc_file and not self.should_save_as:
            self.filepath = context.scene.BIMProperties.ifc_file
            if not os.path.isabs(self.filepath):
                self.filepath = os.path.abspath(os.path.join(bpy.path.abspath("//"), self.filepath))
            return self.execute(context)
        if not self.filepath:
            self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".ifc")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

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
        settings.logger.info("Starting export")
        ifc_exporter.export()
        settings.logger.info("Export finished in {:.2f} seconds".format(time.time() - start))
        print("Export finished in {:.2f} seconds".format(time.time() - start))
        scene = context.scene
        if not scene.DocProperties.ifc_files:
            new = scene.DocProperties.ifc_files.add()
            new.name = output_file
        if self.use_relative_path and bpy.data.is_saved:
            output_file = os.path.relpath(output_file, bpy.path.abspath("//"))
        if scene.BIMProperties.ifc_file != output_file and extension not in ["ifczip", "ifcjson"]:
            scene.BIMProperties.ifc_file = output_file
        if bpy.data.is_saved and bpy.data.is_dirty and bpy.data.filepath:
            bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
        blenderbim.bim.handler.purge_module_data()
        return {"FINISHED"}


class ImportIFC(bpy.types.Operator):
    bl_idname = "import_ifc.bim"
    bl_label = "Import IFC"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.bim.load_project("INVOKE_DEFAULT")
        return {"FINISHED"}
