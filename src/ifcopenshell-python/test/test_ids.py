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
import logging
import unittest
import tempfile
import requests
import ifcopenshell
from bcf import bcfxml
from ifcopenshell import ids


def read_web_file(URL):
    return requests.get(URL).text


class TestIdsParsing(unittest.TestCase):

    """Parsing basic IDS files"""

    def test_parse_basic_ids(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_all_fields.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(type(ids_file).__name__, "ids")

    def test_parse_entity_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_entity.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "IfcWall")

    def test_parse_predefinedtype_facet(self):
        IDS_URL = (
            "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_predefinedtype.xml"
        )
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["predefinedtype"]["simpleValue"], "CLADDING"
        )

    def test_parse_property_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["propertyset"]["simpleValue"], "Test_PropertySet"
        )
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"]["simpleValue"], "Test_Value")

    def test_parse_material_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_material.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"]["simpleValue"], "Test_Material")

    def test_parse_classification_facet(self):
        IDS_URL = (
            "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_classification.xml"
        )
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["simpleValue"], "Test_Classification"
        )
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["system"]["simpleValue"], "Test_System")

    """ Parsing invalid IDS.xml """
    # TODO
    # def test_invalid_classification_facet(self):
    #     IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/Invalid_IDS_Wall_needs_classification.xml"
    #     self.assertRaises( XMLSchemaChildrenValidationError, ids.open(read_web_file(IDS_URL)) )

    """ Saving parsed IDS to IDS.xml """

    def test_parsed_ids_to_xml(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_all_fields.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        fn = "TEST_FILE.xml"
        result = ids_file.to_xml(fn)
        os.remove(fn)
        self.assertTrue(result)

    """ Parsing IDS files with restrictions """

    def test_parse_restrictions_enumeration(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property_with_restriction_enumeration.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            [
                x["@value"]
                for x in ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["enumeration"]
            ],
            ["testA", "testB"],
        )

    def test_parse_restrictions_bounds(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property_with_restriction_bounds.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["minInclusive"]["@value"],
            "0",
        )

    def test_parse_restrictions_pattern_simple(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property_with_restriction_pattern.xml"
        ids_file = ids.ids.open(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]["simpleValue"], "Test_Parameter")
        self.assertEqual(
            ids_file.specifications[0].requirements.terms[0].node["value"]["restriction"][0]["pattern"]["@value"],
            "[A-Z]{2,4}",
        )


class TestIdsAuthoring(unittest.TestCase):

    """Creating basic IDS"""

    def test_entity_create(self):
        e = ids.entity.create(name="Test_Name", predefinedtype="Test_PredefinedType")
        self.assertEqual(e.name, "Test_Name")
        self.assertEqual(e.predefinedtype, "Test_PredefinedType")

    def test_classification_create(self):
        c = ids.classification.create(location="any", value="Test_Value", system="Test_System")
        self.assertEqual(c.location, "any")
        self.assertEqual(c.value, "Test_Value")
        self.assertEqual(c.system, "Test_System")

    def test_property_create(self):
        p = ids.property.create(
            location="any", propertyset="Test_PropertySet", name="Test_Parameter", value="Test_Value"
        )
        self.assertEqual(p.location, "any")
        self.assertEqual(p.propertyset, "Test_PropertySet")
        self.assertEqual(p.name, "Test_Parameter")
        self.assertEqual(p.value, "Test_Value")

    def test_material_create(self):
        m = ids.material.create(location="any", value="Test_Value")
        self.assertEqual(m.location, "any")
        self.assertEqual(m.value, "Test_Value")

    def test_specification_create(self):
        s = ids.specification(name="Test_Specification")
        self.assertEqual(s.name, "Test_Specification")

    def test_ids_add_content(self):
        i = ids.ids()
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

    """ Creating IDS with restrictions """

    def test_create_restrictions_enumeration(self):
        i = ids.ids()
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options=["testA", "testB"], type="enumeration", base="string")
        m = ids.material.create(location="any", value=r)
        i.specifications[0].add_requirement(m)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "testA")
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "testB")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "testC")

    def test_create_restrictions_bounds(self):
        i = ids.ids()
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options={"minInclusive": 0, "maxExclusive": 10}, type="bounds", base="integer")
        p = ids.property.create(location="any", propertyset="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, 0)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, 5)
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, -1)
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, 10)

    def test_create_restrictions_pattern_simple(self):
        i = ids.ids()
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        r = ids.restriction.create(options="[A-Z]{2,4}", type="pattern", base="string")
        p = ids.property.create(location="any", propertyset="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "XYZ")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "abc")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "ABCDE")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "A")

    def test_create_restrictions_pattern_advanced(self):
        i = ids.ids()
        i.specifications.append(ids.specification(name="Test_Specification"))
        i.specifications[0].add_applicability(ids.entity.create(name="Test_Name"))
        # r = ids.restriction.create(options="^(Wanddurchbruch.*|Deckendurchbruch.*)", type="pattern", base="string")
        r = ids.restriction.create(options="(Wanddurchbruch|Deckendurchbruch).*", type="pattern", base="string")
        p = ids.property.create(location="any", propertyset="Test", name="Test", value=r)
        i.specifications[0].add_requirement(p)
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "Wanddurchbruch")
        self.assertEqual(i.specifications[0].requirements.terms[0].value, "Deckendurchbruch")
        self.assertNotEqual(i.specifications[0].requirements.terms[0].value, "Deeckendurchbruch")

    """ Saving created IDS to IDS.xml """

    def test_created_ids_to_xml(self):
        i = ids.ids()
        i.specifications.append(ids.specification(name="Test_Specification"))
        e = ids.entity.create(name="Test_Name", predefinedtype="Test_PredefinedType")
        c = ids.classification.create(location="any", value="Test_Value", system="Test_System")
        m = ids.material.create(location="any", value="Test_Value")
        re = ids.restriction.create(options=["testA", "testB"], type="enumeration", base="string")
        rb = ids.restriction.create(options={"minInclusive": 0, "maxExclusive": 10}, type="bounds", base="integer")
        rp = ids.restriction.create(options="[A-Z]{2,4}", type="pattern", base="string")
        p1 = ids.property.create(location="any", propertyset="Test_PropertySet", name="Test_Parameter", value=re)
        p2 = ids.property.create(location="any", propertyset="Test_PropertySet", name="Test_Parameter", value=rb)
        p3 = ids.property.create(location="any", propertyset="Test_PropertySet", name="Test_Parameter", value=rp)
        p4 = ids.property.create(
            location="any", propertyset="Test_PropertySet", name="Test_Parameter", value=[re, rb, rp]
        )
        i.specifications[0].add_applicability(e)
        i.specifications[0].add_applicability(m)
        i.specifications[0].add_requirement(c)
        i.specifications[0].add_requirement(p1)
        i.specifications[0].add_requirement(p2)
        i.specifications[0].add_requirement(p3)
        i.specifications[0].add_requirement(p4)
        fn = "TEST_FILE.xml"
        result = i.to_xml(fn)
        os.remove(fn)
        self.assertTrue(result)

    """ IDS information """

    def test_create_full_information(self):
        i = ids.ids(
            ifcversion="2.3.0.1",
            description="test",
            author="test@test.com",
            copyright="test",
            version=1.23,
            creation_date="2021-01-01",
            purpose="test",
            milestone="test",
        )
        self.assertEqual(i.info["version"], 1.23)


