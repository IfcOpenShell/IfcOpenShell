# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.model


def add_parametric_occurrence(ifc_class, template):
    props = tool.Root.get_root_props()
    props.ifc_product = "IfcElementType"
    props.ifc_class = ifc_class
    props.ifc_predefined_type = template
    props.representation_template = template
    bpy.ops.bim.add_element()
    bpy.ops.bim.add_occurrence(relating_type_id=tool.Ifc.get().by_type(ifc_class)[0].id())
    return tool.Ifc.get().by_type(ifc_class[:-4])[0]


class TestParametricOverallSize(NewIfc):
    @pytest.mark.parametrize(
        "ifc_class,template,props_name",
        [
            ("IfcDoorType", "DOOR", "BIMDoorProperties"),
            ("IfcWindowType", "WINDOW", "BIMWindowProperties"),
        ],
    )
    def test_zero_width_cannot_be_written_to_the_element(self, ifc_class, template, props_name):
        element = add_parametric_occurrence(ifc_class, template)
        obj = tool.Ifc.get_object(element)
        edit = ifc_class[3:-4].lower()
        getattr(bpy.ops.bim, f"enable_editing_{edit}")()
        getattr(obj, props_name).overall_width = 0
        getattr(bpy.ops.bim, f"finish_editing_{edit}")()
        assert element.OverallWidth > 0
