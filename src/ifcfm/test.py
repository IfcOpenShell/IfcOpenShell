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

# This file was generated with the assistance of an AI coding tool.

import ifcfm.cobie24 as cobie24
import ifcfm.cobie24legacy as cobie24legacy
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit


def setup_project() -> tuple[
    ifcopenshell.file,
    ifcopenshell.entity_instance,
    ifcopenshell.entity_instance,
    ifcopenshell.entity_instance,
    ifcopenshell.entity_instance,
]:
    ifc_file = ifcopenshell.file(schema="IFC4")
    project = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test Project")
    ifcopenshell.api.unit.assign_unit(ifc_file)
    site = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(ifc_file, relating_object=building, products=[storey])
    return ifc_file, project, site, building, storey


class TestZeroValuePropertiesAreNotDroppedAsAbsent:
    """Regression tests for a falsy-empty-container defect: cobie24.py and
    cobie24legacy.py used ``and val(value):``/``or not val(value):`` to gate
    on whether a property carries data. val() only maps "" and "n/a" to
    None; every other value, including a genuine 0, 0.0 or False, passes
    through unchanged. Testing that result for truthiness discarded a
    legitimate zero or False property as if it were never set. The fix
    checks ``val(value) is not None`` instead."""

    def test_cobie24_get_attributes_keeps_a_zero_or_false_custom_property(self):
        ifc_file, *_, storey = setup_project()
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=storey, name="Custom_Inspection")
        ifcopenshell.api.pset.edit_pset(
            ifc_file, pset=pset, properties={"OccupancyCount": 0, "IsCompliant": False, "InspectionScore": 7}
        )
        names = {a["Name"] for a in cobie24.get_attributes(ifc_file)}
        assert "OccupancyCount" in names
        assert "IsCompliant" in names
        assert "InspectionScore" in names

    def test_cobie24legacy_get_attributes_keeps_a_zero_or_false_custom_property(self):
        ifc_file, *_, storey = setup_project()
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=storey, name="Custom_Inspection")
        ifcopenshell.api.pset.edit_pset(
            ifc_file, pset=pset, properties={"OccupancyCount": 0, "IsCompliant": False, "InspectionScore": 7}
        )
        names = {a["Name"] for a in cobie24legacy.get_attributes(ifc_file)}
        assert "OccupancyCount" in names
        assert "IsCompliant" in names
        assert "InspectionScore" in names

    def test_cobie24_get_floor_data_keeps_a_zero_height(self):
        ifc_file, *_, storey = setup_project()
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=storey, name="Custom_Storey")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Height": 0.0})
        assert cobie24.get_floor_data(ifc_file, storey)["Height"] == "0.0"

    def test_cobie24legacy_get_floor_data_keeps_a_zero_height(self):
        ifc_file, *_, storey = setup_project()
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=storey, name="Custom_Storey")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Height": 0.0})
        assert cobie24legacy.get_floor_data(ifc_file, storey)["Height"] == "0.0"

    def test_cobie24_get_space_data_keeps_a_zero_area(self):
        ifc_file, project, *_ = setup_project()
        space = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcSpace", name="Placeholder Space")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=space, name="Custom_Space")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"GrossFloorArea": 0.0})
        assert cobie24.get_space_data(ifc_file, space)["GrossArea"] == "0.0"

    def test_cobie24legacy_get_type_data_keeps_a_zero_replacement_cost(self):
        ifc_file, *_ = setup_project()
        etype = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcFurnitureType", name="Chair")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=etype, name="COBie_EconomicImpactValues")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"ReplacementCost": 0.0})
        assert cobie24legacy.get_type_data(ifc_file, etype)["ReplacementCost"] == "0.0"

    def test_cobie24_get_job_data_keeps_a_zero_task_duration(self):
        ifc_file, *_ = setup_project()
        job = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcTask", name="Inspect")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=job, name="COBie_Job")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"TaskDuration": 0})
        assert cobie24.get_job_data(ifc_file, job)["Duration"] == "0"

    def test_cobie24legacy_get_job_data_keeps_a_zero_task_duration(self):
        ifc_file, *_ = setup_project()
        job = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcTask", name="Inspect")
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=job, name="COBie_Job")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"TaskDuration": 0})
        assert cobie24legacy.get_job_data(ifc_file, job)["Duration"] == "0"

    def test_cobie24_get_type_data_warranty_zero_is_not_overridden_by_fallback_pset(self):
        # COBie_Warranty explicitly states a zero-duration parts warranty
        # (no separate parts cover, distinct from "unknown"). A legacy
        # Pset_Warranty also happens to be attached with a real period; it
        # must not override the explicit zero from COBie_Warranty.
        ifc_file, *_ = setup_project()
        etype = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcFurnitureType", name="Chair")
        cobie_warranty = ifcopenshell.api.pset.add_pset(ifc_file, product=etype, name="COBie_Warranty")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=cobie_warranty, properties={"WarrantyDurationParts": 0})
        legacy_warranty = ifcopenshell.api.pset.add_pset(ifc_file, product=etype, name="Pset_Warranty")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=legacy_warranty, properties={"WarrantyPeriod": 5})
        assert cobie24.get_type_data(ifc_file, etype)["WarrantyDurationParts"] == 0
