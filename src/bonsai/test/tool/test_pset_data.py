# This file was generated with the assistance of an AI coding tool.
# Bonsai - OpenBIM Blender Add-on
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

import ifcopenshell

import bonsai.tool as tool
import test.bim.bootstrap
from bonsai.bim.module.pset.data import MaterialPsetsData, WorkSchedulePsetsData


class TestStaleDefinitionId(test.bim.bootstrap.NewFile):
    def test_work_schedule_psets_load_with_a_removed_id(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        schedule = ifc.createIfcWorkSchedule()
        tool.Sequence.get_work_schedule_props().active_work_schedule_id = schedule.id()
        ifc.remove(schedule)
        WorkSchedulePsetsData.load()
        assert WorkSchedulePsetsData.data == {"psets": []}

    def test_material_psets_load_with_a_removed_id(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        material = ifc.createIfcMaterial("Concrete")
        props = tool.Material.get_material_props()
        props.materials.add().ifc_definition_id = material.id()
        props.active_material_index = 0
        ifc.remove(material)
        MaterialPsetsData.load()
        assert MaterialPsetsData.data["psets"] == []
