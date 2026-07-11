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

import contextlib
import json
import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.document
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcpatch
import numpy as np
from ifcpatch.recipes import Ifc2Sql

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.project import Project as subject
from test.bim.bootstrap import NewFile


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
        model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        body = ifcopenshell.api.context.add_context(
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
        ifcopenshell.api.unit.assign_unit(ifc)
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
        document.Name = "X"
        tool.Ifc.set(ifc)
        subject.load_linked_models_from_ifc()
        assert len(props.links) == 0

    def test_load_linked_models_document_with_references(self):
        ifc = ifcopenshell.file()
        props = tool.Project.get_project_props()
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        document = ifcopenshell.api.document.add_information(ifc)
        document.Scope = "LINKED_MODEL"
        reference = ifcopenshell.api.document.add_reference(ifc, document)
        reference.Location = "test.ifc"
        reference.Identification = ""
        reference2 = ifcopenshell.api.document.add_reference(ifc, document)
        reference2.Location = "test2.ifc"
        reference2.Identification = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"
        tool.Ifc.set(ifc)
        subject.load_linked_models_from_ifc()
        assert len(props.links) == 2
        assert props.links[0].name == "test.ifc"
        assert props.links[0].ifc_definition_id == reference.id()
        assert props.links[0].has_transformation is False
        assert props.links[1].name == "test2.ifc"
        assert props.links[1].ifc_definition_id == reference2.id()
        assert props.links[1].has_transformation is True

    def test_load_linked_models_restores_query_from_cache_json(self):
        """The selector query used at link time is persisted only in the
        sidecar cache JSON. Reopening the host IFC must restore it onto the
        Link PropertyGroup so subsequent Reload/Load replay the same filter."""
        ifc = ifcopenshell.file()
        props = tool.Project.get_project_props()
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        document = ifcopenshell.api.document.add_information(ifc)
        document.Scope = "LINKED_MODEL"
        with NamedTemporaryFile(suffix=".ifc.cache.json", mode="w", delete=False) as tmp:
            json.dump({"query": "IfcElement, ! IfcOpeningElement"}, tmp)
            json_path = Path(tmp.name)
        try:
            ifc_filepath = tmp.name.replace(".ifc.cache.json", ".ifc")
            reference = ifcopenshell.api.document.add_reference(ifc, document)
            reference.Location = Path(ifc_filepath).as_posix()
            reference.Identification = ""
            tool.Ifc.set(ifc)
            subject.load_linked_models_from_ifc()
            assert len(props.links) == 1
            assert props.links[0].query == "IfcElement, ! IfcOpeningElement"
        finally:
            json_path.unlink(missing_ok=True)

    def test_load_linked_models_query_defaults_empty_without_cache_json(self):
        """When no sidecar cache JSON exists, the restored Link's query field
        must default to the empty string. Empty query is the documented signal
        for the load path to apply no selector filter."""
        ifc = ifcopenshell.file()
        props = tool.Project.get_project_props()
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        document = ifcopenshell.api.document.add_information(ifc)
        document.Scope = "LINKED_MODEL"
        with tempfile.TemporaryDirectory() as tmpdir:
            ifc_path = Path(tmpdir) / "no-cache.ifc"
            reference = ifcopenshell.api.document.add_reference(ifc, document)
            reference.Location = ifc_path.as_posix()
            reference.Identification = ""
            tool.Ifc.set(ifc)
            subject.load_linked_models_from_ifc()
            assert len(props.links) == 1
            assert props.links[0].query == ""


class TestCalculateLinkMatrix(NewFile):
    def _write_cache_json(self, payload: dict) -> Path:
        """Write ``payload`` to a fresh sidecar cache JSON path and return it.

        On Windows, ``NamedTemporaryFile(delete=True)`` holds an exclusive
        handle for the ``with`` block's duration, so the code-under-test
        cannot open the same path — hence the manual write + unlink pattern.
        """
        tmp = NamedTemporaryFile(suffix=".ifc.cache.json", mode="w", delete=False)
        try:
            json.dump(payload, tmp)
        finally:
            tmp.close()
        return Path(tmp.name)

    def test_linking_a_model_without_an_offset_to_our_session_with_no_offset(self):
        props = tool.Project.get_project_props()
        gprops = tool.Georeference.get_georeference_props()
        json_path = self._write_cache_json({"model_project_north": "0", "model_origin_si": "0,0,0"})
        try:
            link = props.links.add()
            link.filepath = str(json_path).replace(".ifc.cache.json", ".ifc")
            gprops.model_project_north = "0"
            gprops.model_origin_si = "0,0,0"
            assert np.allclose(subject.calculate_link_matrix(link), np.eye(4))
        finally:
            json_path.unlink(missing_ok=True)

    def test_linking_an_offset_model_to_our_session_with_no_offset(self):
        props = tool.Project.get_project_props()
        gprops = tool.Georeference.get_georeference_props()
        json_path = self._write_cache_json({"model_project_north": "0", "model_origin_si": "5,0,0"})
        try:
            link = props.links.add()
            link.filepath = str(json_path).replace(".ifc.cache.json", ".ifc")
            gprops.model_project_north = "0"
            gprops.model_origin_si = "0,0,0"
            m = np.eye(4)
            m[0][3] = 5
            assert np.allclose(subject.calculate_link_matrix(link), m)
        finally:
            json_path.unlink(missing_ok=True)

    def test_linking_an_offset_model_to_our_session_with_offset(self):
        props = tool.Project.get_project_props()
        gprops = tool.Georeference.get_georeference_props()
        json_path = self._write_cache_json({"model_project_north": "0", "model_origin_si": "5,0,0"})
        try:
            link = props.links.add()
            link.filepath = str(json_path).replace(".ifc.cache.json", ".ifc")
            gprops.model_project_north = "0"
            gprops.model_origin_si = "2,0,0"
            m = np.eye(4)
            m[0][3] = 3
            assert np.allclose(subject.calculate_link_matrix(link), m)
        finally:
            json_path.unlink(missing_ok=True)

    def test_linking_an_offset_model_to_our_session_with_offset_and_transformation(self):
        props = tool.Project.get_project_props()
        gprops = tool.Georeference.get_georeference_props()
        json_path = self._write_cache_json({"model_project_north": "0", "model_origin_si": "5,0,0"})
        try:
            link = props.links.add()
            link.filepath = str(json_path).replace(".ifc.cache.json", ".ifc")
            transformation = np.eye(4)
            transformation[0][3] = 4
            link.transformation = ",".join(map(str, transformation.reshape(-1)))
            gprops.model_project_north = "0"
            gprops.model_origin_si = "2,0,0"
            m = np.eye(4)
            m[0][3] = 7
            assert np.allclose(subject.calculate_link_matrix(link), m)
        finally:
            json_path.unlink(missing_ok=True)


class TestLoadingIfcSqlite(NewFile):
    def test_run(self):
        filepath = Path("test/files/basic.ifc")
        ifc_file: ifcopenshell.file
        ifc_file = ifcopenshell.open(filepath)

        patcher = Ifc2Sql.Patcher(
            ifc_file,
            sql_type="SQLite",
        )
        patcher.patch()
        tmp_file = Path(tempfile.mkstemp(suffix=".ifcsqlite")[1])
        ifcpatch.write(patcher.get_output(), tmp_file)

        elements_with_meshes = [
            # Types.
            "IfcSlabType/Slab",
            "IfcWallType/Wall",
            # Occurrences.
            "IfcBeam/Beam",
            "IfcWall/Wall",
        ]

        elements_without_meshes = (
            "IfcProject/My Project",
            "IfcSite/My Site",
            "IfcBuilding/My Building",
            "IfcBuildingStorey/Ground Floor",
        )

        def clean_up() -> None:
            if isinstance(ifc_file := tool.Ifc.get(), ifcopenshell.sqlite):
                ifc_file.db.close()
            tmp_file.unlink(missing_ok=True)

        with contextlib.ExitStack() as stack:
            stack.callback(clean_up)
            bpy.ops.bim.load_project(filepath=tmp_file.as_posix())
            assert isinstance(tool.Ifc.get(), ifcopenshell.sqlite)
            for element_name in elements_with_meshes:
                assert element_name in bpy.data.objects
                assert bpy.data.objects[element_name].data

            for element_name in elements_without_meshes:
                assert element_name in bpy.data.objects
                assert not bpy.data.objects[element_name].data


class TestGettingLinkedElementGeomSlice:
    TEST_OBJ = {
        "guids": ["aaa", "bbb", "ccc"],
        "guid_ids": [5, 10, 15],
    }

    def test_get_first_element(self):
        obj = TestGettingLinkedElementGeomSlice.TEST_OBJ
        obj = cast(bpy.types.Object, obj)
        slice_ = subject.Link.get_linked_element_geom_slice(obj, "aaa")
        assert range(15)[slice_] == range(5)

    def test_get_middle_element(self):
        obj = TestGettingLinkedElementGeomSlice.TEST_OBJ
        obj = cast(bpy.types.Object, obj)
        slice_ = subject.Link.get_linked_element_geom_slice(obj, "bbb")
        assert range(15)[slice_] == range(5, 10)

    def test_skip_hidden_first_element(self):
        obj = TestGettingLinkedElementGeomSlice.TEST_OBJ
        obj = obj | {"hidden_indices": [0]}
        obj = cast(bpy.types.Object, obj)
        slice_ = subject.Link.get_linked_element_geom_slice(obj, "bbb")
        assert range(15)[slice_] == range(5)

    def test_skip_hidden_middle_element(self):
        obj = TestGettingLinkedElementGeomSlice.TEST_OBJ
        obj = obj | {"hidden_indices": [1]}
        obj = cast(bpy.types.Object, obj)
        slice_ = subject.Link.get_linked_element_geom_slice(obj, "ccc")
        assert range(15)[slice_] == range(5, 10)

    def test_handle_hidden_non_first_element(self):
        obj = TestGettingLinkedElementGeomSlice.TEST_OBJ
        obj = obj | {"hidden_indices": [1]}
        obj = cast(bpy.types.Object, obj)
        slice_ = subject.Link.get_linked_element_geom_slice(obj, "aaa")
        assert range(15)[slice_] == range(5)
