# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

import os
import pytest
import logging
import unittest
import tempfile
import xmlschema
from bcf import bcfxml
import ifcopenshell
from ifcopenshell import ids


TEST_PATH = os.path.join(tempfile.gettempdir(), "test.ifc")
IFC_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IFC/", "IFC4_Wall_3_with_properties.ifc")
IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_all_fields.xml")

logger = logging.getLogger("IDS_Logger")
# logging.basicConfig(level=logging.INFO, format="%(message)s")
# logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), "log.txt"), level=logging.INFO, format="%(message)s")

file = open(os.path.join(tempfile.gettempdir(), "test.ifc"), "w")
file.write(IFC_URL)
file.close()
ifc_file = ifcopenshell.open(IFC_URL)
os.remove(os.path.join(tempfile.gettempdir(), "test.ifc"))


class TestIdsParsing(unittest.TestCase):

    """Parsing basic IDS files"""

    def test_parse_basic_ids(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_all_fields.xml")
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(type(ids_file).__name__, "ids")

    def test_parse_entity_facet(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_entity.xml")
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "IfcWall")

    def test_parse_predefinedType_facet(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_predefinedtype.xml")
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["predefinedType"]["simpleValue"], "CLADDING"
        )

    def test_parse_property_facet(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_property.xml")
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["propertySet"]["simpleValue"], "Test_PropertySet"
        )
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"]["simpleValue"], "Test_Value")

    def test_parse_material_facet(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_material.xml")
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"]["simpleValue"], "Test_Material")

    def test_parse_classification_facet(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_classification.xml")
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["simpleValue"], "Test_Classification"
        )
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["system"]["simpleValue"], "Test_System")

    """ Parsing invalid IDS.xml """
    # TODO
    # def test_invalid_classification_facet(self):
    #     IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "Invalid_IDS_Wall_needs_classification.xml")
    #     self.assertRaises( XMLSchemaChildrenValidationError, ids.open(IDS_URL) )

    """ Saving parsed IDS to IDS.xml """

    def test_parsed_ids_to_xml(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files", "IDS", "IDS_Wall_needs_all_fields.xml")
        ids_file = ids.ids.open(IDS_URL)
        fn = "output.xml"
        result = ids_file.to_xml(fn)
        assert os.path.isfile(fn)
        os.remove(fn)
        self.assertTrue(result)

    def test_parsed_ids_to_string(self):
        IDS_URL = os.path.join(os.path.dirname(__file__), "Sample-BIM-Files", "IDS", "IDS_Wall_needs_all_fields.xml")
        ids_file = ids.ids.open(IDS_URL)
        output = ids_file.to_string()
        assert output and "http://standards.buildingsmart.org/IDS" in output

    """ Parsing IDS files with restrictions """

    def test_parse_restrictions_enumeration(self):
        IDS_URL = os.path.join(
            os.path.dirname(__file__),
            "Sample-BIM-Files/IDS/",
            "IDS_Wall_needs_property_with_restriction_enumeration.xml",
        )
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            [
                x["@value"]
                for x in ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["enumeration"]
            ],
            ["testA", "testB"],
        )

    def test_parse_restrictions_bounds(self):
        IDS_URL = os.path.join(
            os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_property_with_restriction_bounds.xml"
        )
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["minInclusive"]["@value"],
            "0",
        )

    def test_parse_restrictions_pattern_simple(self):
        IDS_URL = os.path.join(
            os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_property_with_restriction_pattern.xml"
        )
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["pattern"]["@value"],
            "[A-Z]{2,4}",
        )


