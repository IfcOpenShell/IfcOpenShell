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
import math
import bmesh
import ifcopenshell
import blenderbim.tool as tool
import blenderbim.bim.module.drawing.helper as helper
from math import acos, pi, atan, degrees
from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
from bpy_extras.view3d_utils import location_3d_to_region_2d
from gpu.types import GPUShader, GPUBatch, GPUIndexBuf, GPUVertBuf, GPUVertFormat
from gpu_extras.batch import batch_for_shader
from blenderbim.bim.module.drawing.data import DecoratorData
from blenderbim.bim.module.drawing.shaders import BASE_LIB_GLSL, BASE_DEF_GLSL


def ccw(A, B, C):
    """whether a-b-c located in counter-clockwise order in 2d space"""
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)


class BaseDecorator:
    # base name of objects to decorate
    objecttype = "NOTDEFINED"

    DEF_GLSL = BASE_DEF_GLSL
    LIB_GLSL = BASE_LIB_GLSL

    VERT_GLSL = """
    uniform mat4 viewMatrix;
    in vec3 pos;
    in uint topo;
    in vec3 next_vert;
    out uint type;
    out vec4 v_next_vert;

    void main() {
        gl_Position = viewMatrix * vec4(pos, 1.0);
        type = topo;
        v_next_vert = viewMatrix * vec4(next_vert, 1.0);
    }
    """

    GEOM_GLSL = """
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices = 4) out;

    void main() {
        // default setup for macro to work
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        do_edge_verts(p0, p1);
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    uniform float lineWidth;

    in float smoothline;
    out vec4 fragColor;
    void main() {
        vec2 co = gl_FragCoord.xy;

        fragColor = color;
        if (lineSmooth) {
            fragColor.a *= clamp((lineWidth + SMOOTH_WIDTH) * 0.5 - abs(smoothline), 0.0, 1.0); //test
        }
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

        self.font_id = blf.load(
            os.path.join(bpy.context.scene.BIMProperties.data_dir, "fonts", "OpenGost Type B TT.ttf")
        )

    def get_camera_width_mm(self):
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

        camera_width_mm = get_scale(camera) * camera_width_model
        return camera_width_mm

    def camera_zoom_to_factor(self, zoom):
        return math.pow(((zoom / 50) + math.sqrt(2)) / 2, 2)

    def get_objects(self, collection):
        """find relevant objects
        using class.objecttype

        returns: iterable of blender objects
        """
        results = []
        # NOTE: if the ObjectType is not on the list
        # it will be also drawn with MiscDecorator
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
            "BATTING",
        )
        for obj in collection.all_objects:
            if obj.hide_get():
                continue

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

                elif self.objecttype == "FALL" and element.ObjectType in (
                    "SLOPE_ANGLE",
                    "SLOPE_FRACTION",
                    "SLOPE_PERCENT",
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
        bm = bmesh.from_edit_mesh(obj.data)
        indices = [[v.index for v in edge.verts] for edge in bm.edges]
        vertices = [obj.matrix_world @ v.co for v in bm.verts]
        return vertices, indices

    def decorate(self, context, obj):
        """perform actual drawing stuff"""
        raise NotImplementedError()

    def draw_lines(
        self,
        context,
        obj,
        vertices,
        indices,
        topology=None,
        is_scale_dependant=True,
        fill_next_vertices=False,
        extra_float_kwargs={},
        smoothing=True,
    ):
        """use `is_scale_dependant` = `False` if shader is not using uniform viewportDrawingScale
        otherwise uniform will be discarded during the optimization process
        and you will get `ValueError: GPUShader.uniform_float: uniform viewportDrawingScale not found`
        """

        region = context.region
        region3d = context.region_data
        color = context.scene.DocProperties.decorations_colour

        fmt = GPUVertFormat()
        fmt.attr_add(id="pos", comp_type="F32", len=3, fetch_mode="FLOAT")
        if topology:
            fmt.attr_add(id="topo", comp_type="U8", len=1, fetch_mode="INT")
        if fill_next_vertices:
            fmt.attr_add(id="next_vert", comp_type="F32", len=3, fetch_mode="FLOAT")

        vbo = GPUVertBuf(len=len(vertices), format=fmt)
        vbo.attr_fill(id="pos", data=vertices)
        if topology:
            vbo.attr_fill(id="topo", data=topology)

        if fill_next_vertices:
            shifted_vertices = vertices[1:] + [vertices[0]]
            vbo.attr_fill(id="next_vert", data=shifted_vertices)

        ibo = GPUIndexBuf(type="LINES", seq=indices)

        batch = GPUBatch(type="LINES", buf=vbo, elem=ibo)

        self.shader.bind()
        self.shader.uniform_float("viewMatrix", region3d.perspective_matrix)
        self.shader.uniform_float("winsize", (region.width, region.height))
        self.shader.uniform_float("color", color)
        if smoothing:
            self.shader.uniform_float("lineWidth", 1.0)

        if is_scale_dependant:
            # Horrific prototype code
            factor = self.camera_zoom_to_factor(context.space_data.region_3d.view_camera_zoom)
            camera_width_px = factor * context.region.width
            mm_to_px = camera_width_px / self.get_camera_width_mm()
            # 0.00025 is a magic constant number I visually discovered to get the right number.
            # It probably should be dynamically calculated using system.dpi or something.
            viewport_drawing_scale = 0.00025 * mm_to_px
            self.shader.uniform_float("viewportDrawingScale", viewport_drawing_scale)

        for kwarg, value in extra_float_kwargs.items():
            self.shader.uniform_float(kwarg, value)

        gpu.state.blend_set("ALPHA")
        batch.draw(self.shader)

    def draw_label(
        self,
        context,
        text,
        pos,
        text_dir,
        gap=4,
        center=True,
        vcenter=False,
        font_size_mm=2.5,
        line_no=0,
        box_alignment=None,
    ):
        """Draw text label

        Args:
          pos: bottom-center

        aligned and centered at segment middle

        NOTE: `blf.draw` seems to ignore the \n character, so we have to split the text ourselves
        and use the `line_no` argument of `draw_label`
        """
        # 0 is the default font, but we're fancier than that
        font_id = self.font_id

        dpi = context.preferences.system.dpi

        color = context.scene.DocProperties.decorations_colour

        ang = -Vector((1, 0)).angle_signed(text_dir)
        cos = math.cos(ang)
        sin = math.sin(ang)
        rotation_matrix = Matrix.Rotation(-ang, 2)

        # Horrific prototype code
        factor = self.camera_zoom_to_factor(context.space_data.region_3d.view_camera_zoom)
        camera_width_px = factor * context.region.width
        mm_to_px = camera_width_px / self.get_camera_width_mm()
        # 0.004118616 is a magic constant number I visually discovered to get the right number.
        # In particular it works only for the OpenGOST font and produces a 2.5mm font size.
        # It probably should be dynamically calculated using system.dpi or something.
        # font_size = 16 <-- this is a good default
        # TODO: need to synchronize it better with svg
        font_size_px = int(0.004118616 * mm_to_px) * font_size_mm / 2.5
        pos = pos - line_no * font_size_px * rotation_matrix[1]

        blf.size(font_id, font_size_px, dpi)

        if box_alignment or center or vcenter:
            w, h = blf.dimensions(font_id, text)

        if box_alignment:
            box_alignment_offset = Vector((0, 0))
            if "bottom" in box_alignment:
                pass
            elif "top" in box_alignment:
                box_alignment_offset += Vector((0, h))
            else:
                # middle / center
                box_alignment_offset += Vector((0, h / 2))

            if "left" in box_alignment:
                pass
            elif "right" in box_alignment:
                box_alignment_offset += Vector((w, 0))
            else:
                # middle / center
                box_alignment_offset += Vector((w / 2, 0))

            pos -= rotation_matrix.transposed() @ box_alignment_offset
        else:
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
        blf.position(font_id, pos.x, pos.y, 0) if hasattr(pos, "x") else blf.position(font_id, 0, 0, 0)

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
        #define OBLIQUE_SYMBOL_ANGLE PI / 4.0
        #define OLBIQUE_SYMBOL_SIZE 10.0
        #define OBLIQUE_HEAD_VERTS 7

        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform float viewportDrawingScale;
    uniform float use_oblique_style;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;

    void oblique_dimension_head(in vec4 dir, in float size,
        in float angle, out vec4 head[OBLIQUE_HEAD_VERTS]) {
        float c = cos(angle), s = sin(angle);
        vec4 ortho = vec4(-dir.y, dir.x, 0, 0);
        head[0] = -dir * size*0.66;
        head[1] = vec4(0);
        head[2] = ortho * size;
        head[3] = -ortho * size;
        head[4] = vec4(0);
        head[5] = vec4((mat2(c, +s, -s, c) * dir.xy) * size * 0.47, 0, 0);
        head[6] = -head[5];
    }

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);

        vec4 p, p_next;
        vec2 EDGE_DIR;

        if (use_oblique_style > 0) {
            vec4 head[OBLIQUE_HEAD_VERTS];
            oblique_dimension_head(dir, viewportDrawingScale * OLBIQUE_SYMBOL_SIZE, OBLIQUE_SYMBOL_ANGLE, head);

            // start edge arrow
            p_next = WIN2CLIP( (p0w + head[0]) );
            for (int i = 0; i < OBLIQUE_HEAD_VERTS-1; i++) {
                do_edge_verts_win( (p0w + head[i]),  (p0w + head[i+1]) );
            }
            EndPrimitive();

            // end edge arrow
            p_next = WIN2CLIP( (p1w + head[0]) );
            for (int i = 0; i < OBLIQUE_HEAD_VERTS-1; i++) {
                do_edge_verts_win( (p1w + head[i]),  (p1w + head[i+1]) );
            }
            EndPrimitive();

            // stem
            do_edge_verts(p0, p1);
            EndPrimitive();

        } else {
            vec4 head[3];
            arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

            // start edge arrow
            do_edge_verts( p0, WIN2CLIP( (p0w + head[1]) ) );
            do_edge_verts_win( p0w + head[1], p0w + head[2] );
            do_edge_verts( WIN2CLIP( p0w + head[2] ), p0 );
            EndPrimitive();

            // end edge arrow
            do_edge_verts( p1, WIN2CLIP( p1w - head[1] ) );
            do_edge_verts_win( p1w - head[1], p1w - head[2] );
            do_edge_verts( WIN2CLIP( p1w - head[2] ), p1 );
            EndPrimitive();

            // stem, with gaps for arrows
            do_edge_verts_win( p0w + head[0], p1w - head[0] );
            EndPrimitive();
        }
    }
    """

    def decorate(self, context, obj):
        verts, idxs, _ = self.get_path_geom(obj, topo=False)
        dimension_style = DecoratorData.get_dimension_style(obj)
        self.draw_lines(
            context, obj, verts, idxs, extra_float_kwargs={"use_oblique_style": float(dimension_style == "oblique")}
        )
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


