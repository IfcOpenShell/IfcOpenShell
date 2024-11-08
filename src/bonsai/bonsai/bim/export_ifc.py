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

from __future__ import annotations
import os
import bpy
import json
import numpy as np
import datetime
import zipfile
import tempfile
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import bonsai.tool as tool
import bonsai.core.geometry
import bonsai.core.aggregate
import bonsai.core.spatial
import bonsai.core.style
from bonsai.bim.ifc import IfcStore
from mathutils import Vector
from typing import Union
from logging import Logger


class IfcExporter:
    def __init__(self, ifc_export_settings: IfcExportSettings):
        self.ifc_export_settings = ifc_export_settings

    def export(self):
        self.file = tool.Ifc.get()
        self.set_header()
        IfcStore.update_cache()
        self.sync_all_objects()
        self.sync_edited_objects()
        extension = self.ifc_export_settings.output_file.split(".")[-1].lower()
        if extension == "ifczip":
            with tempfile.TemporaryDirectory() as unzipped_path:
                filename, ext = os.path.splitext(os.path.basename(self.ifc_export_settings.output_file))
                tmp_filename = f"{filename}.ifc"
                tmp_file = os.path.join(unzipped_path, tmp_filename)
                self.file.write(tmp_file)
                with zipfile.ZipFile(
                    self.ifc_export_settings.output_file, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
                ) as zf:
                    zf.write(tmp_file, arcname=tmp_filename)
        elif extension == "ifc":
            self.file.write(self.ifc_export_settings.output_file)
        elif extension == "ifcjson":
            import ifcjson

            if self.ifc_export_settings.json_version == "4":
                jsonData = ifcjson.IFC2JSON4(self.file, self.ifc_export_settings.json_compact).spf2Json()
                with open(self.ifc_export_settings.output_file, "w") as outfile:
                    json.dump(jsonData, outfile, indent=None if self.ifc_export_settings.json_compact else 4)
            elif self.ifc_export_settings.json_version == "5a":
                jsonData = ifcjson.IFC2JSON5a(self.file, self.ifc_export_settings.json_compact).spf2Json()
                with open(self.ifc_export_settings.output_file, "w") as outfile:
                    json.dump(jsonData, outfile, indent=None if self.ifc_export_settings.json_compact else 4)

    def set_header(self):
        self.file.wrapped_data.header.file_name.name = os.path.basename(self.ifc_export_settings.output_file)
        self.file.wrapped_data.header.file_name.time_stamp = (
            datetime.datetime.utcnow()
            .replace(tzinfo=datetime.timezone.utc)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        self.file.wrapped_data.header.file_name.preprocessor_version = "IfcOpenShell {}".format(ifcopenshell.version)
        self.file.wrapped_data.header.file_name.originating_system = "{} {}".format(
            self.get_application_name(), tool.Blender.get_bonsai_version()
        )

    def sync_all_objects(self) -> list[ifcopenshell.entity_instance]:
        results: list[ifcopenshell.entity_instance] = []
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        for ifc_definition_id in list(IfcStore.id_map.keys()):
            obj = IfcStore.id_map[ifc_definition_id]
            try:
                if isinstance(obj, bpy.types.Material):
                    continue
                if obj.library:
                    continue
                result = self.sync_object_placement(obj)
                if result:
                    results.append(result)
                result = self.sync_object_material(obj)
                # TODO: sync_object_material always returns None
                # so it's never really appended
                if result:
                    results.append(result)
            except ReferenceError:
                pass  # The object is likely deleted
        return results

    def sync_edited_objects(self) -> list[ifcopenshell.entity_instance]:
        results: list[ifcopenshell.entity_instance] = []
        for obj in IfcStore.edited_objs.copy():
            if not obj:
                continue
            if not tool.Blender.is_valid_data_block(obj):
                continue
            element = tool.Ifc.get_entity(obj)
            if element:
                results.append(element)
            bpy.ops.bim.update_representation(obj=obj.name)
        IfcStore.edited_objs.clear()
        return results

    def sync_object_material(self, obj: bpy.types.Object) -> None:
        if not obj.data or not isinstance(obj.data, bpy.types.Mesh):
            return
        if not self.has_changed_materials(obj):
            return
        bpy.ops.bim.update_representation(obj=obj.name)

    def has_changed_materials(self, obj: bpy.types.Object) -> bool:
        checksum = obj.data.BIMMeshProperties.material_checksum
        return checksum != tool.Geometry.get_material_checksum(obj)

    def sync_object_placement(self, obj: bpy.types.Object) -> Union[ifcopenshell.entity_instance, None]:
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        if tool.Geometry.is_scaled(obj):
            bpy.ops.bim.update_representation(obj=obj.name)
            # update_representation might not apply scale if the object has openings
            # reset it, so let user know that the scale wasn't saved.
            if tool.Geometry.is_scaled(obj):
                print(f"WARNING. Object '{obj.name}' scales ({obj.scale[:]}) are reset during project save.")
                obj.scale = (1.0, 1.0, 1.0)
            else:
                # Return and don't handle is_moved as
                # updata_representation will run edit_object_placement if object is scaled
                # and had no openings.
                return element
        if not tool.Ifc.is_moved(obj):
            return
        if element.is_a("IfcGridAxis"):
            return self.sync_grid_axis_object_placement(obj, element)
        if not hasattr(element, "ObjectPlacement"):
            return
        bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        return element

    def sync_grid_axis_object_placement(self, obj: bpy.types.Object, element: ifcopenshell.entity_instance) -> None:
        grid = (element.PartOfU or element.PartOfV or element.PartOfW)[0]
        grid_obj = tool.Ifc.get_object(grid)
        if grid_obj:
            self.sync_object_placement(grid_obj)
            if grid_obj.matrix_world != obj.matrix_world:
                bpy.ops.bim.update_representation(obj=obj.name)
        tool.Geometry.record_object_position(obj)

    def get_application_name(self) -> str:
        return "Bonsai"


class IfcExportSettings:
    def __init__(self):
        self.logger: Logger = None
        self.output_file: str = None
        self.json_version: str = None
        self.json_compact: bool = None

    @staticmethod
    def factory(context: bpy.types.Context, output_file: str, logger: Logger) -> IfcExportSettings:
        settings = IfcExportSettings()
        settings.output_file = output_file
        settings.logger = logger
        return settings
