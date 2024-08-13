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
from . import ui, prop, operator

classes = (
    operator.ExecuteIfcTester,
    operator.SelectRequirement,
    operator.SelectFailedEntities,
    operator.SelectEntity,
    operator.ExportBcf,
    prop.FailedEntities,
    prop.Specification,
    prop.IfcTesterProperties,
    ui.BIM_PT_tester,
    ui.BIM_UL_tester_specifications,
    ui.BIM_UL_tester_failed_entities,
)


def register():
    bpy.types.Scene.IfcTesterProperties = bpy.props.PointerProperty(type=prop.IfcTesterProperties)


def unregister():
    del bpy.types.Scene.IfcTesterProperties
