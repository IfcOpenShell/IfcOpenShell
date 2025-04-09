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
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import numpy as np
import numpy.typing as npt
from mathutils import Vector, Matrix
from typing import Union, Optional, Literal, Any, TYPE_CHECKING
from ifcopenshell.util.shape_builder import ifc_safe_vector_type, VectorType

if TYPE_CHECKING:
    from bonsai.bim.module.geometry.helper import Helper


Z_AXIS = Vector((0, 0, 1))
X_AXIS = Vector((1, 0, 0))
EPSILON = 1e-6


def add_representation(
    file: ifcopenshell.file,
    *,  # keywords only as this API implementation is probably not final
    context: ifcopenshell.entity_instance,
    blender_object: bpy.types.Object,
    geometry: Union[bpy.types.Mesh, bpy.types.Curve],
    coordinate_offset: Optional[npt.NDArray[np.float64]] = None,
    total_items: int = 1,
    unit_scale: Optional[float] = None,
    should_force_faceted_brep: bool = False,
    should_force_triangulation: bool = False,
    should_generate_uvs: bool = False,
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
    profile_set_usage: Optional[ifcopenshell.entity_instance] = None,
    text_literal: Optional[ifcopenshell.entity_instance] = None,
) -> Union[ifcopenshell.entity_instance, None]:
    """Add an IfcShapeRepresentation.

    :param context: The IfcGeometricRepresentationContext.
    :param blender_object: This is (currently) a Blender object, hence this depends on Blender now.
    :param geometry: This is (currently) a Blender data object, hence this depends on Blender now.
    :param coordinate_offset: Optionally apply a vector offset to all coordinates (in SI units).
    :param total_items: How many representation items to create.
    :param unit_scale: A scale factor to apply for all vectors in case the unit is different.
    :param should_force_faceted_brep: If we should force faceted breps for meshes.
    :param should_force_triangulation: If we should force triangulation for meshes.
    :param should_generate_uvs:  If UV coordinates should also be generated.
    :param ifc_representation_class: Whether to cast a mesh into a particular class
    :param profile_set_usage: The material profile set if the extrusion requires it
    :param text_literal: The text literal if the representation requires it
    :return: IfcShapeRepresentation or None if couldn't create representation
        for the provided context.
    """
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
        "coordinate_offset": coordinate_offset if coordinate_offset is not None else None,
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
    ifc_vertices: list[ifcopenshell.entity_instance]
    coordinate_offset: Union[npt.NDArray[np.float64], None]
    geometry: Union[bpy.types.Mesh, bpy.types.Curve]
    blender_object: bpy.types.Object

    def execute(self) -> Union[ifcopenshell.entity_instance, None]:
        self.is_manifold = None
        self.coordinate_offset = self.settings["coordinate_offset"]
        self.geometry = self.settings["geometry"]
        self.blender_object = self.settings["blender_object"]

        if isinstance(self.geometry, bpy.types.Mesh) and self.geometry == self.blender_object.data:
            self.evaluate_geometry()
        if self.settings["unit_scale"] is None:
            self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        if self.settings["context"].ContextType == "Model":
            return self.create_model_representation()
        elif self.settings["context"].ContextType == "Plan":
            return self.create_plan_representation()
        return self.create_variable_representation()

    def should_triangulate_face(self, face: bmesh.types.BMFace, threshold: float = EPSILON) -> bool:
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

    def evaluate_geometry(self) -> None:
        for modifier in self.blender_object.modifiers:
            if modifier.type == "BOOLEAN":
                modifier.show_viewport = False

        mesh = self.blender_object.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
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

        for modifier in self.blender_object.modifiers:
            if modifier.type == "BOOLEAN":
                modifier.show_viewport = True

    def create_model_representation(self) -> Union[ifcopenshell.entity_instance, None]:
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
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "Profile":
            return self.create_curve3d_representation()
        elif self.settings["context"].ContextIdentifier == "SurveyPoints":
            return self.create_geometric_curve_set_representation()
        elif self.settings["context"].ContextIdentifier == "Lighting":
            return self.create_lighting_representation()

    def create_plan_representation(self) -> Union[ifcopenshell.entity_instance, None]:
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

    def create_lighting_representation(self) -> ifcopenshell.entity_instance:
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "LightSource",
            [self.create_light_source()],
        )

    def create_light_source(self) -> Union[ifcopenshell.entity_instance, None]:
        if self.settings["geometry"].type == "POINT":
            return self.create_light_source_positional()

    def create_light_source_positional(self) -> ifcopenshell.entity_instance:
        return self.file.create_entity(
            "IfcLightSourcePositional",
            **{
                "LightColour": self.file.createIfcColourRgb(None, *self.settings["geometry"].color),
                "Position": self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                "Radius": self.convert_si_to_unit(self.settings["geometry"].shadow_soft_size),
            },
        )

    def create_text_representation(self, is_2d: bool = False) -> ifcopenshell.entity_instance:
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Annotation2D" if is_2d else "Annotation3D",
            [self.create_text()],
        )

    def create_text(self) -> ifcopenshell.entity_instance:
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

    def create_variable_representation(self) -> Union[ifcopenshell.entity_instance, None]:
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

    def create_camera_block_representation(self) -> ifcopenshell.entity_instance:
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

    def create_camera_pyramid_representation(self) -> ifcopenshell.entity_instance:
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

    def is_camera_landscape(self) -> bool:
        return (
            self.settings["geometry"].BIMCameraProperties.raster_x
            > self.settings["geometry"].BIMCameraProperties.raster_y
        )

    def create_swept_disk_solid_representation(self) -> ifcopenshell.entity_instance:
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "AdvancedSweptSolid",
            self.create_swept_disk_solids(),
        )

    def create_curve3d_representation(self) -> Union[ifcopenshell.entity_instance, None]:
        if curves := self.create_curves():
            return self.file.createIfcShapeRepresentation(
                self.settings["context"], self.settings["context"].ContextIdentifier, "Curve3D", curves
            )

    def create_curve2d_representation(self) -> ifcopenshell.entity_instance:
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Curve2D",
            self.create_curves(is_2d=True),
        )

    def create_curve_bounded_planes(self, is_2d: bool = False) -> list[ifcopenshell.entity_instance]:
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

    def create_plane(self, polygon: bpy.types.MeshPolygon) -> ifcopenshell.entity_instance:
        return self.file.createIfcPlane(
            Position=self.file.createIfcAxis2Placement3D(
                Location=self.file.createIfcCartesianPoint(polygon.center),
                Axis=self.file.createIfcDirection(polygon.normal),
            )
        )

    def create_annotation_fill_areas(self, is_2d: bool = False) -> list[ifcopenshell.entity_instance]:
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
        self, points: ifcopenshell.entity_instance, polygon: bpy.types.MeshPolygon, is_2d: bool = False
    ) -> ifcopenshell.entity_instance:
        indices = list(polygon.vertices)
        indices.append(indices[0])
        edge_loop = [self.file.createIfcLineIndex((v1 + 1, v2 + 1)) for v1, v2 in zip(indices, indices[1:])]
        return self.file.createIfcIndexedPolyCurve(points, edge_loop)

    def create_curve_from_polygon_ifc2x3(
        self, polygon: bpy.types.MeshPolygon, is_2d: bool = False
    ) -> ifcopenshell.entity_instance:
        indices = list(polygon.vertices)
        indices.append(indices[0])
        points = [
            self.create_cartesian_point(v.co.x, v.co.y, v.co.z if not is_2d else None)
            for v in self.settings["geometry"].vertices
        ]
        return self.file.createIfcPolyline([points[i] for i in indices])

    def create_swept_disk_solids(self) -> list[ifcopenshell.entity_instance]:
        curves = self.create_curves()
        results = []
        radius = self.convert_si_to_unit(round(self.settings["geometry"].bevel_depth, 3))
        for curve in curves:
            results.append(self.file.createIfcSweptDiskSolid(curve, radius))
        return results

    def is_mesh_curve_consecutive(self, geom_data: bpy.types.Mesh) -> bool:
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
            return False

        if edge1 and not validate_edge(edge1, start_vert, processed_verts):
            return False

        if len(processed_verts) != n_verts:
            return False
        return True

    def create_curves(
        self, should_exclude_faces: bool = False, is_2d: bool = False, ignore_non_loose_edges: bool = False
    ) -> list[ifcopenshell.entity_instance]:
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
        obj = self.blender_object
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

    def create_curves_from_mesh(
        self, should_exclude_faces: bool = False, is_2d: bool = False
    ) -> list[ifcopenshell.entity_instance]:
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

    def remove_doubles_from_mesh(self, mesh: bpy.types.Mesh) -> None:
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

    def create_curves_from_curve_ifc2x3(
        self, is_2d: bool = False, curve_object_data: Optional[bpy.types.Curve] = None
    ) -> list[ifcopenshell.entity_instance]:
        # TODO: support interpolated curves, not just polylines
        if not curve_object_data:
            curve_object_data = self.settings["geometry"]
        dim = (lambda v: v.xy) if is_2d else (lambda v: v.xyz)
        results = []
        for spline in curve_object_data.splines:
            points = self.get_spline_points(spline)
            ifc_points = [self.create_cartesian_point(*dim(point.co)) for point in points]
            results.append(self.file.createIfcPolyline(ifc_points))
        return results

    def create_curves_from_curve(
        self, is_2d: bool = False, curve_object_data: Optional[bpy.types.Curve] = None
    ) -> list[ifcopenshell.entity_instance]:
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

    def create_point_cloud_representation(self, is_2d: bool = False) -> ifcopenshell.entity_instance:
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

    def create_rectangle_extrusion_representation(self) -> ifcopenshell.entity_instance:
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

    def create_circle_extrusion_representation(self) -> ifcopenshell.entity_instance:
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

    def create_arbitrary_extrusion_representation(self) -> ifcopenshell.entity_instance:
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

    def create_arbitrary_void_extrusion_representation(self) -> ifcopenshell.entity_instance:
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

    def create_material_profile_set_extrusion_representation(self) -> ifcopenshell.entity_instance:
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
            self.convert_si_to_unit(self.blender_object.dimensions[2]),
        )
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "SweptSolid",
            [item],
        )

    def create_mesh_representation(self) -> ifcopenshell.entity_instance:
        if self.file.schema == "IFC2X3" or self.settings["should_force_faceted_brep"]:
            return self.create_faceted_brep()
        if self.settings["should_force_triangulation"]:
            return self.create_triangulated_face_set()
        return self.create_polygonal_face_set()

    def create_faceted_brep(self) -> ifcopenshell.entity_instance:
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

    def create_triangulated_face_set(self) -> ifcopenshell.entity_instance:
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

    def create_polygonal_face_set(self) -> ifcopenshell.entity_instance:
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

    def create_vertices(self, is_2d: bool = False) -> None:
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

    def create_cartesian_point(
        self, x: float, y: float, z: Optional[float] = None, is_model_coords: bool = True
    ) -> ifcopenshell.entity_instance:
        """Create IfcCartesianPoint.

        x, y, z coords are provided in SI units.
        """
        if is_model_coords and self.coordinate_offset is not None:
            x += self.coordinate_offset[0]
            y += self.coordinate_offset[1]
            if z is not None:
                z += self.coordinate_offset[2]
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def create_cartesian_point_list_from_vertices(
        self, vertices: bpy.types.MeshVertices, is_2d: bool = False, is_model_coords: bool = True
    ) -> ifcopenshell.entity_instance:
        # Catch values as floats to benefit from fast buffer copy.
        coords = np.empty(len(vertices) * 3, dtype="f")
        vertices.foreach_get("co", coords)
        coords = coords.reshape(-1, 3)

        if is_2d:
            coords = coords[:, :2]
            coords_class = "IfcCartesianPointList2D"
        else:
            coords_class = "IfcCartesianPointList3D"

        if is_model_coords and (offset := self.coordinate_offset) is not None:
            coords = coords.astype("d")
            if is_2d:
                offset = offset[:2]
            coords += offset

        return self.file.create_entity(coords_class, ifc_safe_vector_type(self.convert_si_to_unit(coords)))

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]

    def create_annotation2d_representation(self) -> ifcopenshell.entity_instance:
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

    def create_annotation3d_representation(self) -> ifcopenshell.entity_instance:
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

    def create_geometric_curve_set_representation(self, is_2d: bool = False) -> ifcopenshell.entity_instance:
        geometric_curve_set = self.file.createIfcGeometricCurveSet(self.create_curves(is_2d=is_2d))
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "GeometricCurveSet",
            [geometric_curve_set],
        )

    def create_box_representation(self) -> ifcopenshell.entity_instance:
        obj = self.blender_object
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

    def create_cog_representation(self) -> Union[ifcopenshell.entity_instance, None]:
        mesh = self.settings["geometry"]
        if not isinstance(mesh, bpy.types.Mesh) or len(verts := mesh.vertices) == 0:
            return
        vert = verts[0].co
        cog = self.create_cartesian_point(vert.x, vert.y, vert.z)
        return self.file.create_entity(
            "IfcShapeRepresentation",
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Point",
            (cog,),
        )

    def create_structural_reference_representation(self) -> ifcopenshell.entity_instance:
        if isinstance(self.geometry, bpy.types.Mesh) and len(self.geometry.vertices) == 1:
            return self.file.createIfcTopologyRepresentation(
                self.settings["context"],
                self.settings["context"].ContextIdentifier,
                "Vertex",
                [self.create_vertex_point(self.geometry.vertices[0].co)],
            )
        return self.file.createIfcTopologyRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Edge",
            [self.create_edge()],
        )

    def create_vertex_point(self, point: Vector) -> ifcopenshell.entity_instance:
        return self.file.createIfcVertexPoint(self.create_cartesian_point(point.x, point.y, point.z))

    def get_spline_points(
        self, spline: bpy.types.Spline
    ) -> list[Union[bpy.types.SplinePoint, bpy.types.BezierSplinePoint]]:
        points = spline.bezier_points[:] + spline.points[:]
        if spline.use_cyclic_u:
            points.append(points[0])
        return points

    def create_edge(self) -> Union[ifcopenshell.entity_instance, None]:
        geometry = self.geometry
        if isinstance(geometry, bpy.types.Curve):
            points = self.get_spline_points(geometry.splines[0])
        elif isinstance(geometry, bpy.types.Mesh):
            points = geometry.vertices
        else:
            assert False, type(geometry)
        if not points:
            return
        return self.file.createIfcEdge(self.create_vertex_point(points[0].co), self.create_vertex_point(points[1].co))
