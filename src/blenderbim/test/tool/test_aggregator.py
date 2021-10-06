import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.aggregator import Aggregator as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Aggregator)


class TestEnableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        assert obj.BIMObjectAggregateProperties.is_editing is True


class TestDisableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        subject.enable_editing(obj)
        subject.disable_editing(obj)
        assert obj.BIMObjectAggregateProperties.is_editing is False


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

    def test_aggregates_with_meshes_are_invalid(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcElementAssembly()
        element_obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        tool.Ifc.link(element, element_obj)
        subelement = ifc.createIfcBeam()
        subelement_obj = bpy.data.objects.new("Object", None)
        tool.Ifc.link(subelement, subelement_obj)
        assert subject.can_aggregate(element_obj, subelement_obj) is False
