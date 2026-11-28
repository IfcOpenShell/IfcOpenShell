# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.material
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.model.opening import FilledOpeningGenerator
from bonsai.bim.module.model.wall import DumbWallPlaner
from test.bim.bootstrap import NewFile


class TestRegenerateFromLayerSet(NewFile):
    def test_hosted_opening_follows_the_new_wall_thickness(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        wall_type = ifcopenshell.api.root.create_entity(ifc, "IfcWallType")
        layer_set = ifcopenshell.api.material.add_material_set(ifc, name="Layers", set_type="IfcMaterialLayerSet")
        material = ifcopenshell.api.material.add_material(ifc, name="Concrete")
        layer = ifcopenshell.api.material.add_layer(ifc, layer_set=layer_set, material=material)
        ifcopenshell.api.material.edit_layer(ifc, layer=layer, attributes={"LayerThickness": 0.5})
        ifcopenshell.api.material.assign_material(ifc, products=[wall_type], material=layer_set)
        props = tool.Model.get_model_props()
        props.ifc_class = "IfcWallType"
        props.relating_type_id = str(wall_type.id())
        bpy.ops.bim.add_occurrence()
        wall_obj = tool.Ifc.get_object(ifc.by_type("IfcWall")[0])
        bpy.ops.mesh.add_door()
        door = ifc.by_type("IfcDoor")[0]
        assert FilledOpeningGenerator().generate(tool.Ifc.get_object(door), wall_obj) is None
        opening = door.FillsVoids[0].RelatingOpeningElement

        def opening_depth():
            body = tool.Geometry.resolve_mapped_representation(tool.Geometry.get_body_representation(opening))
            return body.Items[0].Depth

        assert opening_depth() < 1.5
        ifcopenshell.api.material.edit_layer(ifc, layer=layer, attributes={"LayerThickness": 1.5})
        DumbWallPlaner().regenerate_from_layer_set(layer_set)
        assert opening_depth() >= 1.5
