from math import pi
from mathutils import Vector
import numpy as np
import bpy
import gpu
import blf
from bpy_extras import view3d_utils
from bpy.types import SpaceView3D
from gpu_extras.batch import batch_for_shader
from typing import Iterable, Union
from bonsai.bim.module.structural.shader import ShaderInfo

class LoadsDecorator:
    """Decorator to show strucutural loads in 3D"""
    is_installed = False
    handlers = []
    decoration_data = None
    text_info = []
    shader_info = []
    depth_array = None

    @classmethod
    def install(cls, context: bpy.types.Context)-> None:
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_load_values, ((context,)), "WINDOW", "POST_PIXEL")
            )
        cls.handlers.append(SpaceView3D.draw_handler_add(handler, (), "WINDOW", "POST_VIEW"))
        cls.decoration_data = ShaderInfo()
        cls.update(context)
        cls.is_installed = True

    @classmethod
    def uninstall(cls)-> None:
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.is_installed = False

    @classmethod
    def update(cls, context:bpy.types.Context) -> None:
        cls.decoration_data.update()
        cls.text_info = cls.decoration_data.text_info
        cls.shader_info = cls.decoration_data.info

    def __call__(self) -> None:
        """set gpu configurations to draw 3D representations"""
        # set open gl configurations
        original_blend = gpu.state.blend_get()
        original_depth_test = gpu.state.depth_test_get()
        gpu.state.blend_set('ALPHA')
        gpu.state.depth_test_set('LESS_EQUAL')

        self.draw_batch()

        # restore opengl configurations
        gpu.state.blend_set(original_blend)
        gpu.state.depth_test_set(original_depth_test)

    def draw_batch(self) -> None:
        """draw the 3D representation of loads"""
        if not self.decoration_data.is_empty:
            for info in self.shader_info: 
                shader = info["shader"]
                args = info["args"]
                indices = info["indices"]
                batch = batch_for_shader(shader, 'TRIS', args, indices=indices)
                matrix = bpy.context.region_data.perspective_matrix
                shader.bind()
                shader.uniform_float("viewProjectionMatrix", matrix)

                for key, value in info["uniforms"]:
                    shader.uniform_float(key, value)

                batch.draw(shader)

    def draw_load_values(self, context: bpy.types.Context) -> None:
        """draw text representing the load values"""
        #getting depth buffer info, code adapted from:
        #https://blender.stackexchange.com/questions/177185/is-there-a-way-to-render-depth-buffer-into-a-texture-with-gpu-bgl-python-modules
        framebuffer = gpu.state.active_framebuffer_get()
        viewport_info = gpu.state.viewport_get()
        width = viewport_info[2]
        height = viewport_info[3]
        depth_buffer = framebuffer.read_depth(0, 0, width, height)
        depth_array = np.array(depth_buffer.to_list())

        f = context.area.spaces.active.clip_end
        n = context.area.spaces.active.clip_start

        self.depth_array = n / (f - (f - n) * depth_array) * (f - n)

        for info in self.text_info:
            text_position = self.location_3d_to_region_2d(info["position"],info["normal"],context)
            if text_position is not None:
                font_id = 0
                blf.position(font_id, text_position[0], text_position[1], text_position[2])
                blf.size(font_id, 20.0)
                blf.color(font_id, 0.9, 0.9, 0.9, 1.0)
                blf.draw(font_id, info["text"])

    def location_3d_to_region_2d(self, coord: Iterable, normal: Iterable, context: bpy.types.Context) -> Union[Vector,None]:
        """Convert from 3D space to 2D screen space.
        Filter out the text supposed to be hidden by 3D elements, using the depth array.
        It also hides text that are distant from the camera view to avoid clutter"""

        coord = Vector(coord)
        normal = Vector(normal)
        rv3d = context.region_data
        perspective = rv3d.view_perspective
        view_matrix = rv3d.view_matrix
        point_view_space = view_matrix @ coord


        if perspective == 'ORTHO' or -10 < point_view_space.z < 0:
            prj = rv3d.perspective_matrix @ Vector((coord[0], coord[1], coord[2], 1.0))
            width_half = context.region.width / 2.0
            height_half = context.region.height / 2.0
            coord_2d = Vector((width_half + width_half * (prj.x / prj.w),
                        height_half + height_half * (prj.y / prj.w),
                        point_view_space.z))
            if coord_2d[0] < 0 or coord_2d[0]> context.region.width or coord_2d[1] > context.region.height or coord_2d[1] < 0:
                return None
            depth = self.depth_array[int(coord_2d[1])][int(coord_2d[0])]
            if -0.98*point_view_space.z > depth:
                return None
            return coord_2d
        return None
