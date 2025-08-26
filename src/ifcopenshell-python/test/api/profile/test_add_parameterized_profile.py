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

import test.bootstrap
import ifcopenshell.api.profile
import ifcopenshell.util.schema


class TestAddParametrizedProfileIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        schema = ifcopenshell.schema_by_name(self.file.schema)
        entity = schema.declaration_by_name("IfcParameterizedProfileDef").as_entity()
        assert entity
        for s in ifcopenshell.util.schema.get_subtypes(entity):
            profile = ifcopenshell.api.profile.add_parameterized_profile(self.file, ifc_class=s.name())
            assert profile.is_a() == s.name()
            assert profile.ProfileType == "AREA"


class TestAddParametrizedProfileIFC4(test.bootstrap.IFC4, TestAddParametrizedProfileIFC2X3):
    pass


class TestAddParametrizedProfileIFC4X3(test.bootstrap.IFC4, TestAddParametrizedProfileIFC2X3):
    pass
