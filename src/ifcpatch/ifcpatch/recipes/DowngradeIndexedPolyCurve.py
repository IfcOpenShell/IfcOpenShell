import ifcopenshell
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        curve_map = {}

        for curve in self.file.by_type("IfcIndexedPolyCurve"):
            if "IfcArcIndex" in [s.is_a() for s in curve.Segments]:
                print("Could not convert curve due to arcs", curve)
                continue
            coordinates = curve.Points.CoordList
            points = []
            for i, segment in enumerate(curve.Segments):
                segment = segment.wrappedValue
                if i == 0:
                    points.append(self.file.createIfcCartesianPoint(coordinates[segment[0] - 1]))
                points.append(self.file.createIfcCartesianPoint(coordinates[segment[1] - 1]))
            polyline = self.file.create_entity("IfcPolyline", points)
            curve_map[curve] = polyline

        for curve, polyline in curve_map.items():
            for inverse in self.file.get_inverse(curve):
                ifcopenshell.util.element.replace_attribute(inverse, curve, polyline)
