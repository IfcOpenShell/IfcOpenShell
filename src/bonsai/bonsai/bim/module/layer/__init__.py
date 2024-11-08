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
    operator.AddPresentationLayer,
    operator.AssignPresentationLayer,
    operator.DisableEditingLayer,
    operator.DisableLayerEditingUI,
    operator.EditPresentationLayer,
    operator.EnableEditingLayer,
    operator.LoadLayers,
    operator.RemovePresentationLayer,
    operator.SelectLayerProducts,
    operator.UnassignPresentationLayer,
    prop.Layer,
    prop.BIMLayerProperties,
    ui.BIM_PT_layers,
    ui.BIM_UL_layers,
)


def register():
    bpy.types.Scene.BIMLayerProperties = bpy.props.PointerProperty(type=prop.BIMLayerProperties)


def unregister():
    del bpy.types.Scene.BIMLayerProperties
