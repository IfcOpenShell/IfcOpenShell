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


import ifcopenshell
import ifcopenshell.api
from ifctester.facet import Entity, Attribute, Classification, Property, PartOf, Material, Restriction


def set_facet(facet):
    pass


def run(name, *, facet, inst, expected):
    assert bool(facet(inst)) is expected


class TestEntity:
    def test_creating_an_entity_facet(self):
        facet = Entity(name="IfcName")
        assert facet.asdict() == {"name": {"simpleValue": "IfcName"}}
        facet = Entity(name="IfcName", predefinedType="predefinedType", instructions="instructions")
        assert facet.asdict() == {
            "name": {"simpleValue": "IfcName"},
            "predefinedType": {"simpleValue": "predefinedType"},
            "@instructions": "instructions",
        }

    def test_filtering_using_an_entity_facet(self):
        set_facet("entity")

        ifc = ifcopenshell.file()
        facet = Entity(name="IFCRABBIT")
        run("Invalid entities always fail", facet=facet, inst=ifc.createIfcWall(), expected=False)

        ifc = ifcopenshell.file()
        facet = Entity(name="IFCWALL")
        run("A matching entity should pass", facet=facet, inst=ifc.createIfcWall(), expected=True)
        ifc = ifcopenshell.file()
        run(
            "An matching entity should pass regardless of predefined type",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="SOLIDWALL"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "An entity not matching the specified class should fail",
            facet=facet,
            inst=ifc.createIfcSlab(),
            expected=False,
        )
        # TODO: Some votes to prefer inheritance (For: Moult, Evandro, Artur)
        # Possible argument: CAD tools don't understand IFC
        ifc = ifcopenshell.file()
        run(
            "Subclasses are not considered as matching",
            facet=facet,
            inst=ifc.createIfcWallStandardCase(),
            expected=False,
        )

        # TODO But in that case why are the enumerations for things like partOf using the IFC capitalisation?
        facet = Entity(name="IfcWall")
        ifc = ifcopenshell.file()
        run(
            "Entities must be specified as uppercase strings",
            facet=facet,
            inst=ifc.createIfcWall(),
            expected=False,
        )

        facet = Entity(name="IFCWALL", predefinedType="SOLIDWALL")
        ifc = ifcopenshell.file()
        run(
            "A matching predefined type should pass",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="SOLIDWALL"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "A null predefined type should always fail a specified predefined types",
            facet=facet,
            inst=ifc.createIfcWall(),
            expected=False,
        )
        ifc = ifcopenshell.file()
        run(
            "An entity not matching a specified predefined type will fail",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="PARTITIONING"),
            expected=False,
        )

        facet = Entity(name="IFCWALL", predefinedType="solidwall")
        ifc = ifcopenshell.file()
        run(
            "A predefined type from an enumeration must be uppercase",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="SOLIDWALL"),
            expected=False,
        )

        facet = Entity(name="IFCWALL", predefinedType="WALDO")
        ifc = ifcopenshell.file()
        run(
            "A predefined type may specify a user-defined object type",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"),
            expected=True,
        )

        facet = Entity(name="IFCWALL", predefinedType="WALDO")
        ifc = ifcopenshell.file()
        run(
            "User-defined types are checked case sensitively",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="waldo"),
            expected=False,
        )

        facet = Entity(name="IFCWALLTYPE", predefinedType="WALDO")
        ifc = ifcopenshell.file()
        run(
            "A predefined type may specify a user-defined element type",
            facet=facet,
            inst=ifc.createIfcWallType(PredefinedType="USERDEFINED", ElementType="WALDO"),
            expected=True,
        )

        facet = Entity(name="IFCTASKTYPE", predefinedType="TASKY")
        ifc = ifcopenshell.file()
        run(
            "A predefined type may specify a user-defined process type",
            facet=facet,
            inst=ifc.createIfcTaskType(PredefinedType="USERDEFINED", ProcessType="TASKY"),
            expected=True,
        )

        facet = Entity(name="IFCWALL", predefinedType="USERDEFINED")
        ifc = ifcopenshell.file()
        run(
            "A predefined type must always specify a meaningful type, not USERDEFINED itself",
            facet=facet,
            inst=ifc.createIfcWall(PredefinedType="USERDEFINED", ObjectType="WALDO"),
            expected=False,
        )

        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType", predefined_type="X")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        facet = Entity(name="IFCWALL", predefinedType="X")
        run("Inherited predefined types should pass", facet=facet, inst=wall, expected=True)

        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="X")
        wall_type = ifcopenshell.api.run(
            "root.create_entity", ifc, ifc_class="IfcWallType", predefined_type="NOTDEFINED"
        )
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        facet = Entity(name="IFCWALL", predefinedType="X")
        run("Overridden predefined types should pass", facet=facet, inst=wall, expected=True)

        restriction = Restriction(options=["IFCWALL", "IFCSLAB"], type="enumeration")
        facet = Entity(name=restriction)
        ifc = ifcopenshell.file()
        run("Entities can be specified as an enumeration 1/3", facet=facet, inst=ifc.createIfcWall(), expected=True)
        ifc = ifcopenshell.file()
        run("Entities can be specified as an enumeration 2/3", facet=facet, inst=ifc.createIfcSlab(), expected=True)
        ifc = ifcopenshell.file()
        run("Entities can be specified as an enumeration 3/3", facet=facet, inst=ifc.createIfcBeam(), expected=False)

        restriction = Restriction(options="IFC.*TYPE", type="pattern")
        facet = Entity(name=restriction)
        ifc = ifcopenshell.file()
        run(
            "Entities can be specified as a XSD regex pattern 1/2",
            facet=facet,
            inst=ifc.createIfcWall(),
            expected=False,
        )
        ifc = ifcopenshell.file()
        run(
            "Entities can be specified as a XSD regex pattern 2/2",
            facet=facet,
            inst=ifc.createIfcWallType(),
            expected=True,
        )

        restriction = Restriction(options="FOO.*", type="pattern")
        facet = Entity(name="IFCWALL", predefinedType=restriction)
        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="FOOBAR")
        run("Restrictions an be specified for the predefined type 1/3", facet=facet, inst=wall, expected=True)
        ifc = ifcopenshell.file()
        wall2 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="FOOBAZ")
        run("Restrictions an be specified for the predefined type 2/3", facet=facet, inst=wall2, expected=True)
        ifc = ifcopenshell.file()
        wall3 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall", predefined_type="BAZFOO")
        run("Restrictions an be specified for the predefined type 3/3", facet=facet, inst=wall3, expected=False)


