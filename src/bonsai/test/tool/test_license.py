# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

# AI-assisted development tool was used in writing this file.

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
import pytest

import bonsai.core.tool
from bonsai.tool.license import PSET_NAME
from bonsai.tool.license import License as subject

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def ifc():
    return ifcopenshell.file(schema="IFC4")


def make_spatial_hierarchy(ifc):
    """Return (project, storey, wall) connected through full spatial chain."""
    project = ifc.create_entity("IfcProject", Name="TestProject")
    site = ifc.create_entity("IfcSite", Name="Site")
    building = ifc.create_entity("IfcBuilding", Name="Building")
    storey = ifc.create_entity("IfcBuildingStorey", Name="Ground Floor")
    wall = ifc.create_entity("IfcWall", Name="W1")
    ifc.create_entity(
        "IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=project, RelatedObjects=[site]
    )
    ifc.create_entity(
        "IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=site, RelatedObjects=[building]
    )
    ifc.create_entity(
        "IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=building, RelatedObjects=[storey]
    )
    ifc.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=ifcopenshell.guid.new(),
        RelatingStructure=storey,
        RelatedElements=[wall],
    )
    return project, storey, wall


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------


class TestImplementsTool:
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.License)


# ---------------------------------------------------------------------------
# get_pset
# ---------------------------------------------------------------------------


