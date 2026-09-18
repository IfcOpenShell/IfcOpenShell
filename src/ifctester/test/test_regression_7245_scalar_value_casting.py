# IfcTester - IDS based model auditing
# Copyright (C) 2021-2022 Thomas Krijnen <thomas@aecgeeks.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

"""Regression test for #7245.

An IDS value built through the Python API with a raw int or float used to be
compared directly against the model value, so ``ids.Property(value=1)``
never matched a model IfcLabel of ``"1"``.

Unlike the other ifctester regression fixes, this defect cannot be
demonstrated with a minimal .ids/.ifc pair: the IDS schema types
``simpleValue`` as ``xs:string`` (see ids.xsd), so a value parsed out of an
.ids file is always already a string. The bug only exists on the Python
construction path (``Facet.__init__``), which XML-loaded specifications
never go through (they are built empty and populated via ``Facet.parse``).
So this test drives the defect through the same Python API the original
bug report (#7245) used.
"""

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.guid

from ifctester import ids


class TestScalarValueCastingRegression:
    def test_int_value_matches_model_string_property(self):
        f = ifcopenshell.file()
        f.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        wall = f.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="Wall1")
        pset = ifcopenshell.api.pset.add_pset(f, product=wall, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(f, pset=pset, properties={"Foo": "1"})

        spec = ids.Specification(name="numeric value via API")
        spec.applicability.append(ids.Entity(name="IFCWALL"))
        spec.requirements.append(ids.Property(baseName="Foo", value=1, propertySet="Foo_Bar", dataType="IFCLABEL"))
        specs = ids.Ids(title="t")
        specs.specifications.append(spec)
        specs.validate(f)

        assert spec.status is True
