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

import blenderbim.core.aggregate as subject
from test.core.bootstrap import ifc, aggregate, collector


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
        ifc.get_entity("related_obj").should_be_called().will_return("related_object")
        ifc.run(
            "aggregate.assign_object", product="related_object", relating_object="relating_object"
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
        ifc.run("spatial.assign_container", product="element", relating_structure="container").should_be_called()
        ifc.run("aggregate.unassign_object", product="element").should_be_called().will_return("rel")
        collector.assign("relating_obj").should_be_called()
        collector.assign("related_obj").should_be_called()
        subject.unassign_object(ifc, aggregate, collector, relating_obj="relating_obj", related_obj="related_obj")
