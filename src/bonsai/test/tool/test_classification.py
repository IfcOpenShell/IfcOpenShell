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

        bpy.ops.bim.load_bsdd_domains()
        uri = "https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0"
        bpy.ops.bim.set_active_bsdd_domain(name="CCI Construction", uri=uri)
        props = context.scene.BIMBSDDProperties
        bpy.context.scene.BIMClassificationProperties.classification_source = "BSDD"
        props.should_filter_ifc_class = True
        props.keyword = "Room"
        bpy.ops.bim.search_bsdd_classifications()
        props.active_classification_index = next(i for i, c in enumerate(props.classifications) if c.name == "Room")
        bpy.ops.bim.add_classification_reference_from_bsdd(obj="IfcSpace/Cube", obj_type="Object")
        refs = ifcopenshell.util.classification.get_references(element)
        assert len(refs) == 1
        assert list(refs)[0].Location.startswith(uri)

    def test_add_classification_refence_with_props(self):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        context = bpy.context
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcSpace", predefined_type="SPACE", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.load_bsdd_domains()
        uri = "https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0"
        bpy.ops.bim.set_active_bsdd_domain(name="CCI Construction", uri=uri)
        props = context.scene.BIMBSDDProperties
        bpy.context.scene.BIMClassificationProperties.classification_source = "BSDD"
        props.should_filter_ifc_class = True
        props.keyword = "Room"
        bpy.ops.bim.search_bsdd_classifications()
        # https://identifier.buildingsmart.org/uri/molio/cciconstruction/1.0/class/A-AAA
        props.active_classification_index = next(i for i, c in enumerate(props.classifications) if c.name == "Room")
        bpy.ops.bim.get_bsdd_classification_properties()
        psets = props.classification_psets
        assert len(psets) == 1
        pset = psets[0]
        assert pset.name == "Pset_SpaceCommon"
        assert len(pset.properties) == 1
        pset_prop = pset.properties[0]
        assert pset_prop.name == "HandicapAccessible"
        pset_prop.bool_value = True

        bpy.ops.bim.add_classification_reference_from_bsdd(obj="IfcSpace/Cube", obj_type="Object")
        pset = ifcopenshell.util.element.get_pset(element, "Pset_SpaceCommon")
        assert pset and pset["HandicapAccessible"] == True
        refs = ifcopenshell.util.classification.get_references(element)
        assert len(refs) == 1
        assert list(refs)[0].Location.startswith(uri)

    def test_add_clasification_reference_with_object_type(self):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        context = bpy.context
        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcSpace", predefined_type="SPACE", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.load_bsdd_domains()
        uri = "https://identifier.buildingsmart.org/uri/ifcairport/ifcairport/1.0"
        bpy.ops.bim.set_active_bsdd_domain(name="IFC Airport", uri=uri)
        props = context.scene.BIMBSDDProperties
        bpy.context.scene.BIMClassificationProperties.classification_source = "BSDD"
        props.should_filter_ifc_class = False  # Important due to class mismatch.
        props.keyword = "Check-In Conveyor"
        bpy.ops.bim.search_bsdd_classifications()
        # https://identifier.buildingsmart.org/uri/ifcairport/ifcairport/1.0/class/ifcairport0000000004
        props.active_classification_index = next(
            i for i, c in enumerate(props.classifications) if c.name == "Check-In Conveyor"
        )
        bpy.ops.bim.get_bsdd_classification_properties()
        psets = props.classification_psets
        assert len(psets) == 1
        pset = psets[0]
        assert pset.name == "undefined_set"
        assert len(pset.properties) == 1
        pset_prop = pset.properties[0]
        assert pset_prop.name == "ObjectType"

        bpy.ops.bim.add_classification_reference_from_bsdd(obj="IfcSpace/Cube", obj_type="Object")
        assert element.ObjectType == "CHECKINCONVEYOR"
        assert not ifcopenshell.util.element.get_psets(element)
