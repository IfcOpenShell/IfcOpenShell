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

from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper

import bonsai.tool as tool


class AddIESLight(bpy.types.Operator, ImportHelper):
    """Upload and add an IES light fixture to the scene"""

    bl_idname = "radiance.add_ies_light"
    bl_label = "Add IES Light"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".ies"
    filter_glob: bpy.props.StringProperty(default="*.ies;*.IES", options={"HIDDEN"})

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()

        # Create new IES light entry
        ies_light = props.ies_lights.add()
        # Store as relative path if the blend file is saved
        if bpy.data.filepath:
            ies_light.ies_file_path = bpy.path.relpath(self.filepath)
        else:
            ies_light.ies_file_path = self.filepath
        ies_light.rotation_z = 0.0
        ies_light.is_enabled = True

        # Set as active
        props.active_ies_light_index = len(props.ies_lights) - 1

        self.report({"INFO"}, f"Added IES light: {Path(self.filepath).name}")
        return {"FINISHED"}


class RemoveIESLight(bpy.types.Operator):
    """Remove an IES light fixture mapping"""

    bl_idname = "radiance.remove_ies_light"
    bl_label = "Remove IES Light"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()

        if 0 <= self.index < len(props.ies_lights):
            props.ies_lights.remove(self.index)

            # Adjust active index if needed
            if props.active_ies_light_index >= len(props.ies_lights):
                props.active_ies_light_index = len(props.ies_lights) - 1

            self.report({"INFO"}, "IES light removed")
            return {"FINISHED"}

        self.report({"WARNING"}, "Invalid IES light index")
        return {"CANCELLED"}