class TestAttribute:
    def test_creating_an_attribute_facet(self):
        attribute = Attribute(name="name")
        assert attribute.asdict() == {"name": {"simpleValue": "name"}}
        attribute = Attribute(name="name", value="value")
        assert attribute.asdict() == {"name": {"simpleValue": "name"}, "value": {"simpleValue": "value"}}
        attribute = Attribute(
            name="name", value="value", minOccurs="0", maxOccurs="unbounded", instructions="instructions"
        )
        assert attribute.asdict() == {
            "name": {"simpleValue": "name"},
            "value": {"simpleValue": "value"},
            "@minOccurs": "0",
            "@maxOccurs": "unbounded",
            "@instructions": "instructions",
        }

    def test_filtering_using_an_attribute_facet(self):
        set_facet("attribute")

        ifc = ifcopenshell.file()
        facet = Attribute(name="Foobar")
        run("Invalid attribute names always fail", facet=facet, inst=ifc.createIfcWall(), expected=False)

        ifc = ifcopenshell.file()
        facet = Attribute(name="Name")
        run(
            "Attributes with a string value should pass",
            facet=facet,
            inst=ifc.createIfcWall(Name="Foobar"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run("Attributes with null values always fail", facet=facet, inst=ifc.createIfcWall(), expected=False)
        # The logic is that unfortunately most BIM users cannot differentiate between the two.
        ifc = ifcopenshell.file()
        run("Attributes with empty strings always fail", facet=facet, inst=ifc.createIfcWall(Name=""), expected=False)

        facet = Attribute(name="CountValue")
        ifc = ifcopenshell.file()
        run(
            "Attributes with a zero number have meaning and should pass",
            facet=facet,
            inst=ifc.createIfcQuantityCount(Name="Foobar", CountValue=0),
            expected=True,
        )

        facet = Attribute(name="IsCritical")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTaskTime(IsCritical=True)
        run("Attributes with a boolean true should pass", facet=facet, inst=element, expected=True)
        element.IsCritical = False
        run("Attributes with a boolean false should pass", facet=facet, inst=element, expected=True)

        facet = Attribute(name="RelatingPriorities")
        ifc = ifcopenshell.file()
        run(
            "Attributes with an empty list always fail",
            facet=facet,
            inst=ifc.createIfcRelConnectsPathElements(
                RelatingElement=ifc.createIfcWall(),
                RelatedElement=ifc.createIfcWall(),
                RelatingPriorities=[],
                RelatedPriorities=[],
                RelatedConnectionType="ATSTART",
                RelatingConnectionType="ATEND",
            ),
            expected=False,
        )

        facet = Attribute(name="LayerStyles")
        ifc = ifcopenshell.file()
        item = ifc.createIfcCartesianPoint([0.0, 0.0, 0.0])
        layer = ifc.createIfcPresentationLayerWithStyle("Foo", None, [item], None, True, False, False, [])
        run("Attributes with an empty set always fail", facet=facet, inst=layer, expected=False)

        layer.LayerOn = "UNKNOWN"
        facet = Attribute(name="LayerOn")
        run("Attributes with a logical unknown always fail", facet=facet, inst=layer, expected=False)

        facet = Attribute(name="ScheduleDuration")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTaskTime(ScheduleDuration="P0D")
        run("Attributes with a zero duration should pass", facet=facet, inst=element, expected=True)

        facet = Attribute(name="TaskTime")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTask(IsMilestone=True, TaskTime=ifc.createIfcTaskTime())
        run("Attributes referencing an object should pass", facet=facet, inst=element, expected=True)

        facet = Attribute(name="DiffuseColour")
        ifc = ifcopenshell.file()
        rgb = ifc.createIfcColourRgb(None, 1, 1, 1)
        run(
            "Attributes with a select referencing an object should pass",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRendering(
                SurfaceColour=rgb, ReflectanceMethod="FLAT", DiffuseColour=ifc.createIfcColourRgb(None, 1, 1, 1)
            ),
            expected=True,
        )

        ifc = ifcopenshell.file()
        rgb = ifc.createIfcColourRgb(None, 1, 1, 1)
        run(
            "Attributes with a select referencing a primitive should pass",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRendering(
                SurfaceColour=rgb, ReflectanceMethod="FLAT", DiffuseColour=ifc.createIfcNormalisedRatioMeasure(0.5)
            ),
            expected=True,
        )

        ifc = ifcopenshell.file()
        facet = Attribute(name="EngagedIn")
        person = ifc.createIfcPerson()
        organisation = ifc.createIfcOrganization(Name="Foo")
        ifc.createIfcPersonAndOrganization(ThePerson=person, TheOrganization=organisation)
        run("Inverse attributes cannot be checked and always fail", facet=facet, inst=person, expected=False)

        ifc = ifcopenshell.file()
        facet = Attribute(name="Dim")
        run(
            "Derived attributes cannot be checked and always fail",
            facet=facet,
            inst=ifc.createIfcCartesianPoint([0.0, 0.0, 0.0]),
            expected=False,
        )

        facet = Attribute(name="Name", value="Foobar")
        ifc = ifcopenshell.file()
        run(
            "Attributes should check strings case sensitively 1/2",
            facet=facet,
            inst=ifc.createIfcWall(Name="Foobar"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Attributes should check strings case sensitively 2/2",
            facet=facet,
            inst=ifc.createIfcWall(Name="foobar"),
            expected=False,
        )

        ifc = ifcopenshell.file()
        facet = Attribute(name="Name", value="♫")
        run(
            "Non-ascii characters are treated without encoding",
            facet=facet,
            inst=ifc.createIfcWall(Name="♫"),
            expected=True,
        )

        facet = Attribute(name="TaskTime", value="Foobar")
        ifc = ifcopenshell.file()
        run(
            "Value checks always fail for objects",
            facet=facet,
            inst=ifc.createIfcTask(IsMilestone=False, TaskTime=ifc.createIfcTaskTime()),
            expected=False,
        )

        facet = Attribute(name="DiffuseColour", value="Foobar")
        ifc = ifcopenshell.file()
        rgb = ifc.createIfcColourRgb(None, 1, 1, 1)
        run(
            "Value checks always fail for selects",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRendering(
                SurfaceColour=rgb, ReflectanceMethod="FLAT", DiffuseColour=ifc.createIfcNormalisedRatioMeasure(0.5)
            ),
            expected=False,
        )

        facet = Attribute(name="Coordinates", value="Foobar")
        ifc = ifcopenshell.file()
        run(
            "Value checks always fail for lists",
            facet=facet,
            inst=ifc.createIfcCartesianPoint([0.0, 0.0, 0.0]),
            expected=False,
        )

        # TODO continue from here

        global_id = ifcopenshell.guid.new()
        facet = Attribute(name="GlobalId", value=global_id)
        ifc = ifcopenshell.file()
        run(
            "GlobalIds are treated as strings and not expanded",
            facet=facet,
            inst=ifc.createIfcWall(GlobalId=global_id),
            expected=True,
        )

        # 255 characters
        identifier = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345"
        facet = Attribute(name="Identification", value=identifier + "_extra_characters")
        ifc = ifcopenshell.file()
        run(
            "IDS does not handle string truncation such as for identifiers",
            facet=facet,
            inst=ifc.createIfcPerson(Identification=identifier),
            expected=False,
        )

        facet = Attribute(name="RefractionIndex", value="42")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 1/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="42.")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 2/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="42.0")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 3/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.0),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="42")
        ifc = ifcopenshell.file()
        run(
            "Numeric values are checked using type casting 4/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.3),
            expected=False,
        )
        facet = Attribute(name="RefractionIndex", value="42,3")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 1/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42.3),
            expected=False,
        )
        facet = Attribute(name="RefractionIndex", value="123,4.5")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 2/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=1234.5),
            expected=False,
        )
        facet = Attribute(name="RefractionIndex", value="1.2345e3")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 3/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=1234.5),
            expected=True,
        )
        facet = Attribute(name="RefractionIndex", value="1.2345E3")
        ifc = ifcopenshell.file()
        run(
            "Only specifically formatted numbers are allowed 4/4",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=1234.5),
            expected=True,
        )

        facet = Attribute(name="NumberOfRisers", value="42")
        ifc = ifcopenshell.file()
        run(
            "Integers follow the same rules as numbers",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )
        facet = Attribute(name="NumberOfRisers", value="42.0")
        ifc = ifcopenshell.file()
        run(
            "Integers follow the same rules as numbers 2/2",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )

        facet = Attribute(name="NumberOfRisers", value="42.3")
        ifc = ifcopenshell.file()
        run(
            "Integers are always floored when cast 1/2",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )
        facet = Attribute(name="NumberOfRisers", value="42.7")
        ifc = ifcopenshell.file()
        run(
            "Integers are always floored when cast 2/2",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )

        facet = Attribute(name="NumberOfRisers", value="42.7")
        ifc = ifcopenshell.file()
        run(
            "Integers are always floored when cast 2/2",
            facet=facet,
            inst=ifc.createIfcStairFlight(NumberOfRisers=42),
            expected=True,
        )

        facet = Attribute(name="IsMilestone", value="TRUE")
        ifc = ifcopenshell.file()
        element = ifc.createIfcTask(IsMilestone=False)
        run("Booleans must be specified as uppercase strings 1/3", facet=facet, inst=element, expected=False)
        facet = Attribute(name="IsMilestone", value="FALSE")
        run("Booleans must be specified as uppercase strings 2/3", facet=facet, inst=element, expected=True)
        facet = Attribute(name="IsMilestone", value="False")
        run("Booleans must be specified as uppercase strings 2/3", facet=facet, inst=element, expected=False)

        facet = Attribute(name="EditionDate", value="2022-01-01")
        ifc = ifcopenshell.file()
        run(
            "Dates are treated as strings 1/2",
            facet=facet,
            inst=ifc.createIfcClassification(Name="Name", EditionDate="2022-01-01"),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Dates are treated as strings 1/2",
            facet=facet,
            inst=ifc.createIfcClassification(Name="Name", EditionDate="2022-01-01+00:00"),
            expected=False,
        )

        facet = Attribute(name="ScheduleDuration", value="PT16H")
        ifc = ifcopenshell.file()
        run(
            "Durations are treated as strings 1/2",
            facet=facet,
            inst=ifc.createIfcClassification(Name="Name", EditionDate="PT16H"),
            expected=False,
        )
        ifc = ifcopenshell.file()
        run(
            "Durations are treated as strings 2/2",
            facet=facet,
            inst=ifc.createIfcClassification(Name="Name", EditionDate="P2D"),
            expected=False,
        )

        restriction = Restriction(options=".*Name.*", type="pattern")
        facet = Attribute(name=restriction)
        ifc = ifcopenshell.file()
        run(
            "Name restrictions may be used 1/4",
            facet=facet,
            inst=ifc.createIfcMaterialLayerSet(
                MaterialLayers=[ifc.createIfcMaterialLayer(LayerThickness=1)], LayerSetName="Foo"
            ),
            expected=True,
        )
        ifc = ifcopenshell.file()
        run(
            "Name restrictions may be used 2/4",
            facet=facet,
            inst=ifc.createIfcMaterialConstituentSet(Name="Foo"),
            expected=True,
        )

        restriction = Restriction(options=["Name", "Description"], type="enumeration")
        facet = Attribute(name=restriction)
        ifc = ifcopenshell.file()
        run("Name restrictions may be used 3/4", facet=facet, inst=ifc.createIfcWall(Name="Foo"), expected=False)
        ifc = ifcopenshell.file()
        run(
            "Name restrictions may be used 4/4",
            facet=facet,
            inst=ifc.createIfcWall(Name="Foo", Description="Bar"),
            expected=True,
        )

        restriction = Restriction(options=["Foo", "Bar"], type="enumeration")
        facet = Attribute(name="Name", value=restriction)
        ifc = ifcopenshell.file()
        run("Value restrictions may be used 1/3", facet=facet, inst=ifc.createIfcWall(Name="Foo"), expected=True)
        ifc = ifcopenshell.file()
        run("Value restrictions may be used 2/3", facet=facet, inst=ifc.createIfcWall(Name="Bar"), expected=True)
        ifc = ifcopenshell.file()
        run("Value restrictions may be used 3/3", facet=facet, inst=ifc.createIfcWall(Name="Foobar"), expected=False)

        ifc = ifcopenshell.file()
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        wall_type.Description = "Foobar"
        run("Attributes are not inherited by the occurrence", facet=facet, inst=wall, expected=False)

        restriction = Restriction(options=["42"], type="enumeration", base="string")
        facet = Attribute(name="RefractionIndex", value=restriction)
        ifc = ifcopenshell.file()
        run(
            "Typecast checking may also occur within enumeration restrictions",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42),
            expected=True,
        )

        restriction = Restriction(options={"minInclusive": 42, "maxInclusive": 42}, type="bounds", base="decimal")
        facet = Attribute(name="RefractionIndex", value=restriction)
        ifc = ifcopenshell.file()
        run(
            "Strict numeric checking may be done with a bounds restriction",
            facet=facet,
            inst=ifc.createIfcSurfaceStyleRefraction(RefractionIndex=42),
            expected=True,
        )


