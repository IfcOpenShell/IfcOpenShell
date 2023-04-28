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
from . import ui, operator, prop

classes = (
    operator.ColourByRelatedBuildingElement,
    operator.DisableEditingBoundary,
    operator.EditBoundaryAttributes,
    operator.EnableEditingBoundary,
    operator.LoadProjectSpaceBoundaries,
    operator.LoadSpaceBoundaries,
    operator.LoadBoundary,
    operator.SelectRelatedElementBoundaries,
    operator.SelectProjectBoundaries,
    operator.SelectRelatedElementTypeBoundaries,
    operator.SelectSpaceBoundaries,
    operator.UpdateBoundaryGeometry,
    ui.BIM_PT_Boundary,
    ui.BIM_PT_SceneBoundaries,
    ui.BIM_PT_SpaceBoundaries,
    prop.BIMBoundaryProperties,
)


def register():
    bpy.types.Object.bim_boundary_properties = bpy.props.PointerProperty(type=prop.BIMBoundaryProperties)


def unregister():
    del bpy.types.Object.bim_boundary_properties
