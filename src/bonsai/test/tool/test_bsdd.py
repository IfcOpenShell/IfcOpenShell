# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.tool.bsdd import Bsdd as subject
from test.bim.bootstrap import NewFile


class TestSearchClass(NewFile):
    def test_classes_missing_reference_code_do_not_crash_the_search(self):
        class FakeClient:
            def get_classes(self, **kwargs):
                return {
                    "name": "NL-SfB",
                    "uri": "https://example.org/dictionary/nl-sfb",
                    "classes": [
                        {"name": "No Reference Code", "uri": "https://example.org/class/1"},
                        {"name": "Kolom", "referenceCode": "17", "uri": "https://example.org/class/2"},
                        {"name": "Fundering", "referenceCode": "16", "uri": "https://example.org/class/3"},
                    ],
                }

        original_client = subject.client
        original_get_classification_props = tool.Classification.get_classification_props

        class FakeClassificationProps:
            classification_source = "https://example.org/dictionary/nl-sfb"

        subject.client = FakeClient()
        tool.Classification.get_classification_props = classmethod(lambda cls: FakeClassificationProps())
        try:
            total = subject.search_class("keyword", None)
        finally:
            subject.client = original_client
            tool.Classification.get_classification_props = original_get_classification_props

        props = subject.get_bsdd_props()
        assert total == 3
        assert [c.name for c in props.classifications] == ["Fundering", "Kolom", "No Reference Code"]
        assert [c.reference_code for c in props.classifications] == ["16", "17", ""]


class TestAddClassificationReferenceFromBsdd(NewFile):
    def test_class_without_reference_code_gets_no_identification(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        props = tool.Bsdd.get_bsdd_props()
        item = props.classifications.add()
        item.name = "No Reference Code"
        item.uri = "https://example.org/class/1"
        item.dictionary_name = "NL-SfB"
        item.dictionary_namespace_uri = "https://example.org/dictionary/nl-sfb"

        bpy.ops.bim.add_classification_reference_from_bsdd(obj="Wall", obj_type="Object")

        reference = ifc.by_type("IfcClassificationReference")[0]
        assert reference.Name == "No Reference Code"
        assert reference.Identification is None
