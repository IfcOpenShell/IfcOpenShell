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

from . import data, operator, prop, ui  # noqa: F401  (data is accessed via refresh_ui_data)

classes = (
    operator.AddRenderOverrideRule,
    operator.RemoveRenderOverrideRule,
    prop.BIMRenderOverrideRule,
    prop.BIMRenderOverrideProperties,
    ui.BIM_UL_render_override_rules,
    ui.BIM_PT_status_render,
)


def register():
    bpy.types.Camera.BIMRenderOverrideProperties = bpy.props.PointerProperty(type=prop.BIMRenderOverrideProperties)
    operator.register_handlers()


def unregister():
    operator.unregister_handlers()
    del bpy.types.Camera.BIMRenderOverrideProperties
