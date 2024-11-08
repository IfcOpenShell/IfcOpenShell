# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell
import test.bim.bootstrap
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.context import Context as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Context)


class TestSetContext(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        context = ifc.createIfcGeometricRepresentationContext()
        subject.set_context(context)
        assert bpy.context.scene.BIMContextProperties.active_context_id == context.id()


class TestImportAttributes(test.bim.bootstrap.NewFile):
    def test_importing_a_context(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        context.ContextIdentifier = "ContextIdentifier"
        context.ContextType = "ContextType"
        context.CoordinateSpaceDimension = 1
        context.Precision = 1
        subject.set_context(context)
        subject.import_attributes()
        props = bpy.context.scene.BIMContextProperties
        assert props.context_attributes.get("ContextIdentifier").string_value == "ContextIdentifier"
        assert props.context_attributes.get("ContextType").string_value == "ContextType"
        assert props.context_attributes.get("CoordinateSpaceDimension").int_value == 1
        assert props.context_attributes.get("Precision").float_value == 1

    def test_importing_a_subcontext(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        subcontext = ifc.createIfcGeometricRepresentationSubcontext()
        subcontext.TargetScale = 0.5
        subcontext.TargetView = "NOTDEFINED"
        subcontext.UserDefinedTargetView = "UserDefinedTargetView"
        subject.set_context(subcontext)
        subject.import_attributes()
        props = bpy.context.scene.BIMContextProperties
        assert props.context_attributes.get("TargetScale").float_value == 0.5
        assert props.context_attributes.get("TargetView").enum_value == "NOTDEFINED"
        assert props.context_attributes.get("UserDefinedTargetView").string_value == "UserDefinedTargetView"
        assert not props.context_attributes.get("Precision")

    def test_importing_twice(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        context.ContextIdentifier = "ContextIdentifier"
        subject.set_context(context)
        subject.import_attributes()
        context.ContextIdentifier = "ContextIdentifier2"
        subject.import_attributes()
        props = bpy.context.scene.BIMContextProperties
        assert props.context_attributes.get("ContextIdentifier").string_value == "ContextIdentifier2"


class TestClearContext(test.bim.bootstrap.NewFile):
    def test_run(self):
        TestSetContext().test_run()
        subject.clear_context()
        assert bpy.context.scene.BIMContextProperties.active_context_id == 0


class TestGetContext(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        context = ifc.createIfcGeometricRepresentationContext()
        subject.set_context(context)
        assert subject.get_context() == context


class TestExportAttributes(test.bim.bootstrap.NewFile):
    def test_exporting_a_context(self):
        TestImportAttributes().test_importing_a_context()
        assert subject.export_attributes() == {
            "ContextIdentifier": "ContextIdentifier",
            "ContextType": "ContextType",
            "CoordinateSpaceDimension": 1,
            "Precision": 1,
        }

    def test_exporting_a_subcontext(self):
        TestImportAttributes().test_importing_a_subcontext()
        assert subject.export_attributes() == {
            "TargetScale": 0.5,
            "TargetView": "NOTDEFINED",
            "UserDefinedTargetView": "UserDefinedTargetView",
            "ContextIdentifier": None,
            "ContextType": None,
        }
