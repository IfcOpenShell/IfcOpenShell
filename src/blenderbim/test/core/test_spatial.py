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

import blenderbim.core.spatial as subject
from test.core.bootstrap import ifc, collector, container


class TestAssignContainer:
    def test_run(self, ifc, collector, container):
        container.can_contain("structure_obj", "element_obj").should_be_called().will_return(True)
        ifc.get_entity("structure_obj").should_be_called().will_return("structure")
        ifc.get_entity("element_obj").should_be_called().will_return("element")
        ifc.run(
            "spatial.assign_container", product="element", relating_structure="structure"
        ).should_be_called().will_return("rel")
        container.disable_editing("element_obj").should_be_called()
        collector.assign("element_obj").should_be_called()
        assert (
            subject.assign_container(
                ifc, collector, container, structure_obj="structure_obj", element_obj="element_obj"
            )
            == "rel"
        )


class TestEnableEditingContainer:
    def test_run(self, container):
        container.enable_editing("obj").should_be_called()
        container.import_containers().should_be_called()
        subject.enable_editing_container(container, obj="obj")


class TestDisableEditingContainer:
    def test_run(self, container):
        container.disable_editing("obj").should_be_called()
        subject.disable_editing_container(container, obj="obj")


class TestChangeSpatialLevel:
    def test_run(self, container):
        container.import_containers(parent="parent").should_be_called()
        subject.change_spatial_level(container, parent="parent")


class TestRemoveContainer:
    def test_run(self, ifc, collector):
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("spatial.remove_container", product="element").should_be_called()
        collector.assign("obj").should_be_called()
        subject.remove_container(ifc, collector, obj="obj")
