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

import os
import bpy
import json
import numpy as np
import datetime
import zipfile
import tempfile
import addon_utils
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.placement
import blenderbim.tool as tool
import blenderbim.core.geometry
import blenderbim.core.aggregate
import blenderbim.core.spatial
import blenderbim.core.style
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector


class IfcExporter:
    def __init__(self, ifc_export_settings):
        self.ifc_export_settings = ifc_export_settings

    def export(self):
        self.file = IfcStore.get_file()
        self.set_header()
        IfcStore.update_cache()
        if bpy.context.scene.BIMProjectProperties.is_authoring:
            self.sync_deletions()
            self.sync_all_objects()
            self.sync_edited_objects()
        extension = self.ifc_export_settings.output_file.split(".")[-1]
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
            self.get_application_name(), self.get_application_version()
        )

    def sync_deletions(self):
        results = []
        for ifc_definition_id in IfcStore.deleted_ids:
            try:
                product = self.file.by_id(ifc_definition_id)
                if hasattr(product, "GlobalId"):
                    results.append(product.GlobalId)
            except:
                continue
            ifcopenshell.api.run("root.remove_product", self.file, **{"product": product})
        return results

    def sync_all_objects(self):
        results = []
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        for ifc_definition_id in list(IfcStore.id_map.keys()):
            obj = IfcStore.id_map[ifc_definition_id]
            try:
                if isinstance(obj, bpy.types.Material):
                    continue
                tool.Collector.sync(obj)
                result = self.sync_object_placement(obj)
                if result:
                    results.append(result)
                result = self.sync_object_material(obj)
                if result:
                    results.append(result)
            except ReferenceError:
                pass  # The object is likely deleted
        return results

    def sync_edited_objects(self):
        results = []
        for obj in IfcStore.edited_objs.copy():
            if not obj:
                continue
            try:
                if isinstance(obj, bpy.types.Material):
                    blenderbim.core.style.update_style_colours(tool.Ifc, tool.Style, obj=obj)
                else:
                    element = tool.Ifc.get_entity(obj)
                    if element:
                        results.append(element)
                    bpy.ops.bim.update_representation(obj=obj.name)
            except ReferenceError:
                pass  # The object is likely deleted
        IfcStore.edited_objs.clear()
        return results

    def sync_object_material(self, obj):
        if not obj.data or not isinstance(obj.data, bpy.types.Mesh):
            return
        if not self.has_changed_materials(obj):
            return
        bpy.ops.bim.update_representation(obj=obj.name)

    def has_changed_materials(self, obj):
        checksum = obj.data.BIMMeshProperties.material_checksum
        return checksum != str([s.id() for s in tool.Geometry.get_styles(obj) if s])

    def sync_object_placement(self, obj):
        if not self.has_object_moved(obj):
            return
        blender_matrix = np.array(obj.matrix_world)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        if (obj.scale - Vector((1.0, 1.0, 1.0))).length > 1e-4:
            bpy.ops.bim.update_representation(obj=obj.name)
            return element
        if element.is_a("IfcGridAxis"):
            return self.sync_grid_axis_object_placement(obj, element)
        if not hasattr(element, "ObjectPlacement"):
            return
        blenderbim.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=obj)
        return element

    def has_object_moved(self, obj):
        if not obj.BIMObjectProperties.location_checksum:
            return True  # Let's be conservative
        loc_check = np.frombuffer(eval(obj.BIMObjectProperties.location_checksum))
        rot_check = np.frombuffer(eval(obj.BIMObjectProperties.rotation_checksum))
        loc_real = np.array(obj.matrix_world.translation).flatten()
        rot_real = np.array(obj.matrix_world.to_3x3()).flatten()
        if np.allclose(loc_check, loc_real, atol=1e-4) and np.allclose(rot_check, rot_real, atol=1e-2):
            return False
        return True

    def sync_grid_axis_object_placement(self, obj, element):
        grid = (element.PartOfU or element.PartOfV or element.PartOfW)[0]
        grid_obj = tool.Ifc.get_object(grid)
        if grid_obj:
            self.sync_object_placement(grid_obj)
            if grid_obj.matrix_world != obj.matrix_world:
                bpy.ops.bim.update_representation(obj=obj.name)
        tool.Geometry.record_object_position(obj)

    def get_application_name(self):
        return "BlenderBIM"

    def get_application_version(self):
        return ".".join(
            [
                str(x)
                for x in [
                    addon.bl_info.get("version", (-1, -1, -1))
                    for addon in addon_utils.modules()
                    if addon.bl_info["name"] == "BlenderBIM"
                ][0]
            ]
        )


class IfcExportSettings:
    def __init__(self):
        self.logger = None
        self.output_file = None

    @staticmethod
    def factory(context, output_file, logger):
        settings = IfcExportSettings()
        settings.output_file = output_file
        settings.logger = logger
        return settings
