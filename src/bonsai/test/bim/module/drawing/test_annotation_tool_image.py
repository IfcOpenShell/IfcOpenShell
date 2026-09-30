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

import bonsai.tool as tool
from bonsai.bim.module.drawing.data import AnnotationData
from bonsai.bim.module.drawing.workspace import create_annotation_occurrence
from test.bim.bootstrap import NewIfc


class TestCreateAnnotationOccurrence(NewIfc):
    def test_image_annotation_from_type_without_representation(self):
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        drawing = tool.Ifc.get().by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        props = tool.Drawing.get_annotation_props()
        props.object_type = "IMAGE"
        props.type_name = "Logo"
        bpy.ops.bim.add_annotation_type()
        AnnotationData.is_loaded = False
        AnnotationData.load()
        props.relating_type_id = AnnotationData.data["relating_type_id"][-1][0]
        create_annotation_occurrence(bpy.context)
        assert [a.Name for a in tool.Ifc.get().by_type("IfcAnnotation")].count("Logo") == 1
