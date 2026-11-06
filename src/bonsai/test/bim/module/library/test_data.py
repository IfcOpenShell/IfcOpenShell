# This file was generated with the assistance of an AI coding tool.

import ifcopenshell

import bonsai.tool as tool
from bonsai.bim.module.library.data import LibrariesData
from test.bim.bootstrap import NewFile


class TestReferenceAttributes(NewFile):
    def list_attributes(self, schema):
        ifc = ifcopenshell.file(schema=schema)
        tool.Ifc.set(ifc)
        reference = ifc.createIfcLibraryReference(Name="Reference")
        props = tool.Library.get_library_props()
        props.references.add().ifc_definition_id = reference.id()
        props.active_reference_index = 0
        return {a["name"]: a["value"] for a in LibrariesData.reference_attributes()}

    def test_ifc2x3_reference_without_a_referenced_library_attribute(self):
        assert self.list_attributes("IFC2X3")["Name"] == "Reference"

    def test_ifc4_reference_hides_the_referenced_library(self):
        attributes = self.list_attributes("IFC4")
        assert attributes["Name"] == "Reference"
        assert "ReferencedLibrary" not in attributes
