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
import ifcopenshell
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.core.aggregate
import bonsai.core.context
import bonsai.core.tool
import bonsai.core.root
import bonsai.core.unit
import bonsai.core.owner
import bonsai.bim.schema
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from ifcopenshell.api.project.append_asset import APPENDABLE_ASSET_TYPES
from pathlib import Path
from typing import Optional


class Project(bonsai.core.tool.Project):
    @classmethod
    def append_all_types_from_template(cls, template: str) -> None:
        # TODO refactor
        filepath = os.path.join(bpy.context.scene.BIMProperties.data_dir, "templates", "projects", template)
        bpy.ops.bim.select_library_file(filepath=filepath)
        if IfcStore.library_file.schema != tool.Ifc.get().schema:
            return
        for element in IfcStore.library_file.by_type("IfcTypeProduct"):
            bpy.ops.bim.append_library_element(definition=element.id())

    @classmethod
    def create_empty(cls, name):
        return bpy.data.objects.new(name, None)

    @classmethod
    def load_default_thumbnails(cls):
        if tool.Ifc.get().by_type("IfcElementType"):
            ifc_class = sorted(tool.Ifc.get().by_type("IfcElementType"), key=lambda e: e.is_a())[0].is_a()
            bpy.ops.bim.load_type_thumbnails(ifc_class=ifc_class, offset=0, limit=9)

    @classmethod
    def load_pset_templates(cls):
        pset_dir = tool.Ifc.resolve_uri(bpy.context.scene.BIMProperties.pset_dir)
        if os.path.isdir(pset_dir):
            for path in Path(pset_dir).glob("*.ifc"):
                bonsai.bim.schema.ifc.psetqto.templates.append(ifcopenshell.open(path))

    @classmethod
    def run_aggregate_assign_object(cls, relating_obj=None, related_obj=None):
        return bonsai.core.aggregate.assign_object(
            tool.Ifc, tool.Aggregate, tool.Collector, relating_obj=relating_obj, related_obj=related_obj
        )

    @classmethod
    def run_context_add_context(cls, context_type=None, context_identifier=None, target_view=None, parent=None):
        return bonsai.core.context.add_context(
            tool.Ifc,
            context_type=context_type,
            context_identifier=context_identifier,
            target_view=target_view,
            parent=parent,
        )

    @classmethod
    def run_owner_add_organisation(cls):
        return bonsai.core.owner.add_organisation(tool.Ifc)

    @classmethod
    def run_owner_add_person(cls):
        return bonsai.core.owner.add_person(tool.Ifc)

    @classmethod
    def run_owner_add_person_and_organisation(cls, person=None, organisation=None):
        return bonsai.core.owner.add_person_and_organisation(tool.Ifc, person=person, organisation=organisation)

    @classmethod
    def run_owner_set_user(cls, user=None):
        return bonsai.core.owner.set_user(tool.Owner, user=user)

    @classmethod
    def run_root_assign_class(
        cls,
        obj: bpy.types.Object,
        ifc_class: str,
        predefined_type: Optional[str] = None,
        should_add_representation: bool = True,
        context: Optional[ifcopenshell.entity_instance] = None,
        ifc_representation_class: Optional[str] = None,
    ) -> ifcopenshell.entity_instance:
        return bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class=ifc_class,
            predefined_type=predefined_type,
            should_add_representation=should_add_representation,
            context=context,
            ifc_representation_class=ifc_representation_class,
        )

    @classmethod
    def run_unit_assign_scene_units(cls):
        return bonsai.core.unit.assign_scene_units(tool.Ifc, tool.Unit)

    @classmethod
    def set_context(cls, context):
        bonsai.bim.handler.refresh_ui_data()
        bpy.context.scene.BIMRootProperties.contexts = str(context.id())

    @classmethod
    def set_default_context(cls):
        context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")
        if context:
            bpy.context.scene.BIMRootProperties.contexts = str(context.id())

    @classmethod
    def set_default_modeling_dimensions(cls):
        props = bpy.context.scene.BIMModelProperties
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props.extrusion_depth = 3
        props.length = 1
        props.rl1 = 0
        props.rl2 = 1
        props.x = 0.5
        props.y = 0.5
        props.z = 0.5

    @classmethod
    def get_recent_ifc_projects_path(cls) -> Path:
        return Path(bpy.utils.user_resource("CONFIG")) / "recent-ifc-projects.txt"

    _recent_ifc_projects_loaded: bool = False
    _recent_ifc_projects: list[Path] = []

    @classmethod
    def get_recent_ifc_projects(cls) -> list[Path]:
        if cls._recent_ifc_projects_loaded:
            return cls._recent_ifc_projects

        filepath = cls.get_recent_ifc_projects_path()
        if not filepath.exists():
            cls._recent_ifc_projects = []
            return []

        paths = []
        with open(filepath, "r") as fi:
            for line in fi:
                line = line.strip()
                if not line:
                    continue
                paths.append(Path(line))

        cls._recent_ifc_projects = paths
        return paths

    @classmethod
    def write_recent_ifc_projects(cls, filepaths: list[Path]) -> None:
        recent_projects_path = cls.get_recent_ifc_projects_path()
        try:
            recent_projects_path.parent.mkdir(parents=True, exist_ok=True)
            with open(recent_projects_path, "w") as fo:
                fo.write("\n".join(str(p) for p in filepaths))
            cls._recent_ifc_projects_loaded = False
        except PermissionError:
            msg = (
                f"WARNING. PermissionError trying to access '{str(recent_projects_path)}'. "
                "List of recently opened IFC projects won't be stored between Blender sessions."
            )
            print(msg)
            cls._recent_ifc_projects = filepaths

    @classmethod
    def add_recent_ifc_project(cls, filepath: Path) -> None:
        """Add `filepath` to the list of the recently opened IFC projects.

        If `filepath` was opened before, bump it in the list.
        """
        filepath = filepath.absolute()
        current_filepaths = cls.get_recent_ifc_projects()
        if filepath in current_filepaths:
            current_filepaths.remove(filepath)
        current_filepaths = [filepath] + current_filepaths
        # Limit it to 20 recent files.
        current_filepaths = current_filepaths[:20]
        cls.write_recent_ifc_projects(current_filepaths)

    @classmethod
    def clear_recent_ifc_projects(cls) -> None:
        cls.write_recent_ifc_projects([])

    @classmethod
    def get_appendable_asset_types(cls) -> tuple[str, ...]:
        return tuple(e for e in APPENDABLE_ASSET_TYPES if e != "IfcProduct")

    @classmethod
    def run_root_reload_grid_decorator(cls) -> None:
        tool.Root.reload_grid_decorator()
