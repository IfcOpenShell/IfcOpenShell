# IfcTester - IDS based model auditing
# Copyright (C) 2021-2022 Thomas Krijnen <thomas@aecgeeks.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell

from ifctester import ids, reporter


class TestJson:
    def test_a_forced_failed_requirement_without_failures_is_not_reported_as_100_percent_pass(self):
        # A violated prohibited specification (or a required specification with
        # no applicable entities) forces requirement.status to False without
        # ever populating requirement.failures, since per-element requirement
        # checks are skipped in both cases. The reporter must not derive a
        # pass count from the empty failures list in that situation.
        specs = ids.Ids(title="Title")
        spec = ids.Specification(name="No walls allowed")
        spec.applicability.append(ids.Entity(name="IFCWALL"))
        requirement = ids.Attribute(name="Name")
        spec.requirements.append(requirement)
        specs.specifications.append(spec)
        spec.set_usage("prohibited")

        model = ifcopenshell.file()
        wall = model.createIfcWall(Name="Wally")
        specs.validate(model)

        assert requirement.failures == []
        requirement.status = False  # As forced by a violated prohibited specification

        results = reporter.Json(specs).report()
        requirement_result = results["specifications"][0]["requirements"][0]
        assert requirement_result["status"] is False
        assert requirement_result["total_pass"] == 0
        assert requirement_result["total_fail"] == 1
        assert requirement_result["percent_pass"] == 0
