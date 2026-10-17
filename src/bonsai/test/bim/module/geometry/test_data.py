# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.geometry.data import RepresentationsData
from test.bim.bootstrap import NewFile


class TestRepresentations(NewFile):
    def test_a_mapped_representation_whose_source_has_no_representation_type(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext(ContextType="Model")
        source = ifc.createIfcShapeRepresentation(context, "Body", None, [])
        mapped_item = ifc.createIfcMappedItem(
            ifc.createIfcRepresentationMap(
                ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))), source
            ),
            ifc.createIfcCartesianTransformationOperator3D(LocalOrigin=ifc.createIfcCartesianPoint((0.0, 0.0, 0.0))),
        )
        mapped = ifc.createIfcShapeRepresentation(context, "Body", "MappedRepresentation", [mapped_item])
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        wall.Representation = ifc.createIfcProductDefinitionShape(Representations=[mapped])
        obj = bpy.data.objects.new("Wall", None)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        tool.Ifc.link(wall, obj)
        assert [r["RepresentationType"] for r in RepresentationsData.representations()] == ["*"]
