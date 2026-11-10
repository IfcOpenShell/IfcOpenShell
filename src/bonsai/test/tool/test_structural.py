# This file was generated with the assistance of an AI coding tool.

import ifcopenshell

import bonsai.tool as tool
from bonsai.tool.structural import Structural as subject
from test.bim.bootstrap import NewFile


class TestGetVertexRepresentation(NewFile):
    def test_a_connection_without_a_representation(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        connection = ifc.createIfcStructuralPointConnection()
        assert subject.get_vertex_representation(connection) is None
