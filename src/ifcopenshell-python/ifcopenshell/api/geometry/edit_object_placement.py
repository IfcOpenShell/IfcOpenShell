import numpy as np
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "matrix": np.eye(4), "is_si": True, "should_transform_children": False}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if not hasattr(self.settings["product"], "ObjectPlacement"):
            return
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        if not self.settings["is_si"]:
            self.settings["matrix"][0][3] *= self.unit_scale
            self.settings["matrix"][1][3] *= self.unit_scale
            self.settings["matrix"][2][3] *= self.unit_scale

        children_settings = []
        if not self.settings["should_transform_children"]:
            children_settings = self.get_children_settings(self.settings["product"].ObjectPlacement)

        placement_rel_to = self.get_placement_rel_to()
        placement = self.file.createIfcLocalPlacement(placement_rel_to, self.get_relative_placement(placement_rel_to))
        old_placement = self.settings["product"].ObjectPlacement
        if old_placement:
            self.settings["product"].ObjectPlacement = None
            inverses = self.file.get_inverse(old_placement)
            for inverse in inverses:
                ifcopenshell.util.element.replace_attribute(inverse, old_placement, placement)
            old_placement.PlacementRelTo = None
            ifcopenshell.util.element.remove_deep(self.file, old_placement)
        self.settings["product"].ObjectPlacement = placement

        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": self.settings["product"]})

        for settings in children_settings:
            self.settings = settings
            self.execute()

        return placement

    def get_placement_rel_to(self):
        if getattr(self.settings["product"], "ContainedInStructure", None):
            return self.settings["product"].ContainedInStructure[0].RelatingStructure.ObjectPlacement
        elif getattr(self.settings["product"], "Decomposes", None):
            relating_object = self.settings["product"].Decomposes[0].RelatingObject
            return relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None
        elif getattr(self.settings["product"], "VoidsElements", None):
            relating_object = self.settings["product"].VoidsElements[0].RelatingBuildingElement
            return relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None
        elif getattr(self.settings["product"], "FillsVoids", None):
            relating_object = self.settings["product"].FillsVoids[0].RelatingOpeningElement
            return relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None
        elif getattr(self.settings["product"], "ProjectsElements", None):
            relating_object = self.settings["product"].ProjectsElements[0].RelatingElement
            return relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None

    def get_children_settings(self, placement):
        if not placement:
            return []
        results = []
        for referenced_placement in placement.ReferencedByPlacements:
            matrix = ifcopenshell.util.placement.get_local_placement(referenced_placement)
            for obj in referenced_placement.PlacesObject:
                results.append({"product": obj, "matrix": matrix, "is_si": self.settings["is_si"], "should_transform_children": False})
            results.extend(self.get_children_settings(referenced_placement))
        return results

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
