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

import os
import pytest
import xmlschema
import ifcopenshell
from ifctester import ids


class TestIds:
    def test_failing_on_opening_invalid_ids_data(self):
        with pytest.raises(xmlschema.validators.exceptions.XMLSchemaValidationError):
            ids.open("""<?xml version="1.0" encoding="UTF-8"?><clearly_not_an_ids/>""")

    def test_create_an_ids_with_minimal_information(self):
        specs = ids.Ids()
        assert specs.asdict() == {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_05.xsd",
            "info": {"title": "Untitled"},
            "specifications": {"specification": []},
        }

    def test_create_an_ids_with_all_possible_information(self):
        specs = ids.Ids(
            title="title",
            copyright="copyright",
            version="version",
            description="description",
            author="author@test.com",
            date="2020-01-01",
            purpose="purpose",
            milestone="milestone",
        )
        assert specs.asdict() == {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_05.xsd",
            "info": {
                "title": "title",
                "copyright": "copyright",
                "version": "version",
                "description": "description",
                "author": "author@test.com",
                "date": "2020-01-01",
                "purpose": "purpose",
                "milestone": "milestone",
            },
            "specifications": {"specification": []},
        }

    def test_check_invalid_ids_information(self):
        specs = ids.Ids(title=None, author="author", date="9999-99-99")
        assert specs.asdict() == {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_05.xsd",
            "info": {"title": "Untitled"},
            "specifications": {"specification": []},
        }

    def test_authoring_an_ids_with_no_specifications_is_invalid(self):
        specs = ids.Ids()
        with pytest.raises(xmlschema.validators.exceptions.XMLSchemaChildrenValidationError):
            specs.to_string()

    def test_saving_to_xml(self):
        specs = ids.Ids(title="Title")
        spec = ids.Specification(name="Name")
        spec.applicability.append(ids.Entity(name="IFCWALL"))
        spec.requirements.append(ids.Attribute(name="Name", value="Waldo"))
        specs.specifications.append(spec)
        fn = "tmp.xml"
        result = specs.to_xml(fn)
        os.remove(fn)

    def test_creating_a_minimal_ids_and_validating(self):
        specs = ids.Ids(title="Title")
        spec = ids.Specification(name="Name")
        spec.applicability.append(ids.Entity(name="IFCWALL"))
        spec.requirements.append(ids.Attribute(name="Name", value="Waldo"))
        specs.specifications.append(spec)
        assert "http://standards.buildingsmart.org/IDS" in specs.to_string()
        assert spec.status == None

        model = ifcopenshell.file()
        wall = model.createIfcWall()
        waldo = model.createIfcWall(Name="Waldo")
        specs.validate(model)

        assert spec.status == False
        assert set(spec.applicable_entities) == {wall, waldo}
        assert spec.requirements[0].failed_entities == [wall]

    def test_creating_multiple_specifications(self):
        specs = ids.Ids(title="Title")
        spec = ids.Specification(name="Name")
        spec.applicability.append(ids.Entity(name="IFCWALL"))
        spec.requirements.append(ids.Attribute(name="Name", value="Waldo"))
        specs.specifications.append(spec)

        spec2 = ids.Specification(name="Name")
        spec2.applicability.append(ids.Entity(name="IFCWALL"))
        spec2.requirements.append(ids.Attribute(name="Name", value="Waldo"))
        specs.specifications.append(spec2)

        model = ifcopenshell.file()
        wall = model.createIfcWall()
        waldo = model.createIfcWall(Name="Waldo")
        specs.validate(model)

        assert spec.status == False
        assert set(spec.applicable_entities) == {wall, waldo}
        assert spec.requirements[0].failed_entities == [wall]
        assert spec2.requirements[0].failed_entities == [wall]


class TestSpecification:
    def test_create_specification_with_minimal_information(self):
        spec = ids.Specification()
        assert spec.asdict() == {
            "@name": "Unnamed",
            "@ifcVersion": ["IFC2X3", "IFC4"],
            "applicability": {},
            "requirements": {},
        }

    def test_create_specification_with_all_possible_information(self):
        spec = ids.Specification(
            name="name",
            minOccurs="0",
            maxOccurs="unbounded",
            ifcVersion="IFC4",
            identifier="identifier",
            description="description",
            instructions="instructions",
        )
        assert spec.asdict() == {
            "@name": "name",
            "@minOccurs": "0",
            "@maxOccurs": "unbounded",
            "@ifcVersion": "IFC4",
            "@identifier": "identifier",
            "@description": "description",
            "@instructions": "instructions",
            "applicability": {},
            "requirements": {},
        }
