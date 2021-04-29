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
        else:
            warnings.warn("Types other than solids are not yet supported")
            return

    def create_IFC_composite_closed_shell(self, IFC_model, geometry):
        shells = []
        for shell in geometry.boundaries:
            outershell = shell[0]
            faces = []
            for face in outershell:  # exterior shell
                for triangle in face:
                    faces.append(self.create_IFC_face(IFC_model, triangle))

            shells.append(IFC_model.create_entity("IfcClosedShell", faces))
        IFC_geometry = IFC_model.create_entity("IfcShellBasedSurfaceModel", shells)
        return IFC_geometry

    def create_IFC_closed_shell(self, IFC_model, geometry):
        outershell = geometry.boundaries[0]
        # print(geometry.surfaces[0]['surface_idx'][0])
        faces = []
        for face in outershell:  # exterior shell
            for triangle in face:
                faces.append(self.create_IFC_face(IFC_model, triangle))

        if len(geometry.boundaries) == 1:
            shell = IFC_model.create_entity("IfcClosedShell", faces)
            IFC_geometry = IFC_model.create_entity("IfcShellBasedSurfaceModel", [shell])
            return IFC_geometry

        # TODO: INTERIOR SHELL
        warnings.warn("Solid interior shell not yet supported")
        return
        # for boundary in geometry.boundaries[1]:  # interior shell
        #     for face in boundary:
        #         for triangle in face:
        #             print(triangle)
        # print(geometry.boundaries)

    def create_IFC_surface(self, IFC_model, geometry, surface_id):
        face_ids = geometry.surfaces[surface_id]["surface_idx"]
        faces = []

        for shell, face_id in face_ids:
            for triangle in geometry.boundaries[shell][face_id]:
                faces.append(self.create_IFC_face(IFC_model, triangle))

        shell = IFC_model.create_entity("IfcOpenShell", faces)
        IFC_geometry = IFC_model.create_entity("IfcShellBasedSurfaceModel", [shell])
        return IFC_geometry

    def create_IFC_face(self, IFC_model, face):
        vertices = []
        for vertex in face:
            vertices.append(self.vertices[tuple(vertex)])
        polyloop = IFC_model.create_entity("IfcPolyLoop", vertices)
        outerbound = IFC_model.create_entity("IfcFaceOuterBound", polyloop, True)
        return IFC_model.create_entity("IfcFace", [outerbound])