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

from types import SimpleNamespace

import bpy

import bonsai.bim.module.drawing.decoration
import bonsai.tool as tool
from bonsai.bim.module.drawing.data import DecoratorData
from test.bim.bootstrap import NewIfc


class TestObjectDecorators(NewIfc):
    def test_foreign_annotation_with_text_literal_gets_the_text_decorator(self, monkeypatch):
        monkeypatch.setattr(bonsai.bim.module.drawing.decoration.DecorationsHandler, "installed", True)
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        drawing = tool.Ifc.get().by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())

        ifc = tool.Ifc.get()
        element = ifc.createIfcAnnotation()
        context = ifc.createIfcGeometricRepresentationSubContext(ContextType="Plan", ContextIdentifier="Annotation")
        item = ifc.createIfcTextLiteralWithExtent(Literal="Text", Path="RIGHT", BoxAlignment="bottom-left")
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context, Items=[item])
        element.Representation = ifc.createIfcProductDefinitionShape(Representations=[representation])
        obj = bpy.data.objects.new("Foreign", None)
        tool.Ifc.link(element, obj)
        collection = tool.Blender.get_object_bim_props(tool.Ifc.get_object(drawing)).collection
        collection.objects.link(obj)

        text_decorator, misc_decorator = object(), object()
        handler = SimpleNamespace(decorators={"TEXT": text_decorator, "MISC": misc_decorator})
        assert (obj, text_decorator) in DecoratorData.object_decorators(handler)
