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
        assert bpy.context.scene.BIMRootProperties.contexts == str(context.id())


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
        assert bpy.context.scene.BIMRootProperties.contexts == str(body.id())


class TestSetDefaultModelingDimensions(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifc.createIfcProject()
        ifcopenshell.api.run("unit.assign_unit", ifc)
        subject.set_default_modeling_dimensions()
        props = bpy.context.scene.BIMModelProperties
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
