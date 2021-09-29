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

import blenderbim.core.context as subject
from test.core.bootstrap import ifc


class TestAddContext:
    def test_adding_a_context(self, ifc):
        ifc.run(
            "context.add_context", context="Model", subcontext="Body", target_view="MODEL_VIEW"
        ).should_be_called().will_return("context")
        assert subject.add_context(ifc, context="Model", subcontext="Body", target_view="MODEL_VIEW") == "context"


class TestRemoveContext:
    def test_removing_a_context(self, ifc):
        ifc.run("context.remove_context", context="context").should_be_called()
        subject.remove_context(ifc, context="context")
