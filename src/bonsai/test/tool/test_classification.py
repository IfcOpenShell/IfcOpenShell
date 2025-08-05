# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import ifcopenshell.util.classification
import ifcopenshell.util.element
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.classification import Classification as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Classification)


class TestAddClassificationReferenceFromBSDD(NewFile):
    def test_add_classification_reference(self):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        context = bpy.context
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcSpace", predefined_type="SPACE", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.load_bsdd_dictionaries()
        uri = "https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0"
        tool.Bsdd.set_library_active(uri, True)
        props = tool.Bsdd.get_bsdd_props()
        tool.Classification.get_classification_props().classification_source = "BSDD"
        props.should_filter_ifc_class = True
        props.keyword = "Room"
        bpy.ops.bim.search_bsdd_classifications()
        props.active_classification_index = next(i for i, c in enumerate(props.classifications) if c.name == "Room")
        bpy.ops.bim.add_classification_reference_from_bsdd(obj="IfcSpace/Cube", obj_type="Object")
        refs = ifcopenshell.util.classification.get_references(element)
        assert len(refs) == 1
        assert next(iter(refs)).Location.startswith(uri)

    def test_add_classification_refence_with_props(self):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        context = bpy.context
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcSpace", predefined_type="SPACE", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.load_bsdd_dictionaries()
        uri = "https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0"
        tool.Bsdd.set_library_active(uri, True)
        props = tool.Bsdd.get_bsdd_props()
        tool.Classification.get_classification_props().classification_source = "BSDD"
        props.should_filter_ifc_class = True
        props.keyword = "Room"
        bpy.ops.bim.search_bsdd_classifications()
        # https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0/class/A-AAA
        props.active_classification_index = next(i for i, c in enumerate(props.classifications) if c.name == "Room")
        tool.Pset.get_pset_props(obj="IfcSpace/Cube", obj_type="Object").pset_name = uri
        bpy.ops.bim.add_classification_reference_from_bsdd(obj="IfcSpace/Cube", obj_type="Object")
        bpy.ops.bim.import_bsdd_classes(obj="IfcSpace/Cube", obj_type="Object")
        props.active_class_index = 0
        assert len(props.properties) == 1
        bsdd_property = props.properties[0]
        assert bsdd_property.pset == "Pset_SpaceCommon"
        assert bsdd_property.name == "Handicap Accessible"
        bsdd_property.is_selected = True
        bpy.ops.bim.add_bsdd_properties(obj="IfcSpace/Cube", obj_type="Object")
        pset = ifcopenshell.util.element.get_pset(element, "Pset_SpaceCommon")
        assert pset and pset["HandicapAccessible"] == False
        refs = ifcopenshell.util.classification.get_references(element)
        assert len(refs) == 1
        assert next(iter(refs)).Location.startswith(uri)

    def test_add_clasification_reference_with_object_type(self):
        """
        Check that an IfcSpace cube can be selected and receive a BSDD classification reference/property set
        even if its IFC class mismatches the class bSDD expects by disabling class filtering.
        Sets up the IFC4X3_ADD2 project, creates the cube, assigns IfcSpace, loads and activates the BSDD library,
        searches for "check-in conveyor", adds the classification reference with obj_type="Object", and imports it.
        Asserts 20 properties were loaded and that the first is in "ISet_AirportDomain", named "Conveying speed", and selected.
        """
        tool.Project.get_project_props().export_schema = "IFC4X3_ADD2"
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        context = bpy.context
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcSpace", predefined_type="SPACE", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.load_bsdd_dictionaries()
        uri = "https://identifier.buildingsmart.org/uri/bs-airport/airport/1.0"
        tool.Bsdd.set_library_active(uri, True)
        props = tool.Bsdd.get_bsdd_props()
        tool.Classification.get_classification_props().classification_source = "BSDD"
        props.should_filter_ifc_class = False  # Important due to class mismatch.
        props.keyword = "check-in conveyor"
        bpy.ops.bim.search_bsdd_classifications()
        # https://identifier.buildingsmart.org/uri/bs-airport/airport/1.0/class/AD-BHS-007

        props.active_classification_index = next(
            i for i, c in enumerate(props.classifications) if c.name.lower() == "check-in conveyor"
        )

        bpy.ops.bim.add_classification_reference_from_bsdd(obj="IfcSpace/Cube", obj_type="Object")
        tool.Pset.get_pset_props(obj="IfcSpace/Cube", obj_type="Object").pset_name = uri
        bpy.ops.bim.import_bsdd_classes(obj="IfcSpace/Cube", obj_type="Object")

        props.active_class_index = 0
        assert len(props.properties) == 20
        bsdd_property = props.properties[0]
        assert bsdd_property.pset == "ISet_AirportDomain"
        assert bsdd_property.name == "Conveying speed"
        assert not ifcopenshell.util.element.get_psets(element)
