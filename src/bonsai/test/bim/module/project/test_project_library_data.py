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


def _make_library_file(*, with_child: bool = False) -> ifcopenshell.file:
    """Build a spec-valid IFC4 library file: IfcProject + IfcProjectLibrary declared to it.

    Per the IFC Project Context concept template, every project data set (library
    files included) shall contain exactly one IfcProject, and IfcProjectLibrary
    instances are assigned to it via IfcRelDeclares. This matches how every library
    file shipped in bonsai/bim/data/libraries is actually authored. ``with_child=True``
    also nests a sub-library under the root via IfcRelNests.
    """
    library_file = ifcopenshell.api.project.create_file(version="IFC4")
    project = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProject", name="Demo Project")
    root = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="RootLib")
    ifcopenshell.api.project.assign_declaration(library_file, definitions=[root], relating_context=project)
    if with_child:
        child = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="ChildLib")
        ifcopenshell.api.nest.assign_object(library_file, [child], root)
    return library_file


class TestLibraryFile(NewIfc):
    """Project-library UI code operating on a spec-valid model (IfcProject root).

    A file containing only IfcProjectLibrary and no IfcProject is not valid IFC and
    is not supported; see test_parent_libraries_enum_raises_for_a_file_without_a_project.
    """

    def test_parent_libraries_enum_raises_for_a_file_without_a_project(self):
        library_file = ifcopenshell.api.project.create_file(version="IFC4")
        ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="RootLib")
        IfcStore.library_file = library_file
        try:
            with pytest.raises(IndexError):
                ProjectLibraryData.parent_libraries_enum()
        finally:
            IfcStore.library_file = None

    def test_get_parent_library_returns_project_for_declared_root_library(self):
        library_file = _make_library_file()
        project = library_file.by_type("IfcProject")[0]
        root = library_file.by_type("IfcProjectLibrary")[0]

        assert tool.Project.get_parent_library(root) == project

    def test_get_parent_library_returns_the_library_for_a_nested_sub_library(self):
        library_file = _make_library_file(with_child=True)
        root = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "RootLib")
        child = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "ChildLib")

        assert tool.Project.get_parent_library(child) == root

    def test_get_parent_library_returns_none_for_an_orphaned_library(self):
        library_file = ifcopenshell.api.project.create_file(version="IFC4")
        orphan = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="Orphan")

        assert tool.Project.get_parent_library(orphan) is None

    def test_get_project_hierarchy_roots_libraries_under_the_project(self):
        library_file = _make_library_file(with_child=True)
        project = library_file.by_type("IfcProject")[0]
        root = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "RootLib")
        child = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "ChildLib")

        hierarchy = tool.Project.get_project_hierarchy(library_file)

        assert root in hierarchy[project]
        assert child in hierarchy[root]

    def test_project_library_data_loads_with_unique_enum_keys(self):
        IfcStore.library_file = _make_library_file(with_child=True)
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

    def test_refresh_library_succeeds(self):
        import bpy

        IfcStore.library_file = _make_library_file(with_child=True)
        try:
            result = bpy.ops.bim.refresh_library()
            assert result == {"FINISHED"}
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_edit_project_library_moves_a_project_declared_library_under_another_library(self):
        import bpy

        library_file = _make_library_file()
        project = library_file.by_type("IfcProject")[0]
        root = library_file.by_type("IfcProjectLibrary")[0]
        target = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="TargetLib")
        ifcopenshell.api.project.assign_declaration(library_file, definitions=[target], relating_context=project)
        IfcStore.library_file = library_file
        try:
            props = tool.Project.get_project_props()
            props.selected_project_library = str(root.id())
            props.is_editing_project_library = True
            props.parent_library = str(target.id())

            result = bpy.ops.bim.edit_project_library()

            assert result == {"FINISHED"}
            assert tool.Project.get_parent_library(root) == target
            assert root.Nests and root.Nests[0].RelatingObject == target
            assert not root.HasContext
        finally:
            if props.is_editing_project_library:
                props.is_editing_project_library = False
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_edit_project_library_moves_a_nested_library_back_under_the_project(self):
        import bpy

        library_file = _make_library_file(with_child=True)
        project = library_file.by_type("IfcProject")[0]
        child = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "ChildLib")
        IfcStore.library_file = library_file
        try:
            props = tool.Project.get_project_props()
            props.selected_project_library = str(child.id())
            props.is_editing_project_library = True
            props.parent_library = str(project.id())

            result = bpy.ops.bim.edit_project_library()

            assert result == {"FINISHED"}
            assert tool.Project.get_parent_library(child) == project
            assert child.HasContext and child.HasContext[0].RelatingContext == project
            assert not child.Nests
        finally:
            if props.is_editing_project_library:
                props.is_editing_project_library = False
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_add_project_library_declares_new_library_under_the_project_root(self):
        import bpy

        IfcStore.library_file = _make_library_file()
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
