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
from blenderbim.tool.material import Material as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Material)


class TestAddDefaultMaterialObject(NewFile):
    def test_run(self):
        material = subject.add_default_material_object()
        assert isinstance(material, bpy.types.Material)
        assert material.name == "Default"


class TestLink(NewFile):
    def test_run(self):
        obj = bpy.data.materials.new("Material")
        ifc = ifcopenshell.file()
        material = ifc.createIfcMaterial()
        subject.link(material, obj)
        assert obj.BIMObjectProperties.ifc_definition_id == material.id()


class TestUnlink(NewFile):
    def test_run(self):
        obj = bpy.data.materials.new("Material")
        ifc = ifcopenshell.file()
        material = ifc.createIfcMaterial()
        subject.link(material, obj)
        subject.unlink(obj)
        assert obj.BIMObjectProperties.ifc_definition_id == 0
