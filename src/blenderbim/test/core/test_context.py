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

import blenderbim.core.context
from test.core.bootstrap import Spec, subject, ifc, blender


@subject(blenderbim.core.context.AddContext)
class TestAddContext(Spec):
    def test_adding_a_context(self, ifc):
        self.construct_with(ifc, context="Model", subcontext="Body", target_view="MODEL_VIEW")
        ifc.run(
            "context.add_context", context="Model", subcontext="Body", target_view="MODEL_VIEW"
        ).should().be_called().return_with("context")
        assert self.subject.execute() == "context"


@subject(blenderbim.core.context.RemoveContext)
class TestRemoveContext(Spec):
    def test_removing_a_context(self, ifc):
        self.construct_with(ifc, context="context")
        ifc.run("context.remove_context", context="context").should().be_called()
        self.subject.execute()