class TestClassification:
    def test_creating_a_classification_facet(self):
        facet = Classification()
        assert facet.asdict() == {}
        facet = Classification(value="value", system="system")
        assert facet.asdict() == {"value": {"simpleValue": "value"}, "system": {"simpleValue": "system"}}
        facet = Classification(
            value="value",
            system="system",
            uri="https://test.com",
            minOccurs="0",
            maxOccurs="unbounded",
            instructions="instructions",
        )
        assert facet.asdict() == {
            "value": {"simpleValue": "value"},
            "system": {"simpleValue": "system"},
            "@uri": "https://test.com",
            "@minOccurs": "0",
            "@maxOccurs": "unbounded",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_classification_facet(self):
        set_facet("classification")

        library = ifcopenshell.file()
        system_a = library.createIfcClassification(Name="Foobar")
        ref1 = library.createIfcClassificationReference(Identification="1", ReferencedSource=system_a)
        ref11 = library.createIfcClassificationReference(Identification="11", ReferencedSource=ref1)
        ref2 = library.createIfcClassificationReference(Identification="2", ReferencedSource=system_a)
        ref22 = library.createIfcClassificationReference(Identification="22", ReferencedSource=ref2)
        system_b = library.createIfcClassification(Name="Foobaz")
        refx = library.createIfcClassificationReference(Identification="X", ReferencedSource=system_b)

        ifc = ifcopenshell.file()
        project = ifc.createIfcProject()
        system_a = ifcopenshell.api.run("classification.add_classification", ifc, classification=system_a)
        element0 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        element1 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=element1, reference=ref1, classification=system_a
        )
        element11 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=element11, reference=ref11, classification=system_a
        )
        element22 = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run(
            "classification.add_reference",
            ifc,
            product=element22,
            reference=ref22,
            classification=system_a,
            is_lightweight=False,
        )

        facet = Classification()
        run(
            "A classification facet with no data matches any classification 1/2",
            facet=facet,
            inst=element0,
            expected=False,
        )
        run(
            "A classification facet with no data matches any classification 2/2",
            facet=facet,
            inst=element1,
            expected=True,
        )

        facet = Classification(value="1")
        run(
            "Values should match exactly if lightweight classifications are used",
            facet=facet,
            inst=element1,
            expected=True,
        )

        facet = Classification(value="2")
        run(
            "Values match subreferences if full classifications are used (e.g. EF_25_10 should match EF_25_10_25, EF_25_10_30, etc)",
            facet=facet,
            inst=element22,
            expected=True,
        )

        facet = Classification(system="Foobar")
        run("Systems should match exactly 1/5", facet=facet, inst=project, expected=True)
        run("Systems should match exactly 2/5", facet=facet, inst=element0, expected=False)
        run("Systems should match exactly 3/5", facet=facet, inst=element1, expected=True)
        run("Systems should match exactly 4/5", facet=facet, inst=element11, expected=True)
        run("Systems should match exactly 5/5", facet=facet, inst=element22, expected=True)

        restriction = Restriction(options="1.*", type="pattern")
        facet = Classification(value=restriction)
        run("Restrictions can be used for values 1/3", facet=facet, inst=element1, expected=True)
        run("Restrictions can be used for values 2/3", facet=facet, inst=element11, expected=True)
        run("Restrictions can be used for values 3/3", facet=facet, inst=element22, expected=False)

        restriction = Restriction(options="Foo.*", type="pattern")
        facet = Classification(system=restriction)
        run("Restrictions can be used for systems 1/2", facet=facet, inst=element0, expected=False)
        run("Restrictions can be used for systems 2/2", facet=facet, inst=element1, expected=True)

        facet = Classification(system="Foobar", value="1")
        run(
            "Both system and value must match (all, not any) if specified 1/2",
            facet=facet,
            inst=element1,
            expected=True,
        )
        run(
            "Both system and value must match (all, not any) if specified 2/2",
            facet=facet,
            inst=element11,
            expected=False,
        )

        # IFC doesn't yet formally specify how inheritance and overrides work here. We follow these rules:
        # https://github.com/buildingSMART/IFC4.3.x-development/issues/475
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall, reference=ref11, classification=system_a
        )
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall_type, reference=ref22, classification=system_a
        )

        system_b = ifcopenshell.api.run("classification.add_classification", ifc, classification=system_b)
        ifcopenshell.api.run(
            "classification.add_reference", ifc, product=wall_type, reference=refx, classification=system_b
        )

        facet = Classification(value="11")
        run("Occurrences override the type classification per system 1/3", facet=facet, inst=wall, expected=True)
        facet = Classification(value="22")
        run("Occurrences override the type classification per system 2/3", facet=facet, inst=wall, expected=False)
        facet = Classification(value="X")
        run("Occurrences override the type classification per system 3/3", facet=facet, inst=wall, expected=True)


