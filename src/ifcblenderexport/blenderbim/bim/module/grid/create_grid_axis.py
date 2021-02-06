import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.placement
from mathutils import Matrix  # For now, we depend on Blender
from blenderbim.bim.module.owner.api import create_owner_history


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {
            "AxisTag": "A",
            "AxisCurve": None,  # A Blender object
            "SameSense": True,
            "UVWAxes": "UAxes",  # Choose which axes
            "Grid": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        points = [
            Matrix(ifcopenshell.util.placement.get_local_placement(self.settings["Grid"].ObjectPlacement)).inverted()
            @ (self.settings["AxisCurve"].matrix_world @ v.co)
            for v in self.settings["AxisCurve"].data.vertices[0:2]
        ]
        self.settings["AxisCurve"] = self.file.createIfcPolyline(
            [
                self.create_cartesian_point(points[0][0], points[0][1], points[0][2]),
                self.create_cartesian_point(points[1][0], points[1][1], points[1][2]),
            ]
        )
        element = self.file.create_entity("IfcGridAxis", **{
            "AxisTag": self.settings["AxisTag"],
            "AxisCurve": self.settings["AxisCurve"],
            "SameSense": self.settings["SameSense"]
        })
        axes = list(getattr(self.settings["Grid"], self.settings["UVWAxes"]) or [])
        axes.append(element)
        setattr(self.settings["Grid"], self.settings["UVWAxes"], axes)
        return element

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