class TestIfcValidation(unittest.TestCase):
    def test_validate_simple(self):
        # TODO
        pass

    def test_validate_all_facets(self):
        # TODO
        pass

    """ Validating IDS files with restrictions """

    # def test_validate_restrictions_enumeration(self):
    #     IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property_with_restriction_enumeration.xml"
    #     ids_file = ids.ids.open(read_web_file(IDS_URL))
    #     self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]['simpleValue'], "Test_Parameter")
    #     self.assertEqual( [x['@value'] for x in ids_file.specifications[0].requirements.terms[0].node["value"]['restriction'][0]['enumeration'] ], ['testA', 'testB'])
    #     # TODO actual test of validation result
    #     # self.assertTrue(   )

    # def test_validate_restrictions_boundsInclusive(self):
    #     IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property_with_restriction_bounds.xml"
    #     ids_file = ids.ids.open(read_web_file(IDS_URL))
    #     self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]['simpleValue'], "Test_Parameter")
    #     self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"]['restriction'][0]['minInclusive']['@value'], '0')
    #     # TODO actual test of validation result
    #     # self.assertTrue(   )

    # def test_validate_restrictions_boundsExclusive(self):
    #     #TODO
    #     pass

    # def test_validate_restrictions_pattern_simple(self):
    #     IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property_with_restriction_pattern.xml"
    #     ids_file = ids.ids.open(read_web_file(IDS_URL))
    #     self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"]['simpleValue'], "Test_Parameter")
    #     self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"]['restriction'][0]['pattern']['@value'], '[A-Z]{2,4}')
    #     # TODO actual test of validation result
    #     # self.assertTrue(   )


class TestIdsReporting(unittest.TestCase):

    TEST_PATH = os.getcwd()
    IFC_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IFC/IFC4_Wall_3_with_properties.ifc"
    IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_all_fields.xml"

    logger = logging.getLogger("IDS_Logger")
    # logging.basicConfig(level=logging.INFO, format="%(message)s")
    # logging.basicConfig(filename=TEST_PATH+r"\log.txt", level=logging.INFO, format="%(message)s")

    content = read_web_file(IFC_URL)
    file = open(TEST_PATH + r"\test.ifc", "w")
    file.write(content)
    file.close()
    ifc_file = ifcopenshell.open(TEST_PATH + r"\test.ifc")
    os.remove(TEST_PATH + r"\test.ifc")

    def test_simple_report(self):
        ids_file = ids.ids.open(read_web_file(self.IDS_URL))
        report = ids.SimpleHandler()
        self.logger.addHandler(report)
        ids_file.validate(self.ifc_file, self.logger)
        self.assertEqual(len(report.statements), 5)

    def test_bcf_report(self):
        ids_file = ids.ids.open(read_web_file(self.IDS_URL))
        fn = os.path.join(tempfile.gettempdir(), "test.bcf")
        bcf_handler = ids.BcfHandler(project_name="Default IDS Project", author="your@email.com", filepath=fn)
        self.logger.addHandler(bcf_handler)
        ids_file.validate(self.ifc_file, self.logger)
        my_bcfxml = bcfxml.load(fn)
        topics = my_bcfxml.get_topics()
        self.assertEqual(len(topics), 5)


if __name__ == "__main__":
    unittest.main()