class TestProperty:
    def test_creating_a_property_facet(self):
        facet = Property()
        assert facet.asdict() == {
            "propertySet": {"simpleValue": "Property_Set"},
            "name": {"simpleValue": "PropertyName"},
        }
        facet = Property(
            propertySet="propertySet",
            name="name",
            value="value",
            measure="String",
            uri="https://test.com",
            minOccurs="0",
            maxOccurs="unbounded",
            instructions="instructions",
        )
        assert facet.asdict() == {
            "propertySet": {"simpleValue": "propertySet"},
            "name": {"simpleValue": "name"},
            "value": {"simpleValue": "value"},
            "@measure": "String",
            "@uri": "https://test.com",
            "@minOccurs": "0",
            "@maxOccurs": "unbounded",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_property_facet(self):
        set_facet("property")

        ifc = ifcopenshell.file()
        ifc.createIfcProject()
        # Milli prefix used to check measurement conversions
        lengthunit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
        areaunit = ifcopenshell.api.run(
            "unit.add_si_unit", ifc, unit_type="AREAUNIT", name="SQUARE_METRE", prefix="MILLI"
        )
        volumeunit = ifcopenshell.api.run(
            "unit.add_si_unit", ifc, unit_type="VOLUMEUNIT", name="CUBIC_METRE", prefix="MILLI"
        )
        timeunit = ifcopenshell.api.run("unit.add_si_unit", ifc, unit_type="TIMEUNIT", name="SECOND")
        ifcopenshell.api.run("unit.assign_unit", ifc, units=[lengthunit, areaunit, volumeunit, timeunit])

        # A name check by itself only checks that a property is non-null and non empty string
        # The logic is that unfortunately most BIM users cannot differentiate between the two.
        facet = Property(propertySet="Foo_Bar", name="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        run("", facet=facet, inst=element, expected=False)
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": None})
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        run("", facet=facet, inst=element, expected=True)

        # A simple value checks an exact case-sensitive match
        facet = Property(propertySet="Foo_Bar", name="Foo", value="Bar")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        run("", facet=facet, inst=element, expected=True)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Baz"})
        run("", facet=facet, inst=element, expected=False)

        # Simple values only check string matches
        facet = Property(propertySet="Foo_Bar", name="Foo", value="1")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "1"})
        run("", facet=facet, inst=element, expected=True)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": ifc.createIfcInteger(1)})
        run("", facet=facet, inst=element, expected=False)

        # Restrictions are supported for property sets. If multiple are matched, all must satisfy requirements.
        restriction = Restriction(options="Foo_.*", type="pattern")
        facet = Property(propertySet=restriction, name="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        run("", facet=facet, inst=element, expected=True)
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Baz")
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        run("", facet=facet, inst=element, expected=True)

        # Restrictions are supported for names. If multiple are matched, all must satisfy requirements.
        restriction = Restriction(options="Foo.*", type="pattern")
        facet = Property(propertySet="Foo_Bar", name=restriction, value="x")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": "x"})
        run("", facet=facet, inst=element, expected=True)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "x"})
        run("", facet=facet, inst=element, expected=True)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "y"})
        run("", facet=facet, inst=element, expected=False)

        # Restrictions are supported for values. If multiple are matched, all must satisfy requirements.
        restriction1 = Restriction(options="Foo.*", type="pattern")
        restriction2 = Restriction(options=["x", "y"], type="enumeration")
        facet = Property(propertySet="Foo_Bar", name=restriction1, value=restriction2)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "y"})
        run("", facet=facet, inst=element, expected=True)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": "x", "Foobaz": "z"})
        run("", facet=facet, inst=element, expected=False)

        # Restrictions may be used to check basic data primitives
        restriction = Restriction(options=[42.12], type="enumeration", base="decimal")
        facet = Property(propertySet="Foo_Bar", name="Foobar", value=restriction)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": 42.12})
        run("", facet=facet, inst=element, expected=True)
        restriction = Restriction(options=[42], type="enumeration", base="integer")
        facet = Property(propertySet="Foo_Bar", name="Foobar", value=restriction)
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": 42})
        run("", facet=facet, inst=element, expected=True)
        restriction = Restriction(options=[True], type="enumeration", base="boolean")
        facet = Property(propertySet="Foo_Bar", name="Foobar", value=restriction)
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": True})
        run("", facet=facet, inst=element, expected=True)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": False})
        run("", facet=facet, inst=element, expected=False)

        # When measure is not specified, no unit conversion is done and only primitives are checked
        restriction = Restriction(options=[42.12], type="enumeration", base="decimal")
        facet = Property(propertySet="Foo_Bar", name="Foobar", value=restriction)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foobar": 42.12})
        run("", facet=facet, inst=element, expected=True)

        # Measure may be used to specify an IFC data type
        restriction = Restriction(options=[2], type="enumeration", base="decimal")
        facet = Property(propertySet="Foo_Bar", name="Foo", value=restriction, measure="Time")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": ifc.createIfcMassMeasure(2)})
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": ifc.createIfcTimeMeasure(2)})
        run("", facet=facet, inst=element, expected=True)

        # Measure also implies that a unit matters, and so a conversion shall take place to SI units
        restriction = Restriction(options=[2], type="enumeration", base="decimal")
        facet = Property(propertySet="Foo_Bar", name="Foo", value=restriction, measure="Length")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": ifc.createIfcLengthMeasure(2)})
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": ifc.createIfcLengthMeasure(2000)})
        run("", facet=facet, inst=element, expected=True)

        # The facet checks inherited properties from the type
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=wall_type, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        facet = Property(propertySet="Foo_Bar", name="Foo")
        run("", facet=facet, inst=wall, expected=True)
        run("", facet=facet, inst=wall_type, expected=True)

        # The facet checks overriden properties from the occurrence
        wall = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        wall_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=wall, relating_type=wall_type)
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=wall_type, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Baz"})
        pset = ifcopenshell.api.run("pset.add_pset", ifc, product=wall, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", ifc, pset=pset, properties={"Foo": "Bar"})
        facet = Property(propertySet="Foo_Bar", name="Foo", value="Bar")
        run("", facet=facet, inst=wall, expected=True)
        run("", facet=facet, inst=wall_type, expected=False)


class TestMaterial:
    def test_creating_a_material_facet(self):
        facet = Material()
        assert facet.asdict() == {}
        facet = Material(
            value="value", uri="https://test.com", minOccurs="0", maxOccurs="unbounded", instructions="instructions"
        )
        assert facet.asdict() == {
            "value": {"simpleValue": "value"},
            "@uri": "https://test.com",
            "@minOccurs": "0",
            "@maxOccurs": "unbounded",
            "@instructions": "instructions",
        }

    def test_filtering_using_a_material_facet(self):
        set_facet("material")

        facet = Material()
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        run("Elements without a material always fail", facet=facet, inst=element, expected=False)
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material)
        run("Elements with any material will pass an empty material facet", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material)
        run("Material with no data will fail a value check", facet=facet, inst=element, expected=False)
        material.Name = "Foo"
        run("A material name may pass the value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("A material category may pass the value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.run("material.add_material_set", ifc, set_type="IfcMaterialList")
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material_set)
        run("A material list with no data will fail a value check", facet=facet, inst=element, expected=False)
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.add_list_item", ifc, material_list=material_set, material=material)
        material.Name = "Foo"
        run("Any material Name in a list will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("Any material Category in a list will pass a value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.run("material.add_material_set", ifc, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material_set)
        material = ifcopenshell.api.run("material.add_material", ifc)
        layer = ifcopenshell.api.run("material.add_layer", ifc, layer_set=material_set, material=material)
        layer.Name = "Foo"
        run("Any layer Name in a layer set will pass a value check", facet=facet, inst=element, expected=True)
        layer.Name = "Bar"
        layer.Category = "Foo"
        run("Any layer Category in a layer set will pass a value check", facet=facet, inst=element, expected=True)
        layer.Category = "Bar"
        material.Name = "Foo"
        run("Any material Name in a layer set will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("Any material Category in a layer set will pass a value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.run("material.add_material_set", ifc, set_type="IfcMaterialProfileSet")
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material_set)
        material = ifcopenshell.api.run("material.add_material", ifc)
        profile = ifcopenshell.api.run("material.add_profile", ifc, profile_set=material_set, material=material)
        profile.Name = "Foo"
        profile.Profile = ifc.createIfcCircleProfileDef("AREA", None, None, 1)
        run("Any profile Name in a profile set will pass a value check", facet=facet, inst=element, expected=True)
        profile.Name = "Bar"
        profile.Category = "Foo"
        run("Any profile Category in a profile set will pass a value check", facet=facet, inst=element, expected=True)
        profile.Category = "Bar"
        material.Name = "Foo"
        run("Any material Name in a profile set will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run("Any material category in a profile set will pass a value check", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        facet = Material(value="Foo")
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        material_set = ifcopenshell.api.run("material.add_material_set", ifc, set_type="IfcMaterialConstituentSet")
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material_set)
        run("A constituent set with no data will fail a value check", facet=facet, inst=element, expected=False)
        material = ifcopenshell.api.run("material.add_material", ifc)
        constituent = ifcopenshell.api.run(
            "material.add_constituent", ifc, constituent_set=material_set, material=material
        )
        constituent.Name = "Foo"
        run(
            "Any constituent Name in a constituent set will pass a value check",
            facet=facet,
            inst=element,
            expected=True,
        )
        constituent.Name = "Bar"
        constituent.Category = "Foo"
        run(
            "Any constituent Category in a constituent set will pass a value check",
            facet=facet,
            inst=element,
            expected=True,
        )
        constituent.Category = "Bar"
        material.Name = "Foo"
        run("Any material Name in a constituent set will pass a value check", facet=facet, inst=element, expected=True)
        material.Name = "Bar"
        material.Category = "Foo"
        run(
            "Any material Category in a constituent set will pass a value check",
            facet=facet,
            inst=element,
            expected=True,
        )

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=element, relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.assign_material", ifc, product=element_type, material=material)
        material.Name = "Foo"
        facet = Material(value="Foo")
        run("Occurrences can inherit materials from their types", facet=facet, inst=element, expected=True)

        ifc = ifcopenshell.file()
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", ifc, related_object=element, relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.assign_material", ifc, product=element_type, material=material)
        material.Name = "Bar"
        material = ifcopenshell.api.run("material.add_material", ifc)
        ifcopenshell.api.run("material.assign_material", ifc, product=element, material=material)
        material.Name = "Foo"
        facet = Material(value="Foo")
        run("Occurrences can override materials from their types", facet=facet, inst=element, expected=True)


