import os
import bpy
import json
import numpy as np
import datetime
import zipfile
import tempfile
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.api
from ifcopenshell.api.spatial.data import Data as SpatialData
from blenderbim.bim.ifc import IfcStore
import addon_utils


class IfcExporter:
    def __init__(self, ifc_export_settings):
        self.ifc_export_settings = ifc_export_settings

    def export(self):
        self.file = IfcStore.get_file()
        self.set_header()
        if bpy.context.scene.BIMProjectProperties.is_authoring:
            self.sync_object_placements_and_deletions()
            self.sync_edited_objects()
        extension = self.ifc_export_settings.output_file.split(".")[-1]
        if extension == "ifczip":
            with tempfile.TemporaryDirectory() as unzipped_path:
                filename, ext = os.path.splitext(os.path.basename(self.ifc_export_settings.output_file))
                tmp_name = "{}.ifc".format(filename)
                tmp_file = os.path.join(unzipped_path, tmp_name)
                self.file.write(tmp_file)
                with zipfile.ZipFile(
                    self.ifc_export_settings.output_file, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
                ) as zf:
                    zf.write(tmp_file)
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
        # TODO: add all metadata, pending bug #747
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
        # TODO: reimplement. See #1222.
        # if self.owner_history:
        #    if self.schema_version == "IFC2X3":
        #        self.file.wrapped_data.header.file_name.authorization = self.owner_history.OwningUser.ThePerson.Id
        #    else:
        #        self.file.wrapped_data.header.file_name.authorization = (
        #            self.owner_history.OwningUser.ThePerson.Identification
        #        )
        # else:
        #    self.file.wrapped_data.header.file_name.authorization = "Nobody"

    def sync_object_placements_and_deletions(self):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        to_delete = []

        for guid, obj in IfcStore.guid_map.items():
            try:
                self.sync_object_placement(obj)
            except:
                pass
            self.sync_object_container(guid, obj)
            if self.should_delete(obj):
                to_delete.append(guid)

        SpatialData.purge()

        for guid in to_delete:
            product = self.file.by_id(guid)
            IfcStore.unlink_element(product)
            ifcopenshell.api.run("root.remove_product", self.file, **{"product": product})

    def sync_edited_objects(self):
        for obj_name in IfcStore.edited_objs.copy():
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                continue
            representation = IfcStore.get_file().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
            if representation.RepresentationType == "Tessellation" or representation.RepresentationType == "Brep":
                bpy.ops.bim.update_mesh_representation(obj=obj.name)
        IfcStore.edited_objs.clear()

    def sync_object_placement(self, obj):
        blender_matrix = np.matrix(obj.matrix_world)
        ifc_matrix = ifcopenshell.util.placement.get_local_placement(
            self.file.by_id(obj.BIMObjectProperties.ifc_definition_id).ObjectPlacement
        )
        ifc_matrix[0][3] *= self.unit_scale
        ifc_matrix[1][3] *= self.unit_scale
        ifc_matrix[2][3] *= self.unit_scale

        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset and props.blender_offset_type == "OBJECT_PLACEMENT":
            ifc_matrix = ifcopenshell.util.geolocation.global2local(
                ifc_matrix,
                float(props.blender_eastings) * self.unit_scale,
                float(props.blender_northings) * self.unit_scale,
                float(props.blender_orthogonal_height) * self.unit_scale,
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
            )
        if not np.allclose(ifc_matrix, blender_matrix, atol=0.0001):
            bpy.ops.bim.edit_object_placement(obj=obj.name)

    def sync_object_container(self, guid, obj):
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        element_collection = bpy.data.collections.get(obj.name)

        if element.is_a("IfcProject"):
            return

        if (element.is_a("IfcElement") and element_collection) or element.is_a("IfcSpatialStructureElement"):
            try:
                parent_collection = [c for c in bpy.data.collections if c.children.get(element_collection.name)][0]
            except:
                return  # Out of the spatial tree
        else:
            parent_collection = obj.users_collection[0]

        parent_obj = bpy.data.objects.get(parent_collection.name)
        if not parent_obj or not parent_obj.BIMObjectProperties.ifc_definition_id:
            return
        parent = self.file.by_id(parent_obj.BIMObjectProperties.ifc_definition_id)

        if parent.is_a("IfcSpatialStructureElement") and not element.is_a("IfcSpatialStructureElement"):
            if parent != ifcopenshell.util.element.get_container(element):
                bpy.ops.bim.assign_container(relating_structure=parent.id(), related_element=obj.name)
        elif parent != ifcopenshell.util.element.get_aggregate(element):
            bpy.ops.bim.assign_object(relating_object=parent_obj.name, related_object=obj.name)

    def should_delete(self, obj):
        try:
            # This will throw an exception if the Blender object no longer exists
            foo = obj.name
            return False
        except:
            return True

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
        scene_bim = context.scene.BIMProperties
        settings = IfcExportSettings()
        settings.output_file = output_file
        settings.logger = logger
        return settings
