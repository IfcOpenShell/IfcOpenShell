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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.layer
import ifcopenshell.api.root
import ifcopenshell.validate
from ifcopenshell.util.shape_builder import ShapeBuilder

import ifcpatch
import test.bootstrap


class TestExtractElementsPresentationLayers(test.bootstrap.IFC4):
    def test_keep_presentation_layer_items_of_extracted_elements(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        builder = ShapeBuilder(self.file)
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        layer = ifcopenshell.api.layer.add_layer(self.file, name="TestLayer")
        for _ in range(2):
            wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
            item = builder.extrude(builder.profile(builder.rectangle((1, 1))))
            representation = builder.get_representation(model, item)
            ifcopenshell.api.geometry.assign_representation(self.file, wall, representation)
            ifcopenshell.api.layer.assign_layer(self.file, items=[representation], layer=layer)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        layers = output.by_type("IfcPresentationLayerAssignment")
        assert len(layers) == 1
        representations = output.by_type("IfcShapeRepresentation")
        assert len(representations) == 2
        assert set(layers[0].AssignedItems) == set(representations)
        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output, logger)
        assert not [s for s in logger.statements if "AssignedItems" in str(s)]

    def test_keep_presentation_layer_items_extracting_a_single_element(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        builder = ShapeBuilder(self.file)
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        layer = ifcopenshell.api.layer.add_layer(self.file, name="TestLayer")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        item = builder.extrude(builder.profile(builder.rectangle((1, 1))))
        representation = builder.get_representation(model, item)
        ifcopenshell.api.geometry.assign_representation(self.file, wall, representation)
        ifcopenshell.api.layer.assign_layer(self.file, items=[representation], layer=layer)

        output = ifcpatch.execute({"file": self.file, "recipe": "ExtractElements", "arguments": ["IfcWall"]})

        layer_new = output.by_type("IfcPresentationLayerAssignment")[0]
        assert len(layer_new.AssignedItems) == 1
        assert layer_new.AssignedItems[0] == output.by_type("IfcShapeRepresentation")[0]
