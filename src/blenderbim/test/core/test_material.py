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

import blenderbim.core.material as subject
from test.core.bootstrap import ifc, material


class TestUnlinkMaterial:
    def test_run(self, ifc):
        ifc.unlink(obj="obj").should_be_called()
        subject.unlink_material(ifc, obj="obj")


class TestAddDefaultMaterial:
    def test_run(self, ifc, material):
        material.add_default_material_object().should_be_called().will_return("obj")
        ifc.run("material.add_material", name="Default").should_be_called().will_return("material")
        ifc.link("material", "obj").should_be_called()
        assert subject.add_default_material(ifc, material) == "obj"


class TestLoadMaterials:
    def test_run(self, material):
        material.import_material_definitions("material_type").should_be_called()
        material.enable_editing_materials().should_be_called()
        subject.load_materials(material, "material_type")


class TestDisableEditingMaterials:
    def test_run(self, material):
        material.disable_editing_materials().should_be_called()
        subject.disable_editing_materials(material)
