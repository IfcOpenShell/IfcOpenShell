import bpy
import logging
import ifcopenshell
import blenderbim.bim.module.project.create_file as create_file
import blenderbim.bim.module.context.add_context as add_context
import blenderbim.bim.module.root.create_product as create_product
import blenderbim.bim.module.aggregate.assign_object as assign_object
import bpy
from blenderbim.bim.ifc import IfcStore

# from blenderbim.bim.module.project.data import Data


class CreateProject(bpy.types.Operator):
    bl_idname = "bim.create_project"
    bl_label = "Create Project"

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.file:
            return {"FINISHED"}

        IfcStore.file = create_file.Usecase({"version": bpy.context.scene.BIMProperties.export_schema}).execute()
        self.file = IfcStore.get_file()

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

    def assign_object(self, product, relating_object):
        assign_object.Usecase(
            self.file,
            {
                "product": product,
                "relating_object": relating_object,
            },
        ).execute()


class ValidateIfcFile(bpy.types.Operator):
    bl_idname = "bim.validate_ifc_file"
    bl_label = "Validate IFC File"

    def execute(self, context):
        import ifcopenshell.validate

        logger = logging.getLogger("validate")
        logger.setLevel(logging.DEBUG)
        ifcopenshell.validate.validate(IfcStore.get_file(), logger)
        return {"FINISHED"}
