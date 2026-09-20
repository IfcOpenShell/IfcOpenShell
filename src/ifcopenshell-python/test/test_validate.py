# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

from pathlib import Path

import pytest
import tabulate

import ifcopenshell.validate

from .fixture_generate import FailObj, Result, parse_result

_filepaths = list((Path(__file__).parent / "fixtures/validate").glob("*.ifc"))


@pytest.mark.parametrize(
    "filepath,expected_result",
    [(fp, parse_result(fp)) for fp in _filepaths],
    ids=[fp.name for fp in _filepaths],
)
def test_file(filepath: Path, expected_result: Result):
    logger = ifcopenshell.validate.json_logger()
    try:
        ifcopenshell.validate.validate(filepath, logger)
    except ifcopenshell.SchemaError:
        pytest.skip()
    results = logger.statements

    print()
    print(filepath.name)
    print()
    print(f"{len(results)} errors")

    if results:
        print(
            tabulate.tabulate(
                [[c or "" for c in r.values()] for r in results],
                maxcolwidths=[20, 100, 20],
                tablefmt="simple_grid",
                headers=results[0].keys(),
            )
        )

    match expected_result:
        case FailObj(expected_count=expected_count):
            assert len(results) == expected_count
        case "pass":
            assert len(results) == 0


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
