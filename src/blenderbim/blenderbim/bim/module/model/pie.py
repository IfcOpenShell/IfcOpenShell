import bpy
from blenderbim.bim.ifc import IfcStore

class OpenPieClass(bpy.types.Operator):
    bl_idname = "bim.open_pie_class"
    bl_label = "Open Pie Class"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_bim_class")
        return {"FINISHED"}


class PieAddOpening(bpy.types.Operator):
    bl_idname = "bim.pie_add_opening"
    bl_label = "Add Opening"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if len(context.selected_objects) == 2:
            opening_name = None
            obj_name = None
            for obj in context.selected_objects:
                if "IfcOpeningElement" in obj.name or not obj.BIMObjectProperties.ifc_definition_id:
                    opening_name = obj.name
                elif len(obj.children) == 1 and not obj.children[0].BIMObjectProperties.ifc_definition_id:
                    opening_name = obj.children[0].name
                else:
                    opj_name = obj.name
            bpy.ops.bim.add_opening(obj=opj_name, opening=opening_name)
        return {"FINISHED"}


class PieUpdateContainer(bpy.types.Operator):
    bl_idname = "bim.pie_update_container"
    bl_label = "Update Spatial Container"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        for obj in context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            for collection in obj.users_collection:
                spatial_obj = bpy.data.objects.get(collection.name)
                if spatial_obj and spatial_obj.BIMObjectProperties.ifc_definition_id:
                    bpy.ops.bim.assign_container(
                        relating_structure=spatial_obj.BIMObjectProperties.ifc_definition_id, related_element=obj.name
                    )
                    break
        return {"FINISHED"}


class VIEW3D_MT_PIE_bim(bpy.types.Menu):
    bl_label = "Geometry"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("bim.edit_object_placement")
        pie.operator("bim.update_representation")
        pie.operator("bim.pie_add_opening")
        pie.operator("bim.pie_update_container")
        pie.operator("bim.open_pie_class", text="Assign IFC Class")


class VIEW3D_MT_PIE_bim_class(bpy.types.Menu):
    bl_label = "IFC Class"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("bim.assign_class", text="IfcWall").ifc_class = "IfcWall"
        pie.operator("bim.assign_class", text="IfcSlab").ifc_class = "IfcSlab"
        pie.operator("bim.assign_class", text="IfcStair").ifc_class = "IfcStair"
        pie.operator("bim.assign_class", text="IfcDoor").ifc_class = "IfcDoor"
        pie.operator("bim.assign_class", text="IfcWindow").ifc_class = "IfcWindow"
        pie.operator("bim.assign_class", text="IfcColumn").ifc_class = "IfcColumn"
        pie.operator("bim.assign_class", text="IfcBeam").ifc_class = "IfcBeam"
