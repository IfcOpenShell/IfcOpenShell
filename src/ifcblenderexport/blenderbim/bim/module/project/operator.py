import bpy
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

        project = bpy.data.collections.new("My Project")
        site = bpy.data.collections.new("My Site")
        building = bpy.data.collections.new("My Building")
        building_storey = bpy.data.collections.new("Ground Floor")

        project_obj = bpy.data.objects.new("My Project", None)
        site_obj = bpy.data.objects.new("My Site", None)
        building_obj = bpy.data.objects.new("My Building", None)
        building_storey_obj = bpy.data.objects.new("Ground Floor", None)

        bpy.context.scene.collection.children.link(project)
        project.children.link(site)
        site.children.link(building)
        building.children.link(building_storey)

        project.objects.link(project_obj)
        site.objects.link(site_obj)
        building.objects.link(building_obj)
        building_storey.objects.link(building_storey_obj)

        bpy.ops.bim.assign_class(obj=project_obj.name, ifc_class="IfcProject")
        bpy.ops.bim.assign_unit()
        bpy.ops.bim.add_subcontext(context="Model")
        bpy.ops.bim.add_subcontext(context="Model", subcontext="Body", target_view="MODEL_VIEW")
        bpy.ops.bim.add_subcontext(context="Model", subcontext="Box", target_view="MODEL_VIEW")
        bpy.ops.bim.add_subcontext(context="Plan")
        bpy.ops.bim.add_subcontext(context="Plan", subcontext="Annotation", target_view="PLAN_VIEW")
        bpy.ops.bim.assign_class(obj=site_obj.name, ifc_class="IfcSite")
        bpy.ops.bim.assign_class(obj=building_obj.name, ifc_class="IfcBuilding")
        bpy.ops.bim.assign_class(obj=building_storey_obj.name, ifc_class="IfcBuildingStorey")
        bpy.ops.bim.assign_object(related_object=site_obj.name, relating_object=project_obj.name)
        bpy.ops.bim.assign_object(related_object=building_obj.name, relating_object=site_obj.name)
        bpy.ops.bim.assign_object(related_object=building_storey_obj.name, relating_object=building_obj.name)
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
