# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.pset_template

import bonsai.core.tool  # noqa: F401

PSET_TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "bonsai" / "tool" / "pset_template.py"


def test_add_pset_as_template_supports_ifc4x3_specification():
    mock_tool = MagicMock()
    mock_tool.Ifc.Operator = object
    mock_bonsai = MagicMock()
    mock_bonsai.core = sys.modules["bonsai.core"]
    mock_bonsai.tool = mock_tool

    with patch.dict(
        sys.modules,
        {
            "bpy": MagicMock(),
            "bonsai": mock_bonsai,
            "bonsai.bim": MagicMock(),
            "bonsai.bim.handler": MagicMock(),
            "bonsai.bim.ifc": MagicMock(),
            "bonsai.bim.module": MagicMock(),
            "bonsai.bim.module.pset_template": MagicMock(),
            "bonsai.bim.module.pset_template.prop": MagicMock(),
            "bonsai.tool": mock_tool,
        },
    ):
        spec = importlib.util.spec_from_file_location("pset_template_under_test", PSET_TEMPLATE_PATH)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
        mod.tool.Ifc.get = MagicMock(return_value=ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Custom")
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"PropA": "ValueA"})
        pset.HasProperties[0].Specification = "IFC4X3 spec text"
        prop_b = ifc.create_entity("IfcPropertySingleValue", Name="PropB", Specification="Null nominal")
        pset.HasProperties = list(pset.HasProperties) + [prop_b]

        library = ifcopenshell.file()
        pset_template = mod.PsetTemplate.add_pset_as_template("Pset_Custom", library)
        assert pset_template.is_a("IfcPropertySetTemplate")
        templates = {t.Name: t for t in pset_template.HasPropertyTemplates}
        assert set(templates.keys()) == {"PropA", "PropB"}
        assert templates["PropA"].Description == "IFC4X3 spec text"
        assert templates["PropA"].PrimaryMeasureType == "IfcLabel"
        assert templates["PropB"].Description == "Null nominal"
        assert templates["PropB"].PrimaryMeasureType == "IfcLabel"
