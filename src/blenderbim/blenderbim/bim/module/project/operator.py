import bpy
import logging
import ifcopenshell
import ifcopenshell.api
import bpy
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim import import_ifc


class CreateProject(bpy.types.Operator):
    bl_idname = "bim.create_project"
    bl_label = "Create Project"

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.file:
            return {"FINISHED"}

        IfcStore.file = ifcopenshell.api.run(
            "project.create_file", **{"version": bpy.context.scene.BIMProperties.export_schema}
        )
        self.file = IfcStore.get_file()

        bpy.ops.bim.add_person()
        bpy.ops.bim.add_organisation()

        project = bpy.data.objects.new("My Project", None)
        site = bpy.data.objects.new("My Site", None)
        building = bpy.data.objects.new("My Building", None)
        building_storey = bpy.data.objects.new("Ground Floor", None)

        bpy.ops.bim.assign_class(obj=project.name, ifc_class="IfcProject")
        bpy.ops.bim.assign_unit()
        bpy.ops.bim.add_subcontext(context="Model")
        bpy.ops.bim.add_subcontext(context="Model", subcontext="Body", target_view="MODEL_VIEW")
        bpy.ops.bim.add_subcontext(context="Model", subcontext="Box", target_view="MODEL_VIEW")
        bpy.ops.bim.add_subcontext(context="Plan")
        bpy.ops.bim.add_subcontext(context="Plan", subcontext="Annotation", target_view="PLAN_VIEW")

        for subcontext in self.file.by_type("IfcGeometricRepresentationSubContext"):
            if subcontext.ContextIdentifier == "Body":
                bpy.context.scene.BIMProperties.contexts = str(subcontext.id())
                break

        bpy.ops.bim.assign_class(obj=site.name, ifc_class="IfcSite")
        bpy.ops.bim.assign_class(obj=building.name, ifc_class="IfcBuilding")
        bpy.ops.bim.assign_class(obj=building_storey.name, ifc_class="IfcBuildingStorey")
        bpy.ops.bim.assign_object(related_object=site.name, relating_object=project.name)
        bpy.ops.bim.assign_object(related_object=building.name, relating_object=site.name)
        bpy.ops.bim.assign_object(related_object=building_storey.name, relating_object=building.name)
        # Data.load()
        return {"FINISHED"}


class CreateProjectLibrary(bpy.types.Operator):
    bl_idname = "bim.create_project_library"
    bl_label = "Create Project Library"

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.file:
            return {"FINISHED"}

        IfcStore.file = ifcopenshell.api.run(
            "project.create_file", **{"version": bpy.context.scene.BIMProperties.export_schema}
        )
        self.file = IfcStore.get_file()

        if self.file.schema == "IFC2X3":
            bpy.ops.bim.add_person()
            bpy.ops.bim.add_organisation()

        project_library = bpy.data.objects.new("My Project Library", None)
        bpy.ops.bim.assign_class(obj=project_library.name, ifc_class="IfcProjectLibrary")
        bpy.ops.bim.assign_unit()
        return {"FINISHED"}


class ValidateIfcFile(bpy.types.Operator):
    bl_idname = "bim.validate_ifc_file"
    bl_label = "Validate IFC File"

    def execute(self, context):
        import ifcopenshell.validate

        logger = logging.getLogger("validate")
        logger.setLevel(logging.DEBUG)
        ifcopenshell.validate.validate(IfcStore.get_file(), logger)
        return {"FINISHED"}


class SelectLibraryFile(bpy.types.Operator):
    bl_idname = "bim.select_library_file"
    bl_label = "Select Library File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})

    def execute(self, context):
        IfcStore.library_path = self.filepath
        IfcStore.library_file = ifcopenshell.open(self.filepath)
        bpy.ops.bim.refresh_library()
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


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
        if "IfcTypeProduct" in types:
            new = self.props.library_elements.add()
            new.name = "IfcTypeProduct"
        return {"FINISHED"}


class ChangeLibraryElement(bpy.types.Operator):
    bl_idname = "bim.change_library_element"
    bl_label = "Change Library Element"
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
        if len(ifc_classes) == 1:
            for element in elements:
                new = self.props.library_elements.add()
                new.name = element.Name or "Unnamed"
                new.ifc_definition_id = element.id()
                if IfcStore.library_file.schema == "IFC2X3" or not IfcStore.library_file.by_type("IfcProjectLibrary"):
                    new.is_declared = False
                elif element.HasContext and element.HasContext[0].RelatingContext.is_a("IfcProjectLibrary"):
                    new.is_declared = True
        else:
            for ifc_class in ifc_classes:
                new = self.props.library_elements.add()
                new.name = ifc_class
        return {"FINISHED"}


class RewindLibrary(bpy.types.Operator):
    bl_idname = "bim.rewind_library"
    bl_label = "Rewind Library"

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
    definition: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties
        ifcopenshell.api.run(
            "project.assign_declaration",
            IfcStore.library_file,
            definition=IfcStore.library_file.by_id(self.definition),
            relating_context=IfcStore.library_file.by_type("IfcProjectLibrary")[0],
        )
        element_name = self.props.active_library_element
        bpy.ops.bim.rewind_library()
        bpy.ops.bim.change_library_element(element_name = element_name)
        return {"FINISHED"}


class UnassignLibraryDeclaration(bpy.types.Operator):
    bl_idname = "bim.unassign_library_declaration"
    bl_label = "Unassign Library Declaration"
    definition: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMProjectProperties
        ifcopenshell.api.run(
            "project.unassign_declaration",
            IfcStore.library_file,
            definition=IfcStore.library_file.by_id(self.definition),
            relating_context=IfcStore.library_file.by_type("IfcProjectLibrary")[0],
        )
        element_name = self.props.active_library_element
        bpy.ops.bim.rewind_library()
        bpy.ops.bim.change_library_element(element_name = element_name)
        return {"FINISHED"}


class SaveLibraryFile(bpy.types.Operator):
    bl_idname = "bim.save_library_file"
    bl_label = "Save Library File"

    def execute(self, context):
        IfcStore.library_file.write(IfcStore.library_path)
        return {"FINISHED"}


class AppendLibraryElement(bpy.types.Operator):
    bl_idname = "bim.append_library_element"
    bl_label = "Append Library Element"
    definition: bpy.props.IntProperty()

    def execute(self, context):
        element = ifcopenshell.api.run(
            "project.append_asset",
            IfcStore.get_file(),
            element=IfcStore.library_file.by_id(self.definition),
        )
        self.import_type_from_ifc(element)
        return {"FINISHED"}

    def import_type_from_ifc(self, element):
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, IfcStore.path, logger)

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
        ifc_importer.create_type_product(element)
        ifc_importer.place_objects_in_spatial_tree()
