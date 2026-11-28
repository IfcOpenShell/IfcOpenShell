# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import ifcopenshell
import pytest

import bonsai.bim.module.project.operator as project_operator
import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.project


class TestCreateProjectSurfaceStyles(NewFile):
    def test_creates_blender_materials_for_orphan_surface_styles(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        orphan_style = ifc_file.create_entity("IfcSurfaceStyle", Name="OrphanStyle", Side="BOTH")
        linked_style = ifc_file.create_entity("IfcSurfaceStyle", Name="LinkedStyle", Side="BOTH")

        fake_importer = MagicMock()
        fake_importer_cls = MagicMock(return_value=fake_importer)
        fake_settings_factory = MagicMock(return_value=SimpleNamespace())

        def fake_get_object(entity):
            if entity == linked_style:
                return SimpleNamespace(name="LinkedStyle")
            return None

        op = project_operator.CreateProject()
        with (
            patch.object(tool.Ifc, "get", return_value=ifc_file),
            patch.object(tool.Ifc, "get_object", side_effect=fake_get_object),
            patch.object(project_operator.import_ifc.IfcImportSettings, "factory", fake_settings_factory),
            patch.object(project_operator.import_ifc, "IfcImporter", fake_importer_cls),
        ):
            op.create_objects_for_orphan_spatial_elements(SimpleNamespace())

        fake_importer.create_style.assert_called_once_with(orphan_style)
        fake_importer.create_generic_elements.assert_not_called()
