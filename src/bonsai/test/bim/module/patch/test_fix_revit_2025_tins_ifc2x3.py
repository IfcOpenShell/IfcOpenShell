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
#
# This file was generated with the assistance of an AI coding tool.

import logging
import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest
from ifcpatch.recipes import FixRevit2025TINs

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.patch


class TestFixRevit2025TINsIfc2x3(NewFile):
    def test_ifc2x3_tin_is_patched_and_keeps_its_class(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        ifcopenshell.api.root.create_entity(ifc, "IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        tin = ifcopenshell.api.root.create_entity(ifc, "IfcBuildingElementProxy", name="TIN")
        representation = ifcopenshell.api.geometry.add_mesh_representation(
            ifc,
            context=body,
            vertices=[[(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)]],
            faces=[[(0, 1, 2), (0, 2, 3)]],
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=tin, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(ifc, product=tin)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "tin.ifc"
            ifc.write(str(path))
            patcher = FixRevit2025TINs.Patcher(None, logging.getLogger("test"), str(path))
            patcher.patch()

        patched = tool.Ifc.get()
        assert patched.schema == "IFC2X3"
        assert patched.by_type("IfcBuildingElementProxy")[0].ObjectType == "TIN"
        assert [e.ObjectType for e in patched.by_type("IfcVirtualElement")] == ["TINBOUNDARY"]
