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
import tempfile
import time

import pytest

import ifcopenshell.validate


@pytest.mark.parametrize(
    "file",
    glob.glob(os.path.join(os.path.dirname(__file__), "fixtures/validate/*.ifc")),
)
def test_file(file):
    logger = ifcopenshell.validate.json_logger()
    with tempfile.TemporaryDirectory() as d:
        rocks = os.path.join(d, os.path.basename(file) + ".rdb")

        # certain errors such as attribute counts / invalid enumeration literals
        # are only captured during parsing of SPF as they are not represented in
        # rocksdb, these errors need to be captured during conversion to rocksdb
        # but can still be handled ifcopenshell.validate logger.
        ifcopenshell.get_log()
        ifcopenshell.ifcopenshell_wrapper.set_log_format_json()
        ifcopenshell.convert_path_to_rocksdb(file, rocks)
        log = ifcopenshell.get_log()

        try:
            ifcopenshell.validate.validate(rocks, logger)
        except ifcopenshell.SchemaError as e:
            pytest.skip()
        ifcopenshell.validate.log_internal_cpp_errors(None, file, logger, log_content=log)
        file = os.path.basename(file)
        if file.startswith("fail-"):
            assert len(logger.statements) > 0
        if file.startswith("pass-"):
            assert len(logger.statements) == 0


if __name__ == "__main__":
    pytest.main(["-sx", __file__])
