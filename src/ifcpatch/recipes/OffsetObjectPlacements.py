import math


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        absolute_placements = []

        for product in self.file.by_type("IfcProduct"):
            if not product.ObjectPlacement:
                continue
            absolute_placement = self.get_absolute_placement(product.ObjectPlacement)
            if absolute_placement.is_a("IfcLocalPlacement"):
                absolute_placements.append(absolute_placement)
        absolute_placements = set(absolute_placements)

        for placement in absolute_placements:
            offset_location = (
                placement.RelativePlacement.Location.Coordinates[0] + float(self.args[0]),
                placement.RelativePlacement.Location.Coordinates[1] + float(self.args[1]),
                placement.RelativePlacement.Location.Coordinates[2] + float(self.args[2]),
            )

            relative_placement = self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint(offset_location))

            if placement.RelativePlacement.Axis:
                relative_placement.Axis = placement.RelativePlacement.Axis
            if placement.RelativePlacement.RefDirection:
                relative_placement.RefDirection = placement.RelativePlacement.RefDirection

            angle = float(self.args[3])
            if not angle:
                placement.RelativePlacement = relative_placement
                continue

            rotation_matrix = self.z_rotation_matrix(math.radians(angle))
            relative_placement.Location.Coordinates = self.multiply_by_matrix(offset_location, rotation_matrix)

            if placement.RelativePlacement.Axis:
                z_axis = placement.RelativePlacement.Axis.DirectionRatios
                relative_placement.Axis = self.file.createIfcDirection(self.multiply_by_matrix(z_axis, rotation_matrix))

            if placement.RelativePlacement.RefDirection:
                x_axis = placement.RelativePlacement.RefDirection.DirectionRatios
            else:
                x_axis = (1.0, 0.0, 0.0)
            relative_placement.RefDirection = self.file.createIfcDirection(
                self.multiply_by_matrix(x_axis, rotation_matrix)
            )

            placement.RelativePlacement = relative_placement

    def get_absolute_placement(self, object_placement):
        if object_placement.PlacementRelTo:
            return self.get_absolute_placement(object_placement.PlacementRelTo)
        return object_placement

    def z_rotation_matrix(self, angle):
        return [[math.cos(angle), -math.sin(angle), 0.0], [math.sin(angle), math.cos(angle), 0.0], [0.0, 0.0, 1.0]]

    def multiply_by_matrix(self, v, m):
        return [
            v[0] * m[0][0] + v[1] * m[0][1] + v[2] * m[0][2],
            v[0] * m[1][0] + v[1] * m[1][1] + v[2] * m[1][2],
            v[0] * m[2][0] + v[1] * m[2][1] + v[2] * m[2][2],
        ]
