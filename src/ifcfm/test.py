# IfcFM - IFC for facility management
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcFM.
#
# IfcFM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcFM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcFM.  If not, see <http://www.gnu.org/licenses/>.

import ifcfm.basic as basic
import ifcfm.cobie24 as cobie24
import ifcfm.cobie24legacy as cobie24legacy
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.util.element


def setup_project() -> tuple[
    ifcopenshell.file,
    ifcopenshell.entity_instance,
    ifcopenshell.entity_instance,
    ifcopenshell.entity_instance,
    ifcopenshell.entity_instance,
]:
    ifc_file = ifcopenshell.file(schema="IFC4")
    project = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test Project")
    unit = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
    ifcopenshell.api.unit.assign_unit(ifc_file, units=[unit])
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=building, products=[storey])
    return ifc_file, project, site, building, storey


class TestUnassignedComponentGuard:
    """Regression tests for the crash fixed in 4e322d7: get_container() can
    legitimately return None for a component that isn't (yet) placed in a
    spatial container. Elements/get_element_data must not crash on that, in
    all three presets."""

    def test_basic_element_with_no_container_does_not_crash(self):
        ifc_file, *_ = setup_project()
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        assert ifcopenshell.util.element.get_container(door) is None

        data = basic.get_element_data(ifc_file, door)
        assert data["SpaceName"] is None

    def test_cobie24_component_with_no_container_does_not_crash(self):
        ifc_file, *_ = setup_project()
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        assert ifcopenshell.util.element.get_container(door) is None

        data = cobie24.get_component_data(ifc_file, door)
        assert data["Space"] is None

    def test_cobie24legacy_component_with_no_container_does_not_crash(self):
        ifc_file, *_ = setup_project()
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        assert ifcopenshell.util.element.get_container(door) is None

        data = cobie24legacy.get_component_data(ifc_file, door)
        assert data["Space"] is None


class TestContainedComponentHappyPath:
    """The unassigned-container guard must not affect elements that DO have
    a spatial container: the Space/SpaceName column must still be populated."""

    def test_basic_element_in_space_reports_space_name(self):
        ifc_file, project, site, building, storey = setup_project()
        space = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSpace", name="Room 101")
        ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=storey, products=[space])
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=space, products=[door])

        data = basic.get_element_data(ifc_file, door)
        assert data["SpaceName"] == "Room 101"

    def test_cobie24_component_in_space_reports_space_name(self):
        ifc_file, project, site, building, storey = setup_project()
        space = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSpace", name="Room 101")
        ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=storey, products=[space])
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=space, products=[door])

        data = cobie24.get_component_data(ifc_file, door)
        assert data["Space"] == "Room 101"

    def test_cobie24legacy_component_in_space_reports_space_name(self):
        ifc_file, project, site, building, storey = setup_project()
        space = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSpace", name="Room 101")
        ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=storey, products=[space])
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        ifcopenshell.api.spatial.assign_container(ifc_file, relating_structure=space, products=[door])

        data = cobie24legacy.get_component_data(ifc_file, door)
        assert data["Space"] == "Room 101"


class TestUntypedElementGuard:
    """Regression test for basic.py:157: get_type() legitimately returns
    None for an element with no assigned IfcTypeObject, which is ordinary
    valid IFC. TypeName must fall back to None instead of crashing."""

    def test_basic_element_with_no_type_does_not_crash(self):
        ifc_file, *_ = setup_project()
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        assert ifcopenshell.util.element.get_type(door) is None

        data = basic.get_element_data(ifc_file, door)
        assert data["TypeName"] is None

    def test_basic_element_with_type_reports_type_name(self):
        ifc_file, *_ = setup_project()
        door_type = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoorType", name="DT01")
        door = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcDoor", name="D01")
        ifcopenshell.api.type.assign_type(
            ifc_file, related_objects=[door], relating_type=door_type, should_map_representations=False
        )

        data = basic.get_element_data(ifc_file, door)
        assert data["TypeName"] == "DT01"


class TestZoneDataUnnamedZone:
    """cobie24.get_zone_data concatenated parent.Name + "-" + zone.Name
    unguarded. Name is optional on IfcRoot, so an unnamed IfcZone nested
    under a named IfcZone raised TypeError: can only concatenate str (not
    "NoneType") to str."""

    def test_unnamed_zone_with_named_parent_does_not_crash(self):
        ifc_file, *_ = setup_project()
        zone = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcZone", name=None)
        parent_zone = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcZone", name="Group A")
        ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=parent_zone, products=[zone])
        assert zone.Name is None
        assert ifcopenshell.util.element.get_aggregate(zone).Name == "Group A"

        data = cobie24.get_zone_data(ifc_file, (zone, None))
        assert data["Name"] is None

    def test_named_zone_with_named_parent_prefixes_name(self):
        # Happy path: the guard must not affect the original prefixing
        # behaviour when both names are present.
        ifc_file, *_ = setup_project()
        zone = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcZone", name="Wet Areas")
        parent_zone = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcZone", name="Group A")
        ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=parent_zone, products=[zone])

        data = cobie24.get_zone_data(ifc_file, (zone, None))
        assert data["Name"] == "Group A-Wet Areas"
