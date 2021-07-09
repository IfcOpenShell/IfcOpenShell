import unittest
import ids
import requests
import os
# from xmlschema.validators.exceptions import XMLSchemaChildrenValidationError


def read_web_file(URL):
    return requests.get(URL).text


class TestIdsParsing(unittest.TestCase):

    def test_basic_ids_parse(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_all_fields.xml"
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        self.assertEqual(type(ids_file).__name__, "ids")

    def test_entity_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_entity.xml"
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"], "IfcWall")

    def test_predefinedtype_facet(self):
        IDS_URL = (
            "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_predefinedtype.xml"
        )
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["predefinedtype"], "CLADDING")

    def test_property_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property.xml"
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["propertyset"], "Test_PropertySet")
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["name"], "Test_Parameter")
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"], "Test_Value")

    def test_material_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_material.xml"
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"], "Test_Material")

    def test_classification_facet(self):
        IDS_URL = (
            "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_classification.xml"
        )
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["value"], "Test_Classification")
        self.assertEqual(ids_file.specifications[0].requirements.terms[0].node["system"], "Test_System")

    """ Parsing invalid IDS.xml """
    # TODO
    # def test_invalid_classification_facet(self):
    #     IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/Invalid_IDS_Wall_needs_classification.xml"
    #     self.assertRaises( XMLSchemaChildrenValidationError, ids.parse(read_web_file(IDS_URL)) )

    """ Saving parsed IDS to IDS.xml """

    def test_parsed_ids_to_xml(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_all_fields.xml"
        ids_file = ids.ids.parse(read_web_file(IDS_URL))
        fn = "TEST_FILE.xml"
        result = ids_file.to_xml(fn)
        os.remove(fn)
        self.assertTrue(result)


class TestIdsAuthoring(unittest.TestCase):

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

    def test_ids_create(self):
        i = ids.ids()
        self.assertEqual(i.specifications, [])
        self.assertEqual(i.info, None)

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

    """ Saving created IDS to IDS.xml """

    def test_created_ids_to_xml(self):
        i = ids.ids()
        i.specifications.append(ids.specification(name="Test_Specification"))
        e = ids.entity.create(name="Test_Name", predefinedtype="Test_PredefinedType")
        c = ids.classification.create(location="any", value="Test_Value", system="Test_System")
        m = ids.material.create(location="any", value="Test_Value")
        p = ids.property.create(location="any", propertyset="Test_PropertySet", name="Test_Parameter", value="Test_Value")
        i.specifications[0].add_applicability(e)
        i.specifications[0].add_applicability(m)
        i.specifications[0].add_requirement(c)
        i.specifications[0].add_requirement(p)
        fn = "TEST_FILE.xml"
        result = i.to_xml(fn)
        os.remove(fn)
        self.assertTrue(result)


class TestIfcValidation(unittest.TestCase):
    pass
    # TODO


class TestIdsResults(unittest.TestCase):
    pass
    # TODO


if __name__ == "__main__":
    unittest.main()
