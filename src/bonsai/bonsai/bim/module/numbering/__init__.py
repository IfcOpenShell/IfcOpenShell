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
from . import prop, operator, ui, workspace

classes = (
    prop.BIMNumberingProperties,
    operator.AssignNumbers,
    operator.RemoveNumbers,
    operator.SaveSettings,
    operator.LoadSettings,
    operator.DeleteSettings,
    operator.ClearSettings,
    operator.ImportSettings,
    operator.ExportSettings,
    operator.ShowMessage,
    ui.BIM_PT_Numbering,
)


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(workspace.NumberingTool, after={"bim.structural_tool"}, separator=False, group=False)
    bpy.types.Scene.BIMNumberingProperties = bpy.props.PointerProperty(type=prop.BIMNumberingProperties)


# When someone disables the add-on, we need to unload everything we loaded. This
# does the reverse of the register function.
def unregister():
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.NumberingTool)
    del bpy.types.Scene.BIMNumberingProperties
