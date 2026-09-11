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

"""Regression guard for #9262: entering IFC Item/Edit mode must not blank
out a dimension/line annotation's decoration (arrows, text) in the viewport.

``ImportRepresentationItems._execute`` (bonsai/bim/module/geometry/operator.py)
hides the original annotation object with ``obj.hide_set(True)`` while its
representation items are edited, and only unhides it again in
``Geometry.disable_item_mode``. ``DecoratorData.object_decorators`` used to
filter candidates purely on ``obj.visible_get()``, so the hidden original
silently dropped out of the decorated list for the whole Item/Edit mode
session, and its arrow/text decoration disappeared from the viewport."""

import bpy
import ifcopenshell
import ifcopenshell.api.group
import pytest

import bonsai.tool as tool
from bonsai.bim.module.drawing.data import DecoratorData
from bonsai.bim.module.drawing.decoration import DecorationsHandler
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.drawing


def _create_dimension_annotation(drawing):
    obj = tool.Drawing.create_annotation_object(drawing, "DIMENSION")
    obj.name = "Test Dimension"
    ifc_context = tool.Drawing.get_annotation_context(tool.Drawing.get_drawing_target_view(drawing), "DIMENSION")
    element = tool.Drawing.run_root_assign_class(
        obj=obj,
        ifc_class="IfcAnnotation",
        predefined_type="DIMENSION",
        should_add_representation=True,
        context=ifc_context,
        ifc_representation_class=tool.Drawing.get_ifc_representation_class("DIMENSION"),
    )
    assert element
    ifcopenshell.api.group.assign_group(
        tool.Ifc.get(), group=tool.Drawing.get_drawing_group(drawing), products=[element]
    )
    tool.Collector.assign(obj)
    return obj


def _fake_decorations_handler():
    # A real DecorationsHandler() calls gpu.shader.from_builtin() per decorator,
    # which needs an initialized GPU context that headless test runs don't have.
    # object_decorators() only reads handler.decorators, so a stand-in with the
    # same keys is enough to exercise the visibility filtering under test.
    return type(
        "FakeHandler", (), {"decorators": {cls.objecttype: object() for cls in DecorationsHandler.decorators_classes}}
    )()


class TestObjectDecoratorsSurviveItemModeHide(NewFile):
    def setup_dimension_drawing(self):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        ifc = tool.Ifc.get()
        drawing = next(d for d in ifc.by_type("IfcAnnotation") if d.ObjectType == "DRAWING")
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        return _create_dimension_annotation(drawing)

    def test_hidden_representation_obj_still_gets_decorated(self):
        obj = self.setup_dimension_drawing()
        handler = _fake_decorations_handler()
        DecorationsHandler.installed = True
        try:
            decorated = [o for o, _ in DecoratorData.object_decorators(handler)]
            assert obj in decorated, "sanity check: a visible dimension should be decorated"

            # Simulate entering IFC Item/Edit mode: the original object gets
            # hidden while its representation items are edited (#9262).
            gprops = tool.Geometry.get_geometry_props()
            gprops.representation_obj = obj
            obj.hide_set(True)

            decorated = [o for o, _ in DecoratorData.object_decorators(handler)]
            assert obj in decorated, "dimension preview must survive Item/Edit mode"
        finally:
            DecorationsHandler.installed = None
            tool.Geometry.get_geometry_props().representation_obj = None

    def test_unrelated_hidden_annotation_stays_excluded(self):
        """A merely-hidden annotation (not the one being item-edited) is still filtered out."""
        obj = self.setup_dimension_drawing()
        obj.hide_set(True)

        handler = _fake_decorations_handler()
        DecorationsHandler.installed = True
        try:
            decorated = [o for o, _ in DecoratorData.object_decorators(handler)]
            assert obj not in decorated
        finally:
            DecorationsHandler.installed = None
