import bpy
import bmesh


class CalculateEdgeLengths(bpy.types.Operator):
    bl_idname = "bim.calculate_edge_lengths"
    bl_label = "Calculate Edge Lengths"

    def execute(self, context):
        result = 0
        for obj in bpy.context.selected_objects:
            if not obj.data or not obj.data.edges:
                continue
            for edge in obj.data.edges:
                if edge.select:
                    result += (obj.data.vertices[edge.vertices[1]].co - obj.data.vertices[edge.vertices[0]].co).length
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateFaceAreas(bpy.types.Operator):
    bl_idname = "bim.calculate_face_areas"
    bl_label = "Calculate Face Areas"

    def execute(self, context):
        result = 0
        for obj in bpy.context.selected_objects:
            if not obj.data or not obj.data.polygons:
                continue
            for polygon in obj.data.polygons:
                if polygon.select:
                    result += polygon.area
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateObjectVolumes(bpy.types.Operator):
    bl_idname = "bim.calculate_object_volumes"
    bl_label = "Calculate Object Volumes"

    def execute(self, context):
        result = 0
        for obj in bpy.context.selected_objects:
            if not obj.data or not isinstance(obj.data, bpy.types.Mesh):
                continue
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            result += bm.calc_volume()
            bm.free()
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}
