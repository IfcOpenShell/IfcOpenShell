import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.placement
from mathutils import Matrix  # For now, we depend on Blender


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "AxisCurve": None,  # A Blender object
            "grid_axis": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["grid_axis"].AxisCurve:
            ifcopenshell.util.element.remove_deep(self.file, self.settings["grid_axis"].AxisCurve)

        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        grid = [i for i in self.file.get_inverse(self.settings["grid_axis"]) if i.is_a("IfcGrid")][0]
        points = [
            Matrix(ifcopenshell.util.placement.get_local_placement(grid.ObjectPlacement)).inverted()
            @ (self.settings["AxisCurve"].matrix_world @ v.co)
            for v in self.settings["AxisCurve"].data.vertices[0:2]
        ]
        self.settings["grid_axis"].AxisCurve = self.file.createIfcPolyline(
            [
                self.create_cartesian_point(points[0][0], points[0][1], points[0][2]),
                self.create_cartesian_point(points[1][0], points[1][1], points[1][2]),
            ]
        )

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
