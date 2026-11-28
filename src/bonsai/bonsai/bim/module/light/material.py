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

import json
import webbrowser

import bpy
from bpy_extras.io_utils import ExportHelper, ImportHelper

import bonsai.tool as tool


class RefreshIFCMaterials(bpy.types.Operator):
    bl_idname = "bim.refresh_ifc_materials"
    bl_label = "Refresh IFC Materials"
    bl_description = "Refresh the list of IFC materials for mapping"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file loaded in Bonsai.")
            return False
        return True

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        ifc_file = tool.Ifc.get()

        props.materials.clear()

        for style in ifc_file.by_type("IfcSurfaceStyle"):
            for render_item in style.Styles:
                if render_item.is_a("IfcSurfaceStyleRendering"):
                    style_id = f"IfcSurfaceStyleRendering-{render_item.id()}"
                    style_name = style.Name or f"Unnamed Style {render_item.id()}"

                    # Extract color
                    color = (1.0, 1.0, 1.0)  # Default white
                    if render_item.SurfaceColour:
                        color = (
                            render_item.SurfaceColour.Red,
                            render_item.SurfaceColour.Green,
                            render_item.SurfaceColour.Blue,
                        )

                    material = props.add_material_mapping(style_id, style_name)
                    material.color = color

                    material.category = ""
                    material.subcategory = ""
                    material.is_mapped = False

        props.active_material_index = 0 if props.materials else -1

        self.report({"INFO"}, f"Refreshed {len(props.materials)} IFC materials")
        return {"FINISHED"}


class UnmapMaterial(bpy.types.Operator):
    bl_idname = "bim.unmap_material"
    bl_label = "Unmap Material"
    bl_options = {"REGISTER", "UNDO"}

    material_index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        material = props.materials[self.material_index]
        props.unmap_material(material.name)
        return {"FINISHED"}


class RADIANCE_OT_export_material_mappings(bpy.types.Operator, ExportHelper):
    bl_idname = "radiance.export_material_mappings"
    bl_label = "Export Material Mappings"
    bl_description = "Export material mappings to a JSON file"

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        mappings = {}

        for material in props.materials:
            if material.is_mapped:
                mappings[material.style_id] = {
                    "name": material.name,
                    "category": material.category,
                    "subcategory": material.subcategory,
                }

        with open(self.filepath, "w") as f:
            json.dump(mappings, f, indent=4)

        self.report({"INFO"}, f"Material mappings exported to {self.filepath}")
        return {"FINISHED"}


class RADIANCE_OT_import_material_mappings(bpy.types.Operator, ImportHelper):
    bl_idname = "radiance.import_material_mappings"
    bl_label = "Import Material Mappings"
    bl_description = "Import material mappings from a JSON file"

    filename_ext = ".json"

    def execute(self, context):
        props = tool.Blender.get_radiance_exporter_props()
        props.import_mappings(self.filepath)
        self.report({"INFO"}, f"Material mappings imported from {self.filepath}")
        return {"FINISHED"}


class RADIANCE_OT_open_spectraldb(bpy.types.Operator):
    bl_idname = "radiance.open_spectraldb"
    bl_label = "Open SpectralDB"
    bl_description = "Open the SpectralDB website for reference"

    def execute(self, context):
        webbrowser.open("https://spectraldb.com")
        return {"FINISHED"}
