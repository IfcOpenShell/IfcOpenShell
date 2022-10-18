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


def run(name, ids, ifc, expected, applicable_entities=None, failed_entities=None):
    ids.validate(ifc)
    all_applicable = set()
    all_failures = set()
    if not applicable_entities:
        applicable_entities = []
    if not failed_entities:
        failed_entities = []
    for spec in ids.specifications:
        assert spec.status is expected
        all_applicable.update(spec.applicable_entities)
        for requirement in spec.requirements:
            if requirement.status is False:
                all_failures.update(requirement.failed_entities)
    assert set(all_applicable) == set(applicable_entities)
    assert set(all_failures) == set(failed_entities)


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
        run("A minimal IDS can check a minimal IFC 1/2", specs, model, False, [wall, waldo], [wall])
        wall.Name = "Waldo"
        run("A minimal IDS can check a minimal IFC 2/2", specs, model, True, [wall, waldo])

        spec.ifcVersion = ["IFC2X3"]
        run(
            "Specification version is purely metadata and does not impact pass or fail result",
            specs,
            model,
            True,
            [wall, waldo]
        )

        spec.ifcVersion = []
        spec.minOccurs = 1
        model = ifcopenshell.file()
        waldo = model.createIfcWall(Name="Waldo")
        run("Required specifications need at least one applicable entity 1/2", specs, model, True, [waldo])
        model = ifcopenshell.file()
        waldo = model.createIfcSlab(Name="Waldo")
        run("Required specifications need at least one applicable entity 2/2", specs, model, False)

        spec.minOccurs = 0
        model = ifcopenshell.file()
        waldo = model.createIfcSlab(Name="Waldo")
        run("Optional specifications may still pass if nothing is applicable", specs, model, True)

        spec.minOccurs = 0
        spec.maxOccurs = 0
        model = ifcopenshell.file()
        wall = model.createIfcSlab(Name="Waldo")
        run("Prohibited specifications fail if at least one entity passes all requirements 1/3", specs, model, True)
        model = ifcopenshell.file()
        wall = model.createIfcWall(Name="Wally")
        run("Prohibited specifications fail if at least one entity passes all requirements 2/3", specs, model, True, [wall], [wall])
        model = ifcopenshell.file()
        wall = model.createIfcWall(Name="Waldo")
        run("Prohibited specifications fail if at least one entity passes all requirements 3/3", specs, model, False, [wall])

        spec.minOccurs = 0
        spec.maxOccurs = "unbounded"
        model = ifcopenshell.file()
        wall = model.createIfcWall(Name="Waldo")
        spec.requirements.append(ids.Attribute(name="Description", value="Foobar"))
        run("A specification passes only if all requirements pass 1/2", specs, model, False, [wall], [wall])
        wall.Description = "Foobar"
        run("A specification passes only if all requirements pass 2/2", specs, model, True, [wall])

        spec.requirements[1].minOccurs = 0
        wall.Description = None
        run("Specification optionality and facet optionality can be combined", specs, model, True, [wall])

        spec.minOccurs = 0
        spec.maxOccurs = 0
        spec.requirements[0].minOccurs = 0
        spec.requirements[0].maxOccurs = 0
        spec.requirements[1].minOccurs = 0
        spec.requirements[1].maxOccurs = 0
        wall.Name = "Waldo"
        wall.Description = "Foobar"
        run("A prohibited specification and a prohibited facet results in a double negative", specs, model, True, [wall])

        spec = ids.Specification(name="Name")
        spec.applicability.append(ids.Entity(name="IFCWALL"))
        spec.requirements.append(ids.Attribute(name="Name", value="Waldo"))
        specs.specifications.append(spec)
        wall2 = model.createIfcWall(Name="Waldo")
        run("Multiple specifications are independent of one another", specs, model, True, [wall, wall2])

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
        print(spec.asdict())
        assert spec.asdict() == {
            "@name": "Unnamed",
            "@ifcVersion": ["IFC2X3", "IFC4"],
            "@minOccurs": 0,
            "@maxOccurs": "unbounded",
            "applicability": {},
            "requirements": {},
        }

    def test_create_specification_with_all_possible_information(self):
        spec = ids.Specification(
            name="name",
            minOccurs=1,
            maxOccurs=1,
            ifcVersion="IFC4",
            identifier="identifier",
            description="description",
            instructions="instructions",
        )
        assert spec.asdict() == {
            "@name": "name",
            "@minOccurs": 1,
            "@maxOccurs": 1,
            "@ifcVersion": "IFC4",
            "@identifier": "identifier",
            "@description": "description",
            "@instructions": "instructions",
            "applicability": {},
            "requirements": {},
        }
