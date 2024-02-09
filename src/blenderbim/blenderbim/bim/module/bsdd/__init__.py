# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
    operator.GetBSDDClassificationProperties,
    operator.LoadBSDDDomains,
    operator.SearchBSDDClass,
    operator.SetActiveBSDDDictionary,
    prop.BSDDDomain,
    prop.BSDDClassification,
    prop.BSDDPset,
    prop.BIMBSDDProperties,
    ui.BIM_UL_bsdd_domains,
    ui.BIM_UL_bsdd_classifications,
    ui.BIM_PT_bsdd,
)


def register():
    bpy.types.Scene.BIMBSDDProperties = bpy.props.PointerProperty(type=prop.BIMBSDDProperties)


def unregister():
    del bpy.types.Scene.BIMBSDDProperties
