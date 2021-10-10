import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.element


class TestUnassignObject(test.bootstrap.IFC4):
    def test_unassigning_an_object(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        ifcopenshell.api.run("aggregate.unassign_object", self.file, product=subelement)
        assert ifcopenshell.util.element.get_aggregate(subelement) is None

    def test_the_rel_is_kept_if_there_are_more_decomposed_elements(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite")
        subelement2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement1, relating_object=element)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement2, relating_object=element)
        ifcopenshell.api.run("aggregate.unassign_object", self.file, product=subelement1)
        assert len(self.file.by_type("IfcRelAggregates")) == 1

    def test_the_rel_is_purged_if_there_are_no_more_decomposed_elements(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSite")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        ifcopenshell.api.run("aggregate.unassign_object", self.file, product=subelement)
        assert len(self.file.by_type("IfcRelAggregates")) == 0
