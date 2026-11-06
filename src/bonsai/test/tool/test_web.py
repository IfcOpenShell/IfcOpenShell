# This file was generated with the assistance of an AI coding tool.

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


import ifcopenshell
import ifcopenshell.api.cost

import bonsai.core.tool
from bonsai.tool.web import Web as subject
from bonsai.tool.web import web_operator_queue
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Web)


class TestCheckOperatorQueue(NewFile):
    def test_a_failing_operator_does_not_stop_later_ones(self, monkeypatch):
        class DummyProps:
            is_connected = True

        handled = []
        monkeypatch.setattr("bonsai.tool.Web.get_web_props", lambda: DummyProps())
        monkeypatch.setattr(subject, "handle_csv_operator", lambda operator_data: handled.append(operator_data))
        web_operator_queue.put_nowait({"sourcePage": "cost", "operator": {}})
        web_operator_queue.put_nowait({"sourcePage": "csv", "operator": {"type": "selection"}})
        assert subject.check_operator_queue() == 1.0
        assert handled == [{"type": "selection"}]
        assert web_operator_queue.empty()


class TestHandleCostOperator(NewFile):
    def test_edit_cost_values_to_sum_without_a_unit_basis(self, monkeypatch):
        ifc_file = ifcopenshell.file(schema="IFC4")
        cost_schedule = ifcopenshell.api.cost.add_cost_schedule(ifc_file)
        cost_item = ifcopenshell.api.cost.add_cost_item(ifc_file, cost_schedule=cost_schedule)
        cost_value = ifcopenshell.api.cost.add_cost_value(ifc_file, parent=cost_item)
        monkeypatch.setattr("bonsai.tool.Ifc.get", lambda: ifc_file)
        monkeypatch.setattr(subject, "load_cost_schedule_web_ui", lambda cost_schedule: None)
        subject.handle_cost_operator(
            {
                "type": "editCostValues",
                "costItemId": cost_item.id(),
                "costValues": [
                    {
                        "costType": "SUM",
                        "costCategory": "*",
                        "appliedValue": 0,
                        "id": cost_value.id(),
                        "costItemId": cost_item.id(),
                    }
                ],
            }
        )
        assert cost_value.Category == "*"
