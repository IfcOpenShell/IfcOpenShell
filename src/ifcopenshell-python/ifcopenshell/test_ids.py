import unittest
from ids import ids, specification, entity, classification, property, material
import requests

def read_web_file(URL):
    return requests.get(URL).text
    

class TestIds(unittest.TestCase):

    """ Parsing IDS.xml """

    def test_basic_ids_parse(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_all_fields.xml"
        ids_file = ids.parse(read_web_file(IDS_URL))
        self.assertEqual( type(ids_file).__name__, "ids" )
        
    def test_entity_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_entity.xml"
        ids_file = ids.parse(read_web_file(IDS_URL))
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['name'] , "IfcWall" )

    def test_predefinedtype_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_predefinedtype.xml"
        ids_file = ids.parse(read_web_file(IDS_URL))
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['predefinedtype'] , "CLADDING" )

    def test_property_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_property.xml"
        ids_file = ids.parse(read_web_file(IDS_URL))
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['propertyset'] , "Test_PropertySet" )
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['name'] , "Test_Parameter" )
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['value'] , "Test_Value" )

    def test_material_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_material.xml"
        ids_file = ids.parse(read_web_file(IDS_URL))
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['value'] , "Test_Material" )

    def test_classification_facet(self):
        IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/IDS_Wall_needs_classification.xml"
        ids_file = ids.parse(read_web_file(IDS_URL))
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['value'] , "Test_Classification" )
        self.assertEqual( ids_file.specifications[0].requirements.terms[0].node['system'] , "Test_System" )

    """ Parsing invalid IDS.xml """
    # TODO
    # def test_invalid_classification_facet(self):
    #     IDS_URL = "https://raw.githubusercontent.com/atomczak/Sample-BIM-Files/main/IDS/Invalid_IDS_Wall_needs_classification.xml"
    #     self.assertRaises( XMLSchemaChildrenValidationError, ids.parse(read_web_file(IDS_URL)) )
   
    """ IDS authoring """
    # TODO

    """ IFC validation with IDS """
    # TODO

    """ IDS validation results """
    # TODO


if __name__ == '__main__':
    import sys
    unittest.main()