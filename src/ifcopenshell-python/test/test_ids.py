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
import ifcopenshell
import ifcopenshell.api
from bcf import bcfxml
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
            use="required",
            ifcVersion="IFC4",
            identifier="identifier",
            description="description",
            instructions="instructions",
        )
        assert spec.asdict() == {
            "@name": "name",
            "@use": "required",
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

        # Wrong IFC classes are never matched.
        facet = ids.entity.create(name="IfcRabbit")
        assert bool(facet(ifc.createIfcWall())) is False

        # IFC class is checked for an exact match. Subclasses should not match.
        facet = ids.entity.create(name="IfcWall")
        assert bool(facet(ifc.createIfcWall())) is True
        assert bool(facet(ifc.createIfcWall(PredefinedType="SOLIDWALL"))) is True
        assert bool(facet(ifc.createIfcSlab())) is False
        assert bool(facet(ifc.createIfcWallStandardCase())) is False

        # IFC class is case insensitive.
        facet = ids.entity.create(name="IFCWALL")
        assert bool(facet(ifc.createIfcWall())) is True
        assert bool(facet(ifc.createIfcWall(PredefinedType="SOLIDWALL"))) is True
        assert bool(facet(ifc.createIfcSlab())) is False

        # Predefined types are checked from standard enumeration values
        facet = ids.entity.create(name="IfcWall", predefinedType="SOLIDWALL")
        assert bool(facet(ifc.createIfcWall())) is False
        assert bool(facet(ifc.createIfcWall(PredefinedType="SOLIDWALL"))) is True
        assert bool(facet(ifc.createIfcWall(PredefinedType="PARTITIONING"))) is False

        # Predefined types are checked from the object type field if not standard
        facet = ids.entity.create(name="IfcWall", predefinedType="WALDO")
        assert bool(facet(ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"))) is True

        # Predefined types are checked from the element type field if not standard for types
        facet = ids.entity.create(name="IfcWallType", predefinedType="WALDO")
        assert bool(facet(ifc.createIfcWallType(PredefinedType="USERDEFINED", ElementType="WALDO"))) is True

        # Userdefined is not an allowed filter because userdefined implies a specified object or element type
        facet = ids.entity.create(name="IfcWall", predefinedType="USERDEFINED")
        assert bool(facet(ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"))) is False

        # Predefined types should match inherited predefined types from the element type
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType", predefined_type="X")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        facet = ids.entity.create(name="IfcWall", predefinedType="X")
        assert bool(facet(wall)) is True

        # Predefined types should match overridden predefined types from the element type
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="X")
        wall_type = ifcopenshell.api.run(
            "root.create_entity", ifc, ifc_class="IfcWallType", predefined_type="NOTDEFINED"
        )
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        facet = ids.entity.create(name="IfcWall", predefinedType="X")
        assert bool(facet(wall)) is True

        # Restrictions are allowed when matching the IFC class
        restriction = ids.restriction.create(options=["IfcWall", "IfcSlab"], type="enumeration", base="string")
        facet = ids.entity.create(name=restriction)
        assert bool(facet(ifc.createIfcWall())) is True
        assert bool(facet(ifc.createIfcSlab())) is True
        assert bool(facet(ifc.createIfcBeam())) is False

        # Another example of how restrictions are allowed when matching the IFC class
        restriction = ids.restriction.create(options="Ifc.*Type", type="pattern", base="string")
        facet = ids.entity.create(name=restriction)
        assert bool(facet(ifc.createIfcWall())) is False
        assert bool(facet(ifc.createIfcWallType())) is True

        # Restrictions are allowed when matching the predefined type
        restriction = ids.restriction.create(options="FOO.*", type="pattern", base="string")
        facet = ids.entity.create(name="IfcWall", predefinedType=restriction)
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="FOOBAR")
        wall2 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="FOOBAZ")
        assert bool(facet(wall)) is True
        assert bool(facet(wall2)) is True

    def test_creating_an_attribute_facet(self):
        attribute = ids.attribute.create(name="name")
        assert attribute.asdict() == {"name": {"simpleValue": "name"}, "@location": "any"}
        attribute = ids.attribute.create(name="name", value="value", location="instance")
        assert attribute.asdict() == {
            "name": {"simpleValue": "name"},
            "value": {"simpleValue": "value"},
            "@location": "instance",
        }
        attribute = ids.attribute.create(
            name="name", value="value", location="instance", use="required", instructions="instructions"
        )
        assert attribute.asdict() == {
            "name": {"simpleValue": "name"},
            "value": {"simpleValue": "value"},
            "@location": "instance",
            "@use": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_an_attribute_facet(self):
        ifc = ifcopenshell.file()

        # Attribute names that don't exist are never matched
        facet = ids.attribute.create(name="Foobar")
        assert bool(facet(ifc.createIfcWall())) is False

        # Attribute names that are either null or empty string are not matched.
        # The logic is that unfortunately most BIM users cannot differentiate between the two.
        facet = ids.attribute.create(name="Name")
        assert bool(facet(ifc.createIfcWall())) is False
        assert bool(facet(ifc.createIfcWall(Name=""))) is False
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is True

        # When a value is specified, the value shall match case sensitively
        facet = ids.attribute.create(name="Name", value="Foobar")
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is True
        assert bool(facet(ifc.createIfcWall(Name="Foobaz"))) is False

        # A value that is 0 is still considered a value, not "null-like", so it is matched
        facet = ids.attribute.create(name="Eastings")
        assert bool(facet(ifc.createIfcMapConversion(Eastings=0))) is True

        # Values are checked with strict typing. No type casting shall occur.
        facet = ids.attribute.create(name="Eastings", value=42)
        assert bool(facet(ifc.createIfcMapConversion(Eastings=0))) is False
        assert bool(facet(ifc.createIfcMapConversion(Eastings=42))) is True
        facet = ids.attribute.create(name="Eastings", value="42")
        assert bool(facet(ifc.createIfcMapConversion(Eastings=42))) is False

        # Restrictions are allowed for the name
        restriction = ids.restriction.create(options=".*Name.*", type="pattern", base="string")
        facet = ids.attribute.create(name=restriction)
        assert bool(facet(ifc.createIfcMaterialLayerSet(LayerSetName="Foo"))) is True
        assert bool(facet(ifc.createIfcMaterialConstituentSet(Name="Foo"))) is True

        # Restrictions for the name imply that multiple names may be matched. All, not any, must pass the checks.
        restriction = ids.restriction.create(options=["Name", "Description"], type="enumeration", base="string")
        facet = ids.attribute.create(name=restriction)
        assert bool(facet(ifc.createIfcWall(Name="Foo"))) is False
        assert bool(facet(ifc.createIfcWall(Name="Foo", Description="Bar"))) is True

        # Restrictions are allowed for the value
        restriction = ids.restriction.create(options=["Foo", "Bar"], type="enumeration", base="string")
        facet = ids.attribute.create(name="Name", value=restriction)
        assert bool(facet(ifc.createIfcWall(Name="Foo"))) is True
        assert bool(facet(ifc.createIfcWall(Name="Bar"))) is True
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is False

        # Location instance only checks on the instance, this seems like intuitive behaviour
        facet = ids.attribute.create(name="Name", value="Foobar", location="instance")
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is True
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        wall_type.Name = "Foobar"
        assert bool(facet(wall)) is False

        # Location type only checks on the type. This seems a bit weird honestly.
        facet = ids.attribute.create(name="Name", value="Foobar", location="type")
        assert bool(facet(ifc.createIfcWall(Name="Foobar"))) is False
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        wall_type.Name = "Foobar"
        assert bool(facet(wall)) is True

        # Location any checks on attributes on the type, which may be inherited by the occurence
        facet = ids.attribute.create(name="Description", value="Foobar", location="any")
        assert bool(facet(ifc.createIfcWall(Description="Foobar"))) is True
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        wall_type.Description = "Foobar"
        assert bool(facet(wall)) is True

        # Location any checks on attributes on the type, which may be overriden by attributes on the occurence
        facet = ids.attribute.create(name="Description", value="Foobar", location="any")
        assert bool(facet(ifc.createIfcWall(Description="Foobar"))) is True
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        wall_type.Description = "Foobaz"
        wall.Description = "Foobar"
        assert bool(facet(wall)) is True

    def test_creating_a_classification_facet(self):
        facet = ids.classification.create()
        assert facet.asdict() == {"@location": "any"}
        facet = ids.classification.create(value="value", system="system", location="instance")
        assert facet.asdict() == {
            "value": {"simpleValue": "value"},
            "system": {"simpleValue": "system"},
            "@location": "instance",
        }
        facet = ids.classification.create(
            value="value",
            system="system",
            location="instance",
            uri="https://test.com",
            use="required",
            instructions="instructions",
        )
        assert facet.asdict() == {
            "value": {"simpleValue": "value"},
            "system": {"simpleValue": "system"},
            "@location": "instance",
            "@uri": "https://test.com",
            "@use": "required",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_classification_facet(self):
        library = ifcopenshell.file()
        system = library.createIfcClassification(Name="Foobar")
        ref1 = library.createIfcClassificationReference(Identification="1", ReferencedSource=system)
        ref11 = library.createIfcClassificationReference(Identification="11", ReferencedSource=ref1)
        ref2 = library.createIfcClassificationReference(Identification="2", ReferencedSource=system)
        ref22 = library.createIfcClassificationReference(Identification="22", ReferencedSource=ref2)

        ifc = ifcopenshell.file()
        project = ifc.createIfcProject()
        ifcopenshell.api.run("classification.add_classification", ifc, classification=system)
        element0 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        element1 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=element1, reference=ref1, classification=system
        )
        element11 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=element11, reference=ref11, classification=system
        )
        element22 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference",
            ifc,
            product=element22,
            reference=ref22,
            classification=system,
            is_lightweight=False,
        )

        # A classification facet with no data matches any present classification
        facet = ids.classification.create()
        assert bool(facet(element0)) is False
        assert bool(facet(element1)) is True

        # Values should match exactly if lightweight classifications are used.
        facet = ids.classification.create(value="1")
        assert bool(facet(element1)) is True

        # Values should match subreferences if full classifications are used.
        # E.g. a facet searching for Uniclass EF_25_10 Walls will match Uniclass EF_25_10_25, EF_25_10_30, etc
        facet = ids.classification.create(value="2")
        assert bool(facet(element22)) is True

        # Systems should match exactly regardless of lightweight or full classifications
        facet = ids.classification.create(system="Foobar")
        assert bool(facet(project)) is True
        assert bool(facet(element0)) is False
        assert bool(facet(element1)) is True
        assert bool(facet(element11)) is True
        assert bool(facet(element22)) is True

        # Restrictions can be used for values
        restriction = ids.restriction.create(options="1.*", type="pattern", base="string")
        facet = ids.classification.create(value=restriction)
        assert bool(facet(element1)) is True
        assert bool(facet(element11)) is True
        assert bool(facet(element22)) is False

        # Restrictions can be used for systems
        restriction = ids.restriction.create(options="Foo.*", type="pattern", base="string")
        facet = ids.classification.create(system=restriction)
        assert bool(facet(element0)) is False
        assert bool(facet(element1)) is True

        # Specifying both a value and a system means that both (as opposed to either) requirements must be met
        facet = ids.classification.create(system="Foobar", value="1")
        assert bool(facet(element1)) is True
        assert bool(facet(element11)) is False

        # Location instance only checks on the instance (even if it's a type), this seems strange though
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall_type, reference=ref1, classification=system
        )
        facet = ids.classification.create(value="1", location="instance")
        assert bool(facet(wall_type)) is True
        assert bool(facet(wall)) is False
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall, reference=ref1, classification=system
        )
        assert bool(facet(wall)) is True

        # Location type only checks on the type
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall, reference=ref1, classification=system
        )
        facet = ids.classification.create(value="1", location="type")
        assert bool(facet(wall)) is False
        assert bool(facet(wall_type)) is False
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall_type, reference=ref1, classification=system
        )
        assert bool(facet(wall)) is True
        assert bool(facet(wall_type)) is True

        # Location any checks on either the type or instance.
        # IFC doesn't specify how inheritance and overrides work here. Two options:
        # Option 1) Occurrences replace inherited type references
        # Option 2) Occurrences union with inherited type references
        # Option 2 is followed here.
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall, reference=ref11, classification=system
        )
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall_type, reference=ref22, classification=system
        )
        facet = ids.classification.create(value="11", location="any")
        assert bool(facet(wall)) is True
        assert bool(facet(wall_type)) is False
        facet = ids.classification.create(value="22", location="any")
        assert bool(facet(wall)) is True
        assert bool(facet(wall_type)) is True

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
