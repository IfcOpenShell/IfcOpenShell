import bpy
import json

from .api import Api

api = Api()

class Login(bpy.types.Operator):
    bl_idname = 'bim.covetool_login'
    bl_label = 'Login to cove.tool'

    def execute(self, context):
        token = api.login(
            bpy.context.scene.CoveToolProperties.username,
            bpy.context.scene.CoveToolProperties.password)
        if token:
            bpy.context.scene.CoveToolProperties.token = token

            projects = api.get_request('projects')
            for project in projects:
                new_project = bpy.context.scene.CoveToolProperties.projects.add()
                new_project.name = project['name']
                new_project.run_set = project['run_set'][0]
                new_project.url = project['url']
        else:
            self.report({'ERROR'}, 'Login failed :(')
        return {'FINISHED'}


class RunSimpleAnalysis(bpy.types.Operator):
    bl_idname = 'bim.covetool_run_simple_analysis'
    bl_label = 'Run Simple Analysis'

    def execute(self, context):
        simple_analysis = bpy.context.scene.CoveToolProperties.simple_analysis
        data = {
            'run': bpy.context.scene.CoveToolProperties.projects[bpy.context.scene.CoveToolProperties.active_project_index].run_set,
            'si_units': simple_analysis.si_units,
            'building_height': simple_analysis.building_height,
            'roof_area': simple_analysis.roof_area,
            'floor_area': simple_analysis.floor_area,
            'skylight_area': simple_analysis.skylight_area,
            'wall_area_e': simple_analysis.wall_area_e,
            'wall_area_ne': simple_analysis.wall_area_ne,
            'wall_area_n': simple_analysis.wall_area_n,
            'wall_area_nw': simple_analysis.wall_area_nw,
            'wall_area_w': simple_analysis.wall_area_w,
            'wall_area_sw': simple_analysis.wall_area_sw,
            'wall_area_s': simple_analysis.wall_area_s,
            'wall_area_se': simple_analysis.wall_area_se,
            'window_area_e': simple_analysis.window_area_e,
            'window_area_ne': simple_analysis.window_area_ne,
            'window_area_n': simple_analysis.window_area_n,
            'window_area_nw': simple_analysis.window_area_nw,
            'window_area_w': simple_analysis.window_area_w,
            'window_area_sw': simple_analysis.window_area_sw,
            'window_area_s': simple_analysis.window_area_s,
            'window_area_se': simple_analysis.window_area_se,
        }
        result = api.post_request('run-values', data)
        covetool_results = bpy.data.texts.new('cove.tool Results')
        covetool_results.write(json.dumps(result, indent=4))
        return {'FINISHED'}
