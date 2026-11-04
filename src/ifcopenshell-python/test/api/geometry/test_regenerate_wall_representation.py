# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.representation
import test.bootstrap


class TestRegenerateWallRepresentation(test.bootstrap.IFC4):
    def test_creating_the_body_context_when_missing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        layer_set = ifcopenshell.api.material.add_material_set(self.file, name="L", set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(self.file, name="M")
        ifcopenshell.api.material.add_layer(self.file, layer_set=layer_set, material=material)
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialLayerSetUsage", material=layer_set
        )
        assert not ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        representation = ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall=wall)
        body = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        assert body
        assert representation.ContextOfItems == body
