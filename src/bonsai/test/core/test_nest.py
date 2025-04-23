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

import bonsai.core.nest as subject
from test.core.bootstrap import ifc, nest, collector


class TestEnableEditingNeset:
    def test_run(self, nest):
        nest.enable_editing("obj").should_be_called()
        subject.enable_editing_nest(nest, obj="obj")


class TestDisableEditingNest:
    def test_run(self, nest):
        nest.disable_editing("obj").should_be_called()
        subject.disable_editing_nest(nest, obj="obj")


class TestAssignObject:
    def test_run(self, ifc, nest, collector):
        nest.can_nest("relating_obj", "related_obj").should_be_called().will_return(True)
        ifc.get_entity("relating_obj").should_be_called().will_return("relating_object")
        ifc.get_entity("related_obj").should_be_called().will_return("related_object")
        ifc.run(
            "nest.assign_object", related_objects=["related_object"], relating_object="relating_object"
        ).should_be_called().will_return("rel")
        nest.disable_editing("related_obj").should_be_called()
        collector.assign("relating_obj").should_be_called()
        collector.assign("related_obj").should_be_called()
        assert (
            subject.assign_object(ifc, nest, collector, relating_obj="relating_obj", related_obj="related_obj") == "rel"
        )


class TestUnassignObject:
    def test_run(self, ifc, nest, collector):
        ifc.get_entity("related_obj").should_be_called().will_return("element")
        nest.get_container("element").should_be_called().will_return("container")
        ifc.run("spatial.assign_container", products=["element"], relating_structure="container").should_be_called()
        ifc.run("nest.unassign_object", related_objects=["element"]).should_be_called().will_return("rel")
        collector.assign("relating_obj").should_be_called()
        collector.assign("related_obj").should_be_called()
        subject.unassign_object(ifc, nest, collector, relating_obj="relating_obj", related_obj="related_obj")
