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

import bpy
import ifcopenshell
import ifcopenshell.api.document
import ifcopenshell.api.root
import bonsai.core.tool
import bonsai.tool as tool
import tempfile
from test.bim.bootstrap import NewFile
from bonsai.tool.project import Project as subject
from pathlib import Path


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Project)


class TestAppendAllTypesFromTemplate(NewFile):
    def test_nothing(self):
        # TODO refactor
        pass


class TestCreateEmpty(NewFile):
    def test_run(self):
        subject.create_empty("Foobar")
        assert bpy.data.objects.get("Foobar")
        assert not bpy.data.objects.get("Foobar").data


class TestLoadDefaultThumbnails(NewFile):
    def test_nothing(self):
        pass  # Not possible to test this headlessly


class TestRunAggregateAssignObject(NewFile):
    def test_nothing(self):
        pass


class TestRunContextAddContext(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerAddOrganisation(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerAddPerson(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerAddPersonAndOrganisation(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerSetUser(NewFile):
    def test_nothing(self):
        pass


class TestRunAssignClass(NewFile):
    def test_nothing(self):
        pass


class TestRunUnitAssignSceneUnits(NewFile):
    def test_nothing(self):
        pass


class TestSetContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        subject.set_context(context)
        rprops = tool.Root.get_root_props()
        assert rprops.contexts == str(context.id())


class TestSetDefaultContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcProject()
        model = ifcopenshell.api.run("context.add_context", ifc, context_type="Model")
        body = ifcopenshell.api.run(
            "context.add_context",
            ifc,
            parent=model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
        )
        subject.set_default_context()
        rprops = tool.Root.get_root_props()
        assert rprops.contexts == str(body.id())


class TestSetDefaultModelingDimensions(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcProject()
        ifcopenshell.api.run("unit.assign_unit", ifc)
        subject.set_default_modeling_dimensions()
        props = tool.Model.get_model_props()
        assert props.extrusion_depth == 3
        assert props.length == 1
        assert props.rl1 == 0
        assert props.rl2 == 1
        assert props.x == 0.5
        assert props.y == 0.5
        assert props.z == 0.5


class PreserveFileContents:
    original_content: str
    filepath: Path

    def __init__(self, filepath: Path):
        self.filepath = filepath

    def __enter__(self):
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            open(self.filepath, "w").close()  # touch.

        with open(self.filepath, "r") as file:
            self.original_content = file.read()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        with open(self.filepath, "w") as file:
            file.write(self.original_content)


class TestRecentIFCProjects(NewFile):
    def test_get_recent_ifc_projects_path(self):
        assert subject.get_recent_ifc_projects_path().name == "recent-ifc-projects.txt"

    def test_clear_recent_ifc_projects(self):
        filepath = subject.get_recent_ifc_projects_path()
        with PreserveFileContents(filepath):
            with open(filepath, "w") as fo:
                fo.write(tempfile.NamedTemporaryFile(suffix=".ifc").name)

            assert filepath.stat().st_size != 0
            subject.clear_recent_ifc_projects()
            assert filepath.stat().st_size == 0

    def test_get_write_recent_ifc_projects(self):
        filepath = subject.get_recent_ifc_projects_path()
        with PreserveFileContents(filepath):
            subject.clear_recent_ifc_projects()
            assert filepath.stat().st_size == 0

            projects: list[Path] = []
            for _ in range(3):
                ifc_file = Path(tempfile.NamedTemporaryFile(suffix=".ifc").name)
                open(ifc_file, "w").close()
                projects.append(ifc_file)

            subject.write_recent_ifc_projects(projects)
            assert filepath.stat().st_size != 0
            assert subject.get_recent_ifc_projects() == projects
            with open(filepath) as fi:
                contents = fi.read()
            assert contents == "\n".join(str(p) for p in projects)

    def test_add_recent_ifc_project(self):
        filepath = subject.get_recent_ifc_projects_path()
        with PreserveFileContents(filepath):
            subject.clear_recent_ifc_projects()
            assert filepath.stat().st_size == 0
            ifc_file = Path(tempfile.NamedTemporaryFile(suffix=".ifc").name)
            subject.add_recent_ifc_project(ifc_file)
            assert filepath.stat().st_size != 0
            assert subject.get_recent_ifc_projects() == [ifc_file]


class TestLoadProject(NewFile):
    def test_load_project_and_start_fresh_sesion(self):
        filepath = Path("test/files/basic.ifc")
        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.object
        assert monkey
        bpy.ops.bim.load_project(filepath=filepath.as_posix())
        assert tool.Ifc.get()
        assert not tool.Blender.is_valid_data_block(monkey)

    def test_load_project_without_starting_fresh_sesion(self):
        filepath = Path("test/files/basic.ifc")
        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.object
        assert monkey
        bpy.ops.bim.load_project(filepath=filepath.as_posix(), should_start_fresh_session=False)
        assert tool.Ifc.get()
        assert tool.Blender.is_valid_data_block(monkey)

    def test_load_project_without_ifc_data(self):
        filepath = Path("test/files/basic.ifc")
        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.object
        assert monkey
        bpy.ops.bim.load_project(filepath=filepath.as_posix(), import_without_ifc_data=True)
        assert not tool.Ifc.get()
        assert bpy.data.objects["IfcWall/Wall"]
        assert not tool.Blender.is_valid_data_block(monkey)

    def test_load_project_without_ifc_data_and_restarting_session(self):
        filepath = Path("test/files/basic.ifc")
        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.object
        assert monkey
        bpy.ops.bim.load_project(
            filepath=filepath.as_posix(), import_without_ifc_data=True, should_start_fresh_session=False
        )
        assert not tool.Ifc.get()
        assert bpy.data.objects["IfcWall/Wall"]
        assert tool.Blender.is_valid_data_block(monkey)


class TestLoadLinkedModels(NewFile):
    def test_load_linked_models_no_document(self):
        props = tool.Project.get_project_props()
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        subject.load_linked_models_from_ifc()
        assert len(props.links) == 0

    def test_load_linked_models_document_no_references(self):
        ifc = ifcopenshell.file()
        props = tool.Project.get_project_props()
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        document = ifcopenshell.api.document.add_information(ifc)
        document.Name = "BBIM_Linked_Models"
        tool.Ifc.set(ifc)
        subject.load_linked_models_from_ifc()
        assert len(props.links) == 0

    def test_load_linked_models_document_with_references(self):
        ifc = ifcopenshell.file()
        props = tool.Project.get_project_props()
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        document = ifcopenshell.api.document.add_information(ifc)
        document.Name = "BBIM_Linked_Models"
        reference = ifcopenshell.api.document.add_reference(ifc, document)
        linked_model_path = "test.ifc"
        reference.Location = linked_model_path
        tool.Ifc.set(ifc)
        subject.load_linked_models_from_ifc()
        assert len(props.links) == 1
        assert props.links[0].name == linked_model_path


class TestSaveLinkedModelsToIfc(NewFile):
    def test_save_linked_models_to_ifc_no_links(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        subject.save_linked_models_to_ifc()
        assert len(ifc.by_type("IfcDocumentInformation")) == 0
        assert len(ifc.by_type("IfcDocumentReference")) == 0

    def test_save_linked_models_to_ifc_paths_to_add(self):
        ifc = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        props = tool.Project.get_project_props()
        link = props.links.add()
        linked_model_path = "test.ifc"
        link.name = linked_model_path
        tool.Ifc.set(ifc)
        subject.save_linked_models_to_ifc()
        assert len(documents := ifc.by_type("IfcDocumentInformation")) == 1
        assert documents[0].Name == "BBIM_Linked_Models"
        assert len(references := ifc.by_type("IfcDocumentReference")) == 1
        assert references[0].Location == linked_model_path

    def test_save_linked_models_to_ifc_already_created_references(self):
        ifc = ifcopenshell.file()
        links = tool.Project.get_project_props().links
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")

        document = ifcopenshell.api.document.add_information(ifc)
        document.Name = "BBIM_Linked_Models"
        document_id = document.id()
        reference = ifcopenshell.api.document.add_reference(ifc, document)
        linked_model_path = "test.ifc"
        reference.Location = linked_model_path
        reference_id = reference.id()

        link = links.add()
        linked_model_path = "test.ifc"
        link.name = linked_model_path
        tool.Ifc.set(ifc)
        subject.save_linked_models_to_ifc()

        # Information and references to stay intact.
        assert len(documents := ifc.by_type("IfcDocumentInformation")) == 1
        assert documents[0].id() == document_id
        assert documents[0].Name == "BBIM_Linked_Models"
        assert len(references := ifc.by_type("IfcDocumentReference")) == 1
        assert references[0].id() == reference_id
        assert references[0].Location == linked_model_path

    def test_save_linked_models_to_ifc_references_to_remove(self):
        ifc = ifcopenshell.file()
        links = tool.Project.get_project_props().links
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")

        document = ifcopenshell.api.document.add_information(ifc)
        document.Name = "BBIM_Linked_Models"
        document_id = document.id()
        reference = ifcopenshell.api.document.add_reference(ifc, document)
        linked_model_path = "test.ifc"
        reference.Location = linked_model_path

        tool.Ifc.set(ifc)
        subject.save_linked_models_to_ifc()
        links.clear()

        # Remove reference for removed link.
        assert len(documents := ifc.by_type("IfcDocumentInformation")) == 1
        assert documents[0].id() == document_id
        assert documents[0].Name == "BBIM_Linked_Models"
        assert len(ifc.by_type("IfcDocumentReference")) == 0
