import test.bootstrap
import ifcopenshell.api


class TestReassignClass(test.bootstrap.IFC4):
    def test_reassigning_a_simple_class(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run("root.reassign_class", self.file, product=element, ifc_class="IfcSlab")
        assert len([e for e in self.file]) == 1
        assert new.id() == 2
        assert new.is_a("IfcSlab")

    def test_reassigning_a_predefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run(
            "root.reassign_class", self.file, product=element, ifc_class="IfcSlab", predefined_type="FLOOR"
        )
        assert new.PredefinedType == "FLOOR"

    def test_falling_back_to_userdefined_if_the_predefined_type_cannot_be_reassigned(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run(
            "root.reassign_class", self.file, product=element, ifc_class="IfcSlab", predefined_type="FOO"
        )
        assert new.PredefinedType == "USERDEFINED"
        assert new.ObjectType == "FOO"
