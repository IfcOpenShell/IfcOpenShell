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


@pytest.mark.parametrize("attributes,expected_count", [("$,$,$,$", 4), ("3,1.E-05,#2,#5", 4), ("*,*,*,*", 0)])
@pytest.mark.parametrize(
    "backend",
    [
        "memory",
        "lazy",
        pytest.param(
            "rocksdb",
            marks=pytest.mark.skipif(
                not hasattr(ifcopenshell.ifcopenshell_wrapper, "RocksDbSerializer"), reason="RocksDB not available"
            ),
        ),
    ],
)
def test_derived_attributes(tmp_path, attributes, expected_count, backend):
    filepath = tmp_path / "derived.ifc"
    filepath.write_text(
        f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCCARTESIANPOINT((0.,0.,0.));
#2=IFCAXIS2PLACEMENT3D(#1,$,$);
#3=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#2,$);
#5=IFCDIRECTION((0.,1.));
#4=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',{attributes},#3,$,.MODEL_VIEW.,$);
ENDSEC;
END-ISO-10303-21;
"""
    )
    if backend == "rocksdb":
        rocks = tmp_path / "derived.rdb"
        ifcopenshell.convert_path_to_rocksdb(str(filepath), str(rocks))
        model = ifcopenshell.open(rocks)
    else:
        model = ifcopenshell.open(filepath, lazy=backend == "lazy")
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(model, logger)
    errors = [s for s in logger.statements if s["message"] == "Attribute is derived in subtype"]
    assert len(errors) == expected_count
    assert all(s["instance"].id() == 4 for s in errors)
    if not expected_count:
        output = tmp_path / "roundtrip.ifc"
        model.write(str(output))
        assert "'Body','Model',*,*,*,*,#3" in output.read_text()


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
