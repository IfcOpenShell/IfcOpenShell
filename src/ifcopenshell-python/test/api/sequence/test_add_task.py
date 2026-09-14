# This file was generated with the assistance of an AI coding tool.
# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


import ifcopenshell.api.sequence
import test.bootstrap


# NOTE: sequence module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestAddTask(test.bootstrap.IFC4):
    def test_task_is_named_by_default(self):
        # IfcTask carries a WHERE rule (exists(SELF.Name)) that plain schema
        # validation does not check but ifcopenshell.validate.validate(...,
        # express_rules=True) does. Bonsai's "Add Task" / "Add Summary Task"
        # operators call this api with no name= argument at all, so an
        # unnamed default here means a real, silently invalid IfcTask.
        task = ifcopenshell.api.sequence.add_task(self.file)
        assert task.Name is not None
        assert task.Name == "Unnamed"

    def test_task_name_is_still_overridable(self):
        task = ifcopenshell.api.sequence.add_task(self.file, name="Excavation")
        assert task.Name == "Excavation"


class TestAddTaskIFC4X3(test.bootstrap.IFC4X3, TestAddTask):
    pass
