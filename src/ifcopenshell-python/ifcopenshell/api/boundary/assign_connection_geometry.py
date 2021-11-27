import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, **settings):
        """location, axis and ref_direction defines the plane"""
        self.file = file
        self.settings = {
            "rel_space_boundary": None,
            "outer_boundary": None,
            "inner_boundaries": (),
            "location": None,
            "axis": None,
            "ref_direction": None,
            "unit_scale": None,
        }
        self.ifc_vertices = []
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["unit_scale"] is None:
            self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        outer_boundary = self.create_polyline(self.settings["outer_boundary"])
        inner_boundaries = tuple(self.create_polyline(boundary) for boundary in self.settings["inner_boundaries"])
        plane = self.create_plane(self.settings["location"], self.settings["axis"], self.settings["ref_direction"])
        curve_bounded_plane = self.file.createIfcCurveBoundedPlane(plane, outer_boundary, inner_boundaries)
        connection_geometry = self.file.createIfcConnectionSurfaceGeometry(curve_bounded_plane)
        self.settings["rel_space_boundary"].ConnectionGeometry = connection_geometry

    def create_point(self, point):
        return self.file.createIfcCartesianPoint(point / self.settings["unit_scale"])

    def close_polyline(self, points):
        return points + (points[0],)

    def create_polyline(self, points):
        if points[0] == points[-1]:
            points = points[0 : len(points) - 1]
        return self.file.createIfcPolyline(self.close_polyline(tuple(self.create_point(point) for point in points)))

    def create_plane(self, location, axis, ref_direction):
        return self.file.createIfcPlane(
            self.file.createIfcAxis2Placement3D(
                self.create_point(location),
                self.file.createIfcDirection(axis),
                self.file.createIfcDirection(ref_direction),
            )
        )
