# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 @Andrej730
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import csv
import random
import ifcopenshell
import ifcopenshell.api
import bonsai.tool as tool
from math import cos, sin, tan, pi
from pathlib import Path
from itertools import chain
from ifcopenshell.util.shape_builder import ShapeBuilder
from collections import namedtuple
from mathutils import Vector, Matrix
from random import uniform


# When run from Blender
BLEND_DIR = os.path.dirname(bpy.data.filepath)
OUT_PATH = os.path.join(BLEND_DIR, "..", "bonsai", "bim", "data", "libraries", "IFC4 Landscape Library.ifc")

SimpleTreeParams = namedtuple("SimpleTreeParams", "plant_height crown_diameter trunk_diameter")
LowPolyTreeParams = namedtuple(
    "LowPolyTreeParams", "plant_height crown_diameter crown_max_loc crown_taper trunk_height trunk_diameter random_seed"
)
PalmTreeParams = namedtuple("PalmTreeParams", "plant_height crown_diameter trunk_diameter")
TreePresetData = namedtuple("TreePresetData", "preset_class generator")


GeneratedGeometry = namedtuple("GeneratedGeometry", "items_2d items_3d")


def generate_low_poly_tree(
    builder: ShapeBuilder,
    crown_taper=0.5,
    crown_max_loc=0.3,
    plant_height=12.0,
    trunk_height=2.0,
    crown_diameter=4,
    trunk_diameter=0.3,
    random_seed=10,
) -> GeneratedGeometry:
    unit_conversion = 1 / ifcopenshell.util.unit.calculate_unit_scale(builder.file)
    random.seed(random_seed)
    res = 6
    plant_height *= unit_conversion
    trunk_height *= unit_conversion
    crown_diameter *= unit_conversion
    trunk_diameter *= unit_conversion
    crown_height = plant_height - trunk_height

    def circle(center, r, res):
        points = []
        for i in range(res):
            # fmt: off
            vert = (
                cos(i * 2 * pi / res) * r + center[0],
                sin(i * 2 * pi / res) * r + center[1],
                0.0 + center[2]
            )
            # fmt: on
            points.append(vert)
        return points

    def merge_lists(lists):
        merged_list = []
        for i in range(len(lists)):
            merged_list = merged_list + lists[i]
        return merged_list

    def XY_scale(vert, scale):
        vert_scaled = (vert[0] * scale, vert[1] * scale, vert[2])
        return vert_scaled

    def rand_add(vert, amp):
        # fmt: off
        vert_new = (
            vert[0] + uniform(-amp, amp),
            vert[1] + uniform(-amp, amp),
            vert[2] + uniform(-amp, amp)
        )
        # fmt: on
        return vert_new

    height_segments_trunk = 2
    height_segments_crown = 7
    height_segments_total = height_segments_trunk + height_segments_crown

    verts = []

    # Trunk
    for i in range(height_segments_trunk):
        points = circle((0.0, 0.0, i * trunk_height), trunk_diameter / 2, res)
        verts.append(points)

    # Crown
    h_crown_max_loc = int((height_segments_crown - 1) * crown_max_loc)
    crown_indices = []
    for i in range(0, h_crown_max_loc):
        crown_indices.append(i)
    for i in range(0, height_segments_crown - h_crown_max_loc):
        crown_indices.append(h_crown_max_loc - i)

    my_min_val = min(crown_indices)
    my_max_val = max(crown_indices)

    n_crown_taper = crown_taper * 0.8

    crown_diameters = []
    for x in crown_indices:
        crown_diameters.append(((x - my_min_val) / (my_max_val - my_min_val)) * n_crown_taper + (1 - n_crown_taper))

    randomize_amplitude = plant_height / 50

    crown_segment_height = crown_height / height_segments_crown
    for i in range(0, height_segments_crown - 1):
        points = circle(
            (0.0, 0.0, trunk_height + (i + 1) * crown_segment_height),
            crown_diameter * crown_diameters[i] / 2,
            res,
        )
        for i in range(0, len(points)):
            points[i] = rand_add(points[i], randomize_amplitude)
        verts.append(points)

    # Top
    verts.append(circle((0.0, 0.0, plant_height), 0.05, res))

    edge_loops = []
    for i in range(height_segments_total):
        edge_loops.append(range(i * res, (i + 1) * res))

    verts = merge_lists(verts)

    faces = []
    bottom = [*edge_loops[0]]
    faces.append(bottom)
    for i in range(height_segments_total - 1):
        for j in range(res):
            face = (edge_loops[i][j - 1], edge_loops[i][j], edge_loops[i + 1][j], edge_loops[i + 1][j - 1])
            faces.append(face)
    top = [*edge_loops[-1]]
    faces.append(top)

    verts_3D = [verts]
    faces_3D = [faces]

    verts_2D = [
        [
            (-0.5865642428398132, 0.8647078275680542, 0.0),
            (-0.7583824992179871, 0.6572927236557007, 0.0),
            (-0.7234422564506531, 0.5865941047668457, 0.0),
            (-0.8714070916175842, 0.46631893515586853, 0.0),
            (-0.9203394055366516, 0.15792329609394073, 0.0),
            (-0.6487269997596741, 0.11522211134433746, 0.0),
            (-0.9273074269294739, 0.0903107076883316, 0.0),
            (-0.9606701731681824, -0.2852219343185425, 0.0),
            (-0.8060722351074219, -0.35055163502693176, 0.0),
            (-0.8271104693412781, -0.4677186608314514, 0.0),
            (-0.6899875998497009, -0.6695915460586548, 0.0),
            (-0.6215555667877197, -0.6767659187316895, 0.0),
            (-0.4315463900566101, -0.8824808597564697, 0.0),
            (-0.30316293239593506, -0.9023936986923218, 0.0),
            (-0.32218849658966064, -0.8037619590759277, 0.0),
            (-0.21792533993721008, -0.9530860185623169, 0.0),
            (0.36917445063591003, -0.877334475517273, 0.0),
            (0.30831706523895264, -0.685136079788208, 0.0),
            (0.4778200685977936, -0.8094909191131592, 0.0),
            (0.9163193106651306, -0.368840754032135, 0.0),
            (0.827597439289093, -0.29377281665802, 0.0),
            (0.9478662610054016, -0.245104119181633, 0.0),
            (0.9667968153953552, 0.08458180725574493, 0.0),
            (0.7529001832008362, 0.05212751030921936, 0.0),
            (0.9102436900138855, 0.19098728895187378, 0.0),
            (0.8279229998588562, 0.5522171258926392, 0.0),
            (0.6635335087776184, 0.6461355686187744, 0.0),
            (0.5753684639930725, 0.8170149326324463, 0.0),
            (0.3976244330406189, 0.8779193162918091, 0.0),
            (0.18733686208724976, 0.7513588666915894, 0.0),
            (0.338344544172287, 0.910933256149292, 0.0),
            (-0.013130240142345428, 0.9798095226287842, 0.0),
            (-0.18649885058403015, 0.9414206743240356, 0.0),
            (-0.3193224370479584, 0.8835403919219971, 0.0),
        ]
    ]
    edges_2D = []
    faces_2D = []

    verts_2D_new = []
    for vert in verts_2D[0]:
        verts_2D_new.append(XY_scale(vert, crown_diameter / 2))

    range_of_verts = range(0, len(verts_2D[0]))
    for i in range_of_verts:
        edges_2D.append([range_of_verts[i - 1], i])
        faces_2D.append(i)

    verts_2D[0] = verts_2D_new
    edges_2D = [edges_2D]
    faces_2D = [[faces_2D]]

    verts_2D = [Vector(v).to_2d() for v in verts_2D[0]]
    shape_2d = builder.polyline(points=verts_2D, closed=True)
    shape_3d = builder.polygonal_face_set(points=verts_3D[0], faces=faces_3D[0])

    return GeneratedGeometry((shape_2d,), (shape_3d,))


