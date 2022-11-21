# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Maxim Vasilyev <qwiglydee@gmail.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import gpu
import bpy
import blf
import bgl
import math
import bmesh
import blenderbim.tool as tool
import blenderbim.bim.module.drawing.helper as helper
from functools import reduce
from itertools import chain
from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader


class BaseDecorator:
    # base name of objects to decorate
    objecttype = "NOTDEFINED"

    DEF_GLSL = """
        #define PI 3.141592653589793
        #define MAX_POINTS 64
        #define CIRCLE_SEGS 12
    """

    LIB_GLSL = """
    #define matCLIP2WIN() vec4(winsize.x/2, winsize.y/2, 1, 1)
    #define matWIN2CLIP() vec4(2/winsize.x, 2/winsize.y, 1, 1)
    #define CLIP2WIN(v) (clip2win * v / v.w)
    #define WIN2CLIP(v) (win2clip * v * v.w)

    void arrow_head(in vec4 dir, in float size, in float angle, out vec4 head[3]) {
        vec4 nose = dir * size;
        float c = cos(angle), s = sin(angle);
        head[0] = nose;
        head[1] = vec4(mat2(c, -s, +s, c) * nose.xy, 0, 0);
        head[2] = vec4(mat2(c, +s, -s, c) * nose.xy, 0, 0);
    }

    void circle_head(in float size, out vec4 head[CIRCLE_SEGS]) {
        float angle_d = PI * 2 / CIRCLE_SEGS;
        for(int i = 0; i<CIRCLE_SEGS; i++) {
            float angle = angle_d * i;
            head[i] = vec4(cos(angle), sin(angle), 0, 0) * size;
        }
    }

    void cross_head(in vec4 dir, in float size, out vec4 head[3]) {
        vec4 nose = dir * size;
        float c = cos(PI/2), s = sin(PI/2);
        head[0] = nose;
        head[1] = vec4(mat2(c, -s, +s, c) * nose.xy, 0, 0);
        head[2] = vec4(mat2(c, +s, -s, c) * nose.xy, 0, 0);
    }
    """

    VERT_GLSL = """
    uniform mat4 viewMatrix;
    in vec3 pos;
    in uint topo;
    out vec4 gl_Position;
    out uint type;

    void main() {
        gl_Position = viewMatrix * vec4(pos, 1.0);
        type = topo;
    }
    """

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=2) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    out vec4 fragColor;

    void main() {
        fragColor = color;
    }
    """

    def __init__(self):
        # NB: libcode param doesn't work
        self.shader = GPUShader(
            vertexcode=self.VERT_GLSL,
            fragcode=self.FRAG_GLSL,
            geocode=self.LIB_GLSL + self.GEOM_GLSL,
            defines=self.DEF_GLSL,
        )

        # Horrific prototype code to ensure bgl draws at drawing scales
        # https://blender.stackexchange.com/questions/16493/is-there-a-way-to-fit-the-viewport-to-the-current-field-of-view
        def is_landscape(render):
            return render.resolution_x > render.resolution_y

        def get_scale(camera):
            if camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
                human_scale, fraction = camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
            else:
                human_scale, fraction = camera.data.BIMCameraProperties.diagram_scale.split("|")
            numerator, denominator = fraction.split("/")
            return float(numerator) / float(denominator)

        camera = bpy.context.scene.camera
        render = bpy.context.scene.render
        if is_landscape(render):
            camera_width_model = camera.data.ortho_scale
        else:
            camera_width_model = camera.data.ortho_scale / render.resolution_y * render.resolution_x
        self.camera_width_mm = get_scale(camera) * camera_width_model

        self.font_id = blf.load(
            os.path.join(bpy.context.scene.BIMProperties.data_dir, "fonts", "OpenGost Type B TT.ttf")
        )

    def camera_zoom_to_factor(self, zoom):
        return math.pow(((zoom / 50) + math.sqrt(2)) / 2, 2)

    def get_objects(self, collection):
        """find relevant objects
        using class.objecttype

        returns: iterable of blender objects
        """
        results = []
        decoration_presets = (
            "DIMENSION",
            "TEXT_LEADER",
            "STAIR_ARROW",
            "HIDDEN_LINE",
            "PLAN_LEVEL",
            "SECTION_LEVEL",
            "BREAKLINE",
            "GRID",
            "ELEVATION",
            "SECTION",
            "TEXT",
        )
        for obj in collection.all_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            if element.is_a("IfcAnnotation"):
                if element.ObjectType == self.objecttype:
                    results.append(obj)
                elif (
                    self.objecttype == "MISC"
                    and element.ObjectType not in decoration_presets
                    and isinstance(obj.data, bpy.types.Mesh)
                ):
                    results.append(obj)
        return results

    def get_path_geom(self, obj, topo=True):
        """Parses path geometry into line segments

        Args:
          obj: Blender object with data of type Curve
          topo: bool; if types of vertices are needed

        Returns:
          vertices: 3-tuples of coords
          indices: 2-tuples of each segment verices' indices
          topology: types of vertices
            0: internal
            1: beginning
            2: ending
        """
        vertices = []
        indices = []
        topology = []

        idx = 0
        for spline in obj.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            if len(spline_points) < 2:
                continue
            points = [obj.matrix_world @ p.co for p in spline_points]
            cnt = len(points)
            vertices.extend(p[:3] for p in points)
            if topo:
                topology.append(1)
                topology.extend([0] * max(0, cnt - 2))
                topology.append(2)
            indices.extend((idx + i, idx + i + 1) for i in range(cnt - 1))
            idx += cnt

        return vertices, indices, topology

    def get_mesh_geom(self, obj):
        """Parses mesh geometry into line segments

        Args:
          obj: Blender object with data of type Mesh

        Returns:
          vertices: 3-tuples of coords
          indices: 2-tuples of each segment verices' indices
        """
        vertices = [obj.matrix_world @ v.co for v in obj.data.vertices]
        indices = [e.vertices for e in obj.data.edges]
        return vertices, indices

    def get_editmesh_geom(self, obj):
        """Parses editmode mesh geometry into line segments"""
        mesh = bmesh.from_edit_mesh(obj.data)
        vertices = []
        indices = []
        idx = 0

        for edge in mesh.edges:
            vertices.extend(edge.verts)
            indices.append((idx, idx + 1))
            idx += 2
        vertices = [obj.matrix_world @ v.co for v in vertices]

        return vertices, indices

    def decorate(self, context, object):
        """perform actual drawing stuff"""
        raise NotImplementedError()

    def draw_lines(self, context, obj, vertices, indices, topology=None, is_scale_dependant=True):
        region = context.region
        region3d = context.region_data
        color = context.scene.DocProperties.decorations_colour

        fmt = GPUVertFormat()
        fmt.attr_add(id="pos", comp_type="F32", len=3, fetch_mode="FLOAT")
        if topology:
            fmt.attr_add(id="topo", comp_type="U8", len=1, fetch_mode="INT")

        vbo = GPUVertBuf(len=len(vertices), format=fmt)
        vbo.attr_fill(id="pos", data=vertices)
        if topology:
            vbo.attr_fill(id="topo", data=topology)

        ibo = GPUIndexBuf(type="LINES", seq=indices)

        batch = GPUBatch(type="LINES", buf=vbo, elem=ibo)

        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

        self.shader.bind()
        self.shader.uniform_float
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("winsize", (region.width, region.height))
        self.shader.uniform_float("color", color)

        if is_scale_dependant:
            # Horrific prototype code
            factor = self.camera_zoom_to_factor(context.space_data.region_3d.view_camera_zoom)
            camera_width_px = factor * context.region.width
            mm_to_px = camera_width_px / self.camera_width_mm
            # 0.00025 is a magic constant number I visually discovered to get the right number.
            # It probably should be dynamically calculated using system.dpi or something.
            viewport_drawing_scale = 0.00025 * mm_to_px
            self.shader.uniform_float("viewportDrawingScale", viewport_drawing_scale)

        batch.draw(self.shader)

    def draw_label(self, context, text, pos, dir, gap=4, center=True, vcenter=False):
        """Draw text label

        Args:
          pos: bottom-center

        aligned and centered at segment middle
        """
        # 0 is the default font, but we're fancier than that
        font_id = self.font_id

        dpi = context.preferences.system.dpi

        color = context.scene.DocProperties.decorations_colour

        ang = -Vector((1, 0)).angle_signed(dir)
        cos = math.cos(ang)
        sin = math.sin(ang)

        # Horrific prototype code
        factor = self.camera_zoom_to_factor(context.space_data.region_3d.view_camera_zoom)
        camera_width_px = factor * context.region.width
        mm_to_px = camera_width_px / self.camera_width_mm
        # 0.004118616 is a magic constant number I visually discovered to get the right number.
        # In particular it works only for the OpenGOST font and produces a 2.5mm font size.
        # It probably should be dynamically calculated using system.dpi or something.
        # font_size = 16 <-- this is a good default
        font_size = int(0.004118616 * mm_to_px)

        blf.size(font_id, font_size, dpi)

        w, h = 0, 0
        if center or vcenter:
            w, h = blf.dimensions(font_id, text)

        if center:
            # horizontal centering
            pos -= Vector((cos, sin)) * w * 0.5

        if vcenter:
            # vertical centering
            pos -= Vector((-sin, cos)) * h * 0.5

        if gap:
            # side-shifting
            pos += Vector((-sin, cos)) * gap

        blf.enable(font_id, blf.ROTATION)
        blf.position(font_id, pos.x, pos.y, 0)

        blf.rotation(font_id, ang)
        blf.color(font_id, *color)
        # blf.enable(font_id, blf.SHADOW)
        # blf.shadow(font_id, 5, 0, 0, 0, 1)
        # blf.shadow_offset(font_id, 1, -1)
        blf.draw(font_id, text)
        blf.disable(font_id, blf.ROTATION)

    def format_value(self, context, value):
        unit_system = context.scene.unit_settings.system
        if unit_system == "IMPERIAL":
            precision = context.scene.BIMProperties.imperial_precision
            if precision == "NONE":
                precision = 256
            elif precision == "1":
                precision = 1
            elif "/" in precision:
                precision = int(precision.split("/")[1])
        elif unit_system == "METRIC":
            precision = 4
        else:
            return

        return bpy.utils.units.to_string(unit_system, "LENGTH", value, precision=precision)


class DimensionDecorator(BaseDecorator):
    """Decorator for dimension objects
    - each edge of a segment with arrow
    - puts metric text next to each segment
    """

    objecttype = "DIMENSION"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);

        vec4 p;

        vec4 head[3];
        arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

        // start edge arrow
        gl_Position = p0;
        EmitVertex();
        p = p0w + head[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p0;
        EmitVertex();
        EndPrimitive();

        // end edge arrow
        gl_Position = p1;
        EmitVertex();
        p = p1w - head[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - head[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();

        // stem, with gaps for arrows
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        verts, idxs, _ = self.get_path_geom(obj, topo=False)
        self.draw_lines(context, obj, verts, idxs)
        self.draw_labels(context, obj, verts, idxs)

    def draw_labels(self, context, obj, vertices, indices):
        region = context.region
        region3d = context.region_data
        for i0, i1 in indices:
            v0 = Vector(vertices[i0])
            v1 = Vector(vertices[i1])
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            length = (v1 - v0).length
            text = self.format_value(context, length)
            self.draw_label(context, text, p0 + (dir) * 0.5, dir)


class DiameterDecorator(DimensionDecorator):
    objecttype = "DIAMETER"


class LeaderDecorator(BaseDecorator):
    """Decorating text with arrows
    - head point with arrow
    """

    objecttype = "TEXT_LEADER"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap1 = vec4(0);

        vec4 p;

        // end edge arrow for last segment
        if (t1 == 2u) {
            vec4 head[3];
            arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

            gl_Position = p1;
            EmitVertex();
            p = p1w - head[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            p = p1w - head[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            gl_Position = p1;
            EmitVertex();
            EndPrimitive();

            gap1 = dir * viewportDrawingScale * ARROW_SIZE;
        }

        // stem, adjusted for and arrow
        gl_Position = p0;
        EmitVertex();
        p = p1w - gap1;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def get_spline_end(self, obj):
        spline = obj.data.splines[0]
        spline_points = spline.bezier_points if spline.bezier_points else spline.points
        if not spline_points:
            return Vector((0, 0, 0))
        return obj.matrix_world @ spline_points[0].co

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)
        self.draw_labels(context, obj)

    def draw_labels(self, context, obj):
        region = context.region
        region3d = context.region_data
        dir = Vector((1, 0))
        pos = location_3d_to_region_2d(region, region3d, self.get_spline_end(obj))
        self.draw_label(context, obj.BIMTextProperties.value, pos, dir, gap=0, center=False, vcenter=False)


class RadiusDecorator(BaseDecorator):
    """Decorating text with arrows
    - head point with arrow
    """

    objecttype = "RADIUS"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap1 = vec4(0);

        vec4 p;

        // end edge arrow for last segment
        if (t1 == 2u) {
            vec4 head[3];
            arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

            gl_Position = p1;
            EmitVertex();
            p = p1w - head[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            p = p1w - head[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            gl_Position = p1;
            EmitVertex();
            EndPrimitive();

            gap1 = dir * viewportDrawingScale * ARROW_SIZE;
        }

        // stem, adjusted for and arrow
        gl_Position = p0;
        EmitVertex();
        p = p1w - gap1;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def get_spline_end(self, obj):
        spline = obj.data.splines[0]
        spline_points = spline.bezier_points if spline.bezier_points else spline.points
        if not spline_points:
            return Vector((0, 0, 0))
        return obj.matrix_world @ spline_points[0].co

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)
        self.draw_labels(context, obj)

    def draw_labels(self, context, obj):
        region = context.region
        region3d = context.region_data
        dir = Vector((1, 0))
        pos = location_3d_to_region_2d(region, region3d, self.get_spline_end(obj))

        spline = obj.data.splines[0]
        spline_points = spline.bezier_points if spline.bezier_points else spline.points
        if spline_points:
            length = (spline_points[-1].co - spline_points[-2].co).length
            text = self.format_value(context, length)
            self.draw_label(context, text, pos, dir, gap=0, center=False, vcenter=False)


class StairDecorator(BaseDecorator):
    """Decorating stairs
    - head point with arrow
    - tail point with circle
    - middle points w/out decorations
    """

    objecttype = "STAIR_ARROW"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 6.0
        #define ARROW_ANGLE PI / 3.0
        #define ARROW_SIZE 24.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap0 = vec4(0), gap1 = vec4(0);

        vec4 p;

        // start edge circle for first segment
        if (t0 == 1u) {
            vec4 head[CIRCLE_SEGS];
            circle_head(viewportDrawingScale * CIRCLE_SIZE, head);

            for(int i=0; i<CIRCLE_SEGS; i++) {
                p = p0w + head[i];
                gl_Position = WIN2CLIP(p);
                EmitVertex();
            }
            p = p0w + head[0];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();

            gap0 = dir * viewportDrawingScale * CIRCLE_SIZE;
        }

        // end edge arrow for last segment
        if (t1 == 2u) {
            vec4 head[3];
            arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

            p = p1w - head[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();

            gl_Position = p1;
            EmitVertex();

            p = p1w - head[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();
        }

        // stem, with gaps for edge decoration
        p = p0w + gap0;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)


class HiddenDecorator(BaseDecorator):
    objecttype = "HIDDEN_LINE"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define DASH_SIZE 16.0
        #define DASH_PATTERN 0x0000FFFFU
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 1;

        vec4 p;

        // NB: something should be used to affect position, otherwise compiler eliminates winsize

        dist = 0;
        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        dist = length(edge);
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform float viewportDrawingScale;
    uniform vec4 color;
    in vec2 gl_FragCoord;
    in float dist;
    out vec4 fragColor;

    void main() {
        uint bit = uint(fract(dist / (viewportDrawingScale * DASH_SIZE)) * 32);
        if ((DASH_PATTERN & (1U<<bit)) == 0U) discard;
        fragColor = color;
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, idxs)


class MiscDecorator(BaseDecorator):
    objecttype = "MISC"

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 1;

        vec4 p;

        // NB: something should be used to affect position, otherwise compiler eliminates winsize

        dist = 0;
        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        dist = length(edge);
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    in vec2 gl_FragCoord;
    in float dist;
    out vec4 fragColor;

    void main() {
        fragColor = color;
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, idxs, is_scale_dependant=False)


class LevelDecorator(BaseDecorator):
    def get_splines(self, obj):
        """Iterates through splines
        Args:
          obj: Blender object with Curve data

        Yields:
          verts: points of each spline, world coords
        """
        for spline in obj.data.splines:
            spline_points = spline.bezier_points if spline.bezier_points else spline.points
            if len(spline_points) < 2:
                continue
            yield [obj.matrix_world @ p.co for p in spline_points]

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo)
        splines = self.get_splines(obj)
        self.draw_labels(context, obj, splines)


class PlanLevelDecorator(LevelDecorator):
    objecttype = "PLAN_LEVEL"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 8.0
        #define CROSS_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap1 = vec4(0);

        vec4 p;

        // end edge cross+circle for last segment
        if (t1 == 2u) {
            vec4 head_o[CIRCLE_SEGS];
            circle_head(viewportDrawingScale * CIRCLE_SIZE, head_o);

            for(int i=0; i<CIRCLE_SEGS; i++) {
                p = p1w + head_o[i];
                gl_Position = WIN2CLIP(p);
                EmitVertex();
            }
            p = p1w + head_o[0];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();

            vec4 head_x[3];
            cross_head(dir, viewportDrawingScale * CROSS_SIZE, head_x);

            p = p1w + head_x[1];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            p = p1w + head_x[2];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
            EndPrimitive();

            gap1 = head_x[0];
        }

        // stem, adjusted for and arrow
        gl_Position = p0;
        EmitVertex();
        p = p1w + gap1;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def draw_labels(self, context, obj, splines):
        region = context.region
        region3d = context.region_data
        for verts in splines:
            v0 = verts[0]
            v1 = verts[1]
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            text = "RL " + self.format_value(context, verts[-1].z)
            self.draw_label(context, text, p0, dir, gap=8, center=False)


class SectionLevelDecorator(LevelDecorator):
    objecttype = "SECTION_LEVEL"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CALLOUT_GAP 8.0
        #define CALLOUT_SIZE 64.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;
    in uint type[];
    out float dist; // distance from starging point along segment

    void callout_head(in vec4 dir, out vec4 head[4]) {
        vec2 gap = dir.xy * viewportDrawingScale * CALLOUT_GAP;
        vec2 tail = dir.xy * viewportDrawingScale * -CALLOUT_SIZE;
        vec2 side = cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy * CALLOUT_GAP;

        head[0] = vec4(tail + side, 0, 0);
        head[1] = vec4(gap * 2 + side, 0, 0);
        head[2] = vec4(gap, 0, 0);
        head[3] = vec4(side, 0, 0);
    }

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        // start edge callout
        if (t0 == 1u) {
            vec4 head[4];
            callout_head(dir, head);

            for(int i=0; i<4; i++) {
                p = p0w + head[i];
                gl_Position = WIN2CLIP(p);
                EmitVertex();
            }
            EndPrimitive();
        }

        // stem
        dist = 0;
        gl_Position = p0;
        EmitVertex();
        dist = length(p1w - p0w);
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def draw_labels(self, context, obj, splines):
        region = context.region
        region3d = context.region_data
        for verts in splines:
            v0 = verts[0]
            v1 = verts[1]
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            dir = p1 - p0
            if dir.length < 1:
                continue
            text = "RL " + self.format_value(context, verts[-1].z)
            self.draw_label(context, text, p0 + dir.normalized() * 16, -dir, gap=16, center=False)


class BreakDecorator(BaseDecorator):
    """Decorator for breakline objects
    - first edge of a mesh with zigzag thingy in the middle

    Uses first two vertices in verts list.
    """

    objecttype = "BREAKLINE"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define BREAK_LENGTH 32.0
        #define BREAK_WIDTH 16.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1), pmw = (p0w + p1w) * .5;
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        vec4 quart = dir * viewportDrawingScale * BREAK_LENGTH * .25;
        vec4 side = vec4(cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy, 0, 0) * viewportDrawingScale * BREAK_WIDTH;

        // TODO: check if there's enough length for zigzag

        gl_Position = p0;
        EmitVertex();

        p = pmw;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        p = pmw + quart - side;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        p = pmw + quart * 3 + side;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        p = pmw + quart * 4;
        gl_Position = WIN2CLIP(p);
        EmitVertex();

        gl_Position = p1;
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, idxs)


class GridDecorator(BaseDecorator):
    objecttype = "GRID"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 16.0
        #define DASH_SIZE 48.0
        #define DASH_PATTERN 0x03C0FFFFU
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * CIRCLE_SIZE * viewportDrawingScale;

        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(CIRCLE_SIZE * viewportDrawingScale, head);

        dist = 0;

        // start edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p0w + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p1w + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p1w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // stem
        dist = 0;
        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        dist = length(edge);
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    in vec2 gl_FragCoord;
    in float dist;
    out vec4 fragColor;

    void main() {
        uint bit = uint(fract(dist / DASH_SIZE) * 32);
        if ((DASH_PATTERN & (1U<<bit)) == 0U) discard;
        fragColor = color;
    }
    """

    def get_mesh_geom(self, obj):
        # first vertices only
        vertices = [obj.matrix_world @ obj.data.vertices[i].co for i in (0, 1)]
        return vertices

    def get_editmesh_geom(self, obj):
        # first vertices only
        mesh = bmesh.from_edit_mesh(obj.data)
        vertices = [obj.matrix_world @ v.co for v in mesh.edges[0].verts]
        return vertices

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts = self.get_editmesh_geom(obj)
        else:
            verts = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, [(0, 1)])
        self.draw_labels(context, obj, verts)

    def draw_labels(self, context, obj, vertices):
        region = context.region
        region3d = context.region_data
        v0 = Vector(vertices[0])
        v1 = Vector(vertices[1])
        p0 = location_3d_to_region_2d(region, region3d, v0)
        p1 = location_3d_to_region_2d(region, region3d, v1)
        dir = Vector((1, 0))
        text = obj.name.split("/")[1].split(".")[0]
        self.draw_label(context, text, p0, dir, vcenter=True, gap=0)
        self.draw_label(context, text, p1, dir, vcenter=True, gap=0)


