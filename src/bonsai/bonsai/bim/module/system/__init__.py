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
from . import ui, prop, operator, decorator

classes = (
    operator.AddPort,
    operator.AddSystem,
    operator.AddZone,
    operator.AssignSystem,
    operator.AssignUnassignFlowControl,
    operator.ConnectPort,
    operator.DisableEditingSystem,
    operator.DisableEditingZone,
    operator.DisableSystemEditingUI,
    operator.DisconnectPort,
    operator.EditSystem,
    operator.EditZone,
    operator.EnableEditingSystem,
    operator.EnableEditingZone,
    operator.HidePorts,
    operator.LoadSystems,
    operator.LoadZones,
    operator.MEPConnectElements,
    operator.RemovePort,
    operator.RemoveSystem,
    operator.RemoveZone,
    operator.SelectSystemProducts,
    operator.SetFlowDirection,
    operator.ShowPorts,
    operator.UnassignSystem,
    operator.UnloadZones,
    prop.System,
    prop.Zone,
    prop.BIMSystemProperties,
    prop.BIMZoneProperties,
    ui.BIM_PT_systems,
    ui.BIM_PT_zones,
    ui.BIM_PT_active_object_zones,
    ui.BIM_PT_ports,
    ui.BIM_PT_port,
    ui.BIM_PT_flow_controls,
    ui.BIM_UL_systems,
    ui.BIM_UL_zones,
)


def register():
    bpy.types.Scene.BIMSystemProperties = bpy.props.PointerProperty(type=prop.BIMSystemProperties)
    bpy.types.Scene.BIMZoneProperties = bpy.props.PointerProperty(type=prop.BIMZoneProperties)
    bpy.app.handlers.load_post.append(decorator.toggle_decorations_on_load)


def unregister():
    del bpy.types.Scene.BIMSystemProperties
    del bpy.types.Scene.BIMZoneProperties
    bpy.app.handlers.load_post.remove(decorator.toggle_decorations_on_load)
