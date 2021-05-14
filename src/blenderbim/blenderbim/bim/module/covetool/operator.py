import bpy
import json
import ifcopenshell
import ifcopenshell.util.element
from math import degrees, atan2
from blenderbim.bim.ifc import IfcStore

from .api import Api

api = Api()


class Login(bpy.types.Operator):
    bl_idname = "bim.covetool_login"
    bl_label = "Login to cove.tool"

    def execute(self, context):
        token = api.login(bpy.context.scene.CoveToolProperties.username, bpy.context.scene.CoveToolProperties.password)
        if token:
            bpy.context.scene.CoveToolProperties.token = token

            projects = api.get_request("projects")
            for project in projects:
                new_project = bpy.context.scene.CoveToolProperties.projects.add()
                new_project.name = project["name"]
                new_project.run_set = project["run_set"][0]
                new_project.url = project["url"]
        else:
            self.report({"ERROR"}, "Login failed :(")
        return {"FINISHED"}


class RunSimpleAnalysis(bpy.types.Operator):
    bl_idname = "bim.covetool_run_simple_analysis"
    bl_label = "Run Simple Analysis"

    def execute(self, context):
        simple_analysis = bpy.context.scene.CoveToolProperties.simple_analysis
        data = {
            "run": bpy.context.scene.CoveToolProperties.projects[
                bpy.context.scene.CoveToolProperties.active_project_index
            ].run_set,
            "si_units": simple_analysis.si_units,
            "building_height": simple_analysis.building_height,
            "roof_area": simple_analysis.roof_area,
            "floor_area": simple_analysis.floor_area,
            "skylight_area": simple_analysis.skylight_area,
            "wall_area_e": simple_analysis.wall_area_e,
            "wall_area_ne": simple_analysis.wall_area_ne,
            "wall_area_n": simple_analysis.wall_area_n,
            "wall_area_nw": simple_analysis.wall_area_nw,
            "wall_area_w": simple_analysis.wall_area_w,
            "wall_area_sw": simple_analysis.wall_area_sw,
            "wall_area_s": simple_analysis.wall_area_s,
            "wall_area_se": simple_analysis.wall_area_se,
            "window_area_e": simple_analysis.window_area_e,
            "window_area_ne": simple_analysis.window_area_ne,
            "window_area_n": simple_analysis.window_area_n,
            "window_area_nw": simple_analysis.window_area_nw,
            "window_area_w": simple_analysis.window_area_w,
            "window_area_sw": simple_analysis.window_area_sw,
            "window_area_s": simple_analysis.window_area_s,
            "window_area_se": simple_analysis.window_area_se,
        }
        result = api.post_request("run-values", data)
        covetool_results = bpy.data.texts.new("cove.tool Results")
        covetool_results.write(json.dumps(result, indent=4))
        return {"FINISHED"}


class RunAnalysis(bpy.types.Operator):
    bl_idname = "bim.covetool_run_analysis"
    bl_label = "Run Analysis"

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.inputs = {
            "floors": [],
            "walls": [],
            "interior_walls": [],
            "windows": [],
            "skylights": [],
            "roofs": [],
            "shading_devices": [],
        }
        self.parse_objects()
        data = {
            "run": bpy.context.scene.CoveToolProperties.projects[
                bpy.context.scene.CoveToolProperties.active_project_index
            ].run_set,
            "source": "BlenderBIM",
            "rotation_angle": self.get_rotation_angle(),
            **self.inputs,
        }
        result = api.post_request("run-values", data)
        covetool_results = bpy.data.texts.new("cove.tool Results")
        covetool_results.write(json.dumps(result, indent=4))
        return {"FINISHED"}

    def get_rotation_angle(self):
        if not self.file.by_type("IfcMapConversion"):
            return 0
        map_conversion = self.file.by_type("IfcMapConversion")[0]
        rotation = -1 * degrees(
            atan2(
                float(map_conversion.XAxisOrdinate or 0),
                float(map_conversion.XAxisAbscissa or 1),
            )
        )
        if rotation < 0:
            rotation = 360 - rotation
        return rotation

    def parse_objects(self):
        for obj in bpy.context.visible_objects:
            covetool_category = self.get_covetool_category(obj)
            if not covetool_category:
                continue
            if not self.has_triangulate_modifier(obj):
                obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
            mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
            meshes = {}
            for polygon in mesh.polygons:
                normal = "{}|{}|{}".format(
                    round(polygon.normal[0], 2), round(polygon.normal[1], 2), round(polygon.normal[2], 2)
                )
                meshes.setdefault(
                    normal,
                    {
                        "Mesh": {"vertex_indices": {}, "Vertices": [], "Triangles": []},
                        "Center": {},
                        "Normal": {
                            "X": round(polygon.normal[0], 2),
                            "Y": round(polygon.normal[1], 2),
                            "Z": round(polygon.normal[2], 2),
                        },
                    },
                )
                for vertex in polygon.vertices:
                    global_vertex = obj.matrix_world @ mesh.vertices[vertex].co
                    meshes[normal]["Mesh"]["vertex_indices"][vertex] = {
                        "X": global_vertex[0] * 3.28084,  # Covetools require feet
                        "Y": global_vertex[1] * 3.28084,
                        "Z": global_vertex[2] * 3.28084,
                    }
                meshes[normal]["Mesh"]["Triangles"].append(
                    [polygon.vertices[0], polygon.vertices[1], polygon.vertices[2]]
                )
            for normal, mesh in meshes.items():
                sorted_keys = sorted(mesh["Mesh"]["vertex_indices"])
                mesh["Mesh"]["Vertices"] = [mesh["Mesh"]["vertex_indices"][k] for k in sorted_keys]
                for triangle in mesh["Mesh"]["Triangles"]:
                    triangle[0] = sorted_keys.index(triangle[0])
                    triangle[1] = sorted_keys.index(triangle[1])
                    triangle[2] = sorted_keys.index(triangle[2])
                mesh["Center"] = mesh["Mesh"]["Vertices"][0]  # Not correct, but just for now
                del mesh["Mesh"]["vertex_indices"]
            self.inputs[covetool_category].extend(meshes.values())

    def has_triangulate_modifier(self, obj):
        for modifier in obj.modifiers:
            if modifier.type == "TRIANGULATE":
                return True

    def get_covetool_category(self, obj):
        if not hasattr(obj, "data") or not isinstance(obj.data, bpy.types.Mesh):
            return
        if not obj.BIMObjectProperties.ifc_definition_id:
            return
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        ifc_class = element.is_a()
        if "IfcSlab" in ifc_class:
            return "floors"
        elif "IfcRoof" in ifc_class:
            return "roofs"
        elif "IfcWall" in ifc_class:
            if self.is_wall_internal(element):
                return "interior_walls"
            return "walls"
        elif "IfcWindow" in ifc_class:
            if self.is_window_skylight(element):
                return "skylights"
            return "windows"
        elif "IfcShadingDevice" in ifc_class:
            return "shading_devices"

    def is_wall_internal(self, element):
        psets = ifcopenshell.util.element.get_psets(element)
        pset = psets.get("Pset_WallCommon")
        if pset:
            is_external = pset.get("IsExternal", None)
            if is_external is not None:
                return is_external
        predefined_type = element.get_info().get("PredefinedType")
        if predefined_type and predefined_type in ["MOVABLE", "PARTITIONING", "PLUMBINGWALL"]:
            return True

    def is_window_skylight(self, element):
        predefined_type = element.get_info().get("PredefinedType")
        return predefined_type and predefined_type.string_value == "SKYLIGHT"
