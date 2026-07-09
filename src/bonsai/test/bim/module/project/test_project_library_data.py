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


def _make_library_only_file(*, with_child: bool = False) -> ifcopenshell.file:
    """Build a minimal IFC4 file containing only an IfcProjectLibrary (no IfcProject).

    Per IFC4+, a file must contain at least one IfcContext; IfcProjectLibrary is a
    valid root on its own. ``with_child=True`` nests a sub-library under the root via
    IfcRelNests, mirroring real authored library files.
    """
    library_file = ifcopenshell.api.project.create_file(version="IFC4")
    root = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="RootLib")
    if with_child:
        child = ifcopenshell.api.root.create_entity(library_file, ifc_class="IfcProjectLibrary", name="ChildLib")
        ifcopenshell.api.nest.assign_object(library_file, [child], root)
    return library_file


class TestLibraryOnlyFile(NewIfc):
    def test_get_root_context_returns_project_library_when_no_project(self):
        library_file = _make_library_only_file()
        assert not library_file.by_type("IfcProject")

        root = tool.Project.get_root_context(library_file)

        assert root.is_a("IfcProjectLibrary")
        assert root.Name == "RootLib"

    def test_get_parent_library_returns_none_for_root_library(self):
        library_file = _make_library_only_file()
        root = library_file.by_type("IfcProjectLibrary")[0]

        assert tool.Project.get_parent_library(root) is None

    def test_get_project_hierarchy_skips_root_library(self):
        library_file = _make_library_only_file(with_child=True)
        root = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "RootLib")
        child = next(lib for lib in library_file.by_type("IfcProjectLibrary") if lib.Name == "ChildLib")

        hierarchy = tool.Project.get_project_hierarchy(library_file)

        assert root in hierarchy
        assert child in hierarchy[root]

    def test_project_library_data_loads_without_crash(self):
        IfcStore.library_file = _make_library_only_file()
        try:
            ProjectLibraryData.is_loaded = False
            ProjectLibraryData.load()
            assert ProjectLibraryData.is_loaded
            enum = ProjectLibraryData.data["parent_libraries_enum"]
            assert len(enum) == 1
            assert enum[0][1].startswith("IfcProjectLibrary ")
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_refresh_library_succeeds_on_library_only_file(self):
        import bpy

        IfcStore.library_file = _make_library_only_file(with_child=True)
        try:
            result = bpy.ops.bim.refresh_library()
            assert result == {"FINISHED"}
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False

    def test_add_project_library_nests_under_root_when_no_project(self):
        import bpy

        IfcStore.library_file = _make_library_only_file()
        library_file = IfcStore.library_file
        try:
            root = library_file.by_type("IfcProjectLibrary")[0]
            before = set(library_file.by_type("IfcProjectLibrary"))

            result = bpy.ops.bim.add_project_library()

            assert result == {"FINISHED"}
            after = set(library_file.by_type("IfcProjectLibrary"))
            new_libraries = after - before
            assert len(new_libraries) == 1
            new_library = next(iter(new_libraries))
            assert new_library.Nests
            assert new_library.Nests[0].RelatingObject == root
            assert not new_library.HasContext
        finally:
            IfcStore.library_file = None
            ProjectLibraryData.is_loaded = False