class TestGetPset:
    def test_returns_none_when_no_pset(self, ifc):
        wall = ifc.create_entity("IfcWall")
        assert subject.get_pset(wall) is None

    def test_returns_pset_when_present(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.set_license(ifc, wall, "CC-BY-4.0", "(c) 2026 Test")
        result = subject.get_pset(wall)
        assert result is not None
        assert result["SpdxLicenseIdentifier"] == "CC-BY-4.0"

    def test_does_not_inherit_from_type(self, ifc):
        """get_pset is direct-only; a pset on the type must not appear on the occurrence."""
        wall_type = ifc.create_entity("IfcWallType", Name="WT")
        wall = ifc.create_entity("IfcWall")
        ifc.create_entity(
            "IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            RelatingType=wall_type,
            RelatedObjects=[wall],
        )
        subject.set_license(ifc, wall_type, "CC0-1.0", "Public Domain")
        assert subject.get_pset(wall) is None


# ---------------------------------------------------------------------------
# get_effective_pset
# ---------------------------------------------------------------------------


class TestGetEffectivePset:
    def test_returns_none_when_no_license_anywhere(self, ifc):
        _, _, wall = make_spatial_hierarchy(ifc)
        pset, source = subject.get_effective_pset(wall)
        assert pset is None
        assert source is None

    def test_returns_own_pset_with_self_as_source(self, ifc):
        _, _, wall = make_spatial_hierarchy(ifc)
        subject.set_license(ifc, wall, "MIT", "(c) 2026 Someone")
        pset, source = subject.get_effective_pset(wall)
        assert pset is not None
        assert pset["SpdxLicenseIdentifier"] == "MIT"
        assert source.id() == wall.id()

    def test_inherits_from_project(self, ifc):
        project, _, wall = make_spatial_hierarchy(ifc)
        subject.set_license(ifc, project, "CC-BY-4.0", "(c) 2026 Corp")
        pset, source = subject.get_effective_pset(wall)
        assert pset["SpdxLicenseIdentifier"] == "CC-BY-4.0"
        assert source.id() == project.id()

    def test_own_pset_overrides_project(self, ifc):
        project, _, wall = make_spatial_hierarchy(ifc)
        subject.set_license(ifc, project, "CC-BY-4.0", "(c) 2026 Corp")
        subject.set_license(ifc, wall, "CC-BY-SA-4.0", "(c) 2026 Other")
        pset, source = subject.get_effective_pset(wall)
        assert pset["SpdxLicenseIdentifier"] == "CC-BY-SA-4.0"
        assert source.id() == wall.id()

    def test_inherits_from_storey(self, ifc):
        _, storey, wall = make_spatial_hierarchy(ifc)
        subject.set_license(ifc, storey, "ODbL-1.0", "(c) 2026 Storey Owner")
        pset, source = subject.get_effective_pset(wall)
        assert pset["SpdxLicenseIdentifier"] == "ODbL-1.0"
        assert source.id() == storey.id()

    def test_stops_at_project(self, ifc):
        project, _, _ = make_spatial_hierarchy(ifc)
        subject.set_license(ifc, project, "CC0-1.0", "Public Domain")
        pset, source = subject.get_effective_pset(project)
        assert source.id() == project.id()

    def test_type_without_own_pset(self, ifc):
        wall_type = ifc.create_entity("IfcWallType", Name="WT")
        pset, source = subject.get_effective_pset(wall_type)
        assert pset is None
        assert source is None

    def test_type_with_own_pset(self, ifc):
        wall_type = ifc.create_entity("IfcWallType", Name="WT")
        subject.set_license(ifc, wall_type, "Apache-2.0", "(c) 2026 Firm")
        pset, source = subject.get_effective_pset(wall_type)
        assert pset["SpdxLicenseIdentifier"] == "Apache-2.0"
        assert source.id() == wall_type.id()


# ---------------------------------------------------------------------------
# set_license
# ---------------------------------------------------------------------------


class TestSetLicense:
    def test_creates_pset_on_occurrence(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.set_license(ifc, wall, "CC-BY-4.0", "(c) 2026 Corp")
        result = ifcopenshell.util.element.get_pset(wall, PSET_NAME, should_inherit=False)
        assert result["SpdxLicenseIdentifier"] == "CC-BY-4.0"
        assert result["CopyrightNotice"] == "(c) 2026 Corp"

    def test_creates_pset_on_type(self, ifc):
        wall_type = ifc.create_entity("IfcWallType", Name="WT")
        subject.set_license(ifc, wall_type, "MIT", "(c) 2026 Lib")
        result = ifcopenshell.util.element.get_pset(wall_type, PSET_NAME, should_inherit=False)
        assert result["SpdxLicenseIdentifier"] == "MIT"

    def test_creates_pset_on_project(self, ifc):
        project = ifc.create_entity("IfcProject", Name="P")
        subject.set_license(ifc, project, "CC0-1.0", "Public Domain")
        result = ifcopenshell.util.element.get_pset(project, PSET_NAME, should_inherit=False)
        assert result["SpdxLicenseIdentifier"] == "CC0-1.0"

    def test_updates_existing_pset_in_place(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.set_license(ifc, wall, "CC-BY-4.0", "First")
        subject.set_license(ifc, wall, "MIT", "Second")
        psets = [e for e in ifc.by_type("IfcPropertySet") if e.Name == PSET_NAME]
        assert len(psets) == 1, "Should update in place, not duplicate"
        result = ifcopenshell.util.element.get_pset(wall, PSET_NAME, should_inherit=False)
        assert result["SpdxLicenseIdentifier"] == "MIT"
        assert result["CopyrightNotice"] == "Second"

    def test_optional_fields_stored_when_provided(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.set_license(
            ifc,
            wall,
            "CC-BY-4.0",
            "(c) 2026 Corp",
            attribution_text="Designed by Corp",
            source_url="https://example.com",
        )
        result = ifcopenshell.util.element.get_pset(wall, PSET_NAME, should_inherit=False)
        assert result["AttributionText"] == "Designed by Corp"
        assert result["SourceUrl"] == "https://example.com"

    def test_optional_fields_omitted_when_empty(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.set_license(ifc, wall, "CC-BY-4.0", "(c) 2026 Corp")
        result = ifcopenshell.util.element.get_pset(wall, PSET_NAME, should_inherit=False)
        assert not result.get("AttributionText")
        assert not result.get("SourceUrl")


# ---------------------------------------------------------------------------
# remove_license
# ---------------------------------------------------------------------------


class TestRemoveLicense:
    def test_removes_pset(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.set_license(ifc, wall, "CC-BY-4.0", "(c) 2026 Corp")
        assert subject.get_pset(wall) is not None
        subject.remove_license(ifc, wall)
        assert subject.get_pset(wall) is None

    def test_no_error_when_no_pset(self, ifc):
        wall = ifc.create_entity("IfcWall")
        subject.remove_license(ifc, wall)  # Must not raise


# ---------------------------------------------------------------------------
# inherit_library_license
# ---------------------------------------------------------------------------


class TestInheritLibraryLicense:
    def make_library(self, spdx_id, notice, on="project"):
        """Library with license on IfcProject (default) or on the type."""
        lib = ifcopenshell.file(schema="IFC4")
        lib_project = lib.create_entity("IfcProject", Name="Library")
        wall_type = lib.create_entity("IfcWallType", Name="WAL01")
        if on == "project":
            subject.set_license(lib, lib_project, spdx_id, notice)
        elif on == "type":
            subject.set_license(lib, wall_type, spdx_id, notice)
        return lib, wall_type

    def test_stamps_project_license_onto_untagged_type(self, ifc):
        lib, lib_type = self.make_library("CC0-1.0", "Public Domain", on="project")
        dest_type = ifc.create_entity("IfcWallType", Name="WAL01")
        subject.inherit_library_license(ifc, dest_type, lib, lib_type)
        result = subject.get_pset(dest_type)
        assert result is not None
        assert result["SpdxLicenseIdentifier"] == "CC0-1.0"
        assert result["CopyrightNotice"] == "Public Domain"

    def test_does_not_overwrite_existing_tag(self, ifc):
        """An element already tagged (pset traveled via append_asset) must not be overwritten."""
        lib, lib_type = self.make_library("CC0-1.0", "Public Domain", on="project")
        dest_type = ifc.create_entity("IfcWallType", Name="WAL01")
        subject.set_license(ifc, dest_type, "CC-BY-SA-4.0", "(c) 2026 Studio")
        subject.inherit_library_license(ifc, dest_type, lib, lib_type)
        assert subject.get_pset(dest_type)["SpdxLicenseIdentifier"] == "CC-BY-SA-4.0"

    def test_no_license_in_library_does_nothing(self, ifc):
        lib = ifcopenshell.file(schema="IFC4")
        lib.create_entity("IfcProject", Name="Library")
        lib_type = lib.create_entity("IfcWallType", Name="WAL01")
        dest_type = ifc.create_entity("IfcWallType", Name="WAL01")
        subject.inherit_library_license(ifc, dest_type, lib, lib_type)
        assert subject.get_pset(dest_type) is None

    def test_type_level_library_license_is_resolved(self, ifc):
        """License on the library type itself is also found."""
        lib, lib_type = self.make_library("MIT", "(c) 2026 Lib", on="type")
        dest_type = ifc.create_entity("IfcWallType", Name="WAL01")
        subject.inherit_library_license(ifc, dest_type, lib, lib_type)
        result = subject.get_pset(dest_type)
        assert result is not None
        assert result["SpdxLicenseIdentifier"] == "MIT"

    def test_all_optional_fields_are_propagated(self, ifc):
        lib = ifcopenshell.file(schema="IFC4")
        lib_project = lib.create_entity("IfcProject", Name="Library")
        lib_type = lib.create_entity("IfcWallType", Name="WAL01")
        subject.set_license(
            lib,
            lib_project,
            "CC-BY-4.0",
            "(c) 2026 Corp",
            attribution_text="Credit: Corp",
            source_url="https://example.com/lib",
        )
        dest_type = ifc.create_entity("IfcWallType", Name="WAL01")
        subject.inherit_library_license(ifc, dest_type, lib, lib_type)
        result = subject.get_pset(dest_type)
        assert result["AttributionText"] == "Credit: Corp"
        assert result["SourceUrl"] == "https://example.com/lib"