class TestIdsAuthoring(unittest.TestCase):
    def test_creating_a_minimal_ids_and_validating(self):
        specs = ids.ids(title="Title")
        spec = ids.specification(name="Name")
        spec.add_applicability(ids.entity.create(name="IfcWall"))
        spec.add_requirement(ids.attribute.create(name="Name", value="Waldo"))
        specs.specifications.append(spec)
        assert "http://standards.buildingsmart.org/IDS" in specs.to_string()

        model = ifcopenshell.file()
        model.createIfcWall(Name="Waldo")
        specs.validate(model)
        # TODO test this without resorting to hooking into logger output

    def test_create_an_ids_with_minimal_information(self):
        specs = ids.ids()
        assert specs.asdict() == {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_05.xsd",
            "info": {"title": "Untitled"},
            "specifications": [],
        }

    def test_create_an_ids_with_all_possible_information(self):
        specs = ids.ids(
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
            "specifications": [],
        }

    def test_check_invalid_ids_information(self):
        specs = ids.ids(title=None, author="author", date="9999-99-99")
        assert specs.asdict() == {
            "@xmlns": "http://standards.buildingsmart.org/IDS",
            "@xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:schemaLocation": "http://standards.buildingsmart.org/IDS/ids_05.xsd",
            "info": {"title": "Untitled"},
            "specifications": [],
        }

    def test_authoring_an_ids_with_no_specifications_is_invalid(self):
        specs = ids.ids()
        with pytest.raises(xmlschema.validators.exceptions.XMLSchemaChildrenValidationError):
            specs.to_string()

    def test_create_specification_with_minimal_information(self):
        spec = ids.specification()
        assert spec.asdict() == {
            "@name": "Unnamed",
            "@use": "required",
            "@ifcVersion": ["IFC2X3", "IFC4"],
            "applicability": {},
            "requirements": {},
        }

    def test_create_specification_with_all_possible_information(self):
        spec = ids.specification(
            name="name",
            use="use",
            ifcVersion="IFC4",
            identifier="identifier",
            description="description",
            instructions="instructions",
        )
        assert spec.asdict() == {
            "@name": "name",
            "@use": "use",
            "@ifcVersion": "IFC4",
            "@identifier": "identifier",
            "@description": "description",
            "@instructions": "instructions",
            "applicability": {},
            "requirements": {},
        }

    def test_ids_add_content(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        self.assertEqual(i.specifications[0].name, "Test_Specification")
        m = ids.material.create(location="any", value="Test_Value")
        i.specifications[0].add_applicability(m)
        self.assertEqual(i.specifications[0].applicability.terms[0].value, "Test_Value")
        i.specifications[0].add_applicability(m)
        self.assertEqual(i.specifications[0].applicability.terms[1].value, "Test_Value")
        i.specifications[0].add_requirement(m)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "Test_Value")
        i.specifications[0].add_requirement(m)
        self.assertEqual(i.specifications[0].requirements.terms[1].value, "Test_Value")

    def test_create_an_entity_facet(self):
        facet = ids.entity.create(name="IfcName")
        assert facet.asdict() == {"name": {"simpleValue": "IfcName"}}
        facet = ids.entity.create(name="IfcName", predefinedType="predefinedType")
        assert facet.asdict() == {
            "name": {"simpleValue": "IfcName"},
            "predefinedType": {"simpleValue": "predefinedType"},
        }

    def test_filtering_using_an_entity_facet(self):
        ifc = ifcopenshell.file()

        facet = ids.entity.create(name="IfcWall")
        assert bool(facet(ifc.createIfcWall())) is True
        assert bool(facet(ifc.createIfcWall(PredefinedType="SOLIDWALL"))) is True
        assert bool(facet(ifc.createIfcSlab())) is False

        facet = ids.entity.create(name="IFCWALL")
        assert bool(facet(ifc.createIfcWall())) is True
        assert bool(facet(ifc.createIfcWall(PredefinedType="SOLIDWALL"))) is True
        assert bool(facet(ifc.createIfcSlab())) is False

        facet = ids.entity.create(name="IfcWall", predefinedType="SOLIDWALL")
        assert bool(facet(ifc.createIfcWall())) is False
        assert bool(facet(ifc.createIfcWall(PredefinedType="SOLIDWALL"))) is True
        assert bool(facet(ifc.createIfcWall(PredefinedType="PARTITIONING"))) is False

        facet = ids.entity.create(name="IfcWall", predefinedType="WALDO")
        assert bool(facet(ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"))) is True

        facet = ids.entity.create(name="IfcWallType", predefinedType="WALDO")
        assert bool(facet(ifc.createIfcWallType(PredefinedType="USERDEFINED", ElementType="WALDO"))) is True

        restriction = ids.restriction.create(options=["IfcWall", "IfcSlab"], type="enumeration", base="string")
        facet = ids.entity.create(name=restriction)
        assert bool(facet(ifc.createIfcWall())) is True
        assert bool(facet(ifc.createIfcSlab())) is True
        assert bool(facet(ifc.createIfcBeam())) is False

        restriction = ids.restriction.create(options="Ifc.*Type", type="pattern", base="string")
        facet = ids.entity.create(name=restriction)
        assert bool(facet(ifc.createIfcWall())) is False
        assert bool(facet(ifc.createIfcWallType())) is True

    def test_creating_an_attribute_facet(self):
        attribute = ids.attribute.create(name="Name", value="Value")
        assert attribute.name == "Name"
        assert attribute.value == "Value"
        assert attribute.asdict() == {
            "name": {"simpleValue": "Name"},
            "value": {"simpleValue": "Value"},
            "@location": "any",
        }

    def test_filtering_using_an_attribute_facet(self):
        ifc = ifcopenshell.file()

        facet = ids.attribute.create(name="Foobar")
        assert bool(facet(ifc.createIfcWall())) is False

        facet = ids.attribute.create(name="Name")
        assert bool(facet(ifc.createIfcWall())) is False
        assert bool(facet(ifc.createIfcWall(Name=""))) is False
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is True

        facet = ids.attribute.create(name="Name", value="Foobar")
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is True
        assert bool(facet(ifc.createIfcWall(Name="Foobaz"))) is False

        facet = ids.attribute.create(name="Eastings")
        assert bool(facet(ifc.createIfcMapConversion(Eastings=0))) is True

        facet = ids.attribute.create(name="Eastings", value=42)
        assert bool(facet(ifc.createIfcMapConversion(Eastings=0))) is False
        assert bool(facet(ifc.createIfcMapConversion(Eastings=42))) is True

        restriction = ids.restriction.create(options=["Foo", "Bar"], type="enumeration", base="string")
        facet = ids.attribute.create(name="Name", value=restriction)
        assert bool(facet(ifc.createIfcWall(Name="Foo"))) is True
        assert bool(facet(ifc.createIfcWall(Name="Bar"))) is True
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is False

    def test_classification_create(self):
        c = ids.classification.create(location="any", value="Test_Value", system="Test_System")
        self.assertEqual(c.location, "any")
        self.assertEqual(c.value, "Test_Value")
        self.assertEqual(c.system, "Test_System")

    def test_property_create(self):
        p = ids.property.create(
            location="any", propertySet="Test_PropertySet", name="Test_Parameter", value="Test_Value"
        )
        self.assertEqual(p.location, "any")
        self.assertEqual(p.propertySet, "Test_PropertySet")
        self.assertEqual(p.name, "Test_Parameter")
        self.assertEqual(p.value, "Test_Value")

    def test_material_create(self):
        m = ids.material.create(location="any", value="Test_Value")
        self.assertEqual(m.location, "any")
        self.assertEqual(m.value, "Test_Value")

    """ Creating IDS with restrictions """

    def test_create_restrictions_enumeration(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options=["testA", "testB"], type="enumeration", base="string")
        m = ids.material.create(location="any", value=r)
        i.specifications[0].add_requirement(m)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "testA")
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "testB")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "testC")

    def test_create_restrictions_bounds(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options={"minInclusive": 0, "maxExclusive": 10}, type="bounds", base="integer")
        p = ids.property.create(location="any", propertySet="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, 0)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, 5)
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, -1)
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, 10)

    def test_create_restrictions_pattern_simple(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options="[A-Z]{2,4}", type="pattern", base="string")
        p = ids.property.create(location="any", propertySet="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "XYZ")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "abc")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "ABCDE")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "A")

    def test_create_restrictions_pattern_advanced(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options="(Wanddurchbruch|Deckendurchbruch).*", type="pattern", base="string")
        p = ids.property.create(location="any", propertySet="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "Wanddurchbruch")
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "Deckendurchbruch")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "Deeckendurchbruch")

    def test_create_restrictions_pattern_utf(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options="èêóòâôæøåążźćęóʑʒʓʔʕʗʘʙʚʛʜʝʞ", type="pattern", base="string")
        p = ids.property.create(location="any", propertySet="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "èêóòâôæøåążźćęóʑʒʓʔʕʗʘʙʚʛʜʝʞ")

    """ Saving created IDS to IDS.xml """

    def test_created_ids_to_xml(self):
        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        e = ids.entity.create(name="Test_Name", predefinedType="Test_PredefinedType")
        c = ids.classification.create(location="any", value="Test_Value", system="Test_System")
        m = ids.material.create(location="any", value="Test_Value")
        re = ids.restriction.create(options=["testA", "testB"], type="enumeration", base="string")
        rb = ids.restriction.create(options={"minInclusive": 0, "maxExclusive": 10}, type="bounds", base="integer")
        rp1 = ids.restriction.create(options="[A-Z]{2,4}", type="pattern", base="string")
        rp2 = ids.restriction.create(options="èêóòâôæøåążźćęóʑʒʓʔʕʗʘʙʚʛʜʝʞ", type="pattern", base="string")
        p1 = ids.property.create(location="any", propertySet="Test_PropertySet", name="Test_Parameter", value=re)
        p2 = ids.property.create(location="any", propertySet="Test_PropertySet", name="Test_Parameter", value=rb)
        p3 = ids.property.create(location="any", propertySet="Test_PropertySet", name="Test_Parameter", value=rp1)
        p4 = ids.property.create(location="any", propertySet="Test_PropertySet", name="Test_Parameter", value=rp2)
        p5 = ids.property.create(
            location="any", propertySet="Test_PropertySet", name="Test_Parameter", value=[re, rb, rp1]
        )
        i.specifications[0].add_applicability(e)
        i.specifications[0].add_applicability(m)
        i.specifications[0].add_requirement(c)
        i.specifications[0].add_requirement(p1)
        # TODO i.specifications[0].add_requirement(p2)
        i.specifications[0].add_requirement(p3)
        i.specifications[0].add_requirement(p4)
        # TODO i.specifications[0].add_requirement(p5)
        fn = "TEST_FILE.xml"
        result = i.to_xml(fn)
        os.remove(fn)
        self.assertTrue(result)


class TestIfcValidation(unittest.TestCase):
    def test_validate_simple(self):
        # Same test as in reporting...
        ids_file = ids.ids.open(IDS_URL)
        report = ids.SimpleHandler()
        logger.addHandler(report)
        ids_file.validate(ifc_file, logger)
        self.assertEqual(len(report.statements), 5)
        logger.handlers.pop()

    def test_validate_all_facets(self):
        # Those are true:
        e = ids.entity.create(name="IfcWall")
        p1 = ids.property.create(location="any", propertySet="MySet", name="Param1", value="banan")
        p2 = ids.property.create(location="any", propertySet="MySet", name="Param2", value=120.0)
        p3 = ids.property.create(location="any", propertySet="Pset_WallCommon", name="LoadBearing", value=False)
        # Those are false:
        p4 = ids.property.create(location="any", propertySet="MySet", name="Param1", value="orange")
        p5 = ids.property.create(location="any", propertySet="MySet", name="Param2", value=123.4)
        p6 = ids.property.create(location="any", propertySet="Pset_WallCommon", name="LoadBearing", value=True)

        i = ids.ids(title="My IDS")
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(e)
        i.specifications[0].add_requirement(p1)
        i.specifications[0].add_requirement(p2)
        i.specifications[0].add_requirement(p3)
        i.specifications[0].add_requirement(p4)
        i.specifications[0].add_requirement(p5)
        i.specifications[0].add_requirement(p6)

        report = ids.SimpleHandler(report_valid=True)
        logger.addHandler(report)

        i.validate(ifc_file, logger)
        # TODO self.assertEqual(len(report.statements), 27) #there are 5 walls in the IFC, one passed 3 criteria, est should fail (27 failures)
        logger.handlers.pop()

    """ Validating IDS files with restrictions """

    def test_validate_restrictions_enumeration(self):
        IDS_URL = os.path.join(
            os.path.dirname(__file__),
            "Sample-BIM-Files/IDS/",
            "IDS_Wall_needs_property_with_restriction_enumeration.xml",
        )
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            [
                x["@value"]
                for x in ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["enumeration"]
            ],
            ["testA", "testB"],
        )
        # TODO actual test of validation result
        # self.assertTrue(   )

    def test_validate_restrictions_boundsInclusive(self):
        IDS_URL = os.path.join(
            os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_property_with_restriction_bounds.xml"
        )
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["minInclusive"]["@value"],
            "0",
        )
        # TODO actual test of validation result
        # self.assertTrue(   )

    def test_validate_restrictions_boundsExclusive(self):
        # TODO
        pass

    def test_validate_restrictions_pattern_simple(self):
        IDS_URL = os.path.join(
            os.path.dirname(__file__), "Sample-BIM-Files/IDS/", "IDS_Wall_needs_property_with_restriction_pattern.xml"
        )
        ids_file = ids.ids.open(IDS_URL)
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["pattern"]["@value"],
            "[A-Z]{2,4}",
        )
        # TODO actual test of validation result
        # self.assertTrue(   )


class TestIdsReporting(unittest.TestCase):
    def test_simple_report(self):
        # Same test as in validation...
        ids_file = ids.ids.open(IDS_URL)
        report = ids.SimpleHandler()
        logger.addHandler(report)
        ids_file.validate(ifc_file, logger)
        self.assertEqual(len(report.statements), 5)
        logger.handlers.pop()

    def test_bcf_report(self):
        ids_file = ids.ids.open(IDS_URL)
        fn = os.path.join(tempfile.gettempdir(), "test.bcf")
        bcf_handler = ids.BcfHandler(project_name="Default IDS Project", author="your@email.com", filepath=fn)
        logger.addHandler(bcf_handler)
        ids_file.validate(ifc_file, logger)
        my_bcfxml = bcfxml.load(fn)
        topics = my_bcfxml.get_topics()
        self.assertEqual(len(topics), 5)
        logger.handlers.pop()


if __name__ == "__main__":
    unittest.main()
