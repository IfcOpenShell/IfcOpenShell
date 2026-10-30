# This file was generated with the assistance of an AI coding tool.

import numpy as np

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import test.bootstrap


class TestRegenerateWallRepresentation(test.bootstrap.IFC4):
    def add_wall(self, priorities, x, y, angle, length):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        layer_set = ifcopenshell.api.material.add_material_set(self.file, name="LS", set_type="IfcMaterialLayerSet")
        for priority in priorities:
            material = ifcopenshell.api.material.add_material(self.file, name="M")
            layer = ifcopenshell.api.material.add_layer(self.file, layer_set=layer_set, material=material)
            layer.LayerThickness = 0.1
            layer.Priority = priority
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialLayerSetUsage", material=layer_set
        )
        matrix = np.eye(4)
        matrix[:2, :2] = [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
        matrix[0, 3], matrix[1, 3] = x, y
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix, is_si=True)
        representation = ifcopenshell.api.geometry.regenerate_wall_representation(
            self.file, wall, length=length, height=3.0
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=representation)
        return wall

    def test_stitching_multiple_path_cuts_in_order_along_the_edge(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        wall = self.add_wall((5, 0), 0.0, 0.0, 0.0, 10.0)
        near = self.add_wall((3, 3), 3.0, 0.0, np.pi / 2, 3.0)
        far = self.add_wall((3, 3), 6.0, 0.0, np.pi / 2, 3.0)
        for other in (far, near):
            ifcopenshell.api.geometry.connect_path(
                self.file,
                relating_element=wall,
                related_element=other,
                relating_connection="ATPATH",
                related_connection="ATSTART",
            )
        representation = ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall, length=10.0)
        profile = representation.Items[0].SweptArea
        points = [tuple(round(c, 3) for c in p) for p in profile.OuterCurve.Points.CoordList]
        assert points == [
            (0.0, 0.0),
            (0.0, 0.2),
            (2.8, 0.2),
            (2.8, 0.1),
            (3.0, 0.1),
            (3.0, 0.2),
            (5.8, 0.2),
            (5.8, 0.1),
            (6.0, 0.1),
            (6.0, 0.2),
            (10.0, 0.2),
            (10.0, 0.0),
        ]
