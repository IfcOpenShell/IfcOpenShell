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

import os
import bpy
import bonsai.tool as tool
import ifcopenshell.util.file
from bonsai.bim.ifc import IfcStore
from pathlib import Path
from typing import Union


def refresh():
    ProjectData.is_loaded = False
    LinksData.is_loaded = False


class ProjectData:
    data = {}
    is_loaded = False
    filepath_schema_cache: dict[Path, Union[str, None]] = {}

    @classmethod
    def load(cls):
        cls.data = {
            "export_schema": cls.get_export_schema(),
            "library_file": cls.library_file(),
            "template_file": cls.template_file(),
            "last_saved": cls.last_saved(),
        }
        cls.is_loaded = True

    @classmethod
    def get_file_schema(cls, filepath: Path) -> Union[str, None]:
        # Let's assume that filepath won't be changing schema during current Blender session
        # to avoid reading header from the library files on every UI update.
        # If it will be an issue, we can also consider last modified time.
        if filepath not in cls.filepath_schema_cache:
            extractor = ifcopenshell.util.file.IfcHeaderExtractor(str(filepath))
            schema_name = extractor.extract().get("schema_name")
            cls.filepath_schema_cache[filepath] = schema_name
        return cls.filepath_schema_cache[filepath]

    @classmethod
    def get_export_schema(cls):
        return [(s, "IFC4X3" if s == "IFC4X3_ADD2" else s, "") for s in IfcStore.schema_identifiers]

    @classmethod
    def library_file(cls):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return []
        current_schema = tool.Ifc.get().schema_identifier
        files = (Path(bpy.context.scene.BIMProperties.data_dir) / "libraries").iterdir()
        results = [("0", "Custom Library", "")]
        for f in files:
            if not f.suffix.lower().startswith(".ifc"):
                continue
            if cls.get_file_schema(f) != current_schema:
                continue
            results.append((f.name, f.stem, "Library"))
        return results

    @classmethod
    def template_file(cls):
        files = os.listdir(os.path.join(bpy.context.scene.BIMProperties.data_dir, "templates", "projects"))
        results = [("0", "Blank Project", "")]
        results.extend([(f, os.path.splitext(f)[0], "") for f in files if ".ifc" in f])
        return results

    @classmethod
    def last_saved(cls):
        ifc = tool.Ifc.get()
        if not ifc:
            return ""
        try:
            save_datetime = ifc.wrapped_data.header.file_name.time_stamp
            save_date, save_time = save_datetime.split("T")
            return f"{save_date} {':'.join(save_time.split(':')[0:2])}"
        except:
            return ""


class LinksData:
    linked_data = {}
    enable_culling = False
    is_loaded = False
