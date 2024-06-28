# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api.project


class TestCreateFile(test.bootstrap.IFC4):
    def test_run(self):
        ifc = ifcopenshell.api.project.create_file()
        assert ifc.schema == "IFC4"
        ifc = ifcopenshell.api.project.create_file(version="IFC2X3")
        assert ifc.schema == "IFC2X3"
        assert ifc.wrapped_data.header.file_name.name == "/dev/null"
        assert ifc.wrapped_data.header.file_name.time_stamp
        assert "IfcOpenShell" in ifc.wrapped_data.header.file_name.preprocessor_version
        assert "IfcOpenShell" in ifc.wrapped_data.header.file_name.originating_system
        assert ifc.wrapped_data.header.file_name.authorization == "Nobody"
        assert ifc.wrapped_data.header.file_description.description == ("ViewDefinition[DesignTransferView]",)
