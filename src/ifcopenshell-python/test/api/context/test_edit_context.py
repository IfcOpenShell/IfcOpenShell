# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api.context


class TestEditContext(test.bootstrap.IFC4):
    def test_editing_a_context(self):
        context = self.file.createIfcGeometricRepresentationContext()
        ifcopenshell.api.context.edit_context(
            self.file,
            context=context,
            attributes={
                "ContextIdentifier": "ContextIdentifier",
                "ContextType": "ContextType",
                "CoordinateSpaceDimension": 1,
                "Precision": 1,
            },
        )
        assert context.ContextIdentifier == "ContextIdentifier"
        assert context.ContextType == "ContextType"
        assert context.CoordinateSpaceDimension == 1
        assert context.Precision == 1

    def test_editing_a_subcontext(self):
        subcontext = self.file.createIfcGeometricRepresentationSubcontext()
        ifcopenshell.api.context.edit_context(
            self.file,
            context=subcontext,
            attributes={
                "ContextIdentifier": "ContextIdentifier",
                "ContextType": "ContextType",
                "TargetScale": 0.5,
                "TargetView": "MODEL_VIEW",
                "UserDefinedTargetView": "UserDefinedTargetView",
            },
        )
        assert subcontext.ContextIdentifier == "ContextIdentifier"
        assert subcontext.ContextType == "ContextType"
        assert subcontext.TargetScale == 0.5
        assert subcontext.TargetView == "MODEL_VIEW"
        assert subcontext.UserDefinedTargetView == "UserDefinedTargetView"


class TestEditContextIFC2X3(test.bootstrap.IFC2X3, TestEditContext):
    pass
