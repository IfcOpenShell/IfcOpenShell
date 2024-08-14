# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import brickschema
import brickschema.persistent
from brickschema.namespaces import REF, A
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import bonsai.core.tool
import bonsai.tool as tool
from rdflib.namespace import RDF
from rdflib import Literal, URIRef, Namespace
from test.bim.bootstrap import NewFile
from bonsai.tool.brick import Brick as subject
from bonsai.tool.brick import BrickStore


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Brick)


class TestAddBrick(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        result = subject.add_brick(
            "https://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "label"
        )
        assert "https://example.org/digitaltwin#" in result
        assert list(
            BrickStore.graph.triples((URIRef(result), A, URIRef("https://brickschema.org/schema/Brick#Equipment")))
        )
        assert list(
            BrickStore.graph.triples(
                (URIRef(result), URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("label"))
            )
        )


class TestAddBrickBreadcrumb(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        subject.add_brick_breadcrumb()
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[0].name == "brick_class"
        subject.add_brick_breadcrumb()
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[1].name == "brick_class"

    def test_run_split_screen(self):
        subject.set_active_brick_class("brick_class", split_screen=True)
        subject.add_brick_breadcrumb(split_screen=True)
        assert bpy.context.scene.BIMBrickProperties.split_screen_brick_breadcrumbs[0].name == "brick_class"
        subject.add_brick_breadcrumb(split_screen=True)
        assert bpy.context.scene.BIMBrickProperties.split_screen_brick_breadcrumbs[1].name == "brick_class"


class TestAddBrickFromElement(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcChiller()
        element.Name = "Chiller"
        element.GlobalId = ifcopenshell.guid.new()
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        result = subject.add_brick_from_element(
            element, "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment"
        )
        uri = f"http://example.org/digitaltwin#{element.GlobalId}"
        assert result == uri
        assert list(
            BrickStore.graph.triples((URIRef(uri), A, URIRef("https://brickschema.org/schema/Brick#Equipment")))
        )
        assert list(
            BrickStore.graph.triples(
                (URIRef(uri), URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Chiller"))
            )
        )

    def test_run_no_element_name(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcChiller()
        element.GlobalId = ifcopenshell.guid.new()
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        result = subject.add_brick_from_element(
            element, "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment"
        )
        uri = f"http://example.org/digitaltwin#{element.GlobalId}"
        assert result == uri
        assert list(
            BrickStore.graph.triples((URIRef(uri), A, URIRef("https://brickschema.org/schema/Brick#Equipment")))
        )
        assert list(
            BrickStore.graph.triples(
                (URIRef(uri), URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("Unnamed"))
            )
        )


class TestAddBrickifcProject(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        project = ifc.createIfcProject(ifcopenshell.guid.new())
        project.Name = "My Project"
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        result = subject.add_brickifc_project("http://example.org/digitaltwin#")
        assert result == f"http://example.org/digitaltwin#{project.GlobalId}"
        brick = URIRef(result)
        assert list(BrickStore.graph.triples((brick, A, REF.ifcProject)))
        assert list(BrickStore.graph.triples((brick, REF.ifcProjectID, Literal(project.GlobalId))))
        assert list(
            BrickStore.graph.triples((brick, REF.ifcFileLocation, Literal(bpy.context.scene.BIMProperties.ifc_file)))
        )
        assert list(
            BrickStore.graph.triples(
                (brick, URIRef("http://www.w3.org/2000/01/rdf-schema#label"), Literal("My Project"))
            )
        )


class TestAddBrickifcReference(NewFile):
    def test_run(self):
        TestAddBrickifcProject().test_run()
        element = tool.Ifc.get().createIfcChiller(ifcopenshell.guid.new())
        element.Name = "Chiller"
        project = URIRef(f"http://example.org/digitaltwin#{tool.Ifc.get().by_type('IfcProject')[0].GlobalId}")
        subject.add_brickifc_reference("http://example.org/digitaltwin#foo", element, project)
        brick = URIRef("http://example.org/digitaltwin#foo")
        bnode = list(BrickStore.graph.triples((brick, A, REF.IFCReference)))
        assert list(BrickStore.graph.triples((bnode, REF.hasIfcProjectReference, URIRef(project))))
        assert list(BrickStore.graph.triples((bnode, REF.ifcGlobalID, Literal(element.GlobalId))))
        assert list(BrickStore.graph.triples((bnode, REF.ifcName, Literal(element.Name))))


class TestAddRelation(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        source = subject.add_brick(
            "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "source"
        )
        destination = subject.add_brick(
            "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "destination"
        )
        subject.add_relation(source, "https://brickschema.org/schema/Brick#feeds", destination)
        assert list(
            BrickStore.graph.triples(
                (
                    URIRef(source),
                    URIRef("https://brickschema.org/schema/Brick#feeds"),
                    URIRef(destination),
                )
            )
        )


class TestRemoveRelation(NewFile):
    def test_run(self):
        TestAddRelation().test_run()
        source, relation, destination = list(
            BrickStore.graph.triples((None, URIRef("https://brickschema.org/schema/Brick#feeds"), None))
        )[0]
        subject.remove_relation(source, relation, destination)
        assert not list(
            BrickStore.graph.triples(
                (
                    URIRef(source),
                    URIRef(relation),
                    URIRef(destination),
                )
            )
        )


class TestClearBrickBrowser(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.bricks.add()
        subject.clear_brick_browser()
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 0

    def test_run_split_screen(self):
        bpy.context.scene.BIMBrickProperties.split_screen_bricks.add()
        subject.clear_brick_browser(split_screen=True)
        assert len(bpy.context.scene.BIMBrickProperties.split_screen_bricks) == 0


class TestClearProject(NewFile):
    def test_run(self):
        BrickStore.graph = "graph"
        bpy.context.scene.BIMBrickProperties.active_brick_class == "brick_class"
        bpy.context.scene.BIMBrickProperties.split_screen_active_brick_class == "brick_class2"
        subject.clear_project()
        assert BrickStore.graph is None
        assert bpy.context.scene.BIMBrickProperties.active_brick_class == ""
        assert bpy.context.scene.BIMBrickProperties.split_screen_active_brick_class == ""


class TestExportBrickAttributes(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        brick = subject.add_brick(
            "https://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "name"
        )
        assert subject.export_brick_attributes(brick) == {
            "Identification": brick,
            "Name": "name",
        }

    def test_run_ifc2x3(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        brick = subject.add_brick(
            "https://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "name"
        )
        tool.Ifc.set(ifcopenshell.file(schema="IFC2X3"))
        assert subject.export_brick_attributes(brick) == {
            "ItemReference": brick,
            "Name": "name",
        }


class TestGetActiveBrickClass(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        assert subject.get_active_brick_class() == "brick_class"

    def test_run_split_screen(self):
        subject.set_active_brick_class("brick_class", split_screen=True)
        assert subject.get_active_brick_class(split_screen=True) == "brick_class"


class TestGetBrick(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcChiller()
        library = ifc.createIfcLibraryReference(Identification="http://example.org/digitaltwin#globalid")
        ifc.createIfcRelAssociatesLibrary(RelatedObjects=[element], RelatingLibrary=library)
        assert subject.get_brick(element) == "http://example.org/digitaltwin#globalid"

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        element = ifc.createIfcEnergyConversionDevice()
        library = ifc.createIfcLibraryReference(ItemReference="http://example.org/digitaltwin#globalid")
        ifc.createIfcRelAssociatesLibrary(RelatedObjects=[element], RelatingLibrary=library)
        assert subject.get_brick(element) == "http://example.org/digitaltwin#globalid"


class TestGetBrickClass(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcAirTerminalBox()
        assert subject.get_brick_class(element) == "https://brickschema.org/schema/Brick#TerminalUnit"


class TestGetBrickPath(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        cwd = os.path.dirname(os.path.realpath(__file__))
        assert subject.get_brick_path() == os.path.join(cwd, "..", "files", "spaces.ttl")


class TestGetBrickPathName(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        assert subject.get_brick_path_name() == "spaces.ttl"


class TestGetBrickifcProject(NewFile):
    def test_run(self):
        TestAddBrickifcProject().test_run()
        assert (
            subject.get_brickifc_project()
            == f"http://example.org/digitaltwin#{tool.Ifc.get().by_type('IfcProject')[0].GlobalId}"
        )


class TestGetConvertableBrickElements(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcAirTerminalBox()
        ifc.createIfcWall()
        assert subject.get_convertable_brick_elements() == {element}


class TestGetConvertableBrickSpaces(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcBuildingStorey()
        ifc.createIfcWall()
        assert subject.get_convertable_brick_spaces() == {element}


class TestGetConvertableBrickSystems(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcSystem()
        ifc.createIfcWall()
        assert subject.get_convertable_brick_systems() == {element}


class TestGetParentSpace(NewFile):
    def test_run(cls):
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuildingStorey")
        subelement = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSpace")
        project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject")
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[subelement], relating_object=element)
        ifcopenshell.api.run("aggregate.assign_object", ifc, products=[element], relating_object=project)
        assert subject.get_parent_space(subelement) == element
        assert subject.get_parent_space(element) is None


class TestGetElementContainer(NewFile):
    def test_nothing(cls):
        pass


class TestGetElementSystems(NewFile):
    def test_nothing(cls):
        pass


class TestGetElementFeeds(NewFile):
    def test_run(cls):
        pass


class TestGetItemClass(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        assert subject.get_item_class("https://example.org/digitaltwin#floor") == "Floor"


class TestGetLibraryBrickReference(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        library = ifc.createIfcLibraryInformation()
        reference = ifc.createIfcLibraryReference(
            Identification="http://example.org/digitaltwin#floor", ReferencedLibrary=library
        )
        assert subject.get_library_brick_reference(library, "http://example.org/digitaltwin#floor") == reference

    def test_run_ifc2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        reference = ifc.createIfcLibraryReference(ItemReference="http://example.org/digitaltwin#floor")
        library = ifc.createIfcLibraryInformation(LibraryReference=[reference])
        assert subject.get_library_brick_reference(library, "http://example.org/digitaltwin#floor") == reference


class TestGetNamespace(NewFile):
    def test_run(self):
        assert subject.get_namespace("http://example.org/digitaltwin#globalid") == "http://example.org/digitaltwin#"


class TestImportBrickClasses(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_classes("Class")
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 2
        brick = bpy.context.scene.BIMBrickProperties.bricks[0]
        assert brick.name == "Building"
        assert brick.uri == "https://brickschema.org/schema/Brick#Building"
        assert brick.total_items == 1
        assert not brick.label
        brick = bpy.context.scene.BIMBrickProperties.bricks[1]
        assert brick.name == "Location"
        assert brick.uri == "https://brickschema.org/schema/Brick#Location"
        assert brick.total_items == 1
        assert not brick.label

    def test_run_split_sccreen(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_classes("Class", split_screen=True)
        assert len(bpy.context.scene.BIMBrickProperties.split_screen_bricks) == 2
        brick = bpy.context.scene.BIMBrickProperties.split_screen_bricks[0]
        assert brick.name == "Building"
        assert brick.uri == "https://brickschema.org/schema/Brick#Building"
        assert brick.total_items == 1
        assert not brick.label
        brick = bpy.context.scene.BIMBrickProperties.split_screen_bricks[1]
        assert brick.name == "Location"
        assert brick.uri == "https://brickschema.org/schema/Brick#Location"
        assert brick.total_items == 1
        assert not brick.label


class TestImportBrickItems(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_items("Building")
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 1
        brick = bpy.context.scene.BIMBrickProperties.bricks[0]
        assert brick.name == "bldg"
        assert brick.label == "My Building"
        assert brick.uri == "https://example.org/digitaltwin#bldg"
        assert brick.total_items == 0

    def test_run_split_screen(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_items("Building", split_screen=True)
        assert len(bpy.context.scene.BIMBrickProperties.split_screen_bricks) == 1
        brick = bpy.context.scene.BIMBrickProperties.split_screen_bricks[0]
        assert brick.name == "bldg"
        assert brick.label == "My Building"
        assert brick.uri == "https://example.org/digitaltwin#bldg"
        assert brick.total_items == 0


class TestLoadBrickFile(NewFile):
    def test_run(self):
        # We stub the schema to make tests run faster
        cwd = os.path.dirname(os.path.realpath(__file__))
        BrickStore.schema = os.path.join(cwd, "..", "files", "BrickStub.ttl")

        # This is the actual test
        cwd = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(cwd, "..", "files", "spaces.ttl")
        subject.load_brick_file(filepath)
        assert BrickStore.graph
        namespaces = [(ns[0], ns[1].toPython()) for ns in BrickStore.graph.namespaces()]
        assert ("brick", "https://brickschema.org/schema/Brick#") in namespaces


class TestNewBrickFile(NewFile):
    def test_run(self):
        # We stub the schema to make tests run faster
        cwd = os.path.dirname(os.path.realpath(__file__))
        BrickStore.schema = os.path.join(cwd, "..", "files", "BrickStub.ttl")

        # This is the actual test
        subject.new_brick_file()
        assert BrickStore.graph
        namespaces = [(ns[0], ns[1].toPython()) for ns in BrickStore.graph.namespaces()]
        assert ("digitaltwin", "https://example.org/digitaltwin#") in namespaces
        assert ("brick", "https://brickschema.org/schema/Brick#") in namespaces
        assert ("rdfs", "http://www.w3.org/2000/01/rdf-schema#") in namespaces


class TestPopBrickBreadcrumb(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "bar"
        assert subject.pop_brick_breadcrumb() == "bar"
        assert len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) == 1
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[0].name == "foo"

    def test_run_split_screen(self):
        bpy.context.scene.BIMBrickProperties.split_screen_brick_breadcrumbs.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.split_screen_brick_breadcrumbs.add().name = "bar"
        assert subject.pop_brick_breadcrumb(split_screen=True) == "bar"
        assert len(bpy.context.scene.BIMBrickProperties.split_screen_brick_breadcrumbs) == 1
        assert bpy.context.scene.BIMBrickProperties.split_screen_brick_breadcrumbs[0].name == "foo"


class TestRemoveBrick(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        result = subject.add_brick(
            "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "label"
        )
        subject.remove_brick(result)
        assert not list(BrickStore.graph.triples((URIRef(result), None, None)))

    def test_run_with_bnode(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        result = subject.add_brick(
            "http://example.org/digitaltwin#", "https://brickschema.org/schema/Brick#Equipment", "label"
        )
        TestAddBrickifcProject().test_run()
        element = tool.Ifc.get().createIfcChiller(ifcopenshell.guid.new())
        element.Name = "Chiller"
        project = URIRef(f"http://example.org/digitaltwin#{tool.Ifc.get().by_type('IfcProject')[0].GlobalId}")
        subject.add_brickifc_reference(result, element, project)
        subject.remove_brick(result)
        assert not list(BrickStore.graph.triples((URIRef(result), None, None)))
        assert not list(BrickStore.graph.triples((None, REF.hasIfcProjectReference, None)))


class TestRunAssignBrickReference(NewFile):
    def test_nothing(self):
        pass


class TestRunRefreshBrickViewer(NewFile):
    def test_nothing(self):
        pass


class TestRunViewBrickClass(NewFile):
    def test_nothing(self):
        pass


class TestSelectBrowserItem(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        assert bpy.context.scene.BIMBrickProperties.active_brick_class == "brick_class"

    def test_run(self):
        subject.set_active_brick_class("brick_class", split_screen=True)
        assert bpy.context.scene.BIMBrickProperties.split_screen_active_brick_class == "brick_class"


class TestSetActiveBrickClass(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.bricks.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.bricks.add().name = "bar"
        subject.select_browser_item("namespace#bar")
        assert bpy.context.scene.BIMBrickProperties.active_brick_index == 1


class TestSerializeBrick(NewFile):
    def test_nothing(self):
        pass


class TestAddNamespace(NewFile):
    def test_run(self):
        BrickStore.graph = brickschema.persistent.VersionedGraphCollection("sqlite://")
        subject.add_namespace("digitaltwin", "http://example.org/digitaltwin")
        assert ("digitaltwin", "http://example.org/digitaltwin") in BrickStore.namespaces
