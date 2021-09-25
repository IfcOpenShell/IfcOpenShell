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


class AddContext:
    def __init__(self, ifc, context=None, subcontext=None, target_view=None):
        self.ifc = ifc
        self.context = context
        self.subcontext = subcontext
        self.target_view = target_view

    def execute(self):
        return self.ifc.run(
            "context.add_context",
            context=self.context,
            subcontext=self.subcontext,
            target_view=self.target_view,
        )


class RemoveContext:
    def __init__(self, ifc, context=None):
        self.ifc = ifc
        self.context = context

    def execute(self):
        self.ifc.run("context.remove_context", context=self.context)
