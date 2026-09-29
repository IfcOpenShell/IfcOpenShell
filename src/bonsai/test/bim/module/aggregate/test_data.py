# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.guid

import bonsai.tool as tool
from bonsai.bim.module.aggregate.data import AggregateData
from test.bim.bootstrap import NewFile


class TestTotalLinkedAggregate(NewFile):
    def add_aggregate_in_group(self, group_name):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        aggregate = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcElementAssembly")
        part = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeam")
        ifcopenshell.api.aggregate.assign_object(ifc, products=[part], relating_object=aggregate)
        group = ifc.createIfcGroup(ifcopenshell.guid.new(), Name=group_name)
        ifcopenshell.api.group.assign_group(ifc, products=[aggregate], group=group)
        obj = bpy.data.objects.new("Aggregate", None)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        tool.Ifc.link(aggregate, obj)

    def test_an_aggregate_assigned_to_an_unnamed_group(self):
        self.add_aggregate_in_group(None)
        assert AggregateData.total_linked_aggregate() is None

    def test_an_aggregate_assigned_to_a_linked_aggregate_group(self):
        self.add_aggregate_in_group("BBIM_Linked_Aggregate/1")
        assert AggregateData.total_linked_aggregate() == 1
