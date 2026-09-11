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

import glob
import os
import tempfile

import pytest

import ifcopenshell
import ifcopenshell.validate


@pytest.mark.parametrize(
    "file",
    glob.glob(os.path.join(os.path.dirname(__file__), "fixtures/validate/*.ifc")),
)
def test_file(file):
    logger = ifcopenshell.validate.json_logger()
    try:
        ifcopenshell.validate.validate(file, logger)
    except ifcopenshell.SchemaError as e:
        pytest.skip()
    file = os.path.basename(file)
    if file.startswith("fail-"):
        assert len(logger.statements) > 0
    if file.startswith("pass-"):
        assert len(logger.statements) == 0


def test_validate_rejects_sqlite_file_instead_of_crashing():
    # ifcopenshell.sqlite only keeps a partial, query-oriented header (see
    # ifcopenshell.sql.sqlite.header), so it cannot be validated. Regression
    # test for validate() previously raising an unguarded AttributeError
    # deep inside validate_ifc_header() instead of failing cleanly.
    from ifcpatch.recipes import Ifc2Sql

    ifc_path = os.path.join(os.path.dirname(__file__), "files", "basic.ifc")
    ifc_file = ifcopenshell.open(ifc_path)
    with tempfile.NamedTemporaryFile(suffix=".ifcsqlite") as tmp:
        Ifc2Sql.Patcher(ifc_file, database=tmp.name).patch()
        ifc_sqlite = ifcopenshell.open(tmp.name)
        assert isinstance(ifc_sqlite, ifcopenshell.sqlite)

        logger = ifcopenshell.validate.json_logger()
        with pytest.raises(NotImplementedError):
            ifcopenshell.validate.validate(ifc_sqlite, logger)


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