class AngleDecorator(BaseDecorator):
    """Decorator for angle objects
    - each edge of a segment with arrow
    - every non-last edge has angle circle
    - every circle is labeled with angle in degrees
    """

    objecttype = "ANGLE"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 8.0
        #define CIRCLE_SIZE 6.0
    """
    )

    GEOM_GLSL = """
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
    in uint type[];
    in vec4 v_next_vert[];

    // per edge shader
    void main() {
        // default setup for macro to work
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        vec4 p2 = v_next_vert[1];
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 p2w = CLIP2WIN(p2);
        vec4 edge0 = p1w - p0w, dir = normalize(edge0);
        vec4 p;

        // draw a segment line
        do_edge_verts(p0, p1);
        EndPrimitive();

        // end edge with angle circle for the non-last segment
        if (t1 == 0u) { // draws only on internal vertex
            edge0 = p0w - p1w;
            vec4 dir0 = normalize(edge0);
            vec4 edge1 = p2w - p1w;
            vec4 dir1 = normalize(edge1);

            float angle_circle_size = min( length(edge0), length(edge1) );
            vec4 circle_start = dir0 * angle_circle_size;
            vec4 circle_end = dir1 * angle_circle_size;

            float cos_a = dot( edge0, edge1 ) / ( length(edge0) * length(edge1) );
            float circle_angle = acos(cos_a);

            vec4 circle_head_data[CIRCLE_SEGS+1];
            float angle_segs;
            bool counterclockwise = check_counterclockwise(p2w, p1w, p0w);
            angle_circle_head(
                circle_start,
                circle_angle,
                counterclockwise,
                circle_head_data,
                angle_segs);

            for(int i=0; i<angle_segs; i++) {
                do_edge_verts_win( p1w + circle_head_data[i], p1w + circle_head_data[i+1] );
                EmitVertex();
            }
            EndPrimitive();
        }
    }
    """

    def decorate(self, context, obj):
        verts, idxs, topo = self.get_path_geom(obj)
        self.draw_lines(context, obj, verts, idxs, topo, fill_next_vertices=True, is_scale_dependant=False)
        self.draw_labels(context, obj, verts, idxs)

    def draw_labels(self, context, obj, vertices, indices):
        region = context.region
        region3d = context.region_data

        last_segment_i = len(indices) - 1
        for edge_i, edge_vertices in enumerate(indices):
            if edge_i == last_segment_i:
                continue

            # draw angle label
            i0, i1 = edge_vertices
            v0 = Vector(vertices[i0])
            v1 = Vector(vertices[i1])
            v2 = Vector(vertices[i1 + 1])
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            p2 = location_3d_to_region_2d(region, region3d, v2)

            edge0 = p0 - p1
            edge1 = p2 - p1
            cos_a = edge0.dot(edge1) / (edge0.length * edge1.length)
            circle_angle = acos(cos_a) / pi * 180

            text = f"{int(circle_angle)}d"

            # TODO: set label position pased on p1
            # + y relative to p0p1 if p0p1p2 is clockwise
            # - y relative to p0p1 if p0p1p2 is counter-clockwise
            # counter_clockwise = ccw(p0, p1, p2)
            # label_position = (p1 + Vector( (0, 10) ) * (1 if counter_clockwise else -1)) + edge1 * 0.1
            label_position = p1 + edge1 * 0.1

            # TODO: set label direction based on the first edge (p0, p1)
            label_dir = Vector((1, 0))
            self.draw_label(context, text, label_position, label_dir)


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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

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

            do_edge_verts( p1, WIN2CLIP( p1w - head[1] ) );
            do_edge_verts_win( p1w - head[1], p1w - head[2] );
            do_edge_verts( WIN2CLIP( p1w - head[2] ), p1 );
            EndPrimitive();

            gap1 = dir * viewportDrawingScale * ARROW_SIZE;
        }

        // stem, adjusted for an arrow
        do_edge_verts_win( p0w, p1w - gap1 );
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

        props = obj.BIMTextProperties
        text_data = props.get_text_edited_data() if props.is_editing else DecoratorData.get_ifc_text_data(obj)
        text = text_data["Literals"][0]["CurrentValue"]

        self.draw_label(context, text, pos, dir, gap=0, center=False, vcenter=False)


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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

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

            do_edge_verts( p1, WIN2CLIP( p1w - head[1] ) );
            do_edge_verts_win( p1w - head[1], p1w - head[2] );
            do_edge_verts( WIN2CLIP( p1w - head[2] ), p1 );
            EndPrimitive();

            gap1 = dir * viewportDrawingScale * ARROW_SIZE;
        }

        // stem, adjusted for an arrow
        do_edge_verts_win( p0w, p1w - gap1 );
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


class FallDecorator(BaseDecorator):
    """Decorating text with arrows
    - head point with arrow
    """

    objecttype = "FALL"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define ARROW_ANGLE PI / 12.0
        #define ARROW_SIZE 16.0
    """
    )

    GEOM_GLSL = """
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

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

            do_edge_verts( p1, WIN2CLIP( p1w - head[1] ) );
            do_edge_verts_win( p1w - head[1], p1w - head[2] );
            do_edge_verts( WIN2CLIP( p1w - head[2] ), p1 );
            EndPrimitive();

            gap1 = dir * viewportDrawingScale * ARROW_SIZE;
        }

        // stem, adjusted for an arrow
        do_edge_verts_win( p0w, p1w - gap1 );
        EndPrimitive();
    }
    """

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

        # generate label text
        # same function as in svgwriter.py
        def get_label_text():
            element = tool.Ifc.get_entity(obj)
            B, A = [v.co.xyz for v in spline_points[:2]]
            rise = abs(A.z - B.z)
            O = A.copy()
            O.z = B.z
            run = (B - O).length
            if run != 0:
                angle_tg = rise / run
                angle = round(degrees(atan(angle_tg)))
            else:
                angle = 90

            # ues SLOPE_ANGLE as default
            if element.ObjectType in ("FALL", "SLOPE_ANGLE"):
                return f"{angle}°"
            elif element.ObjectType == "SLOPE_FRACTION":
                if angle == 90:
                    return "-"
                return f"{self.format_value(context, rise)} / {self.format_value(context, run)}"
            elif element.ObjectType == "SLOPE_PERCENT":
                if angle == 90:
                    return "-"
                return f"{round(angle_tg * 100)} %"

        if spline_points:
            text = get_label_text()
            self.draw_label(context, text, pos, dir, gap=0, center=False, vcenter=False)

    def get_spline_end(self, obj):
        spline = obj.data.splines[0]
        spline_points = spline.bezier_points if spline.bezier_points else spline.points
        if not spline_points:
            return Vector((0, 0, 0))
        return obj.matrix_world @ spline_points[0].co


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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

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

            for(int i=0; i<CIRCLE_SEGS-1; i++) {
                do_edge_verts_win(p0w + head[i], p0w + head[i+1]);
            }
            do_edge_verts_win( p0w + head[CIRCLE_SEGS-1], p0w + head[0] );
            EndPrimitive();

            gap0 = dir * viewportDrawingScale * CIRCLE_SIZE;
        }

        // end edge arrow for last segment
        if (t1 == 2u) {
            vec4 head[3];
            arrow_head(dir, viewportDrawingScale * ARROW_SIZE, ARROW_ANGLE, head);

            do_edge_verts( WIN2CLIP( p1w - head[1] ), p1 );
            do_edge_verts( p1, WIN2CLIP( p1w - head[2] ) );
            EndPrimitive();
        }

        // stem, with gaps for edge decoration
        do_edge_verts( p0, p1 );
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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 1;

        vec4 p;

        // NB: something should be used to affect position, otherwise compiler eliminates winsize

        dist = 0;
        do_vertex_win( p0w + gap, dir.xy);

        dist = length(edge);
        do_vertex_win( p1w - gap, dir.xy);
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform float viewportDrawingScale;
    uniform vec4 color;
    uniform float lineWidth;

    in float dist;
    in float smoothline;
    out vec4 fragColor;

    void main() {
        uint bit = uint(fract(dist / (viewportDrawingScale * DASH_SIZE)) * 32);
        if ((DASH_PATTERN & (1U<<bit)) == 0U) discard;

        fragColor = color;
        if (lineSmooth) {
            fragColor.a *= clamp((lineWidth + SMOOTH_WIDTH) * 0.5 - abs(smoothline), 0.0, 1.0);
        }
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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;

    out float dist; // distance from starging point along segment

    void main() {
        DEFAULT_SETUP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 1;

        vec4 p;

        // NB: something should be used to affect position, otherwise compiler eliminates winsize

        dist = 0;
        do_vertex_win( p0w + gap, dir.xy);

        dist = length(edge);
        do_vertex_win( p1w - gap, dir.xy);
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    uniform float lineWidth;

    in float dist;
    in float smoothline;
    out vec4 fragColor;

    void main() {
        fragColor = color;
        if (lineSmooth) {
            fragColor.a *= clamp((lineWidth + SMOOTH_WIDTH) * 0.5 - abs(smoothline), 0.0, 1.0);
        }
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, idxs, is_scale_dependant=False)


# TODO: outdated code?
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
        self.draw_labels(context, obj, self.get_splines(obj))


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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
    in uint type[];

    void main() {
        DEFAULT_SETUP();

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

            for(int i=0; i<CIRCLE_SEGS-1; i++) {
                do_edge_verts_win(p1w + head_o[i], p1w + head_o[i+1]);
            }
            do_edge_verts_win( p1w + head_o[CIRCLE_SEGS-1], p1w + head_o[0] );
            EndPrimitive();

            vec4 head_x[3];
            cross_head(dir, viewportDrawingScale * CROSS_SIZE, head_x);

            do_edge_verts_win( p1w + head_x[1], p1w + head_x[2] );
            EndPrimitive();

            gap1 = head_x[0];
        }

        // stem, adjusted for an arrow
        do_edge_verts_win( p0w, p1w + gap1 );
        EndPrimitive();
    }
    """

    def draw_labels(self, context, obj, splines):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        region = context.region
        region3d = context.region_data
        for verts in splines:
            p0, p1 = [location_3d_to_region_2d(region, region3d, v) for v in verts[:2]]
            dir = p1 - p0
            if dir.length < 1:
                continue

            if dir.x > 0:
                box_alignment = "bottom-left"
            else:
                box_alignment = "bottom-right"
                dir *= -1

            z = verts[-1].z / unit_scale
            z = ifcopenshell.util.geolocation.auto_z2e(tool.Ifc.get(), z)
            z *= unit_scale
            text = "RL " + self.format_value(context, z)
            self.draw_label(context, text, p0, dir, gap=8, center=False, box_alignment=box_alignment)


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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;
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
        DEFAULT_SETUP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        uint t0 = type[0], t1 = type[1];

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        dist = 0; // make sure dist is defined to prevent flickering
        // start edge callout
        if (t0 == 1u) {
            vec4 head[4];
            callout_head(dir, head);

            for(int i=0; i<3; i++) {
                do_edge_verts_win( p0w + head[i], p0w + head[i+1] );
            }
            EndPrimitive();
        }

        // stem
        dist = 0;
        do_vertex_win( p0w + gap, dir.xy);

        dist = length(edge);
        do_vertex_win( p1w - gap, dir.xy);
        EndPrimitive();
    }
    """

    def draw_labels(self, context, obj, splines):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        region = context.region
        region3d = context.region_data

        element = tool.Ifc.get_entity(obj)
        storey = tool.Drawing.get_annotation_element(element)
        tag = storey.Name if storey else element.Description

        for verts in splines:
            v0 = verts[0]
            v1 = verts[1]
            p0 = location_3d_to_region_2d(region, region3d, v0)
            p1 = location_3d_to_region_2d(region, region3d, v1)
            if not p0 or not p1:
                continue
            text_dir = p1 - p0
            if text_dir.length < 1:
                continue
            z = verts[-1].z / unit_scale
            z = ifcopenshell.util.geolocation.auto_z2e(tool.Ifc.get(), z)
            z *= unit_scale

            text_lines = ["RL " + self.format_value(context, z)]
            if tag:
                text_lines.append(tag)

            for line_i, line in zip((0, -1), text_lines):
                self.draw_label(
                    context,
                    line,
                    p0 + text_dir.normalized() * 16,
                    -text_dir,
                    gap=16,
                    center=False,
                    vcenter=False,
                    line_no=line_i,
                )


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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;

    void main() {
        DEFAULT_SETUP();
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1), pmw = (p0w + p1w) * .5;
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * 16.0;

        vec4 p;

        vec4 quart = dir * viewportDrawingScale * BREAK_LENGTH * .25;
        vec4 side = vec4(cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy, 0, 0) * viewportDrawingScale * BREAK_WIDTH;

        // TODO: check if there's enough length for zigzag

        do_edge_verts( p0, WIN2CLIP(pmw) );
        do_edge_verts_win ( pmw, pmw + quart - side );
        do_edge_verts_win ( pmw + quart - side, pmw + quart * 3 + side );
        do_edge_verts_win ( pmw + quart * 3 + side, pmw + quart * 4 );
        do_edge_verts( WIN2CLIP(pmw + quart * 4), p1 );
        EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)
        self.draw_lines(context, obj, verts, idxs)


