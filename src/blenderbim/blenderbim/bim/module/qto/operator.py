import bpy
import bmesh
import ifcopenshell
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.qto import helper
from ifcopenshell.api.pset.data import Data as PsetData


class CalculateEdgeLengths(bpy.types.Operator):
    bl_idname = "bim.calculate_edge_lengths"
    bl_label = "Calculate Edge Lengths"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        result = 0
        for obj in context.selected_objects:
            if not obj.data or not obj.data.edges:
                continue
            for edge in obj.data.edges:
                if edge.select:
                    result += (obj.data.vertices[edge.vertices[1]].co - obj.data.vertices[edge.vertices[0]].co).length
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateFaceAreas(bpy.types.Operator):
    bl_idname = "bim.calculate_face_areas"
    bl_label = "Calculate Face Areas"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        result = 0
        for obj in context.selected_objects:
            if not obj.data or not obj.data.polygons:
                continue
            for polygon in obj.data.polygons:
                if polygon.select:
                    result += polygon.area
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateObjectVolumes(bpy.types.Operator):
    bl_idname = "bim.calculate_object_volumes"
    bl_label = "Calculate Object Volumes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        result = 0
        for obj in context.selected_objects:
            if not obj.data or not isinstance(obj.data, bpy.types.Mesh):
                continue
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            result += bm.calc_volume()
            bm.free()
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class ExecuteQtoMethod(bpy.types.Operator):
    bl_idname = "bim.execute_qto_method"
    bl_label = "Execute Qto Method"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.BIMQtoProperties
        result = 0
        if props.qto_methods == "HEIGHT":
            for obj in context.selected_objects:
                result += helper.calculate_height(obj)
        elif props.qto_methods == "VOLUME":
            for obj in context.selected_objects:
                result += helper.calculate_volume(obj)
        elif props.qto_methods == "FORMWORK":
            result = helper.calculate_formwork_area(context.selected_objects, context)
        props.qto_result = str(round(result, 3))
        return {"FINISHED"}


class QuantifyObjects(bpy.types.Operator):
    bl_idname = "bim.quantify_objects"
    bl_label = "Quantify Objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMQtoProperties
        self.file = IfcStore.get_file()
        for obj in context.selected_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            result = 0
            if props.qto_methods == "HEIGHT":
                result = helper.calculate_height(obj)
            elif props.qto_methods == "VOLUME":
                result = helper.calculate_volume(obj)
            elif props.qto_methods == "FORMWORK":
                result = helper.calculate_formwork_area([obj], context)
            if not result:
                continue
            result = round(result, 3)
            qto = ifcopenshell.api.run(
                "pset.add_qto",
                self.file,
                product=self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                name=props.qto_name,
            )
            ifcopenshell.api.run(
                "pset.edit_qto",
                self.file,
                qto=qto,
                properties={props.prop_name: result}
            )
            PsetData.load(self.file, obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}