def generate_simple_tree(
    builder: ShapeBuilder, plant_height=2, crown_diameter=2, trunk_diameter=0.1
) -> GeneratedGeometry:
    unit_conversion = 1 / ifcopenshell.util.unit.calculate_unit_scale(builder.file)
    plant_height *= unit_conversion
    crown_diameter *= unit_conversion
    trunk_diameter *= unit_conversion

    crown_radius = crown_diameter / 2

    # 3d shape
    trunk_base = builder.circle(radius=trunk_diameter / 2)
    trunk = builder.extrude(trunk_base, magnitude=plant_height - crown_diameter)
    crown_position = (0.0, 0.0, (plant_height - crown_radius))
    crown = builder.sphere(radius=crown_radius, center=crown_position)

    # 2d shape
    shape_2D = builder.circle(radius=crown_radius)

    return GeneratedGeometry((shape_2D,), (trunk, crown))


def generate_palm_tree(
    builder: ShapeBuilder, plant_height=2, crown_diameter=5.8, trunk_diameter=0.1
) -> GeneratedGeometry:
    unit_conversion = 1 / ifcopenshell.util.unit.calculate_unit_scale(builder.file)

    palm_verts = [
        Vector((-3.6415634155273438, -3.8275668621063232, -1.0948246717453003)),
        Vector((-0.3698049783706665, -1.805966854095459, 0.493910551071167)),
        Vector((-1.6397790908813477, -0.5056067705154419, 0.04353363811969757)),
        Vector((0.0, 0.0, 0.0)),
        Vector((5.023162364959717, -1.6531240940093994, -1.0948246717453003)),
        Vector((1.8090602159500122, 0.4589407444000244, 0.493910551071167)),
        Vector((1.1666079759597778, -1.2413609027862549, 0.04353363811969757)),
        Vector((1.6942416429519653, 5.038582801818848, -1.0948246717453003)),
        Vector((-0.43215513229370117, 1.833944320678711, 0.493910551071167)),
        Vector((1.2652605772018433, 1.1839056015014648, 0.04353363811969757)),
        Vector((-4.577561378479004, 2.689336061477661, -1.0948246717453003)),
        Vector((-1.8646581172943115, -0.0367276668548584, 0.493910551071167)),
        Vector((-0.8873085975646973, 1.4957730770111084, 0.04353363811969757)),
    ]
    palm_faces = [(2, 1, 0), (2, 3, 1), (6, 5, 4), (6, 3, 5), (9, 8, 7), (9, 3, 8), (12, 11, 10), (12, 3, 11)]
    # each segment starts with the last point from the previous
    palm_segments_2d_ifc = [(3, 11, 10, 12, 3), (3, 1, 0, 2, 3), (3, 5, 4, 6, 3), (3, 8, 7, 9, 3)]
    palm_segments_2d_ifc = [[i + 1 for i in segment] for segment in palm_segments_2d_ifc]  # IFC indices start with 1

    scale = Vector()
    scale.xyz = crown_diameter / 11.6
    leaves_height = 0.493910551071167 * scale.z
    plant_height -= leaves_height
    for v in palm_verts:
        v *= scale
        v.z += plant_height
        v *= unit_conversion

    plant_height *= unit_conversion
    crown_diameter *= unit_conversion
    trunk_diameter *= unit_conversion

    # 3d
    leaves = builder.polygonal_face_set(palm_verts, palm_faces)
    trunk_base = builder.circle(radius=trunk_diameter / 2)
    trunk = builder.extrude(trunk_base, magnitude=plant_height)

    # 2d
    remove_z = Vector((1, 1, 0))
    verts_2D = [v * remove_z for v in palm_verts]
    ifc_points = builder.file.createIfcCartesianPointList2D(verts_2D)
    ifc_segments = []
    for segment in palm_segments_2d_ifc:
        ifc_segments.append(builder.file.createIfcLineIndex(segment))
    shape_2d = builder.file.createIfcIndexedPolyCurve(Points=ifc_points, Segments=ifc_segments)
    return GeneratedGeometry((shape_2d,), (leaves, trunk))


