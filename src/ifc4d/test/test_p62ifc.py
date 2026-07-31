# Ifc4D - IFC scheduling utility
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Ifc4D.
#
# Ifc4D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc4D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc4D.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import tempfile
from pathlib import Path

from ifc4d.p62ifc import P62Ifc

P6_XML = """<?xml version="1.0" encoding="UTF-8"?>
<APIBusinessObjects xmlns="http://xmlns.oracle.com/Primavera/P6/V1/APIBusinessObjects">
  <Project>
    <ObjectId>1</ObjectId>
    <Name>My Real Schedule Name</Name>
    <ActivityDefaultCalendarObjectId>100</ActivityDefaultCalendarObjectId>
  </Project>
</APIBusinessObjects>
"""


class TestP62IfcParseXml:
    def test_project_name_is_read_from_the_namespaced_xml(self) -> None:
        # The P6 XML uses a default namespace, so every "pr:" tagged
        # find/findtext call must pass namespaces=self.ns to resolve.
        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "schedule.xml"
            xml_path.write_text(P6_XML)

            importer = P62Ifc()
            importer.xml = str(xml_path)
            importer.parse_xml()

        assert importer.project["Name"] == "My Real Schedule Name"
