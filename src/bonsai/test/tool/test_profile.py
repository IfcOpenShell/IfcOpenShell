# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import ifcopenshell.api.root

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestGetProfile(NewFile):
    def test_element_without_representation(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        beam = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        assert tool.Profile.get_profile(beam) is None
