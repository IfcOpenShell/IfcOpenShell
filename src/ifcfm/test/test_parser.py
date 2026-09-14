# IfcFM - IFC for facility management
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcFM.
#
# IfcFM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcFM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcFM.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root
import pytest

import ifcfm


class TestParserDuplicateKeys:
    @staticmethod
    def setup_ifc_file() -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        return ifc_file

    def test_duplicate_key_warns_and_keeps_last_element(self) -> None:
        # Two systems sharing the same Name collide on the same category
        # key. The earlier one used to vanish from every exported format
        # with no warning. It must now be reported.
        ifc_file = self.setup_ifc_file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSystem", name="HVAC")
        second_system = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSystem", name="HVAC")

        parser = ifcfm.Parser(preset="basic")
        with pytest.warns(UserWarning, match="Duplicate key"):
            parser.parse(ifc_file)

        assert len(parser.duplicate_keys) == 1
        systems = parser.categories["Systems"]
        assert len(systems) == 1
        assert systems["HVAC"]["ModelID"] == second_system.GlobalId
