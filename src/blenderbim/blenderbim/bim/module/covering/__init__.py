# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from . import prop, workspace

classes = (
    prop.BIMCoveringProperties,
    workspace.Hotkey,
)


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.CoveringTool, after={"bim.structural_tool"}, separator=False, group=False)
    bpy.types.Scene.BIMCoveringProperties = bpy.props.PointerProperty(type=prop.BIMCoveringProperties)
#    bpy.types.Object.BIMObjectSpatialProperties = bpy.props.PointerProperty(type=prop.BIMObjectSpatialProperties)
#    bpy.types.Scene.BIMSpatialManagerProperties = bpy.props.PointerProperty(type=prop.BIMSpatialManagerProperties)


def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.CoveringTool)
    del bpy.types.Scene.BIMCoveringProperties
#    del bpy.types.Object.BIMObjectSpatialProperties
#    del bpy.types.Scene.BIMSpatialManagerProperties