class BattingDecorator(BaseDecorator):
    """Decorator for batting objects

    Uses first two vertices in verts list.
    """

    objecttype = "BATTING"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define PATTERN_SEGMENT_LENGTH 2
        #define vert_batting_space(ref, vert) (ref) + vec4(m_edge_space * ( (vert) * batting_dimensions ), 0, 0)
    """
    )

    GEOM_GLSL = """
    uniform float viewportDrawingScale;
    uniform float batting_thickness_winspace;

    layout(lines) in;
    layout(triangle_strip, max_vertices=256) out;

    void place_vert(vec4 ref_point, vec2 win_space_vert) {
        vec4 win2clip = matWIN2CLIP();
        vec4 p = ref_point + vec4(win_space_vert, 0, 0);
        gl_Position = WIN2CLIP(p);
        EmitVertex();
    }

    void main() {
        DEFAULT_SETUP();
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1), pmw = (p0w + p1w) * .5;
        vec4 edge = p1w - p0w, dir = normalize(edge);

        float segment_width = batting_thickness_winspace / 2.5;
        vec2 batting_dimensions = vec2(segment_width, batting_thickness_winspace);
        // need to multiply by viewportDrawingScale
        // so the drawing will stay consistent on zoom in / zoom out
        // but since we use winspace batting dimensions we skip it
        mat2 m_edge_space = mat2( dir.xy, dir.yx*vec2(1,-1) );

        // simplified rectangle + cross version to indicate batting
        vec4 off_y = vec4(m_edge_space * ( vec2(0, 0.5) * batting_dimensions ), 0, 0);
        do_edge_verts_win( p0w + off_y, p0w - off_y );
        do_edge_verts_win( p0w - off_y, p1w - off_y );
        do_edge_verts_win( p1w - off_y, p1w + off_y );
        do_edge_verts_win( p1w + off_y, p0w + off_y );
        EndPrimitive();
        do_edge_verts_win( p0w - off_y, p1w + off_y );
        EndPrimitive();
        do_edge_verts_win( p0w + off_y, p1w - off_y );
        EndPrimitive();

        // TODO: more fancy pattern? possibly use of frag shader?
        // we're not using complicated patterns because of the
        // hardware shader limit:
        // Error: C6033: Hardware limitation reached, can only emit 256 vertices of this size
        // vec2 pattern_segment_data[PATTERN_SEGMENT_LENGTH];
        // simplified insulation pattern
        // pattern_segment_data[0] = vec2(0, 1);
        // pattern_segment_data[1] = vec2(0.5, 0.8);
        // pattern_segment_data[2] = vec2(0, 0.2);
        // pattern_segment_data[3] = vec2(0.5, 0);
        // pattern_segment_data[4] = vec2(1.0, 0.2);
        // pattern_segment_data[5] = vec2(0.5, 0.8);
        // pattern_segment_data[6] = vec2(1.0, 1.0);
        // zigzag pattern
        // pattern_segment_data[0] = vec2(0, 1);
        // pattern_segment_data[1] = vec2(0, 0);
        // int segs = int( ceil( length(edge) / (batting_dimensions.x * viewportDrawingScale) ) ); // amount of segments
        // vec4 p;
        // vec2 p_base, p_cur_ver;
        // for (int i = 0; i < segs; i++) {
        //     p_base = m_edge_space * (vec2(i, -0.5) * batting_dimensions);
        //     for(int j=0; j<PATTERN_SEGMENT_LENGTH; j++) {
        //         p_cur_ver = p_base + m_edge_space * (pattern_segment_data[j] * batting_dimensions);
        //         place_vert(p0w, p_cur_ver);
        //     }
        // }
        // gl_Position = p1;
        // EmitVertex();
        // EndPrimitive();
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)

        # TODO: find the less ugly way to figure thickness
        thickness = DecoratorData.get_batting_thickness(obj)
        region = context.region
        region3d = context.region_data
        original_edge_length = (verts[1] - verts[0]).length
        clipspace_verts = [region3d.perspective_matrix @ v for v in verts[:2]]
        winspace_verts = [v * Vector([region.width / 2, region.height / 2, 1]) for v in clipspace_verts]
        win_space_edge_length = (winspace_verts[1] - winspace_verts[0]).xy.length
        k = win_space_edge_length / original_edge_length
        winspace_thickness = k * thickness

        self.draw_lines(
            context,
            obj,
            verts[:2],
            idxs,
            extra_float_kwargs={"batting_thickness_winspace": winspace_thickness},
            is_scale_dependant=False,
        )


