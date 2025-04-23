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
from collections import defaultdict
from typing import Union, Any


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
            "last_saved": cls.last_saved(),
            "total_elements": cls.total_elements(),
        }
        # After export_schema.
        cls.data["template_file"] = cls.template_file()
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
        results = [("0", "Custom Library", "")]
        for f in tool.Blender.get_data_dir_paths("libraries", "*.ifc*"):
            if cls.get_file_schema(f) != current_schema:
                continue
            results.append((f.name, f.stem, "Library"))
        return results

    @classmethod
    def template_file(cls) -> dict[str, list[tuple[str, str, str]]]:
        template_files: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
        for export_schema in cls.data["export_schema"]:
            template_files[export_schema[0]].append(("0", "Blank Project", ""))

        for f in tool.Blender.get_data_dir_paths(Path("templates") / "projects", "*.ifc*"):
            current_schema = cls.get_file_schema(f)
            if current_schema not in template_files:
                continue
            template_files[current_schema].append((f.name, f.stem, "Template"))
        return template_files

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

    @classmethod
    def total_elements(cls):
        if ifc := tool.Ifc.get():
            return len(ifc.by_type("IfcElement"))
        return 0


class ProjectLibraryData:
    data: dict[str, Any] = {}
    is_loaded: bool = False

    @classmethod
    def load(cls):
        cls.data = {}
        cls.data["project_libraries"] = cls.project_libraries()
        # After .project_libraries().
        cls.data["project_libraries_enum"] = cls.project_libraries_enum()
        cls.data["parent_libraries_enum"] = cls.parent_libraries_enum()
        cls.is_loaded = True

    @classmethod
    def project_libraries(cls) -> dict[int, dict[str, Any]]:
        results = {}
        library_file = IfcStore.library_file
        if library_file is None or library_file.schema == "IFC2X3":
            return results
        KEEP_ATTRS = set(("id", "Name", "Description"))
        for l in library_file.by_type("IfcProjectLibrary"):
            results[l.id()] = {k: v for k, v in l.get_info().items() if k in KEEP_ATTRS}
        return results

    @classmethod
    def project_libraries_enum(cls) -> list[tuple[str, str, str, str, int]]:
        results = []
        project_libraries = cls.data["project_libraries"].values()
        if not project_libraries:
            results.append(("-", "No Library", "", "", 0))

        props = tool.Project.get_project_props()
        libs = []
        for i, data in enumerate(cls.data["project_libraries"].values(), len(results)):
            icon = "GREASEPENCIL" if props.editing_project_library_id == data["id"] else ""
            libs.append((str(data["id"]), data["Name"] or "Unnamed", data["Description"] or "", icon, i))
        libs.sort(key=lambda x: x[1])
        results += libs
        return results

    @classmethod
    def parent_libraries_enum(cls) -> list[tuple[str, str, str]]:
        results: list[tuple[str, str, str]] = []
        library_file = IfcStore.library_file
        if library_file is None or library_file.schema == "IFC2X3":
            return results
        project = library_file.by_type("IfcProject")[0]
        results.append((str(project.id()), f"IfcProject {project.Name or 'Unnamed'}", project.Description or ""))
        for library_id, data in cls.data["project_libraries"].items():
            results.append((str(library_id), data["Name"] or "Unnamed", data["Description"] or ""))
        return results


class LinksData:
    linked_data = {}
    enable_culling = False
    is_loaded = False
