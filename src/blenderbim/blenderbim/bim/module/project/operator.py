import bpy
import logging
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
import bpy
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim import import_ifc


class CreateProject(bpy.types.Operator):
    bl_idname = "bim.create_project"
    bl_label = "Create Project"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.add_transaction_operation(self, rollback=self.rollback, commit=lambda data: True)
        result = self._execute(context)
        self.transaction_data = {"file": self.file}
        IfcStore.add_transaction_operation(self, rollback=lambda data: True, commit=self.commit)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.file:
            return {"FINISHED"}

        IfcStore.file = ifcopenshell.api.run(
            "project.create_file", **{"version": context.scene.BIMProperties.export_schema}
        )
        self.file = IfcStore.get_file()

        bpy.ops.bim.add_person()
        bpy.ops.bim.add_organisation()

        project = bpy.data.objects.new(self.get_name("IfcProject", "My Project"), None)
        site = bpy.data.objects.new(self.get_name("IfcSite", "My Site"), None)
        building = bpy.data.objects.new(self.get_name("IfcBuilding", "My Building"), None)
        building_storey = bpy.data.objects.new(self.get_name("IfcBuildingStorey", "My Storey"), None)

        bpy.ops.bim.assign_class(obj=project.name, ifc_class="IfcProject")
        bpy.ops.bim.assign_unit()
        bpy.ops.bim.add_subcontext(context="Model")
        bpy.ops.bim.add_subcontext(context="Model", subcontext="Body", target_view="MODEL_VIEW")
        bpy.ops.bim.add_subcontext(context="Model", subcontext="Box", target_view="MODEL_VIEW")
        bpy.ops.bim.add_subcontext(context="Plan")
        bpy.ops.bim.add_subcontext(context="Plan", subcontext="Annotation", target_view="PLAN_VIEW")

        context.scene.BIMProperties.contexts = str(
            ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW").id()
        )

        bpy.ops.bim.assign_class(obj=site.name, ifc_class="IfcSite")
        bpy.ops.bim.assign_class(obj=building.name, ifc_class="IfcBuilding")
        bpy.ops.bim.assign_class(obj=building_storey.name, ifc_class="IfcBuildingStorey")
        bpy.ops.bim.assign_object(related_object=site.name, relating_object=project.name)
        bpy.ops.bim.assign_object(related_object=building.name, relating_object=site.name)
        bpy.ops.bim.assign_object(related_object=building_storey.name, relating_object=building.name)

        return {"FINISHED"}

    def get_name(self, ifc_class, name):
        if not bpy.data.objects.get(f"{ifc_class}/{name}"):
            return name
        i = 2
        while bpy.data.objects.get(f"{ifc_class}/{name} {i}"):
            i += 1
        return f"{name} {i}"

    def rollback(self, data):
        IfcStore.file = None

    def commit(self, data):
        IfcStore.file = data["file"]


class CreateProjectLibrary(bpy.types.Operator):
    bl_idname = "bim.create_project_library"
    bl_label = "Create Project Library"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.add_transaction_operation(self, rollback=self.rollback, commit=lambda data: True)
        result = self._execute(context)
        self.transaction_data = {"file": self.file}
        IfcStore.add_transaction_operation(self, rollback=lambda data: True, commit=self.commit)
        IfcStore.end_transaction(self)
        return result

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.file:
            return {"FINISHED"}

        IfcStore.file = ifcopenshell.api.run(
            "project.create_file", **{"version": context.scene.BIMProperties.export_schema}
        )
        self.file = IfcStore.get_file()

        if self.file.schema == "IFC2X3":
            bpy.ops.bim.add_person()
            bpy.ops.bim.add_organisation()

        project_library = bpy.data.objects.new("My Project Library", None)
        bpy.ops.bim.assign_class(obj=project_library.name, ifc_class="IfcProjectLibrary")
        bpy.ops.bim.assign_unit()
        return {"FINISHED"}

    def rollback(self, data):
        IfcStore.file = None

    def commit(self, data):
        IfcStore.file = data["file"]


class SelectLibraryFile(bpy.types.Operator):
    bl_idname = "bim.select_library_file"
    bl_label = "Select Library File"
    bl_options = {"REGISTER", "UNDO"}
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

        while len(self.props.library_elements) > 0:
            self.props.library_elements.remove(0)

        while len(self.props.library_breadcrumb) > 0:
            self.props.library_breadcrumb.remove(0)

        self.props.active_library_element = ""

        types = IfcStore.library_file.wrapped_data.types_with_super()
        for importable_type in ["IfcTypeProduct", "IfcMaterial", "IfcCostSchedule", "IfcProfileDef"]:
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
        ifc_classes = set()
        self.props.active_library_element = self.element_name
        crumb = self.props.library_breadcrumb.add()
        crumb.name = self.element_name
        elements = IfcStore.library_file.by_type(self.element_name)
        [ifc_classes.add(e.is_a()) for e in elements]
        while len(self.props.library_elements) > 0:
            self.props.library_elements.remove(0)
        if len(ifc_classes) == 1 and list(ifc_classes)[0] == self.element_name:
            for element in elements:
                new = self.props.library_elements.add()
                if element.is_a("IfcProfileDef"):
                    new.name = element.ProfileName or "Unnamed"
                else:
                    new.name = element.Name or "Unnamed"
                new.ifc_definition_id = element.id()
                if IfcStore.library_file.schema == "IFC2X3" or not IfcStore.library_file.by_type("IfcProjectLibrary"):
                    new.is_declared = False
                elif getattr(element, "HasContext", None) and element.HasContext[0].RelatingContext.is_a(
                    "IfcProjectLibrary"
                ):
                    new.is_declared = True
        else:
            for ifc_class in ifc_classes:
                new = self.props.library_elements.add()
                new.name = ifc_class
        return {"FINISHED"}


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
            for collection in bpy.data.collections:
                if "IfcProject/" in collection.name:
                    collection.children.link(type_collection)
                    break

        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        ifc_importer.type_collection = type_collection
        self.import_type_materials(element, ifc_importer)
        self.import_type_styles(element, ifc_importer)
        ifc_importer.create_type_product(element)
        ifc_importer.place_objects_in_spatial_tree()

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

    def execute(self, context):
        context.scene.BIMProjectProperties.is_editing = False
        return {"FINISHED"}
