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
from . import ui, prop, operator

classes = (
    operator.AddBrick,
    operator.AddBrickFeed,
    operator.AssignBrickReference,
    operator.CloseBrickProject,
    operator.ConvertBrickProject,
    operator.ConvertIfcToBrick,
    operator.LoadBrickProject,
    operator.NewBrickFile,
    operator.RefreshBrickViewer,
    operator.RemoveBrick,
    operator.RewindBrickClass,
    operator.ViewBrickClass,
    operator.ViewBrickItem,
    operator.SerializeBrick,
    prop.Brick,
    prop.BIMBrickProperties,
    ui.BIM_PT_brickschema,
    ui.BIM_PT_ifc_brickschema_references,
    ui.BIM_UL_bricks,
)


def register():
    bpy.types.Scene.BIMBrickProperties = bpy.props.PointerProperty(type=prop.BIMBrickProperties)


def unregister():
    del bpy.types.Scene.BIMBrickProperties
