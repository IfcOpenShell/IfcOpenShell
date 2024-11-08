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

import bpy
from . import operator, prop, workspace

classes = (
    operator.AlignViewToProfile,
    operator.AddIfcArcIndexFillet,
    operator.AddIfcCircle,
    operator.AddRectangle,
    operator.CadArcFrom2Points,
    operator.CadArcFrom3Points,
    operator.CadFillet,
    operator.CadMitre,
    operator.CadOffset,
    operator.CadTrimExtend,
    prop.BIMCadProperties,
    workspace.CadHotkey,
)


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.CadTool, after={"builtin.transform"}, separator=True, group=False)
    bpy.types.Scene.BIMCadProperties = bpy.props.PointerProperty(type=prop.BIMCadProperties)

    workspace.load_custom_icons()


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.CadTool)
    del bpy.types.Scene.BIMCadProperties

    workspace.unload_custom_icons()
