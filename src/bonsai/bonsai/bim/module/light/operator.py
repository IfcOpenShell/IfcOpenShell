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

"""Thin re-export module for backward compatibility.

All operator classes are defined in their respective submodules:
  - export.py:   ExportOBJ, CleanupRadianceFiles
  - prepare.py:  PrepareRadianceScene
  - render.py:   RadianceRender, FalseColorRadiance
  - solar.py:    ImportTrueNorth, ImportLatLong, MoveSunPathTo3DCursor,
                 ViewFromSun, LightPickCoordinates, LightSetTimeToNow
  - material.py: RefreshIFCMaterials, UnmapMaterial,
                 RADIANCE_OT_export_material_mappings,
                 RADIANCE_OT_import_material_mappings,
                 RADIANCE_OT_open_spectraldb
  - ies.py:      AddIESLight, RemoveIESLight

Small operators (EnumPropertySearch, SetEnumProperty) remain defined here.
"""

import bpy

import bonsai.tool as tool
from bonsai.bim.module.light.ui import get_enum_items

# Re-export from submodules
from bonsai.bim.module.light.export import CleanupRadianceFiles, ExportOBJ  # noqa: F401
from bonsai.bim.module.light.ies import AddIESLight, RemoveIESLight  # noqa: F401
from bonsai.bim.module.light.material import (  # noqa: F401
    RADIANCE_OT_export_material_mappings,
    RADIANCE_OT_import_material_mappings,
    RADIANCE_OT_open_spectraldb,
    RefreshIFCMaterials,
    UnmapMaterial,
)
from bonsai.bim.module.light.prepare import PrepareRadianceScene  # noqa: F401
from bonsai.bim.module.light.render import FalseColorRadiance, RadianceRender  # noqa: F401
from bonsai.bim.module.light.solar import (  # noqa: F401
    ImportLatLong,
    ImportTrueNorth,
    LightPickCoordinates,
    LightSetTimeToNow,
    MoveSunPathTo3DCursor,
    ViewFromSun,
)


class EnumPropertySearch(bpy.types.Operator):
    bl_idname = "radiance.enum_property_search"
    bl_label = "Search Enum Property"
    bl_options = {"REGISTER", "UNDO"}

    prop_name: bpy.props.StringProperty()
    search_term: bpy.props.StringProperty()

    def execute(self, context):
        try:
            data = context.space_data.context_pointer_get("data")
        except Exception:
            self.report({"ERROR"}, "Could not access context data for enum search.")
            return {"CANCELLED"}
        if data is None:
            self.report({"ERROR"}, "No context data available for enum search.")
            return {"CANCELLED"}
        enum_items = get_enum_items(data, self.prop_name)
        filtered_items = [item for item in enum_items if self.search_term.lower() in item[1].lower()]

        def draw_menu(self, context):
            layout = self.layout
            for item in filtered_items:
                props = layout.operator("bim.set_enum_property", text=item[1])
                props.prop_name = self.prop_name
                props.enum_value = item[0]

        bpy.context.window_manager.popup_menu(draw_menu, title="Search Results", icon="VIEWZOOM")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "search_term", text="Search")


class SetEnumProperty(bpy.types.Operator):
    bl_idname = "bim.set_enum_property"
    bl_label = "Set Enum Property"
    bl_options = {"REGISTER", "UNDO"}

    prop_name: bpy.props.StringProperty()
    enum_value: bpy.props.StringProperty()

    def execute(self, context):
        data = context.space_data.context_pointer_get("data")
        setattr(data, self.prop_name, self.enum_value)
        return {"FINISHED"}
