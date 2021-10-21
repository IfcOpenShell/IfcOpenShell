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

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.type import Type as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Type)


class TestDisableEditing(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        obj.BIMTypeProperties.is_editing_type = True
        subject.disable_editing(obj)
        assert obj.BIMTypeProperties.is_editing_type is False


class TestGetAnyRepresentation(NewFile):
    def test_get_product_representation(self):
        ifc = ifcopenshell.file()
        representation = ifc.createIfcShapeRepresentation()
        element = ifc.createIfcWall(Representation=ifc.createIfcProductRepresentation(Representations=[representation]))
        assert subject.get_any_representation(element) == representation

    def test_get_type_product_representation(self):
        ifc = ifcopenshell.file()
        representation = ifc.createIfcShapeRepresentation()
        element = ifc.createIfcWallType(
            RepresentationMaps=[ifc.createIfcRepresentationMap(MappedRepresentation=representation)]
        )
        assert subject.get_any_representation(element) == representation


class TestGetBodyContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW"
        )
        tool.Ifc.set(ifc)
        assert subject.get_body_context() == context


class TestGetBodyRepresentation(NewFile):
    def test_get_product_representation(self):
        ifc = ifcopenshell.file()
        rep = ifc.createIfcShapeRepresentation(ContextOfItems=ifc.createIfcGeometricRepresentationSubContext())
        body_rep = ifc.createIfcShapeRepresentation(
            ContextOfItems=ifc.createIfcGeometricRepresentationSubContext(ContextIdentifier="Body")
        )
        element = ifc.createIfcWall(Representation=ifc.createIfcProductRepresentation(Representations=[rep, body_rep]))
        assert subject.get_body_representation(element) == body_rep

    def test_get_type_product_representation(self):
        ifc = ifcopenshell.file()
        rep = ifc.createIfcShapeRepresentation(ContextOfItems=ifc.createIfcGeometricRepresentationSubContext())
        body_rep = ifc.createIfcShapeRepresentation(
            ContextOfItems=ifc.createIfcGeometricRepresentationSubContext(ContextIdentifier="Body")
        )
        element = ifc.createIfcWallType(
            RepresentationMaps=[
                ifc.createIfcRepresentationMap(MappedRepresentation=rep),
                ifc.createIfcRepresentationMap(MappedRepresentation=body_rep),
            ]
        )
        assert subject.get_body_representation(element) == body_rep


class TestGetIfcRepresentationClass(NewFile):
    def test_detecting_profile_set_representations(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcColumn()
        ifc.createIfcRelAssociatesMaterial(
            RelatingMaterial=ifc.createIfcMaterialProfileSetUsage(), RelatedObjects=[element]
        )
        assert subject.get_ifc_representation_class(element) == "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage"

    def test_detecting_layer_set_representations(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcColumn()
        ifc.createIfcRelAssociatesMaterial(
            RelatingMaterial=ifc.createIfcMaterialLayerSetUsage(), RelatedObjects=[element]
        )
        assert (
            subject.get_ifc_representation_class(element)
            == "IfcExtrudedAreaSolid/IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"
        )

    def test_returning_null_for_non_parametric_represntations(self):
        ifc = ifcopenshell.file()
        assert subject.get_ifc_representation_class(ifc.createIfcColumn()) is None


class TestGetProfileSetUsage(NewFile):
    def test_getting_a_profile_set_usage(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcColumn()
        assert subject.get_profile_set_usage(element) is None
        usage = ifc.createIfcMaterialProfileSetUsage()
        ifc.createIfcRelAssociatesMaterial(RelatingMaterial=usage, RelatedObjects=[element])
        assert subject.get_profile_set_usage(element) == usage


class TestGetRepresentationContext(NewFile):
    def test_getting_a_profile_set_usage(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationSubContext()
        representation = ifc.createIfcShapeRepresentation(ContextOfItems=context)
        assert subject.get_representation_context(representation) == context


class TestHasDynamicVoids(NewFile):
    def test_run(self):
        obj = bpy.data.objects.new("Object", None)
        assert subject.has_dynamic_voids(obj) is False

    def test_checking_modifiers(self):
        obj = bpy.data.objects.new("Object", bpy.data.meshes.new("Mesh"))
        obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
        assert subject.has_dynamic_voids(obj) is True


class TestHasMaterialUsage(NewFile):
    def test_getting_a_profile_set_usage(self):
        ifc = ifcopenshell.file()
        element = ifc.createIfcColumn()
        assert subject.has_material_usage(element) is False
        usage = ifc.createIfcMaterialProfileSetUsage()
        ifc.createIfcRelAssociatesMaterial(RelatingMaterial=usage, RelatedObjects=[element])
        assert subject.has_material_usage(element) is True


class TestRunGeometryAddRepresentation(NewFile):
    def test_nothing(self):
        pass


class TestRunGeometrySwitchRepresentation(NewFile):
    def test_nothing(self):
        pass