tree_presets = {
    "simple": TreePresetData(SimpleTreeParams, generate_simple_tree),
    "low_poly": TreePresetData(LowPolyTreeParams, generate_low_poly_tree),
    "palm_tree": TreePresetData(PalmTreeParams, generate_palm_tree),
}


class LibraryGenerator:
    def generate(self, library_name, output_filename):
        ifcopenshell.api.pre_listeners = {}
        ifcopenshell.api.post_listeners = {}

        self.materials = {}

        self.file = ifcopenshell.api.run("project.create_file")
        self.project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name=library_name)
        self.library = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProjectLibrary", name=library_name
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[self.library], relating_context=self.project
        )
        unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])

        model = ifcopenshell.api.run("context.add_context", self.file, context_type="Model")
        plan = ifcopenshell.api.run("context.add_context", self.file, context_type="Plan")
        self.representations = {
            "Model/Body/MODEL_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=model,
            ),
            "Plan/Body/PLAN_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Plan",
                context_identifier="Body",
                target_view="PLAN_VIEW",
                parent=plan,
            ),
            "Model/Body/PLAN_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="PLAN_VIEW",
                parent=model,
            ),
            "Model/Body/SECTION_VIEW": ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type="Model",
                context_identifier="Body",
                target_view="SECTION_VIEW",
                parent=model,
            ),
        }

        # Manually modeled trees
        for obj in bpy.data.objects:
            if not obj.type == "MESH":
                continue
            if "Plan/" in obj.name or "Model/" in obj.name:
                continue
            representations = {"Model/Body/MODEL_VIEW": obj.name}
            for rep_key in self.representations.keys():
                rep_obj = bpy.data.objects.get(obj.name + " " + rep_key)
                if rep_obj:
                    representations[rep_key] = rep_obj.name
            self.create_type("IfcGeographicElementType", obj.name, representations)

        # Auto generated generic trees

        self.builder = ShapeBuilder(self.file)
        builder = self.builder

        TreeData = namedtuple("TreeData", "tree_name preset_name preset_data")
        trees = [
            TreeData("Conical Tree Small (5m)", "low_poly", (5.0, 1.13, 0.0, 1.0, 0.28, 0.16, 5)),
            TreeData("Conical Tree Medium (10m)", "low_poly", (10.0, 2.7, 0.0, 1.0, 0.32, 0.22, 4)),
            TreeData("Conical Tree Big (15m)", "low_poly", (15.0, 4.37, 0.0, 1.0, 0.74, 0.44, 3)),
            TreeData("Palm Tree (15m)", "palm_tree", (15.0, 16.64, 0.4)),
            TreeData("Shrub Small (0.4m)", "low_poly", (0.4, 0.4, 0.535, 0.524, 0.0, 0.0, 10)),
            TreeData("Shrub Big (0.8m)", "low_poly", (0.8, 0.8, 0.535, 0.524, 0.0, 0.0, 10)),
            TreeData("Lollipop Tree (4m)", "simple", (4.0, 2.5, 0.2)),
            TreeData("Lollipop Tree (6m)", "simple", (6.0, 3.5, 0.2)),
            TreeData("Lollipop Tree (8m)", "simple", (8.0, 4.5, 0.2)),
            TreeData("Lollipop Tree (10m)", "simple", (10.0, 5.5, 0.44)),
            TreeData("Lollipop Tree (14m)", "simple", (14.0, 7.5, 0.44)),
            TreeData("Lollipop Tree (18m)", "simple", (18.0, 9.5, 0.44)),
            TreeData("Lollipop Tree (25m)", "simple", (25.0, 13.5, 0.50)),
            TreeData("Tree Small (8m)", "low_poly", (8.0, 6.0, 0.0, 0.8, 1.0, 0.2, 10)),
            TreeData("Tree Medium (12m)", "low_poly", (12.0, 10.0, 0.0, 0.8, 2.0, 0.4, 20)),
            TreeData("Tree Big (20m)", "low_poly", (20.0, 15.0, 0.0, 0.8, 4.0, 0.6, 30)),
        ]

        for tree_data in trees:
            preset = tree_presets.get(tree_data.preset_name)
            preset_data = preset.preset_class(*tree_data.preset_data)._asdict()
            tree_geometry = preset.generator(builder, **preset_data)
            self.create_explicit_type(
                "IfcGeographicElementType", tree_data.tree_name, **self.get_representations(tree_geometry)
            )

        # From tree species table

        with open(os.path.join(BLEND_DIR, "tree_species.csv"), "r") as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0:
                    continue
                preset = tree_presets.get(row[0])
                data = [float(x) for x in row[2:]]
                preset_data = preset.preset_class(*data)._asdict()
                tree_geometry = preset.generator(builder, **preset_data)
                self.create_explicit_type("IfcGeographicElementType", row[1], **self.get_representations(tree_geometry))

        self.file.write(output_filename)

    def get_representations(self, generated_geometry: GeneratedGeometry):
        representation_2d = self.builder.get_representation(
            self.representations["Plan/Body/PLAN_VIEW"], items=generated_geometry.items_2d
        )
        representation_3d = self.builder.get_representation(
            self.representations["Model/Body/MODEL_VIEW"], items=generated_geometry.items_3d
        )
        return {
            "representation_3d": representation_3d,
            "representation_2d": representation_2d,
        }

    def create_explicit_type(self, ifc_class, name, representation_3d, representation_2d, **params):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        for param, value in params.items():
            setattr(element, param, value)

        ifcopenshell.api.run(
            "geometry.assign_representation", self.file, product=element, representation=representation_3d
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", self.file, product=element, representation=representation_2d
        )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )
        return element

    def create_type(self, ifc_class, name, representations):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name)
        for rep_name, obj_name in representations.items():
            obj = bpy.data.objects.get(obj_name)
            representation = ifcopenshell.api.run(
                "geometry.add_representation",
                self.file,
                context=self.representations[rep_name],
                blender_object=obj,
                geometry=obj.data,
                total_items=max(1, len(obj.material_slots)),
            )
            styles = []
            for slot in obj.material_slots:
                style = ifcopenshell.api.run("style.add_style", self.file, name=slot.material.name)
                ifcopenshell.api.run(
                    "style.add_surface_style",
                    self.file,
                    style=style,
                    ifc_class="IfcSurfaceStyleShading",
                    attributes=tool.Style.get_surface_shading_attributes(slot.material),
                )
                styles.append(style)
            if styles:
                ifcopenshell.api.run(
                    "style.assign_representation_styles", self.file, shape_representation=representation, styles=styles
                )
            ifcopenshell.api.run(
                "geometry.assign_representation", self.file, product=element, representation=representation
            )
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definitions=[element], relating_context=self.library
        )


if __name__ == "__main__":
    LibraryGenerator().generate("Landscape Assets Library", output_filename=OUT_PATH)
