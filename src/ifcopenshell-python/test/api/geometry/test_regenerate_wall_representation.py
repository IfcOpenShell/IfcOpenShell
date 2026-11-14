# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
from ifcopenshell.api.geometry.regenerate_wall_representation import (
    PrioritisedLayer,
    Regenerator,
)
import test.bootstrap


class TestRegenerateWallRepresentation(test.bootstrap.IFC4):
    def test_combine_layers_with_override_priorities(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        regenerator = Regenerator(self.file)
        layers = [PrioritisedLayer(50, 0.25), PrioritisedLayer(20, 0.25)]
        combined = regenerator.combine_layers(layers, [60, 60])
        assert combined == [PrioritisedLayer(60, 0.5)]

    def test_regenerate_with_per_connection_priorities(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file, length={"is_metric": True, "raw": "METERS"})
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )
        plan = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        axis = ifcopenshell.api.context.add_context(
            self.file,
            context_type="Plan",
            context_identifier="Axis",
            target_view="GRAPH_VIEW",
            parent=plan,
        )

        layer_set = ifcopenshell.api.material.add_material_set(
            self.file, name="LS", set_type="IfcMaterialLayerSet"
        )
        mat = ifcopenshell.api.material.add_material(self.file, name="Brick")
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=layer_set, material=mat)
        layer.LayerThickness = 0.23
        layer.Priority = 50

        wall1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="W1")
        wall2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="W2")
        for wall in (wall1, wall2):
            ifcopenshell.api.material.assign_material(
                self.file,
                products=[wall],
                type="IfcMaterialLayerSetUsage",
                material=layer_set,
            )

        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall1)
        rep1 = ifcopenshell.api.geometry.add_axis_representation(
            self.file, context=axis, axis=[(0.0, 0.0), (1.0, 0.0)]
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall1, representation=rep1)

        m2 = np.array(
            [
                [0.0, -1.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall2, matrix=m2)
        rep2 = ifcopenshell.api.geometry.add_axis_representation(
            self.file, context=axis, axis=[(0.0, 0.0), (1.0, 0.0)]
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall2, representation=rep2)

        rel = ifcopenshell.api.geometry.connect_path(
            self.file,
            relating_element=wall1,
            related_element=wall2,
            relating_connection="ATEND",
            related_connection="ATSTART",
        )
        rel.RelatingPriorities = [51]
        rel.RelatedPriorities = [50]

        body1 = ifcopenshell.api.geometry.regenerate_wall_representation(
            self.file, wall1, length=1.0, height=3.0
        )
        body2 = ifcopenshell.api.geometry.regenerate_wall_representation(
            self.file, wall2, length=1.0, height=3.0
        )
        assert body1.is_a("IfcShapeRepresentation")
        assert body2.is_a("IfcShapeRepresentation")
