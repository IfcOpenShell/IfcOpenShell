import bpy


class OpenPieClass(bpy.types.Operator):
    bl_idname = "bim.open_pie_class"
    bl_label = "Open Pie Class"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_PIE_bim_class")
        return {"FINISHED"}


class AssignIfcWall(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_wall"
    bl_label = "IfcWall"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcWall")
        return {"FINISHED"}


class AssignIfcSlab(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_slab"
    bl_label = "IfcSlab"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcSlab")
        return {"FINISHED"}


class AssignIfcStair(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_stair"
    bl_label = "IfcStair"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcStair")
        return {"FINISHED"}


class AssignIfcDoor(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_door"
    bl_label = "IfcDoor"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcDoor")
        return {"FINISHED"}


class AssignIfcWindow(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_window"
    bl_label = "IfcWindow"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcWindow")
        return {"FINISHED"}


class AssignIfcColumn(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_column"
    bl_label = "IfcColumn"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcColumn")
        return {"FINISHED"}


class AssignIfcBeam(bpy.types.Operator):
    bl_idname = "bim.assign_ifc_beam"
    bl_label = "IfcBeam"

    def execute(self, context):
        bpy.ops.bim.assign_class(ifc_class="IfcBeam")
        return {"FINISHED"}


class PieAddOpening(bpy.types.Operator):
    bl_idname = "bim.pie_add_opening"
    bl_label = "Add Opening"

    def execute(self, context):
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

    def execute(self, context):
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
        pie.operator("bim.update_mesh_representation")
        pie.operator("bim.pie_add_opening")
        pie.operator("bim.pie_update_container")
        pie.operator("bim.open_pie_class", text="Assign IFC Class")


class VIEW3D_MT_PIE_bim_class(bpy.types.Menu):
    bl_label = "IFC Class"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator("bim.assign_ifc_wall")
        pie.operator("bim.assign_ifc_slab")
        pie.operator("bim.assign_ifc_stair")
        pie.operator("bim.assign_ifc_door")
        pie.operator("bim.assign_ifc_window")
        pie.operator("bim.assign_ifc_column")
        pie.operator("bim.assign_ifc_beam")
