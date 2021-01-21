import numpy as np
import ifcopenshell.util.element
import ifcopenshell.util.placement


class Usecase:
    def __init__(self, file, settings=None):
        self.file = file
        self.settings = {"product": None, "matrix": np.eye(4)}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not hasattr(self.settings["product"], "ObjectPlacement"):
            return
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        dependent_objects = []
        if self.settings["product"].ObjectPlacement:
            for referenced_placement in self.settings["product"].ObjectPlacement.ReferencedByPlacements:
                for placed_obj in referenced_placement.PlacesObject:
                    dependent_objects.append(
                        {
                            "product": placed_obj,
                            "matrix": ifcopenshell.util.placement.get_local_placement(referenced_placement),
                        }
                    )

        placement_rel_to = None
        if hasattr(self.settings["product"], "ContainedInStructure") and self.settings["product"].ContainedInStructure:
            placement_rel_to = self.settings["product"].ContainedInStructure[0].RelatingStructure.ObjectPlacement
        elif hasattr(self.settings["product"], "Decomposes") and self.settings["product"].Decomposes:
            relating_object = self.settings["product"].Decomposes[0].RelatingObject
            placement_rel_to = relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None

        placement = self.file.createIfcLocalPlacement(placement_rel_to, self.get_relative_placement(placement_rel_to))
        if self.settings["product"].ObjectPlacement:
            for inverse in self.file.get_inverse(self.settings["product"]):
                ifcopenshell.util.element.replace_attribute(
                    inverse, self.settings["product"].ObjectPlacement, placement
                )
            self.file.remove(self.settings["product"].ObjectPlacement)
        self.settings["product"].ObjectPlacement = placement

        for settings in dependent_objects:
            self.settings = settings
            self.execute()

        return placement

    def get_relative_placement(self, placement_rel_to):
        if placement_rel_to:
            relating_object_matrix = ifcopenshell.util.placement.get_local_placement(placement_rel_to)
            relating_object_matrix[0][3] = self.convert_unit_to_si(relating_object_matrix[0][3])
            relating_object_matrix[1][3] = self.convert_unit_to_si(relating_object_matrix[1][3])
            relating_object_matrix[2][3] = self.convert_unit_to_si(relating_object_matrix[2][3])
        else:
            relating_object_matrix = np.eye(4)
        m = self.settings["matrix"]
        x = np.array((m[0][0], m[1][0], m[2][0]))
        z = np.array((m[0][2], m[1][2], m[2][2]))
        o = np.array((m[0][3], m[1][3], m[2][3]))
        object_matrix = ifcopenshell.util.placement.a2p(o, z, x)
        relative_placement_matrix = np.linalg.inv(relating_object_matrix) @ object_matrix
        return self.create_ifc_axis_2_placement_3d(
            relative_placement_matrix[:, 3][0:3],
            relative_placement_matrix[:, 2][0:3],
            relative_placement_matrix[:, 0][0:3],
        )

    def create_ifc_axis_2_placement_3d(self, point, up, forward):
        return self.file.createIfcAxis2Placement3D(
            self.create_cartesian_point(point),
            self.file.createIfcDirection(up.tolist()),
            self.file.createIfcDirection(forward.tolist()),
        )

    def create_cartesian_point(self, co):
        co = self.convert_si_to_unit(co)
        return self.file.createIfcCartesianPoint(co.tolist())

    def convert_si_to_unit(self, co):
        return co / self.unit_scale

    def convert_unit_to_si(self, co):
        return co * self.unit_scale
