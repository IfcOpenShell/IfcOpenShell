import warnings

class GeometryIO:
    def __init__(self):
        self.vertices = {}

    def build_vertices(self, IFC_model, coords, scale=None):
        for coord in coords:
            if scale:
                IFC_vertex = tuple([float(xyz) * coord_scale
                                    for xyz, coord_scale
                                    in zip(coord, scale)])
            else:
                IFC_vertex = [float(xyz) for xyz in coord]

            IFC_cartesian_point = IFC_model.create_entity("IfcCartesianPoint", IFC_vertex)
            self.vertices[tuple(coord)] = IFC_cartesian_point

    def create_IFC_geometry(self, IFC_model, geometry):
        if geometry.type == "Solid":
            return self.create_IFC_closed_shell(IFC_model, geometry)
        elif geometry.type in ["CompositeSolid", "MultiSolid"]:
            return self.create_IFC_composite_closed_shell(IFC_model, geometry)
        elif geometry.type in ["CompositeSurface", "MultiSurface"]:
            return self.create_IFC_surface(IFC_model, geometry)
        else:
            warnings.warn("Types other than solids are not yet supported")
            return

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
        faces = None
        if surface_id is not None:
            face_ids = geometry.surfaces[surface_id]["surface_idx"]
            faces = list(map(lambda face_id: geometry.boundaries[face_id[0]][face_id[1]], face_ids))
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
            vertices.append(self.vertices[tuple(vertex)])
        polyloop = IFC_model.create_entity("IfcPolyLoop", vertices)
        outerbound = IFC_model.create_entity("IfcFaceOuterBound", polyloop, True)

        # return if only exterior face
        if len(face) == 1:
            return IFC_model.create_entity("IfcFace", [outerbound])

        # interior face
        innerbounds = []
        for interior_face in face[1:]:
            for vertex in interior_face:
                vertices.append(self.vertices[tuple(vertex)])
            polyloop = IFC_model.create_entity("IfcPolyLoop", vertices)
            innerbounds.append(IFC_model.create_entity("IfcFaceBound", polyloop, True))
        return IFC_model.create_entity("IfcFace", [outerbound] + innerbounds)

