# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from . import ui, prop, operator

classes = (
    operator.AddFilling,
    operator.AddOpening,
    operator.BooleansMarkAsManual,
    operator.DisableEditingBooleans,
    operator.EnableEditingBooleans,
    operator.RemoveFilling,
    operator.RemoveOpening,
    operator.SelectDecomposition,
    prop.Boolean,
    prop.VoidProperties,
    prop.BIMBooleanProperties,
    ui.BIM_PT_voids,
    ui.BIM_PT_booleans,
    ui.BIM_UL_booleans,
)


def register():
    bpy.types.Scene.VoidProperties = bpy.props.PointerProperty(type=prop.VoidProperties)
    bpy.types.Scene.BIMBooleanProperties = bpy.props.PointerProperty(type=prop.BIMBooleanProperties)


def unregister():
    del bpy.types.Scene.VoidProperties
    del bpy.types.Scene.BIMBooleanProperties
