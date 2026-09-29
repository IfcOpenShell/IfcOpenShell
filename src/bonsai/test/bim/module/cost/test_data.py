# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.resource
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.cost.data import CostItemQuantitiesData
from test.bim.bootstrap import NewFile


class TestResourceQuantityNames(NewFile):
    def test_names_are_collected_from_every_quantity_set(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(ifc, ifc_class="IfcCrewResource")
        for name, quantity in (("Qto_A", "Length"), ("Qto_B", "Area")):
            qto = ifcopenshell.api.pset.add_qto(ifc, product=resource, name=name)
            ifcopenshell.api.pset.edit_qto(ifc, qto=qto, properties={quantity: 1.0})
        props = tool.Resource.get_resource_props()
        props.tree.resources.add().ifc_definition_id = resource.id()
        props.active_resource_index = 0
        names = {name for name, _, _ in CostItemQuantitiesData.resource_quantity_names()}
        assert names == {"Length", "Area"}
