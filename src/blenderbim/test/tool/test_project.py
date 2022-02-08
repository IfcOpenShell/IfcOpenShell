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
from blenderbim.tool.project import Project as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.Project)


class TestAppendAllTypesFromTemplate(NewFile):
    def test_nothing(self):
        # TODO refactor
        pass


class TestCreateEmpty(NewFile):
    def test_run(self):
        subject.create_empty("Foobar")
        assert bpy.data.objects.get("Foobar")
        assert not bpy.data.objects.get("Foobar").data


class TestRunAggregateAssignObject(NewFile):
    def test_nothing(self):
        pass


class TestRunContextAddContext(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerAddOrganisation(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerAddPerson(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerAddPersonAndOrganisation(NewFile):
    def test_nothing(self):
        pass


class TestRunOwnerSetUser(NewFile):
    def test_nothing(self):
        pass


class TestRunAssignClass(NewFile):
    def test_nothing(self):
        pass


class TestRunUnitAssignSceneUnits(NewFile):
    def test_nothing(self):
        pass


class TestSetContext(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        subject.set_context(context)
        assert bpy.context.scene.BIMRootProperties.contexts == str(context.id())
