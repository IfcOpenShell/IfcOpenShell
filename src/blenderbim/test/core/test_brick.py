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

import blenderbim.core.brick as subject
from test.core.bootstrap import brick


class TestLoadBrickProject:
    def test_run(self, brick):
        brick.load_brick_file("filepath").should_be_called()
        brick.import_brick_classes("Class").should_be_called()
        brick.set_active_brick_class("Class").should_be_called()
        subject.load_brick_project(brick, filepath="filepath")


class TestViewBrickClass:
    def test_run(self, brick):
        brick.add_brick_breadcrumb().should_be_called()
        brick.clear_brick_browser().should_be_called()
        brick.import_brick_classes("brick_class").should_be_called()
        brick.import_brick_items("brick_class").should_be_called()
        brick.set_active_brick_class("brick_class").should_be_called()
        subject.view_brick_class(brick, brick_class="brick_class")


class TestViewBrickItem:
    def test_run(self, brick):
        brick.add_brick_breadcrumb().should_be_called()
        brick.clear_brick_browser().should_be_called()
        brick.get_item_class("item").should_be_called().will_return("brick_class")
        brick.import_brick_classes("brick_class").should_be_called()
        brick.import_brick_items("brick_class").should_be_called()
        brick.set_active_brick_class("brick_class").should_be_called()
        brick.select_browser_item("item").should_be_called()
        subject.view_brick_item(brick, item="item")


class TestRewindBrickClass:
    def test_run(self, brick):
        brick.pop_brick_breadcrumb().should_be_called().will_return("previous_class")
        brick.clear_brick_browser().should_be_called()
        brick.import_brick_classes("previous_class").should_be_called()
        brick.import_brick_items("previous_class").should_be_called()
        brick.set_active_brick_class("previous_class").should_be_called()
        subject.rewind_brick_class(brick)


class TestCloseBrickProject:
    def test_run(self, brick):
        brick.clear_project().should_be_called()
        subject.close_brick_project(brick)
