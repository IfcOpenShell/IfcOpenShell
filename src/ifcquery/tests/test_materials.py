import ifcopenshell.api.material
import ifcopenshell.api.project

from ifcquery.materials import materials


class TestMaterials:
    def test_empty_model(self, model):
        result = materials(model)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_single_material(self, model):
        ifcopenshell.api.material.add_material(model, name="Concrete", category="concrete")
        result = materials(model)
        assert len(result) == 1
        m = result[0]
        assert m["type"] == "IfcMaterial"
        assert m["name"] == "Concrete"
        assert m["category"] == "concrete"
        assert isinstance(m["id"], int)

    def test_material_layer_set(self, model):
        mat = ifcopenshell.api.material.add_material(model, name="Brick")
        layer_set = ifcopenshell.api.material.add_material_set(model, name="BrickSet", set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.add_layer(model, layer_set=layer_set, material=mat)
        result = materials(model)
        layer_sets = [e for e in result if e["type"] == "IfcMaterialLayerSet"]
        assert len(layer_sets) == 1
        ls = layer_sets[0]
        assert ls["name"] == "BrickSet"
        assert isinstance(ls["layers"], list)
        assert len(ls["layers"]) == 1
        layer = ls["layers"][0]
        assert layer["material"] == "Brick"

    def test_material_constituent_set(self, model):
        mat = ifcopenshell.api.material.add_material(model, name="Steel")
        cs = ifcopenshell.api.material.add_material_set(model, name="CompSet", set_type="IfcMaterialConstituentSet")
        ifcopenshell.api.material.add_constituent(model, constituent_set=cs, material=mat)
        result = materials(model)
        constituent_sets = [e for e in result if e["type"] == "IfcMaterialConstituentSet"]
        assert len(constituent_sets) == 1
        entry = constituent_sets[0]
        assert entry["name"] == "CompSet"
        assert isinstance(entry["constituents"], list)

    def test_ids_are_integers(self, model):
        ifcopenshell.api.material.add_material(model, name="Wood")
        result = materials(model)
        for entry in result:
            assert isinstance(entry["id"], int)
