import bpy
import bmesh
import ifcopenshell.util.unit
from mathutils import Vector, Matrix
from blenderbim.bim.module.geometry.helper import Helper

Z_AXIS = Vector((0, 0, 1))
X_AXIS = Vector((1, 0, 0))
EPSILON = 1e-6


class Usecase:
    def __init__(self, file, **settings):
        # TODO: This usecase currently depends on Blender's data model
        self.file = file
        self.settings = {
            "context": None,  # IfcGeometricRepresentationContext
            "blender_object": None,  # This is (currently) a Blender object, hence this depends on Blender now
            "geometry": None,  # This is (currently) a Blender data object, hence this depends on Blender now
            "coordinate_offset": None,  # Optionally apply a vector offset to all coordinates
            "total_items": 1,  # How many representation items to create
            "unit_scale": None,  # A scale factor to apply for all vectors in case the unit is different
            "should_force_faceted_brep": False,  # If we should force faceted breps for meshes
            "should_force_triangulation": False,  # If we should force triangulation for meshes
            "is_point_cloud": False,  # If the geometry is a point cloud
            #  Possible IFC representation classes:
            #  IfcExtrudedAreaSolid/IfcRectangleProfileDef
            #  IfcExtrudedAreaSolid/IfcCircleProfileDef
            #  IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef
            #  IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids
            #  IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage
            "ifc_representation_class": None,  # Whether to cast a mesh into a particular class
            "profile_set_usage": None,  # The material profile set if the extrusion requires it
        }
        self.ifc_vertices = []
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
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
        if self.settings["context"].ContextIdentifier == "Annotation":
            return self.create_geometric_set_representation()
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
        if self.settings["context"].ContextIdentifier == "Annotation":
            if isinstance(self.settings["geometry"], bpy.types.TextCurve):
                return self.create_text_representation()
            shape_representation = self.create_geometric_curve_set_representation(is_2d=True)
            shape_representation.RepresentationType = "Annotation2D"
            return shape_representation
        elif self.settings["context"].ContextIdentifier == "Axis":
            return self.create_curve2d_representation()
        elif self.settings["context"].ContextIdentifier == "Body":
            pass
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

    def create_text_representation(self):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Annotation2D",
            [self.create_text()],
        )

    def create_text(self):
        text = self.settings["geometry"]
        if text.align_y in ["TOP_BASELINE", "BOTTOM_BASELINE", "BOTTOM"]:
            y = "bottom"
        elif text.align_y == "CENTER":
            y = "middle"
        elif text.align_y == "TOP":
            y = "top"

        if text.align_x == "LEFT":
            x = "left"
        elif text.align_x == "CENTER":
            x = "middle"
        elif text.align_x == "RIGHT":
            x = "right"

        origin = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.file.createIfcDirection((1.0, 0.0, 0.0)),
        )

        # TODO: Planar extent right now is wrong ...
        return self.file.createIfcTextLiteralWithExtent(
            text.body, origin, "RIGHT", self.file.createIfcPlanarExtent(1000, 1000), f"{y}-{x}"
        )

    def create_variable_representation(self):
        if isinstance(self.settings["geometry"], bpy.types.Curve):
            return self.create_curve3d_representation()
        elif isinstance(self.settings["geometry"], bpy.types.Camera):
            return self.create_camera_block_representation()
        elif not len(self.settings["geometry"].polygons):
            return self.create_curve3d_representation()
        elif self.settings["is_point_cloud"]:
            return self.create_point_cloud_representation()
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
            **{
                "Position": self.file.createIfcAxis2Placement3D(
                    self.create_cartesian_point(-width / 2, -height / 2, -self.settings["geometry"].clip_end)
                ),
                "XLength": self.convert_si_to_unit(width),
                "YLength": self.convert_si_to_unit(height),
                "ZLength": self.convert_si_to_unit(self.settings["geometry"].clip_end),
            },
        )

        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "CSG",
            [self.file.createIfcCsgSolid(block)],
        )

    def is_camera_landscape(self):
        return (
            self.settings["geometry"].BIMCameraProperties.raster_x
            > self.settings["geometry"].BIMCameraProperties.raster_y
        )

    def create_curve3d_representation(self):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Curve3D",
            self.create_curves(),
        )

    def create_curve2d_representation(self):
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Curve2D",
            self.create_curves(is_2d=True),
        )

    def create_curves(self, is_2d=False):
        if isinstance(self.settings["geometry"], bpy.types.Mesh):
            if self.file.schema == "IFC2X3":
                return self.create_curves_from_mesh_ifc2x3(is_2d=is_2d)
            else:
                return self.create_curves_from_mesh(is_2d=is_2d)
        elif isinstance(self.settings["geometry"], bpy.types.Curve):
            return self.create_curves_from_curve(is_2d=is_2d)

    def create_curves_from_mesh(self, is_2d=False):
        curves = []
        points = self.create_cartesian_point_list_from_vertices(self.settings["geometry"].vertices, is_2d=is_2d)
        edge_loops = []
        previous_edge = None
        edge_loop = []
        for edge in self.settings["geometry"].edges:
            if (Vector(points.CoordList[edge.vertices[0]]) - Vector(points.CoordList[edge.vertices[1]])).length < 0.001:
                # Maybe we should warn the user to weld vertices in this scenario?
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

    def create_curves_from_mesh_ifc2x3(self, is_2d=False):
        curves = []
        points = [
            self.create_cartesian_point(v.co.x, v.co.y, v.co.z if not is_2d else None)
            for v in self.settings["geometry"].vertices
        ]
        coord_list = [p.Coordinates for p in points]
        edge_loops = []
        previous_edge = None
        edge_loop = []
        for edge in self.settings["geometry"].edges:
            if (Vector(coord_list[edge.vertices[0]]) - Vector(coord_list[edge.vertices[1]])).length < 0.001:
                # Maybe we should warn the user to weld vertices in this scenario?
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

    def create_curves_from_curve(self, is_2d=False):
        results = []
        for spline in self.settings["geometry"].splines:
            # TODO: support interpolated curves, not just polylines
            points = []
            for point in spline.bezier_points:
                if is_2d:
                    points.append(self.create_cartesian_point(point.co.x, point.co.y))
                else:
                    points.append(self.create_cartesian_point(point.co.x, point.co.y, point.co.z))
            for point in spline.points:
                if is_2d:
                    points.append(self.create_cartesian_point(point.co.x, point.co.y))
                else:
                    points.append(self.create_cartesian_point(point.co.x, point.co.y, point.co.z))
            if spline.use_cyclic_u:
                points.append(points[0])
            results.append(self.file.createIfcPolyline(points))
        return results

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

    def create_polygonal_face_set(self):
        ifc_raw_items = [None] * self.settings["total_items"]
        for i, value in enumerate(ifc_raw_items):
            ifc_raw_items[i] = []
        for polygon in self.settings["geometry"].polygons:
            ifc_raw_items[polygon.material_index % self.settings["total_items"]].append(
                self.file.createIfcIndexedPolygonalFace([v + 1 for v in polygon.vertices])
            )
        coordinates = self.file.createIfcCartesianPointList3D(
            [self.convert_si_to_unit(v.co) for v in self.settings["geometry"].vertices]
        )
        items = [self.file.createIfcPolygonalFaceSet(coordinates, None, i) for i in ifc_raw_items if i]
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

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def create_cartesian_point_list_from_vertices(self, vertices, is_2d=False):
        if is_2d:
            return self.file.createIfcCartesianPointList2D([self.convert_si_to_unit(v.co.xy) for v in vertices])
        return self.file.createIfcCartesianPointList3D([self.convert_si_to_unit(v.co) for v in vertices])

    def convert_si_to_unit(self, co):
        if self.settings["coordinate_offset"]:
            return (co / self.settings["unit_scale"]) + self.settings["coordinate_offset"]
        return co / self.settings["unit_scale"]

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
