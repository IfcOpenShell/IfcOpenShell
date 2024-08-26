# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import annotations
import bpy.types
import math
import bmesh
import ifcopenshell.util.unit
from mathutils import Vector, Matrix
from typing import Union, Optional, Literal, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.geometry.helper import Helper


Z_AXIS = Vector((0, 0, 1))
X_AXIS = Vector((1, 0, 0))
EPSILON = 1e-6


def add_representation(
    file: ifcopenshell.file,
    *,  # keywords only as this API implementation is probably not final
    # IfcGeometricRepresentationContext
    context: ifcopenshell.entity_instance,
    # This is (currently) a Blender object, hence this depends on Blender now
    blender_object: bpy.types.Object,
    # This is (currently) a Blender data object, hence this depends on Blender now
    geometry: Union[bpy.types.Mesh, bpy.types.Curve],
    # Optionally apply a vector offset to all coordinates
    coordinate_offset: Optional[Vector] = None,
    # How many representation items to create
    total_items: int = 1,
    # A scale factor to apply for all vectors in case the unit is different
    unit_scale: Optional[float] = None,
    # If we should force faceted breps for meshes
    should_force_faceted_brep: bool = False,
    # If we should force triangulation for meshes
    should_force_triangulation: bool = False,
    # If UV coordinates should also be generated
    should_generate_uvs: bool = False,
    # Whether to cast a mesh into a particular class
    ifc_representation_class: Optional[
        Literal[
            "IfcExtrudedAreaSolid/IfcRectangleProfileDef",
            "IfcExtrudedAreaSolid/IfcCircleProfileDef",
            "IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef",
            "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids",
            "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage",
            "IfcGeometricCurveSet/IfcTextLiteral",
            "IfcTextLiteral",
        ]
    ] = None,
    # The material profile set if the extrusion requires it
    profile_set_usage: Optional[ifcopenshell.entity_instance] = None,
    # The text literal if the representation requires it
    text_literal: Optional[ifcopenshell.entity_instance] = None,
) -> ifcopenshell.entity_instance:
    # lazy import Helper to avoid circular import
    if "Helper" not in globals():
        from bonsai.bim.module.geometry.helper import Helper

        globals()["Helper"] = Helper

    usecase = Usecase()
    # TODO: This usecase currently depends on Blender's data model
    usecase.file = file
    usecase.settings = {
        "context": context,
        "blender_object": blender_object,
        "geometry": geometry,
        "coordinate_offset": coordinate_offset,
        "total_items": total_items,
        "unit_scale": unit_scale,
        "should_force_faceted_brep": should_force_faceted_brep,
        "should_force_triangulation": should_force_triangulation,
        "should_generate_uvs": should_generate_uvs,
        "ifc_representation_class": ifc_representation_class,
        "profile_set_usage": profile_set_usage,
        "text_literal": text_literal,
    }
    usecase.ifc_vertices = []
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        self.is_manifold = None
        if (
            isinstance(self.settings["geometry"], bpy.types.Mesh)
            and self.settings["geometry"] == self.settings["blender_object"].data
        ):
            self.evaluate_geometry()
        if self.settings["unit_scale"] is None:
            self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        if self.settings["context"].ContextType == "Model":
            return self.create_model_representation()
        elif self.settings["context"].ContextType == "Plan":
            return self.create_plan_representation()
        return self.create_variable_representation()

    def should_triangulate_face(self, face, threshold=EPSILON):
        vz = face.normal
        co = face.verts[0].co
        if vz.length < 0.5:
            return True
        if abs(vz.z) < 0.5:
            vx = vz.cross(Z_AXIS)
        else:
            vx = vz.cross(X_AXIS)
        vy = vx.cross(vz)
        tM = Matrix(
            [[vx.x, vy.x, vz.x, co.x], [vx.y, vy.y, vz.y, co.y], [vx.z, vy.z, vz.z, co.z], [0, 0, 0, 1]]
        ).inverted()

        return any([abs((tM @ v.co).z) > threshold for v in face.verts])

    def evaluate_geometry(self):
        for modifier in self.settings["blender_object"].modifiers:
            if modifier.type == "BOOLEAN":
                modifier.show_viewport = False

        mesh = self.settings["blender_object"].evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)

        self.is_manifold = True
        for edge in bm.edges:
            if not edge.is_manifold:
                self.is_manifold = False
                break

        if self.settings["should_force_triangulation"]:
            faces = bm.faces
        else:
            faces = [f for f in bm.faces if self.should_triangulate_face(f)]
        bmesh.ops.triangulate(bm, faces=faces)
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()
        del bm

        self.settings["geometry"] = mesh

        for modifier in self.settings["blender_object"].modifiers:
            if modifier.type == "BOOLEAN":
                modifier.show_viewport = True

    def create_model_representation(self):
        if self.settings["context"].is_a() == "IfcGeometricRepresentationContext":
            return self.create_variable_representation()
        elif self.settings["ifc_representation_class"] == "IfcTextLiteral":
            return self.create_text_representation(is_2d=False)
        elif self.settings["ifc_representation_class"] == "IfcGeometricCurveSet/IfcTextLiteral":
            shape_representation = self.create_geometric_curve_set_representation(is_2d=True)
            shape_representation.RepresentationType = "Annotation3D"
            items = list(shape_representation.Items)
            items.append(self.create_text())
            shape_representation.Items = items
            return shape_representation
        elif self.settings["context"].ContextIdentifier == "Annotation":
            return self.create_annotation3d_representation()
        elif self.settings["context"].ContextIdentifier == "Axis":
            return self.create_curve3d_representation()
        elif self.settings["context"].ContextIdentifier == "Body":
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "Box":
            return self.create_box_representation()
        elif self.settings["context"].ContextIdentifier == "Clearance":
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "CoG":
            return self.create_cog_representation()
        elif self.settings["context"].ContextIdentifier == "FootPrint":
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "Reference":
            if self.settings["context"].TargetView == "GRAPH_VIEW":
                return self.create_structural_reference_representation()
        elif self.settings["context"].ContextIdentifier == "Profile":
            return self.create_curve3d_representation()
        elif self.settings["context"].ContextIdentifier == "SurveyPoints":
            return self.create_geometric_curve_set_representation()
        elif self.settings["context"].ContextIdentifier == "Lighting":
            return self.create_lighting_representation()

    def create_plan_representation(self):
        if self.settings["ifc_representation_class"] == "IfcTextLiteral":
            return self.create_text_representation(is_2d=True)
        elif self.settings["ifc_representation_class"] == "IfcGeometricCurveSet/IfcTextLiteral":
            shape_representation = self.create_geometric_curve_set_representation(is_2d=True)
            shape_representation.RepresentationType = "Annotation2D"
            items = list(shape_representation.Items)
            items.append(self.create_text())
            shape_representation.Items = items
            return shape_representation
        elif self.settings["context"].ContextIdentifier == "Annotation":
            return self.create_annotation2d_representation()
        elif self.settings["context"].ContextIdentifier == "Axis":
            return self.create_curve2d_representation()
        elif self.settings["context"].ContextIdentifier == "Body":
            return self.create_annotation2d_representation()
        elif self.settings["context"].ContextIdentifier == "Box":
            pass
        elif self.settings["context"].ContextIdentifier == "Clearance":
            pass
        elif self.settings["context"].ContextIdentifier == "CoG":
            pass
        elif self.settings["context"].ContextIdentifier == "FootPrint":
            if self.settings["context"].TargetView in ["SKETCH_VIEW", "PLAN_VIEW", "REFLECTED_PLAN_VIEW"]:
                return self.create_geometric_curve_set_representation(is_2d=True)
        elif self.settings["context"].ContextIdentifier == "Reference":
            pass
        elif self.settings["context"].ContextIdentifier == "Profile":
            pass
        elif self.settings["context"].ContextIdentifier == "SurveyPoints":
            pass
        else:
            return self.create_annotation2d_representation()

    def create_lighting_representation(self):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "LightSource",
            [self.create_light_source()],
        )

    def create_light_source(self):
        if self.settings["geometry"].type == "POINT":
            return self.create_light_source_positional()

    def create_light_source_positional(self):
        return self.file.create_entity(
            "IfcLightSourcePositional",
            **{
                "LightColour": self.file.createIfcColourRgb(None, *self.settings["geometry"].color),
                "Position": self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                "Radius": self.convert_si_to_unit(self.settings["geometry"].shadow_soft_size),
            },
        )

    def create_text_representation(self, is_2d=False):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Annotation2D" if is_2d else "Annotation3D",
            [self.create_text()],
        )

    def create_text(self):
        if self.settings["text_literal"]:
            return self.settings["text_literal"]
        origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )

        # TODO: Planar extent right now is wrong ...
        return self.file.createIfcTextLiteralWithExtent(
            "TEXT", origin, "RIGHT", self.file.createIfcPlanarExtent(1000, 1000), "bottom-left"
        )

    def create_variable_representation(self):
        if isinstance(self.settings["geometry"], bpy.types.Curve) and self.settings["geometry"].bevel_depth:
            return self.create_swept_disk_solid_representation()
        elif isinstance(self.settings["geometry"], bpy.types.Curve):
            return self.create_curve3d_representation()
        elif isinstance(self.settings["geometry"], bpy.types.Camera):
            if self.settings["geometry"].type == "ORTHO":
                return self.create_camera_block_representation()
            elif self.settings["geometry"].type == "PERSP":
                return self.create_camera_pyramid_representation()
        elif not len(self.settings["geometry"].edges):
            return self.create_point_cloud_representation()
        elif not len(self.settings["geometry"].polygons):
            return self.create_curve3d_representation()
        elif self.settings["ifc_representation_class"] == "IfcExtrudedAreaSolid/IfcRectangleProfileDef":
            return self.create_rectangle_extrusion_representation()
        elif self.settings["ifc_representation_class"] == "IfcExtrudedAreaSolid/IfcCircleProfileDef":
            return self.create_circle_extrusion_representation()
        elif self.settings["ifc_representation_class"] == "IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef":
            return self.create_arbitrary_extrusion_representation()
        elif self.settings["ifc_representation_class"] == "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids":
            return self.create_arbitrary_void_extrusion_representation()
        elif self.settings["ifc_representation_class"] == "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage":
            return self.create_material_profile_set_extrusion_representation()
        return self.create_mesh_representation()

    def create_camera_block_representation(self):
        raster_x = self.settings["geometry"].BIMCameraProperties.raster_x
        raster_y = self.settings["geometry"].BIMCameraProperties.raster_y

        if self.is_camera_landscape():
            width = self.settings["geometry"].ortho_scale
            height = width / raster_x * raster_y
        else:
            height = self.settings["geometry"].ortho_scale
            width = height / raster_y * raster_x

        block = self.file.create_entity(
            "IfcBlock",
            Position=self.file.createIfcAxis2Placement3D(
                self.create_cartesian_point(-width / 2, -height / 2, -self.settings["geometry"].clip_end)
            ),
            XLength=self.convert_si_to_unit(width),
            YLength=self.convert_si_to_unit(height),
            ZLength=self.convert_si_to_unit(self.settings["geometry"].clip_end),
        )

        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "CSG",
            [self.file.createIfcCsgSolid(block)],
        )

    def create_camera_pyramid_representation(self):
        raster_x = self.settings["geometry"].BIMCameraProperties.raster_x
        raster_y = self.settings["geometry"].BIMCameraProperties.raster_y
        fov = self.settings["geometry"].angle

        clip_end = self.settings["geometry"].clip_end
        clip_start = self.settings["geometry"].clip_start

        if self.is_camera_landscape():
            half_width = math.tan(fov / 2) * clip_end
            half_height = half_width * raster_y / raster_x
        else:
            half_height = math.tan(fov / 2) * clip_end
            half_width = half_height * raster_x / raster_y

        x_length = 2 * half_width
        y_length = 2 * half_height

        pyramid = self.file.create_entity(
            "IfcRectangularPyramid",
            Position=self.file.createIfcAxis2Placement3D(
                self.create_cartesian_point(-x_length / 2, -y_length / 2, -clip_end)
            ),
            XLength=self.convert_si_to_unit(x_length),
            YLength=self.convert_si_to_unit(y_length),
            Height=self.convert_si_to_unit(clip_end),
        )

        surface = self.file.createIfcPlane(
            self.file.createIfcAxis2Placement3D(self.create_cartesian_point(0, 0, -clip_start))
        )
        half_space = self.file.createIfcHalfSpaceSolid(surface, False)

        clipping_result = self.file.create_entity("IfcBooleanResult", "DIFFERENCE", pyramid, half_space)

        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "CSG",
            [self.file.createIfcCsgSolid(clipping_result)],
        )

    def is_camera_landscape(self):
        return (
            self.settings["geometry"].BIMCameraProperties.raster_x
            > self.settings["geometry"].BIMCameraProperties.raster_y
        )

    def create_swept_disk_solid_representation(self):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "AdvancedSweptSolid",
            self.create_swept_disk_solids(),
        )

    def create_curve3d_representation(self):
        if curves := self.create_curves():
            return self.file.createIfcShapeRepresentation(
                self.settings["context"], self.settings["context"].ContextIdentifier, "Curve3D", curves
            )

    def create_curve2d_representation(self):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Curve2D",
            self.create_curves(is_2d=True),
        )

    def create_curve_bounded_planes(self, is_2d=False):
        items = []
        if self.file.schema != "IFC2X3":
            points = self.create_cartesian_point_list_from_vertices(self.settings["geometry"].vertices, is_2d=False)
        for polygon in self.settings["geometry"].polygons:
            plane = self.create_plane(polygon)
            if self.file.schema == "IFC2X3":
                curve = self.create_curve_from_polygon_ifc2x3(polygon, is_2d=False)
            else:
                curve = self.create_curve_from_polygon(points, polygon, is_2d=False)
            items.append(self.file.createIfcCurveBoundedPlane(BasisSurface=plane, OuterBoundary=curve))
        return items

    def create_plane(self, polygon):
        return self.file.createIfcPlane(
            Position=self.file.createIfcAxis2Placement3D(
                Location=self.file.createIfcCartesianPoint(polygon.center),
                Axis=self.file.createIfcDirection(polygon.normal),
            )
        )

    def create_annotation_fill_areas(self, is_2d=False) -> list[ifcopenshell.entity_instance]:
        items = []
        if self.file.schema != "IFC2X3":
            points = self.create_cartesian_point_list_from_vertices(self.settings["geometry"].vertices, is_2d=is_2d)
        for polygon in self.settings["geometry"].polygons:
            if self.file.schema == "IFC2X3":
                curve = self.create_curve_from_polygon_ifc2x3(polygon, is_2d=is_2d)
            else:
                curve = self.create_curve_from_polygon(points, polygon, is_2d=is_2d)
            items.append(self.file.createIfcAnnotationFillArea(OuterBoundary=curve))
        return items

    def create_curve_from_polygon(
        self, points: ifcopenshell.entity_instance, polygon: bpy.types.MeshPolygon, is_2d=False
    ) -> ifcopenshell.entity_instance:
        indices = list(polygon.vertices)
        indices.append(indices[0])
        edge_loop = [self.file.createIfcLineIndex((v1 + 1, v2 + 1)) for v1, v2 in zip(indices, indices[1:])]
        return self.file.createIfcIndexedPolyCurve(points, edge_loop)

    def create_curve_from_polygon_ifc2x3(self, polygon, is_2d=False):
        indices = list(polygon.vertices)
        indices.append(indices[0])
        points = [
            self.create_cartesian_point(v.co.x, v.co.y, v.co.z if not is_2d else None)
            for v in self.settings["geometry"].vertices
        ]
        return self.file.createIfcPolyline([points[i] for i in indices])

    def create_swept_disk_solids(self):
        curves = self.create_curves()
        results = []
        radius = self.convert_si_to_unit(round(self.settings["geometry"].bevel_depth, 3))
        for curve in curves:
            results.append(self.file.createIfcSweptDiskSolid(curve, radius))
        return results

    def is_mesh_curve_consecutive(self, geom_data):
        import bonsai.tool as tool

        bm = tool.Blender.get_bmesh_for_mesh(geom_data)
        bm.verts.ensure_lookup_table()
        start_vert = bm.verts[0]
        n_verts = len(bm.verts)
        cur_edges = bm.verts[0].link_edges

        if len(cur_edges) > 2:
            return False
        elif cur_edges == 2:
            edge0, edge1 = cur_edges
        else:
            edge0, edge1 = cur_edges[0], None

        processed_verts = set()
        processed_verts.add(start_vert)

        def validate_edge(edge, start_vert, processed_verts):
            cur_vert = edge.other_vert(start_vert)
            while True:
                if cur_vert == start_vert:
                    break
                if cur_vert in processed_verts:
                    return
                processed_verts.add(cur_vert)
                edges = cur_vert.link_edges
                if len(edges) > 2:
                    return
                elif len(edges) == 1:
                    return True
                edge = next(e for e in edges if e != edge)
                cur_vert = edge.other_vert(cur_vert)
            return True

        if not validate_edge(edge0, start_vert, processed_verts):
            return

        if edge1 and not validate_edge(edge1, start_vert, processed_verts):
            return

        if len(processed_verts) != n_verts:
            return False
        return True

    def create_curves(self, should_exclude_faces=False, is_2d=False, ignore_non_loose_edges=False):
        geom_data = self.settings["geometry"]

        if isinstance(geom_data, bpy.types.Mesh):
            if self.is_mesh_curve_consecutive(geom_data):
                if self.file.schema == "IFC2X3":
                    return self.create_curves_from_mesh_ifc2x3(should_exclude_faces=should_exclude_faces, is_2d=is_2d)
                return self.create_curves_from_mesh(should_exclude_faces=should_exclude_faces, is_2d=is_2d)

        import bonsai.tool as tool

        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object

        # create dummy object that will have more detailed curves
        # since now we do not really support splines curves natively
        obj = self.settings["blender_object"]
        dummy = bpy.data.objects.new("Dummy", obj.data.copy())
        bpy.context.scene.collection.objects.link(dummy)
        tool.Blender.select_and_activate_single_object(bpy.context, dummy)
        if not isinstance(geom_data, bpy.types.Mesh):
            bpy.ops.object.convert(target="MESH")
        self.remove_doubles_from_mesh(dummy.data)
        bpy.ops.object.convert(target="CURVE")

        if self.file.schema == "IFC2X3":
            curves = self.create_curves_from_curve_ifc2x3(is_2d=is_2d, curve_object_data=dummy.data)
        else:
            curves = self.create_curves_from_curve(is_2d=is_2d, curve_object_data=dummy.data)

        # restore objects selection
        bpy.data.objects.remove(dummy)
        tool.Blender.set_objects_selection(bpy.context, active_object, selected_objects)
        return curves

    def create_curves_from_mesh(self, should_exclude_faces=False, is_2d=False):
        geom_data = self.settings["geometry"].copy()
        self.remove_doubles_from_mesh(geom_data)
        curves = []
        points = self.create_cartesian_point_list_from_vertices(geom_data.vertices, is_2d=is_2d)
        edge_loops = []
        previous_edge = None
        edge_loop = []
        face_edges = set()
        if should_exclude_faces:
            [face_edges.union([geom_data.edge_keys.index(ek) for ek in p.edge_keys]) for p in geom_data.polygons]
        for i, edge in enumerate(geom_data.edges):
            if should_exclude_faces and i in face_edges:
                continue
            elif previous_edge is None:
                edge_loop = [self.file.createIfcLineIndex((edge.vertices[0] + 1, edge.vertices[1] + 1))]
            elif edge.vertices[0] == previous_edge.vertices[1]:
                edge_loop.append(self.file.createIfcLineIndex((edge.vertices[0] + 1, edge.vertices[1] + 1)))
            else:
                edge_loops.append(edge_loop)
                edge_loop = [self.file.createIfcLineIndex((edge.vertices[0] + 1, edge.vertices[1] + 1))]
            previous_edge = edge
        edge_loops.append(edge_loop)
        for edge_loop in edge_loops:
            curves.append(self.file.createIfcIndexedPolyCurve(points, edge_loop))
        return curves

    def remove_doubles_from_mesh(self, mesh):
        import bonsai.tool as tool

        bm = tool.Blender.get_bmesh_for_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        tool.Blender.apply_bmesh(mesh, bm)

    def create_curves_from_mesh_ifc2x3(
        self, should_exclude_faces=False, is_2d=False
    ) -> list[ifcopenshell.entity_instance]:
        geom_data = self.settings["geometry"].copy()
        self.remove_doubles_from_mesh(geom_data)
        curves = []
        points = [
            self.create_cartesian_point(v.co.x, v.co.y, v.co.z if not is_2d else None) for v in geom_data.vertices
        ]
        coord_list = [p.Coordinates for p in points]
        edge_loops = []
        previous_edge = None
        edge_loop = []
        face_edges = set()
        if should_exclude_faces:
            [face_edges.union([geom_data.edge_keys.index(ek) for ek in p.edge_keys]) for p in geom_data.polygons]
        for i, edge in enumerate(geom_data.edges):
            if should_exclude_faces and i in face_edges:
                continue
            elif previous_edge is None:
                edge_loop = [edge.vertices]
            elif edge.vertices[0] == previous_edge.vertices[1]:
                edge_loop.append(edge.vertices)
            else:
                edge_loops.append(edge_loop)
                edge_loop = [edge.vertices]
            previous_edge = edge
        edge_loops.append(edge_loop)
        for edge_loop in edge_loops:
            loop_points = [points[p[0]] for p in edge_loop]
            loop_points.append(points[edge_loop[-1][1]])
            curves.append(self.file.createIfcPolyline(loop_points))
        return curves

    def create_curves_from_curve_ifc2x3(self, is_2d=False, curve_object_data=None):
        # TODO: support interpolated curves, not just polylines
        if not curve_object_data:
            curve_object_data = self.settings["geometry"]
        dim = (lambda v: v.xy) if is_2d else (lambda v: v.xyz)
        results = []
        for spline in curve_object_data.splines:
            points = spline.bezier_points[:] + spline.points[:]
            if spline.use_cyclic_u:
                points.append(points[0])
            ifc_points = [self.create_cartesian_point(*dim(point.co)) for point in points]
            results.append(self.file.createIfcPolyline(ifc_points))
        return results

    def create_curves_from_curve(self, is_2d=False, curve_object_data=None):
        # TODO: support interpolated curves, not just polylines
        if not curve_object_data:
            curve_object_data = self.settings["geometry"]
        dim = (lambda v: v.xy) if is_2d else (lambda v: v.xyz)
        to_units = lambda v: Vector([self.convert_si_to_unit(i) for i in v])
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.file)
        results = []

        for spline in curve_object_data.splines:
            points = spline.bezier_points[:] + spline.points[:]

            points = [to_units(dim(p.co)) for p in points]
            closed_polyline = spline.use_cyclic_u and len(points) > 1
            results.append(builder.polyline(points, closed=closed_polyline))

        return results

    def create_point_cloud_representation(self, is_2d=False):
        if self.file.schema == "IFC2X3":
            geometric_set = []
            for point in self.settings["geometry"].vertices:
                if is_2d:
                    geometric_set.append(self.create_cartesian_point(point.co.x, point.co.y))
                else:
                    geometric_set.append(self.create_cartesian_point(point.co.x, point.co.y, point.co.z))
            return self.file.createIfcShapeRepresentation(
                self.settings["context"],
                self.settings["context"].ContextIdentifier,
                "GeometricSet",
                geometric_set,
            )

        point_cloud = self.create_cartesian_point_list_from_vertices(self.settings["geometry"].vertices, is_2d)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Point" if self.file.schema == "IFC4X3" else "PointCloud",
            [point_cloud],
        )

    def create_rectangle_extrusion_representation(self):
        helper = Helper(self.file)
        indices = helper.auto_detect_rectangle_profile_extruded_area_solid(self.settings["geometry"])
        profile_def = helper.create_rectangle_profile_def(self.settings["geometry"], indices["profile"])
        item = helper.create_extruded_area_solid(self.settings["geometry"], indices["extrusion"], profile_def)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "SweptSolid",
            [item],
        )

    def create_circle_extrusion_representation(self):
        helper = Helper(self.file)
        indices = helper.auto_detect_circle_profile_extruded_area_solid(self.settings["geometry"])
        profile_def = helper.create_circle_profile_def(self.settings["geometry"], indices["profile"])
        item = helper.create_extruded_area_solid(self.settings["geometry"], indices["extrusion"], profile_def)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "SweptSolid",
            [item],
        )

    def create_arbitrary_extrusion_representation(self):
        helper = Helper(self.file)
        indices = helper.auto_detect_arbitrary_closed_profile_extruded_area_solid(self.settings["geometry"])
        profile_def = helper.create_arbitrary_closed_profile_def(self.settings["geometry"], indices["profile"])
        item = helper.create_extruded_area_solid(self.settings["geometry"], indices["extrusion"], profile_def)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "SweptSolid",
            [item],
        )

    def create_arbitrary_void_extrusion_representation(self):
        helper = Helper(self.file)
        indices = helper.auto_detect_arbitrary_profile_with_voids_extruded_area_solid(self.settings["geometry"])
        if not indices["inner_curves"]:
            return self.create_arbitrary_extrusion_representation()
        profile_def = helper.create_arbitrary_profile_def_with_voids(
            self.settings["geometry"], indices["profile"], indices["inner_curves"]
        )
        item = helper.create_extruded_area_solid(self.settings["geometry"], indices["extrusion"], profile_def)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "SweptSolid",
            [item],
        )

    def create_material_profile_set_extrusion_representation(self):
        profile_set = self.settings["profile_set_usage"].ForProfileSet
        profile_def = profile_set.CompositeProfile or profile_set.MaterialProfiles[0].Profile
        position = None
        if self.file.schema == "IFC2X3":
            position = self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                self.file.createIfcDirection((0.0, 0.0, 1.0)),
                self.file.createIfcDirection((1.0, 0.0, 0.0)),
            )
        item = self.file.createIfcExtrudedAreaSolid(
            profile_def,
            position,
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.convert_si_to_unit(self.settings["blender_object"].dimensions[2]),
        )
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "SweptSolid",
            [item],
        )

    def create_mesh_representation(self):
        if self.file.schema == "IFC2X3" or self.settings["should_force_faceted_brep"]:
            return self.create_faceted_brep()
        if self.settings["should_force_triangulation"]:
            return self.create_triangulated_face_set()
        return self.create_polygonal_face_set()

    def create_faceted_brep(self):
        self.create_vertices()
        ifc_raw_items = [None] * self.settings["total_items"]
        for i, value in enumerate(ifc_raw_items):
            ifc_raw_items[i] = []
        for polygon in self.settings["geometry"].polygons:
            ifc_raw_items[polygon.material_index % self.settings["total_items"]].append(
                self.file.createIfcFace(
                    [
                        self.file.createIfcFaceOuterBound(
                            self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                            True,
                        )
                    ]
                )
            )
        # TODO: May not actually be a closed shell, but who checks anyway?
        items = [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(i)) for i in ifc_raw_items if i]
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Brep",
            items,
        )

    def create_triangulated_face_set(self):
        ifc_raw_items = [None] * self.settings["total_items"]
        if self.settings["should_generate_uvs"]:
            ifc_raw_uv_items = [None] * self.settings["total_items"]
        for i, value in enumerate(ifc_raw_items):
            ifc_raw_items[i] = []
            if self.settings["should_generate_uvs"]:
                ifc_raw_uv_items[i] = []
        for polygon in self.settings["geometry"].polygons:
            ifc_raw_items[polygon.material_index % self.settings["total_items"]].append(
                [v + 1 for v in polygon.vertices]
            )
            if self.settings["should_generate_uvs"]:
                ifc_raw_uv_items[polygon.material_index % self.settings["total_items"]].append(
                    [uv + 1 for uv in polygon.loop_indices]
                )

        coordinates = self.create_cartesian_point_list_from_vertices(self.settings["geometry"].vertices)

        if self.settings["should_generate_uvs"]:
            # Blender supports multiple UV layers. We don't. Too bad.
            tex_coords = self.file.createIfcTextureVertexList(
                [tuple(x.uv) for x in self.settings["geometry"].uv_layers[0].data]
            )
            items = []
            for i, coord_index in enumerate(ifc_raw_items):
                if not coord_index:
                    continue
                tex_coords_index = ifc_raw_uv_items[i]
                face_set = self.file.createIfcTriangulatedFaceSet(coordinates, None, None, coord_index)
                texture_map = self.file.createIfcIndexedTriangleTextureMap(
                    MappedTo=face_set, TexCoords=tex_coords, TexCoordIndex=tex_coords_index
                )
                items.append(face_set)
        else:
            items = [self.file.createIfcTriangulatedFaceSet(coordinates, None, None, i) for i in ifc_raw_items if i]

        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Tessellation",
            items,
        )

    def create_polygonal_face_set(self):
        ifc_raw_items = [None] * self.settings["total_items"]
        for i, value in enumerate(ifc_raw_items):
            ifc_raw_items[i] = []
        for polygon in self.settings["geometry"].polygons:
            ifc_raw_items[polygon.material_index % self.settings["total_items"]].append(
                self.file.createIfcIndexedPolygonalFace([v + 1 for v in polygon.vertices])
            )
        coordinates = self.create_cartesian_point_list_from_vertices(self.settings["geometry"].vertices)
        items = [self.file.createIfcPolygonalFaceSet(coordinates, self.is_manifold, i) for i in ifc_raw_items if i]
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Tessellation",
            items,
        )

    def create_vertices(self, is_2d=False):
        if is_2d:
            for v in self.settings["geometry"].vertices:
                co = self.convert_si_to_unit(v.co)
                self.ifc_vertices.append(self.file.createIfcCartesianPoint((co[0], co[1])))
            return
        self.ifc_vertices.extend(
            [
                self.file.createIfcCartesianPoint(self.convert_si_to_unit(v.co))
                for v in self.settings["geometry"].vertices
            ]
        )

    def create_cartesian_point(self, x, y, z=None, is_model_coords=True):
        if is_model_coords and self.settings["coordinate_offset"]:
            x += self.settings["coordinate_offset"][0]
            y += self.settings["coordinate_offset"][1]
            if z:
                z += self.settings["coordinate_offset"][2]
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def create_cartesian_point_list_from_vertices(
        self, vertices: list[bpy.types.MeshVertex], is_2d=False, is_model_coords=True
    ):
        if is_model_coords and self.settings["coordinate_offset"]:
            if is_2d:
                xy_offset = Vector((self.settings["coordinate_offset"][0:2]))
                return self.file.createIfcCartesianPointList2D(
                    [self.convert_si_to_unit(v.co.xy + xy_offset) for v in vertices]
                )
            xyz_offset = Vector((self.settings["coordinate_offset"][0:3]))
            return self.file.createIfcCartesianPointList3D(
                [self.convert_si_to_unit(v.co.xyz + xyz_offset) for v in vertices]
            )
        if is_2d:
            return self.file.createIfcCartesianPointList2D([self.convert_si_to_unit(v.co.xy) for v in vertices])
        return self.file.createIfcCartesianPointList3D([self.convert_si_to_unit(v.co) for v in vertices])

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]

    def create_annotation2d_representation(self):
        if isinstance(self.settings["geometry"], bpy.types.Mesh) and len(self.settings["geometry"].polygons):
            items = self.create_annotation_fill_areas(is_2d=True)
        elif isinstance(self.settings["geometry"], bpy.types.Mesh) and not len(self.settings["geometry"].edges):
            return self.create_point_cloud_representation(is_2d=True)
        else:
            items = [self.file.createIfcGeometricCurveSet(self.create_curves(is_2d=True))]
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Annotation2D",
            items,
        )

    def create_annotation3d_representation(self):
        items = []
        if isinstance(self.settings["geometry"], bpy.types.Mesh) and len(self.settings["geometry"].polygons):
            items = self.create_annotation_fill_areas(is_2d=False)
        else:
            items = [self.file.createIfcGeometricCurveSet(self.create_curves(is_2d=False))]
        # TODO Unsure when it is appropriate to use curve bounded planes
        # surfaces = self.create_curve_bounded_planes()
        # if surfaces:
        #     items.append(self.file.createIfcGeometricSet(surfaces))
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "GeometricSet",
            items,
        )

    def create_geometric_curve_set_representation(self, is_2d=False):
        geometric_curve_set = self.file.createIfcGeometricCurveSet(self.create_curves(is_2d=is_2d))
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "GeometricCurveSet",
            [geometric_curve_set],
        )

    def create_box_representation(self):
        obj = self.settings["blender_object"]
        bounding_box = self.file.createIfcBoundingBox(
            self.create_cartesian_point(obj.bound_box[0][0], obj.bound_box[0][1], obj.bound_box[0][2]),
            self.convert_si_to_unit(obj.dimensions[0]),
            self.convert_si_to_unit(obj.dimensions[1]),
            self.convert_si_to_unit(obj.dimensions[2]),
        )
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "BoundingBox",
            [bounding_box],
        )

    def create_structural_reference_representation(self):
        if len(self.settings["geometry"].vertices) == 1:
            return self.file.createIfcTopologyRepresentation(
                self.settings["context"],
                self.settings["context"].ContextIdentifier,
                "Vertex",
                [self.create_vertex_point(self.settings["geometry"].vertices[0].co)],
            )
        return self.file.createIfcTopologyRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Edge",
            [self.create_edge()],
        )

    def create_vertex_point(self, point):
        return self.file.createIfcVertexPoint(self.create_cartesian_point(point.x, point.y, point.z))

    def create_edge(self):
        if hasattr(self.settings["geometry"], "splines"):
            points = self.get_spline_points(self.settings["geometry"].splines[0])
        else:
            points = self.settings["geometry"].vertices
        if not points:
            return
        return self.file.createIfcEdge(self.create_vertex_point(points[0].co), self.create_vertex_point(points[1].co))
