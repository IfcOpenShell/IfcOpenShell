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
#
# This file was generated with the assistance of an AI coding tool.

import os
import tempfile

import pytest

from ifc4d.common import InvalidInputPathError, InvalidOutputPathError, validate_input_path, validate_output_path
from ifc4d.csv2ifc import Csv2Ifc as ResourceCsv2Ifc
from ifc4d.csv2ifc import Ifc2Csv
from ifc4d.csv4d2ifc import Csv2Ifc
from ifc4d.ifc2msp import Ifc2Msp
from ifc4d.ifc2p6 import Ifc2P6
from ifc4d.msp2ifc import MSP2Ifc
from ifc4d.p62ifc import P62Ifc
from ifc4d.p6xer2ifc import P6XER2Ifc
from ifc4d.pp2ifc import PP2Ifc

IMPORTERS = [MSP2Ifc, P62Ifc, P6XER2Ifc, PP2Ifc, Csv2Ifc]


def make_importer(cls, path):
    converter = cls()
    if cls in (MSP2Ifc, P62Ifc):
        converter.xml = path
    elif cls is P6XER2Ifc:
        converter.xer = path
    elif cls is PP2Ifc:
        converter.pp = path
    else:
        converter.csv = path
    return converter


class TestValidateInputPath:
    def test_empty_path(self):
        with pytest.raises(InvalidInputPathError, match="No schedule file was selected"):
            validate_input_path("", "schedule file")

    def test_none_path(self):
        with pytest.raises(InvalidInputPathError, match="No schedule file was selected"):
            validate_input_path(None, "schedule file")

    def test_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(InvalidInputPathError, match="is a folder, not a file"):
                validate_input_path(tmp_dir, "schedule file")

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(InvalidInputPathError, match="does not exist"):
                validate_input_path(os.path.join(tmp_dir, "nope.xml"), "schedule file")

    def test_existing_file_is_returned(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "schedule.xml")
            with open(path, "w") as f:
                f.write("")
            assert validate_input_path(path, "schedule file") == path


class TestImportersRejectBadPaths:
    # The crash in #9409 was ET.parse() receiving a folder path from the file selector.
    @pytest.mark.parametrize("cls", IMPORTERS)
    def test_directory_is_rejected(self, cls):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(InvalidInputPathError):
                make_importer(cls, tmp_dir).execute()

    @pytest.mark.parametrize("cls", IMPORTERS)
    def test_empty_path_is_rejected(self, cls):
        with pytest.raises(InvalidInputPathError):
            make_importer(cls, "").execute()

    @pytest.mark.parametrize("cls", IMPORTERS)
    def test_missing_file_is_rejected(self, cls):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(InvalidInputPathError):
                make_importer(cls, os.path.join(tmp_dir, "missing.dat")).execute()

    def test_resource_csv_importer_rejects_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(InvalidInputPathError):
                ResourceCsv2Ifc(tmp_dir).execute()


class TestExportersRejectBadPaths:
    def test_msp_export_rejects_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            exporter = Ifc2Msp()
            exporter.xml = tmp_dir
            with pytest.raises(InvalidOutputPathError, match="is a folder, not a file"):
                exporter.execute()

    def test_p6_export_rejects_missing_folder(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            exporter = Ifc2P6()
            exporter.xml = os.path.join(tmp_dir, "nope", "schedule.xml")
            with pytest.raises(InvalidOutputPathError, match="does not exist"):
                exporter.execute()

    def test_resource_csv_export_rejects_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with pytest.raises(InvalidOutputPathError):
                Ifc2Csv(tmp_dir, None).execute()

    def test_validate_output_path_accepts_new_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = os.path.join(tmp_dir, "schedule.xml")
            assert validate_output_path(path, "schedule file") == path
