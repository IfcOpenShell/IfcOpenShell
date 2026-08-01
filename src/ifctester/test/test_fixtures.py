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

"""End-to-end regression tests for specific reported defects.

Each test here loads a minimal .ids/.ifc pair from test/fixtures/ through
the same entry points ifctester's own CLI uses (ids.open, ifcopenshell.open,
Ids.validate), rather than exercising a facet's __call__ directly.
"""

import os

import ifcopenshell

from ifctester import ids, reporter

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TestPropertyOptionalMaskFixture:
    def test_a_bad_value_in_one_pset_is_not_masked_by_another_lacking_it(self):
        # One matching pset lacks the optional property (Foo_Missing), a
        # second has it set to a value that fails the requirement
        # (Foo_Bad, Foo="NotBar" against a required value of "Bar"). The
        # optional short-circuit on the first pset must not end the whole
        # facet check before the second, genuinely bad, pset is examined.
        specs = ids.open(os.path.join(FIXTURES, "property_optional_mask", "property_optional_mask.ids"))
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "property_optional_mask", "property_optional_mask.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False
        assert spec.requirements[0].status is False


class TestConsoleProhibitedCountFixture:
    def test_a_violated_prohibition_does_not_print_a_full_success_count(self):
        # A prohibited specification (no walls allowed) violated by one
        # wall. specification.failed_entities is never populated for a
        # prohibited violation, so the printed success count must not be
        # derived from it as if it meant "all passed".
        specs = ids.open(os.path.join(FIXTURES, "console_prohibited", "console_prohibited.ids"))
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "console_prohibited", "console_prohibited.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False

        console = reporter.Console(specs, use_colour=False)
        console.report()

    def test_a_violated_prohibition_prints_zero_of_one(self, capsys):
        specs = ids.open(os.path.join(FIXTURES, "console_prohibited", "console_prohibited.ids"))
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "console_prohibited", "console_prohibited.ifc"))
        specs.validate(ifc)
        reporter.Console(specs, use_colour=False).report()
        printed = capsys.readouterr().out
        assert "(0/1)" in printed
        assert "(1/1)" not in printed


class TestTxtDroppedTextFixture:
    def test_a_failed_specification_shows_its_label_and_reason(self):
        # Txt.print used "txt + '\\n' if end is None else end", which due to
        # operator precedence discards txt whenever a caller passes an
        # explicit end=. Console.report_specification passes end="" for the
        # [FAIL]/(count) labels and every failure reason, so those must
        # survive in Txt's accumulated text.
        specs = ids.open(os.path.join(FIXTURES, "txt_dropped_text", "txt_dropped_text.ids"))
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "txt_dropped_text", "txt_dropped_text.ifc"))
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is False

        txt = reporter.Txt(specs)
        txt.report()
        assert "[FAIL] (0/1)" in txt.text
        assert "is empty" in txt.text


class TestJsonForcedFailPassCountFixture:
    def test_a_forced_failed_requirement_is_not_reported_as_full_pass(self):
        # See the commit message for why requirement.status is forced here.
        specs = ids.open(os.path.join(FIXTURES, "json_prohibited", "json_prohibited.ids"))
        ifc = ifcopenshell.open(os.path.join(FIXTURES, "json_prohibited", "json_prohibited.ifc"))
        specs.validate(ifc)
        requirement = specs.specifications[0].requirements[0]
        assert requirement.failures == []
        requirement.status = False  # As forced by a violated prohibited specification (#9189).

        results = reporter.Json(specs).report()
        requirement_result = results["specifications"][0]["requirements"][0]
        assert requirement_result["total_pass"] == 0
        assert requirement_result["total_fail"] == 1
        assert requirement_result["percent_pass"] == 0
