# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.brick import Brick as subject
from blenderbim.tool.brick import BrickStore


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Brick)


class TestAddBrickBreadcrumb(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        subject.add_brick_breadcrumb()
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[0].name == "brick_class"
        subject.add_brick_breadcrumb()
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[1].name == "brick_class"


class TestClearBrickBrowser(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.bricks.add()
        subject.clear_brick_browser()
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 0


class TestClearProject(NewFile):
    def test_run(self):
        BrickStore.graph = "graph"
        bpy.context.scene.BIMBrickProperties.active_brick_class == "brick_class"
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "foo"
        subject.clear_project()
        assert BrickStore.graph is None
        assert bpy.context.scene.BIMBrickProperties.active_brick_class == ""
        assert len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) == 0


class TestGetItemClass(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        assert subject.get_item_class("http://buildsys.org/ontologies/bldg#chiller") == "Chiller"


class TestImportBrickClasses(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_classes("Class")
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 4
        brick = bpy.context.scene.BIMBrickProperties.bricks[0]
        assert brick.name == "Equipment"
        assert brick.uri == "https://brickschema.org/schema/Brick#Equipment"
        assert brick.total_items == 20
        brick = bpy.context.scene.BIMBrickProperties.bricks[1]
        assert brick.name == "Location"
        assert brick.uri == "https://brickschema.org/schema/Brick#Location"
        assert brick.total_items == 18


class TestImportBrickItems(NewFile):
    def test_run(self):
        TestLoadBrickFile().test_run()
        subject.import_brick_items("Room")
        assert len(bpy.context.scene.BIMBrickProperties.bricks) == 8
        brick = bpy.context.scene.BIMBrickProperties.bricks[0]
        assert brick.name == "RM100_room"
        assert brick.uri == "http://buildsys.org/ontologies/bldg#RM100_room"
        assert brick.total_items == 0
        brick = bpy.context.scene.BIMBrickProperties.bricks[1]
        assert brick.name == "RM103_room"
        assert brick.uri == "http://buildsys.org/ontologies/bldg#RM103_room"
        assert brick.total_items == 0


class TestLoadBrickFile(NewFile):
    def test_run(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(cwd, "..", "files", "building.ttl")
        subject.load_brick_file(filepath)
        assert BrickStore.graph


class TestPopBrickBreadcrumb(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add().name = "bar"
        assert subject.pop_brick_breadcrumb() == "bar"
        assert len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) == 1
        assert bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[0].name == "foo"


class TestSelectBrowserItem(NewFile):
    def test_run(self):
        subject.set_active_brick_class("brick_class")
        assert bpy.context.scene.BIMBrickProperties.active_brick_class == "brick_class"


class TestSetActiveBrickClass(NewFile):
    def test_run(self):
        bpy.context.scene.BIMBrickProperties.bricks.add().name = "foo"
        bpy.context.scene.BIMBrickProperties.bricks.add().name = "bar"
        subject.select_browser_item("namespace#bar")
        assert bpy.context.scene.BIMBrickProperties.active_brick_index == 1
