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

import os
import glob

import pytest

import ifcopenshell.validate


@pytest.mark.parametrize(
    "file",
    glob.glob(os.path.join(os.path.dirname(__file__), "fixtures/validate/*.ifc")),
)
def test_file(file):
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(file, logger)
    if file.startswith("fail-"):
        assert len(logger.statements) > 0
    if file.startswith("pass-"):
        assert len(logger.statements) == 0


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