class TestPartOf:
    def test_creating_a_partof_facet(self):
        facet = PartOf()
        assert facet.asdict() == {"@entity": "IfcSystem"}
        facet = PartOf(entity="IfcGroup")
        assert facet.asdict() == {"@entity": "IfcGroup"}

    def test_filtering_using_a_partof_facet(self):
        ifc = ifcopenshell.file()

        # An IfcElementAssembly entity only passes those who are part of an assembly
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcWall")
        ifcopenshell.api.run("aggregate.assign_object", ifc, product=subelement, relating_object=element)
        facet = PartOf(entity="IfcElementAssembly")
        run("", facet=facet, inst=element, expected=False)
        run("", facet=facet, inst=subelement, expected=True)

        # An IfcElementAssembly strictly checks that the whole is an IfcElementAssembly class
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSlab")
        subelement = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", ifc, product=subelement, relating_object=element)
        facet = PartOf(entity="IfcElementAssembly")
        run("", facet=facet, inst=subelement, expected=False)

        # A nested subelement still passes so long as one of its parents is an IfcElementAssembly
        # TODO nononono
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSlab")
        subsubelement = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", ifc, product=subelement, relating_object=element)
        ifcopenshell.api.run("aggregate.assign_object", ifc, product=subsubelement, relating_object=subelement)
        facet = PartOf(entity="IfcElementAssembly")
        run("", facet=facet, inst=subsubelement, expected=True)

        # An IfcGroup only checks that a group is assigned without any other logic
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcElementAssembly")
        group = ifcopenshell.api.run("group.add_group", ifc)
        facet = PartOf(entity="IfcGroup")
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("group.assign_group", ifc, product=[element], group=group)
        run("", facet=facet, inst=element, expected=True)

        # An IfcGroup can be passed by subtypes
        # TODO: wrong, subtypes should not be matched
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcElementAssembly")
        group = ifc.createIfcInventory()
        facet = PartOf(entity="IfcGroup")
        ifcopenshell.api.run("group.assign_group", ifc, product=[element], group=group)
        run("", facet=facet, inst=element, expected=True)

        # An IfcSystem only checks that a system is assigned without any other logic
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcElementAssembly")
        system = ifcopenshell.api.run("system.add_system", ifc)
        facet = PartOf(entity="IfcSystem")
        run("", facet=facet, inst=element, expected=False)
        ifcopenshell.api.run("system.assign_system", ifc, product=element, system=system)
        run("", facet=facet, inst=element, expected=True)

        # An IfcSystem allows subtypes
        # TODO: wrong, subtypes should not be matched
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcElementAssembly")
        system = ifcopenshell.api.run("system.add_system", ifc, ifc_class="IfcDistributionSystem")
        ifcopenshell.api.run("system.assign_system", ifc, product=element, system=system)
        facet = PartOf(entity="IfcSystem")
        run("", facet=facet, inst=element, expected=True)


class TestRestriction:
    def test_enumeration(self):
        restriction = Restriction(options=["foo", "bar"], type="enumeration")
        assert restriction == "foo"
        assert restriction == "bar"
        assert restriction != "baz"

    def test_bounds(self):
        restriction = Restriction(options={"minInclusive": 0, "maxExclusive": 10}, type="bounds", base="integer")
        assert restriction == 0
        assert restriction != 10
        assert restriction == 5
        assert restriction != -1

    def test_pattern(self):
        restriction = Restriction(options="[A-Z]{2}[0-9]{2}", type="pattern")
        assert restriction == "AB01"
        assert restriction != "AB"
        assert restriction != "01"
