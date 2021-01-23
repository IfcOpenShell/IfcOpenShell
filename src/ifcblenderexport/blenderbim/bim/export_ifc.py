import os
import bpy
import json
import datetime
import zipfile
import tempfile
import ifcopenshell
from blenderbim.bim.ifc import IfcStore
import addon_utils


class IfcExporter:
    def __init__(self, ifc_export_settings):
        self.ifc_export_settings = ifc_export_settings

    def export(self):
        self.file = IfcStore.get_file()
        self.set_header()
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
        settings.json_version = scene_bim.export_json_version
        settings.json_compact = scene_bim.export_json_compact
        return settings