class GridDecorator(BaseDecorator):
    objecttype = "GRID"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 16.0
        #define DASH_SIZE 48.0
        // dash pattern "----------------      ----      "
        #define DASH_PATTERN 0x03C0FFFFU
    """
    )

    GEOM_GLSL = """
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=256) out;

    out float dist; // distance from starging point along segment

    void main() {
        DEFAULT_SETUP();
        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 gap = dir * CIRCLE_SIZE * viewportDrawingScale;

        dist = 0; // make sure dist is defined to prevent flickering
        vec4 head[CIRCLE_SEGS];
        circle_head(CIRCLE_SIZE * viewportDrawingScale, head);

        // start edge circle
        do_circle_head(p0w, head);
        EndPrimitive();

        // end edge circle
        do_circle_head(p1w, head);
        EndPrimitive();

        // stem
        dist = 0;
        do_vertex_win( p0w + gap, dir.xy);
        dist = length(edge);
        do_vertex_win( p1w - gap, dir.xy);
        EndPrimitive();
    }
    """

    FRAG_GLSL = """
    uniform vec4 color;
    uniform float lineWidth;
    in float smoothline;
    in float dist;
    out vec4 fragColor;

    void main() {
        uint bit = uint(fract(dist / DASH_SIZE) * 32);
        if ((DASH_PATTERN & (1U<<bit)) == 0U) discard;

        fragColor = color;
        if (lineSmooth) {
            fragColor.a *= clamp((lineWidth + SMOOTH_WIDTH) * 0.5 - abs(smoothline), 0.0, 1.0);
        }
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
        self.draw_lines(context, obj, verts, [(0, 1)], smoothing=True)
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
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=128) out;

    void main() {
        DEFAULT_SETUP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;

        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, dir = normalize(edge);
        vec4 side = vec4(cross(vec3(dir.xy, 0), vec3(0, 0, 1)).xy, 0, 0);
        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(viewportDrawingScale * CIRCLE_SIZE, head);

        vec4 head5[5];

        // start edge circle
        do_circle_head(p0w, head);
        EndPrimitive();

        // edge triangle
        triangle_head(side, dir, viewportDrawingScale * TRIANGLE_L, viewportDrawingScale * TRIANGLE_W, viewportDrawingScale * CIRCLE_SIZE, head5);
        do_triangle_head(p0w, head5);
        EndPrimitive();

        // reference divider
        vec4 offset = vec4(1, 0, 0, 0) * viewportDrawingScale * CIRCLE_SIZE;
        do_edge_verts_win( p0w + offset, p0w - offset );
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
    uniform float viewportDrawingScale;
    uniform float connect_markers;
    uniform float display_start_symbol;
    uniform float display_end_symbol;
    uniform float display_start_circle;
    uniform float display_end_circle;

    layout(lines) in;
    layout(triangle_strip, max_vertices=256) out;

    void main() {
        DEFAULT_SETUP();

        vec4 p0 = gl_in[0].gl_Position, p1 = gl_in[1].gl_Position;
        vec4 p0w = CLIP2WIN(p0), p1w = CLIP2WIN(p1);
        vec4 edge = p1w - p0w, side = normalize(edge);
        vec4 edge_ortho_dir = -vec4(cross(vec3(side.xy, 0), vec3(0, 0, 1)).xy, 0, 0);
        vec4 p;

        vec4 head[CIRCLE_SEGS];
        circle_head(viewportDrawingScale * CIRCLE_SIZE, head);

        vec4 head5[5];
        triangle_head(side, edge_ortho_dir, viewportDrawingScale * TRIANGLE_L, viewportDrawingScale * TRIANGLE_W, viewportDrawingScale * CIRCLE_SIZE, head5);

        // start edge circle
        if (display_start_circle > 0) {
            do_circle_head(p0w, head);
            EndPrimitive();
        }

        if (display_start_symbol > 0) {
            // start edge triangle
            do_triangle_head(p0w, head5);
            EndPrimitive();
        }

        // end edge circle
        if (display_end_circle > 0) {
            do_circle_head(p1w, head);
            EndPrimitive();
        }

        // end edge triangle
        if (display_end_symbol > 0) {
            do_triangle_head(p1w, head5);
            EndPrimitive();
        }

        vec4 divider_line_size[2];
        divider_line_size[0] = side * viewportDrawingScale * CIRCLE_SIZE;
        divider_line_size[1] = side * viewportDrawingScale * CIRCLE_SIZE;
        if (connect_markers == 0) {
            divider_line_size[0] = divider_line_size[0] * 3;
        }

        // NOTE: basically we consider first vertex to be
        // start and the second to be the end marker
        // which is a bit inconsistent with svg
        // but not that anyone will use multiple edge section annotation

        vec4 gap[2];

        // start reference divider
        if (display_start_symbol > 0) {
            do_edge_verts_win( p0w + divider_line_size[0], p0w - divider_line_size[1] );
            EndPrimitive();
        }

        // end reference divider
        if (display_end_symbol > 0) {
            do_edge_verts_win( p1w + divider_line_size[1], p1w - divider_line_size[0] );
            EndPrimitive();
        }

        // stem
        if (connect_markers > 0) {
            gap[0] = (display_start_symbol > 0 ? (side * viewportDrawingScale * CIRCLE_SIZE) : vec4(0));
            gap[1] = (display_end_symbol > 0 ? (side * viewportDrawingScale * CIRCLE_SIZE) : vec4(0));
            do_edge_verts_win( p0w + gap[0], p1w - gap[1] );
            EndPrimitive();
        }
    }
    """

    def decorate(self, context, obj):
        if obj.data.is_editmode:
            verts, idxs = self.get_editmesh_geom(obj)
        else:
            verts, idxs = self.get_mesh_geom(obj)

        # TODO: add dashed line to shader with frag shader
        display_data = DecoratorData.get_section_markers_display_data(obj)
        self.draw_lines(
            context,
            obj,
            verts,
            idxs,
            extra_float_kwargs={
                "connect_markers": float(display_data["connect_markers"]),
                "display_start_symbol": float(display_data["start"]["add_symbol"]),
                "display_end_symbol": float(display_data["end"]["add_symbol"]),
                "display_start_circle": float(display_data["start"]["add_circle"]),
                "display_end_circle": float(display_data["end"]["add_circle"]),
            },
        )


class TextDecorator(BaseDecorator):
    """Decorator for text objects
    - draws the text next to the origin
    """

    objecttype = "TEXT"

    DEF_GLSL = (
        BaseDecorator.DEF_GLSL
        + """
        #define CIRCLE_SIZE 4.0
        #define CIRCLE_SEGS_ASTERISK 6
    """
    )

    GEOM_GLSL = """
    uniform float viewportDrawingScale;

    layout(lines) in;
    layout(triangle_strip, max_vertices=MAX_POINTS) out;

    void circle_head_asterisk(in float size, out vec4 head[CIRCLE_SEGS_ASTERISK]) {
        float angle_d = PI * 2 / CIRCLE_SEGS_ASTERISK;
        for(int i = 0; i<CIRCLE_SEGS_ASTERISK; i++) {
            float angle = angle_d * i;
            head[i] = vec4(cos(angle), sin(angle), 0, 0) * size;
        }
    }

    void main() {
        // default setup for macro to work
        vec4 clip2win = matCLIP2WIN();
        vec4 win2clip = matWIN2CLIP();
        vec2 EDGE_DIR;

        vec4 p0 = gl_in[0].gl_Position;
        vec4 p0w = CLIP2WIN(p0);
        vec4 p;

        vec4 head[CIRCLE_SEGS_ASTERISK];
        circle_head_asterisk(viewportDrawingScale * CIRCLE_SIZE, head);

        for (int i=0; i < CIRCLE_SEGS_ASTERISK/2; i++) {
            do_edge_verts_win( p0w + head[i], p0w + head[i+CIRCLE_SEGS_ASTERISK/2] );
            EndPrimitive();
        }
    }
    """

    def decorate(self, context, obj):
        self.draw_labels(context, obj)

    def draw_labels(self, context, obj):
        region = context.region
        region3d = context.region_data

        def matrix_only_rotation(m):
            return m.to_3x3().normalized().to_4x4()

        text_dir = Vector((1, 0))
        text_dir_world = matrix_only_rotation(region3d.perspective_matrix.inverted()) @ text_dir.to_3d()
        text_dir_world_rotated = matrix_only_rotation(obj.matrix_world) @ text_dir_world
        text_dir = (matrix_only_rotation(region3d.perspective_matrix) @ text_dir_world_rotated).to_2d().normalized()

        pos = location_3d_to_region_2d(region, region3d, obj.matrix_world.translation)
        props = obj.BIMTextProperties
        text_data = props.get_text_edited_data() if props.is_editing else DecoratorData.get_ifc_text_data(obj)
        literals_data = text_data["Literals"]

        # draw asterisk symbol to visually indicate that there are multiple literals
        if len(literals_data) > 1:
            verts = [obj.location]
            idxs = [(0, 0)]
            self.draw_lines(context, obj, verts, idxs)

        line_i = 0
        for literal_data in literals_data:
            box_alignment = literal_data["BoxAlignment"]

            for line in literal_data["CurrentValue"].split("\\n"):
                self.draw_label(
                    context,
                    line,
                    pos,
                    text_dir,
                    gap=0,
                    center=False,
                    vcenter=False,
                    font_size_mm=text_data["FontSize"],
                    line_no=line_i,
                    box_alignment=box_alignment,
                )
                line_i += 1


class CutDecorator:
    installed = None
    cache = {}

    @classmethod
    def install(cls, context):
        if cls.installed:
            cls.uninstall()
        handler = cls()
        cls.installed = SpaceView3D.draw_handler_add(handler, (context,), "WINDOW", "POST_VIEW")

    @classmethod
    def uninstall(cls):
        try:
            SpaceView3D.draw_handler_remove(cls.installed, "WINDOW")
        except ValueError:
            pass
        cls.installed = None

    def __call__(self, context):
        for obj in self.get_objects(None):
            self.decorate(context, obj)

    def get_objects(self, collection):
        return [o for o in bpy.context.visible_objects if o.type == "MESH"]

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def decorate(self, context, obj):
        element = tool.Ifc.get_entity(obj)
        if not element:
            return

        # Currently selected objects shall not be cached as they may be being moved / edited.
        # If the camera is selected, we also disable the cache as the user may be moving the camera.
        if obj.select_get() or context.scene.camera.select_get():
            all_vertices, all_edges = None, None
        else:
            all_vertices, all_edges = DecoratorData.cut_cache.get(element.id(), (None, None))

        if all_vertices is False:
            return

        if not self.is_intersecting_camera(obj, context.scene.camera):
            DecoratorData.cut_cache[element.id()] = (False, False)
            return

        if all_vertices is None:
            all_vertices, all_edges = self.bisect_mesh(obj, context.scene.camera)
            DecoratorData.cut_cache[element.id()] = (all_vertices, all_edges)

        gpu.state.point_size_set(2)
        gpu.state.blend_set("ALPHA")

        ### Actually drawing
        # 3D_POLYLINE_UNIFORM_COLOR is good for smoothed lines since `bgl.enable(GL_LINE_SMOOTH)` is deprecated
        self.line_shader = gpu.shader.from_builtin("3D_POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 3.0)

        # general shader
        self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        self.shader.bind()

        green = (0.545, 0.863, 0, 1)
        white = (0, 0, 0, 1)
        color = green if obj.select_get() else white
        self.draw_batch("LINES", all_vertices, color, all_edges)
        self.draw_batch("POINTS", all_vertices, color)

    def is_intersecting_camera(self, obj, camera):
        # Based on separating axis theorem
        plane_co = camera.matrix_world.translation
        plane_no = camera.matrix_world.col[2].xyz

        # Broadphase check using the bounding box
        bounding_box_world_coords = [obj.matrix_world @ Vector(coord) for coord in obj.bound_box]
        bounding_box_signed_distances = [plane_no.dot(v - plane_co) for v in bounding_box_world_coords]

        pos_exists_bb = any(d > 0 for d in bounding_box_signed_distances)
        neg_exists_bb = any(d < 0 for d in bounding_box_signed_distances)

        if not (pos_exists_bb and neg_exists_bb):
            return False

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Transform the vertices to world space
        mesh_mat = obj.matrix_world
        bm.transform(mesh_mat)

        # Calculate the signed distances of all vertices from the plane
        signed_distances = [plane_no.dot(v.co - plane_co) for v in bm.verts]

        bm.free()

        # Check for intersection
        pos_exists = any(d > 0 for d in signed_distances)
        neg_exists = any(d < 0 for d in signed_distances)

        return pos_exists and neg_exists

    def bisect_mesh(self, obj, camera):
        camera_matrix = obj.matrix_world.inverted() @ camera.matrix_world
        plane_co = camera_matrix.translation
        plane_no = camera_matrix.col[2].xyz

        global_offset = camera.matrix_world.col[2].xyz * -camera.data.clip_start

        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Run the bisect operation
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        results = bmesh.ops.bisect_plane(bm, geom=geom, dist=0.0001, plane_co=plane_co, plane_no=plane_no)

        vert_map = {}
        verts = []
        edges = []
        i = 0
        for geom in results["geom_cut"]:
            if isinstance(geom, bmesh.types.BMVert):
                verts.append(tuple((obj.matrix_world @ geom.co) + global_offset))
                vert_map[geom.index] = i
                i += 1
            else:
                # It seems as though edges always appear after verts
                edges.append([vert_map[v.index] for v in geom.verts])

        bm.free()

        return verts, edges


class DecorationsHandler:
    decorators_classes = [
        DimensionDecorator,
        AngleDecorator,
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
        BattingDecorator,
        FallDecorator,
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
