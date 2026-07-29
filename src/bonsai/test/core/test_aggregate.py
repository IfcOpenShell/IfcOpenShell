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

import bonsai.core.aggregate as subject
from test.core.bootstrap import aggregate, collector, ifc


class TestEnableEditingAggregate:
    def test_run(self, aggregate):
        aggregate.enable_editing("obj").should_be_called()
        subject.enable_editing_aggregate(aggregate, obj="obj")


class TestDisableEditingAggregate:
    def test_run(self, aggregate):
        aggregate.disable_editing("obj").should_be_called()
        subject.disable_editing_aggregate(aggregate, obj="obj")


class TestAssignObject:
    def test_run(self, ifc, aggregate, collector):
        aggregate.can_aggregate("relating_obj", "related_obj").should_be_called().will_return(True)
        ifc.get_entity("relating_obj").should_be_called().will_return("relating_object")
        aggregate.has_physical_body_representation("relating_object").should_be_called().will_return(False)
        ifc.get_entity("related_obj").should_be_called().will_return("related_object")
        ifc.run(
            "aggregate.assign_object", products=["related_object"], relating_object="relating_object"
        ).should_be_called().will_return("rel")
        aggregate.disable_editing("related_obj").should_be_called()
        collector.assign("relating_obj").should_be_called()
        collector.assign("related_obj").should_be_called()
        assert (
            subject.assign_object(ifc, aggregate, collector, relating_obj="relating_obj", related_obj="related_obj")
            == "rel"
        )


class TestUnassignObject:
    def test_run(self, ifc, aggregate, collector):
        ifc.get_entity("related_obj").should_be_called().will_return("element")
        aggregate.get_container("element").should_be_called().will_return("container")
        ifc.run("spatial.assign_container", products=["element"], relating_structure="container").should_be_called()
        ifc.run("aggregate.unassign_object", products=["element"]).should_be_called()
        collector.assign("relating_obj").should_be_called()
        collector.assign("related_obj").should_be_called()
        subject.unassign_object(ifc, aggregate, collector, relating_obj="relating_obj", related_obj="related_obj")

    def test_run_without_relating_obj_when_no_aggregate_is_found(self, ifc, aggregate, collector):
        # relating_obj is Optional and defaults to None: the function must look
        # it up itself via aggregate.get_relating_object(). When that lookup
        # finds no aggregate, it must not call ifc.get_object() with that
        # None result, and must not run any unassign/collector side effects.
        ifc.get_entity("related_obj").should_be_called().will_return("element")
        aggregate.get_container("element").should_be_called().will_return(None)
        aggregate.get_relating_object("element").should_be_called().will_return(None)
        subject.unassign_object(ifc, aggregate, collector, related_obj="related_obj")
