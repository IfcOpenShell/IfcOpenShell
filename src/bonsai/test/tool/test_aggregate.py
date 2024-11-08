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

import bpy
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.util.shape_builder
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.aggregate import Aggregate as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Aggregate)


class TestCanAggregate(NewFile):
    def test_elements_can_aggregate(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcElementAssembly()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        subelement = ifc.createIfcBeam()
        subelement_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(subelement, subelement_obj)
        assert subject.can_aggregate(element_obj, subelement_obj) is True

    def test_spatial_elements_can_aggregate(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcSite()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        subelement = ifc.createIfcBuilding()
        subelement_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(subelement, subelement_obj)
        assert subject.can_aggregate(element_obj, subelement_obj) is True

    def test_spatial_elements_can_aggregate_2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        element = ifc.createIfcSite()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        subelement = ifc.createIfcBuilding()
        subelement_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(subelement, subelement_obj)
        assert subject.can_aggregate(element_obj, subelement_obj) is True

    def test_spatial_elements_and_projects_can_aggregate(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcProject()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        subelement = ifc.createIfcBuilding()
        subelement_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(subelement, subelement_obj)
        assert subject.can_aggregate(element_obj, subelement_obj) is True

    def test_spatial_elements_and_projects_can_aggregate_2x3(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        element = ifc.createIfcProject()
        element_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(element, element_obj)
        subelement = ifc.createIfcBuilding()
        subelement_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(subelement, subelement_obj)
        assert subject.can_aggregate(element_obj, subelement_obj) is True

    def test_unlinked_elements_cannot_aggregate(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element_obj = bpy.data.objects.new("Object", None)
        subelement_obj = bpy.data.objects.new("Object", None)
        assert subject.can_aggregate(element_obj, subelement_obj) is False


class TestHasPhysicalBodyRepresentation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcElementAssembly()
        assert subject.has_physical_body_representation(element) is False
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(ifc)
        context = ifcopenshell.api.context.add_context(ifc, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
        )
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc)
        origin = builder.create_axis2_placement_3d()
        block = ifc.createIfcCsgSolid(ifc.createIfcBlock(origin, 200, 200, 200))
        rep = builder.get_representation(context=body, items=[block])
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=rep)
        assert subject.has_physical_body_representation(element) is True


class TestDisableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        subject.disable_editing(obj)
        assert obj.BIMObjectAggregateProperties.is_editing is False


class TestEnableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        assert obj.BIMObjectAggregateProperties.is_editing is True


class TestGetContainer(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        container = ifc.createIfcBuildingStorey()
        ifcopenshell.api.run("spatial.assign_container", ifc, products=[element], relating_structure=container)
        assert subject.get_container(element) == container
