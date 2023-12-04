# ifccityjson - Python CityJSON to IFC converter
# Copyright (C) 2021 Laurens J.N. Oostwegel <l.oostwegel@gmail.com>
#
# This file is part of ifccityjson.
#
# ifccityjson is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ifccityjson is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ifccityjson.  If not, see <http://www.gnu.org/licenses/>.

import warnings


class GeometryIO:
    def __init__(self, scale=None):
        self.vertices = {}
        self.scale = scale

    def set_scale(self, scale):
        self.scale = scale

    def build_vertices(self, IFC_model, vertices):
        for vertex in vertices:
            self.build_vertex(IFC_model, vertex)

    def build_vertex(self, IFC_model, vertex):
        if self.scale:
            IFC_vertex = [float(xyz) * coord_scale for xyz, coord_scale in zip(vertex, self.scale)]
        else:
            IFC_vertex = [float(xyz) for xyz in vertex]

        IFC_cartesian_point = IFC_model.create_entity("IfcCartesianPoint", IFC_vertex)
        self.vertices[tuple(vertex)] = IFC_cartesian_point
        return IFC_cartesian_point

    def get_vertex(self, IFC_model, vertex):
        if tuple(vertex) in self.vertices:
            return self.vertices[tuple(vertex)]
        else:
            return self.build_vertex(IFC_model, vertex)

    # See for CityJSON geometries:
    # https://www.cityjson.org/dev/geom-arrays/
    # https://www.cityjson.org/specs/1.0.3/#geometry-objects
    def create_IFC_geometry(self, IFC_model, geometry):
        IFC_Geometry = None
        geometry_type = "brep"
        if geometry.type in ["MultiPoint"]:
            IFC_geometry = self.create_IFC_cartesian_point_list3D(IFC_model, geometry)
            geometry_type = "PointCloud"
        elif geometry.type in ["MultiLineString"]:
            IFC_geometry = self.create_IFC_composite_curve(IFC_model, geometry)
            geometry_type = "Curve3D"
        elif geometry.type in ["CompositeSurface", "MultiSurface"]:
            IFC_geometry = self.create_IFC_surface(IFC_model, geometry)
        elif geometry.type == "Solid":
            IFC_geometry = self.create_IFC_closed_shell(IFC_model, geometry)
        elif geometry.type in ["CompositeSolid", "MultiSolid"]:
            IFC_geometry = self.create_IFC_composite_closed_shell(IFC_model, geometry)
        elif geometry.type in ["GeometryInstance"]:
            warnings.warn("GeometryInstance is not supported.")
            return None, None
        else:
            warnings.warn("Custom CityJSON geometries are not supported.")
            return None, None
        return IFC_geometry, geometry_type

    def create_IFC_cartesian_point_list3D(self, IFC_model, geometry):
        # https://www.cityjson.org/dev/geom-arrays/
        # https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifcgeometricmodelresource/lexical/ifccartesianpointlist3d.htm
        IFC_geometry = IFC_model.create_entity("IfcCartesianPointList3D", geometry.boundaries)
        return IFC_geometry

    def create_IFC_composite_curve(self, IFC_model, geometry):
        # https://www.cityjson.org/dev/geom-arrays/
        # https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifcgeometryresource/lexical/ifccompositecurve.htm
        # https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifcgeometryresource/lexical/ifccompositecurvesegment.htm
        IFC_geometry = []
        for line in geometry.boundaries:
            vertices = []
            for vertex in line:
                vertices.append(self.get_vertex(IFC_model, vertex))
            polyline = IFC_model.create_entity("IfcPolyLine", vertices)
            IFC_geometry.append(polyline)
        return IFC_geometry

    def create_IFC_composite_closed_shell(self, IFC_model, geometry):
        shells = []
        for shell in geometry.boundaries:
            # exterior shell
            outershell = shell[0]
            faces = []
            for face in outershell:
                faces.append(self.create_IFC_face(IFC_model, face))

            shells.append(IFC_model.create_entity("IfcClosedShell", faces))
        IFC_geometry = IFC_model.create_entity("IfcShellBasedSurfaceModel", shells)
        return IFC_geometry

    def create_IFC_closed_shell(self, IFC_model, geometry):
        # exterior shell
        outershell = geometry.boundaries[0]
        faces = []
        for face in outershell:
            faces.append(self.create_IFC_face(IFC_model, face))

        if len(geometry.boundaries) == 1:
            shell = IFC_model.create_entity("IfcClosedShell", faces)
            IFC_geometry = IFC_model.create_entity("IfcShellBasedSurfaceModel", [shell])
            return IFC_geometry

        # TODO: INTERIOR SHELL
        warnings.warn("Solid interior shell not yet supported")
        return
        # for boundary in geometry.boundaries[1:]:  # interior shells
        #     for face in boundary:
        #         for triangle in face:
        #             print(triangle)

    def create_IFC_surface(self, IFC_model, geometry, surface_id=None):
        faces = []

        if surface_id is not None:
            face_ids = geometry.surfaces[surface_id]["surface_idx"]
            if face_ids is None:
                return  # there is no geometry
            faces = [geometry.boundaries[fid[0]] for fid in face_ids]
        else:
            faces = geometry.boundaries

        IFC_faces = []
        for face in faces:
            IFC_faces.append(self.create_IFC_face(IFC_model, face))

        shell = IFC_model.create_entity("IfcOpenShell", IFC_faces)
        IFC_geometry = IFC_model.create_entity("IfcShellBasedSurfaceModel", [shell])
        return IFC_geometry

    def create_IFC_face(self, IFC_model, face):
        # exterior face
        vertices = []
        for vertex in face[0]:
            vertices.append(self.get_vertex(IFC_model, vertex))
        polyloop = IFC_model.create_entity("IfcPolyLoop", Polygon=vertices)
        outerbound = IFC_model.create_entity("IfcFaceOuterBound", Bound=polyloop, Orientation=True)

        # return if only exterior face
        if len(face) == 1:
            return IFC_model.create_entity("IfcFace", Bounds=[outerbound])

        innerbounds = []
        for interior_face in face[1:]:
            vertices = []
            for vertex in interior_face:
                vertices.append(self.get_vertex(IFC_model, vertex))
            polyloop = IFC_model.create_entity("IfcPolyLoop", Polygon=vertices)
            innerbounds.append(IFC_model.create_entity("IfcFaceBound", Bound=polyloop, Orientation=False))
        return IFC_model.create_entity("IfcFace", Bounds=[outerbound] + innerbounds)
