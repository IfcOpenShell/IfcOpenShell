# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.nest
import ifcopenshell.api.project
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.project.data import ProjectLibraryData
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.project


def _make_valid_library_file(*, with_child: bool = False) -> ifcopenshell.file:
    """Build a spec-valid IFC4 library file: IfcProject + IfcProjectLibrary declared to it.

    Per the IFC Project Context concept template, every project data set (library
    files included) shall contain exactly one IfcProject, and IfcProjectLibrary
    instances are assigned to it via IfcRelDeclares. ``with_child=True`` also nests a
    sub-library under the root via IfcRelNests, mirroring real authored library files.
    """
    library_file = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProject", name="Demo Project")
    root = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="RootLib")
    ifcopenshell.api.project.assign_declaration(library_file, definitions=[root], relating_context=project)
    if with_child:
        child = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="ChildLib")
        ifcopenshell.api.nest.assign_object(library_file, [child], root)
    return library_file


def _make_malformed_library_file(*, with_child: bool = False) -> ifcopenshell.file:
    """Build an IFC4 file containing only an IfcProjectLibrary, no IfcProject.

    This is NOT spec-valid IFC (IfcProject is mandatory per the Project Context
    concept template) but mirrors real externally authored files that omit it, such
    as the one reported in #8183. Used to exercise the repair path
    (tool.Project.ensure_project_context / open_library_file), not as an example of
    a legitimate model.
    """
    library_file = ifcopenshell.api.project.create_file(version="IFC4")
    root = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="RootLib")
    if with_child:
        child = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="ChildLib")
        ifcopenshell.api.nest.assign_object(library_file, [child], root)
    return library_file


class TestEnsureProjectContext(NewIfc):
    """tool.Project.ensure_project_context() repairs files missing the required IfcProject."""

    def test_repairs_malformed_file_by_declaring_root_library_to_a_new_project(self):
        library_file = _make_malformed_library_file()
        root = library_file.by_type("IfcProjectLibrary")[0]

        tool.Project.ensure_project_context(library_file)

        projects = library_file.by_type("IfcProject")
        assert len(projects) == 1
        assert root.HasContext
        assert root.HasContext[0].RelatingContext == projects[0]

    def test_only_declares_root_level_libraries_not_nested_children(self):
        library_file = _make_malformed_library_file(with_child=True)
        root = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "RootLib")
        child = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "ChildLib")

        tool.Project.ensure_project_context(library_file)

        assert root.HasContext
        assert not child.HasContext
        assert child.Nests and child.Nests[0].RelatingObject == root

    def test_is_a_noop_when_project_already_present(self):
        library_file = _make_valid_library_file()
        before = set(library_file.by_type("IfcProject"))

        tool.Project.ensure_project_context(library_file)

        assert set(library_file.by_type("IfcProject")) == before

    def test_is_a_noop_when_no_project_library_either(self):
        library_file = ifcopenshell.api.project.create_file(version="IFC4")

        tool.Project.ensure_project_context(library_file)

        assert not library_file.by_type("IfcProject")

    def test_open_library_file_repairs_a_malformed_file_from_disk(self, tmp_path):
        library_file = _make_malformed_library_file()
        filepath = tmp_path / "malformed_library.ifc"
        library_file.write(str(filepath))

        opened = tool.Project.open_library_file(str(filepath))

        assert len(opened.by_type("IfcProject")) == 1
        assert opened.by_type("IfcProjectLibrary")[0].HasContext


class TestValidLibraryFile(NewIfc):
    """Downstream project-library UI code operating on a spec-valid model (IfcProject root)."""

    def test_get_root_context_returns_the_project(self):
        library_file = _make_valid_library_file()
        project = library_file.by_type("IfcProject")[0]

        root = tool.Project.get_root_context(library_file)

        assert root == project

    def test_get_parent_library_returns_project_for_declared_root_library(self):
        library_file = _make_valid_library_file()
        project = library_file.by_type("IfcProject")[0]
        root = library_file.by_type("IfcProjectLibrary")[0]

        assert tool.Project.get_parent_library(root) == project

    def test_get_project_hierarchy_roots_libraries_under_the_project(self):
        library_file = _make_valid_library_file(with_child=True)
        project = library_file.by_type("IfcProject")[0]
        root = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "RootLib")
        child = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "ChildLib")

        hierarchy = tool.Project.get_project_hierarchy(library_file)

        assert root in hierarchy[project]
        assert child in hierarchy[root]

    def test_project_library_data_loads_with_a_single_unique_root_entry(self):
        # Regression test for the ci-bonsai-daily failure: parent_libraries_enum()
        # must never emit two entries with the same STEP id (Blender's EnumProperty
        # requires unique keys). Reproduced here on a repaired, spec-valid file rather
        # than an invalid library-only one.
        IfcStore.library_file = _make_valid_library_file()
        try:
            ProjectLibraryData.is_loaded = False
            ProjectLibraryData.load()
            assert ProjectLibraryData.is_loaded
            enum = ProjectLibraryData.data["parent_libraries_enum"]
            keys = [entry[0] for entry in enum]
            assert len(keys) == len(set(keys))
            assert enum[0][1].startswith("IfcProject ")
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_refresh_library_succeeds_on_valid_library_file(self):
        import bpy

        IfcStore.library_file = _make_valid_library_file(with_child=True)
        try:
            result = bpy.ops.bim.refresh_library()
            assert result == {"FINISHED"}
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_add_project_library_declares_new_library_under_the_project_root(self):
        import bpy

        IfcStore.library_file = _make_valid_library_file()
        library_file = IfcStore.library_file
        try:
            project = library_file.by_type("IfcProject")[0]
            before = set(library_file.by_type("IfcProjectLibrary"))

            result = bpy.ops.bim.add_project_library()

            assert result == {"FINISHED"}
            after = set(library_file.by_type("IfcProjectLibrary"))
            new_libraries = after - before
            assert len(new_libraries) == 1
            new_library = next(iter(new_libraries))
            assert new_library.HasContext
            assert new_library.HasContext[0].RelatingContext == project
            assert not new_library.Nests
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False