class ElevationDecorator(LevelDecorator):
    objecttype = "ELEVATION"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 8.0
        #define TRIANGLE_L 22.63
        #define TRIANGLE_W 11.31
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void triangle_head(in vec4 side, in vec4 dir, in float length, in float width, in float radius, out vec4 head[5]) {
        vec4 nose = side * length;
        vec4 ear = dir * width;
        head[0] = side * -radius;
        head[1] = nose * -.5;
        head[2] = vec4(0) + ear;
        head[3] = nose * .5;
        head[4] = side * radius;
    }

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 side = vec4(cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy, 0, 0);
        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(viewportDrawingScale * CIRCLE_SIZE, head);

        vec4 head5[5];

        // start edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p0w + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // edge triangle
        triangle_head(side, dir, viewportDrawingScale * TRIANGLE_L, viewportDrawingScale * TRIANGLE_W, viewportDrawingScale * CIRCLE_SIZE, head5);
        p = p0w + head5[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[3];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[4];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // reference divider
        p = p0w + normalize(vec4(-1, 0, 0, 0)) * viewportDrawingScale * CIRCLE_SIZE;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + normalize(vec4(1, 0, 0, 0)) * viewportDrawingScale * CIRCLE_SIZE;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        center = obj.matrix_world.translation
        v1 = obj.matrix_world @ Vector((0, 0, 0))
        v2 = obj.matrix_world @ Vector((0, 0, -1))
        self.draw_lines(context, obj, [v1, v2], [(0, 1)])


class SectionDecorator(LevelDecorator):
    objecttype = "SECTION"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 8.0
        #define TRIANGLE_L 22.63
        #define TRIANGLE_W 11.31
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void triangle_head(in vec4 side, in vec4 dir, in float length, in float width, in float radius, out vec4 head[5]) {
        vec4 nose = side * length;
        vec4 ear = dir * width;
        head[0] = side * -radius;
        head[1] = nose * -.5;
        head[2] = vec4(0) + ear;
        head[3] = nose * .5;
        head[4] = side * radius;
    }

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, side = normalize(edge);
        vec4 gap = side * viewportDrawingScale * CIRCLE_SIZE;
        vec4 dir = vec4(cross(vec3(side.xy, 0), vec3(0, 0, 1)).xy, 0, 0);
        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(viewportDrawingScale * CIRCLE_SIZE, head);

        vec4 head5[5];

        // start edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p0w + head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // start edge triangle
        triangle_head(side, dir, viewportDrawingScale * TRIANGLE_L, viewportDrawingScale * TRIANGLE_W, viewportDrawingScale * CIRCLE_SIZE, head5);
        p = p0w + head5[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[3];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head5[4];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // start reference divider
        p = p0w + normalize(vec4(-1, 0, 0, 0)) * viewportDrawingScale * CIRCLE_SIZE;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + normalize(vec4(1, 0, 0, 0)) * viewportDrawingScale * CIRCLE_SIZE;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end edge circle
        for(int i=0; i<CIRCLE_SEGS; i++) {
            p = p1w - head[i];
            gl_Position = WIN2CLIP(p);
            EmitVertex();
        }
        p = p1w - head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end edge triangle
        triangle_head(side, dir, viewportDrawingScale * TRIANGLE_L, viewportDrawingScale * TRIANGLE_W, viewportDrawingScale * CIRCLE_SIZE, head5);
        p = p1w + head5[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + head5[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + head5[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + head5[3];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + head5[4];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // end reference divider
        p = p1w + normalize(vec4(-1, 0, 0, 0)) * viewportDrawingScale * CIRCLE_SIZE;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w + normalize(vec4(1, 0, 0, 0)) * viewportDrawingScale * CIRCLE_SIZE;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();

        // stem
        p = p0w + gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - gap;
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        vert_map = {v.freeze(): (obj.matrix_world.inverted() @ v).x for v in verts}
        verts = sorted(verts, key=lambda v: vert_map[v], reverse=True)
        self.draw_lines(context, obj, verts, idxs)


class TextDecorator(BaseDecorator):
    """Decorator for text objects
    - draws the text next to the origin
    """

    objecttype = "TEXT"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform vec2 winsize;
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(line_strip, max_vertices=MAX_POINTS) out;

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);

        vec4 p;

        vec4 head[3];
        arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

        // start edge arrow
        gl_Position = p0;
        EmitVertex();
        p = p0w + head[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p0w + head[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p0;
        EmitVertex();
        EndPrimitive();

        // end edge arrow
        gl_Position = p1;
        EmitVertex();
        p = p1w - head[1];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - head[2];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        gl_Position = p1;
        EmitVertex();
        EndPrimitive();

        // stem, with gaps for arrows
        p = p0w + head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        p = p1w - head[0];
        gl_Position = WIN2CLIP(p);
        EmitVertex();
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        self.draw_labels(context, obj)

    def draw_labels(self, context, obj):
        region = context.region
        region3d = context.region_data
        dir = Vector((1, 0))
        pos = location_3d_to_region_2d(region, region3d, obj.matrix_world.translation)
        self.draw_label(context, obj.BIMTextProperties.value, pos, dir, gap=0, center=False, vcenter=False)


class DecorationsHandler:
    decorators_classes = [
        DimensionDecorator,
        GridDecorator,
        HiddenDecorator,
        LeaderDecorator,
        RadiusDecorator,
        DiameterDecorator,
        MiscDecorator,
        PlanLevelDecorator,
        SectionLevelDecorator,
        StairDecorator,
        BreakDecorator,
        SectionDecorator,
        ElevationDecorator,
        TextDecorator,
    ]

    installed = None

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_PIXEL")

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def __init__(self):
        self.decorators = [cls() for cls in self.decorators_classes]

    def __call__(self, context):
        collection, _ = helper.get_active_drawing(context.scene)
        if collection is None:
            return

        for decorator in self.decorators:
            for obj in decorator.get_objects(collection):
                decorator.decorate(context, obj)
