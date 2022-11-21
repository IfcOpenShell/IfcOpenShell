# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

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
            self.convert_matrix_to_si(self.settings["matrix"])

        children_settings = []
        if not self.settings["should_transform_children"]:
            children_settings = self.get_children_settings(self.settings["product"].ObjectPlacement)

        placement_rel_to = self.get_placement_rel_to()
        relative_placement = self.get_relative_placement(placement_rel_to)
        new_placement = self.file.createIfcLocalPlacement(RelativePlacement=relative_placement)

        old_placement = self.settings["product"].ObjectPlacement

        if old_placement:
            inverses = self.file.get_inverse(old_placement)
            if len(inverses) == 1:
                self.settings["product"].ObjectPlacement = None
                old_placement.PlacementRelTo = None
                ifcopenshell.util.element.remove_deep2(self.file, old_placement)
            else:
                for inverse in inverses:
                    if inverse.is_a("IfcLocalPlacement"):
                        ifcopenshell.util.element.replace_attribute(inverse, old_placement, new_placement)

        new_placement.PlacementRelTo = placement_rel_to
        self.settings["product"].ObjectPlacement = new_placement

        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": self.settings["product"]})

        for settings in children_settings:
            self.settings = settings
            self.execute()

        return new_placement

    def convert_matrix_to_si(self, matrix):
        matrix[0][3] *= self.unit_scale
        matrix[1][3] *= self.unit_scale
        matrix[2][3] *= self.unit_scale

    def get_placement_rel_to(self):
        if getattr(self.settings["product"], "ContainedInStructure", None):
            return self.settings["product"].ContainedInStructure[0].RelatingStructure.ObjectPlacement
        elif getattr(self.settings["product"], "Decomposes", None):
            relating_object = self.settings["product"].Decomposes[0].RelatingObject
            return relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None
        elif getattr(self.settings["product"], "Nests", None):
            relating_object = self.settings["product"].Nests[0].RelatingObject
            return relating_object.ObjectPlacement if hasattr(relating_object, "ObjectPlacement") else None
        elif getattr(self.settings["product"], "ContainedIn", None):
            related_element = self.settings["product"].ContainedIn[0].RelatedElement
            return related_element.ObjectPlacement if hasattr(related_element, "ObjectPlacement") else None
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
                if obj.is_a("IfcDistributionPort"):
                    # Although a port is technically a nested child, it is generally
                    # more intuitive that the ports always move with the parent.
                    continue
                elif obj.is_a("IfcFeatureElement"):
                    # Feature elements affect the geometry of their parent, and
                    # so logically should always move with the parent.
                    continue
                results.append({"product": obj, "matrix": matrix, "is_si": False, "should_transform_children": False})
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
