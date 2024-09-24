from math import pi
from mathutils import Vector
import bpy
import gpu
import blf
from bpy_extras import view3d_utils
from bpy.types import SpaceView3D
from gpu_extras.batch import batch_for_shader
from bonsai.bim.module.structural.shader import ShaderInfo

class LoadsDecorator:
    is_installed = False
    handlers = []
    linear_load_shader = None
    text_info = []
    shader_info = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_load_values, ((context,)), "WINDOW", "POST_PIXEL")
            )
        #self.handlers.append(SpaceView3D.draw_handler_add(handler.draw_extra_info, (context,), "WINDOW", "POST_PIXEL"))
        #self.handlers.append(
        #	SpaceView3D.draw_handler_add(handler.draw_curve_loads, (context,), "WINDOW", "POST_VIEW")
        #)
        cls.handlers.append(SpaceView3D.draw_handler_add(handler, (), "WINDOW", "POST_VIEW"))
        cls.linear_load_shader = ShaderInfo("DistributedLoad")
        cls.update(context)
        cls.is_installed = True

    @classmethod
    def uninstall(cls):
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.is_installed = False

    @classmethod
    def update(cls, context):
        cls.linear_load_shader.update()
        cls.text_info = cls.linear_load_shader.text_info
        cls.shader_info = cls.linear_load_shader.info

    def __call__(self):
        # set open gl configurations
        original_blend = gpu.state.blend_get()
        gpu.state.blend_set('ADDITIVE')
        original_depth_mask = gpu.state.depth_mask_get()
        #gpu.state.depth_mask_set(True)
        original_depth_test = gpu.state.depth_test_get()
        gpu.state.depth_test_set('ALWAYS')

        self.draw_batch("DistributedLoad")

        # restore opengl configurations
        gpu.state.blend_set(original_blend)
        gpu.state.depth_mask_set(original_depth_mask)
        gpu.state.depth_test_set(original_depth_test)

    def draw_batch(self,shader_type: str):
        """ param: shader_type: type of shader in ["DistributedLoad", "PointLoad"]"""

        if not self.linear_load_shader.is_empty:
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

    def draw_load_values(self, context):
        for info in self.text_info:
            text_position = location_3d_to_region_2d(info["position"],info["normal"],context)
            if text_position is not None:
                font_id = 0  # , need to find out how best to get this.
                # draw some text
                blf.position(font_id, text_position[0], text_position[1], 0)
                blf.size(font_id, 20.0)
                blf.color(font_id, 0.9, 0.9, 0.9, 1.0)
                blf.draw(font_id, info["text"])

def location_3d_to_region_2d(coord, normal, context):
    """Convert from 3D space to 2D screen space"""
    rv3d = context.region_data
    perspective = rv3d.view_perspective
    view_matrix = rv3d.view_matrix
    point_view_space = view_matrix @ coord

    if perspective == 'ORTHO' or -20 < point_view_space.z < 0:
        prj = rv3d.perspective_matrix @ Vector((coord[0], coord[1], coord[2], 1.0))
        width_half = context.region.width / 2.0
        height_half = context.region.height / 2.0
        co = Vector((width_half + width_half * (prj.x / prj.w),
                    height_half + height_half * (prj.y / prj.w),
                    ))
        view_vector = view3d_utils.region_2d_to_vector_3d(context.region, rv3d, co)
        angle = abs(0.5*pi-normal.angle(view_vector))
        #if small view angle betwen the load and viewport
        if angle<0.05:
            return None
        return co
    return None
