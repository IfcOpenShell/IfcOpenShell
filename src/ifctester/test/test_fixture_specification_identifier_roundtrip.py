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


class TestSpecificationIdentifierRoundtripFixture:
    def test_identifier_is_parsed_from_ids_file(self):
        # buildingSMART/IDS#339: "identifier" is the documented place for a
        # short reference code such as "SP01". If ids.open() does not parse
        # it, every downstream consumer silently loses a value the author
        # explicitly provided.
        specs = ids.open(
            os.path.join(
                FIXTURES,
                "specification_identifier_roundtrip",
                "specification_identifier_roundtrip.ids",
            )
        )
        spec = specs.specifications[0]
        assert spec.identifier == "SP01"

    def test_identifier_survives_to_string_roundtrip(self):
        path = os.path.join(
            FIXTURES,
            "specification_identifier_roundtrip",
            "specification_identifier_roundtrip.ids",
        )
        specs = ids.open(path)
        ifc = ifcopenshell.open(
            os.path.join(
                FIXTURES,
                "specification_identifier_roundtrip",
                "specification_identifier_roundtrip.ifc",
            )
        )
        specs.validate(ifc)
        spec = specs.specifications[0]
        assert spec.status is True

        rewritten = ids.Ids().parse(specs.asdict())
        assert rewritten.specifications[0].identifier == "SP01"
        assert 'identifier="SP01"' in specs.to_string()

    def test_identifier_is_not_dropped_from_json_report(self):
        # A value the author sets on the schema must reach the structured
        # report dict every downstream reporter (Json, Html, Ods, Bcf) is
        # built on, not just the in-memory Specification object.
        specs = ids.open(
            os.path.join(
                FIXTURES,
                "specification_identifier_roundtrip",
                "specification_identifier_roundtrip.ids",
            )
        )
        ifc = ifcopenshell.open(
            os.path.join(
                FIXTURES,
                "specification_identifier_roundtrip",
                "specification_identifier_roundtrip.ifc",
            )
        )
        specs.validate(ifc)
        engine = reporter.Json(specs)
        results = engine.report()
        assert results["specifications"][0]["identifier"] == "SP01"
