# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestEditStructuralItemAxis(test.bootstrap.IFC4):
    def test_setting_an_axis_on_a_member_without_one(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        assert member.Axis is None
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=member, axis=(0.0, 1.0, 0.0))
        assert member.Axis.DirectionRatios == (0.0, 1.0, 0.0)

    def test_replacing_an_existing_axis_removes_the_old_direction(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=member, axis=(0.0, 1.0, 0.0))
        ifcopenshell.api.structural.edit_structural_item_axis(self.file, structural_item=member, axis=(1.0, 0.0, 0.0))
        assert member.Axis.DirectionRatios == (1.0, 0.0, 0.0)
        assert len(self.file.by_type("IfcDirection")) == 1
