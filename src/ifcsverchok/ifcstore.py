# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Martina Jakubowska <martina@jakubowska.dk>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
from ifcopenshell import template
from typing import Union


class SvIfcStore:
    path = ""
    file: Union[ifcopenshell.file, None] = None
    schema = None
    cache = None
    cache_path = None
    id_map = {}
    guid_map = {}
    deleted_ids = set()
    edited_objs = set()
    pset_template_path = ""
    pset_template_file = None
    library_path = ""
    library_file = None
    element_listeners = set()
    undo_redo_stack_objects = set()
    undo_redo_stack_object_names = {}
    current_transaction = ""
    last_transaction = ""
    history = []
    future = []
    schema_identifiers = ["IFC4", "IFC2X3"]

    @staticmethod
    def purge() -> None:
        SvIfcStore.path = ""
        SvIfcStore.file = None
        SvIfcStore.schema = None
        SvIfcStore.cache = None
        SvIfcStore.cache_path = None
        SvIfcStore.id_map = {}
        SvIfcStore.guid_map = {}
        SvIfcStore.deleted_ids = set()
        SvIfcStore.edited_objs = set()
        SvIfcStore.pset_template_path = ""
        SvIfcStore.pset_template_file = None
        SvIfcStore.library_path = ""
        SvIfcStore.library_file = None
        SvIfcStore.last_transaction = ""
        SvIfcStore.history = []
        SvIfcStore.future = []
        SvIfcStore.schema_identifiers = ["IFC4", "IFC2X3"]

    @staticmethod
    def create_boilerplate() -> ifcopenshell.file:
        file = template.create(
            filename="IfcSverchokDemoFile",
            organization=None,
            creator=None,
            project_name="IfcSverchokDemoProject",
        )
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            # TODO change units to imperial
            pass
        model = ifcopenshell.util.representation.get_context(file, context="Model")
        print("model: ", model)
        context = ifcopenshell.api.run(
            "context.add_context",
            file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )

        SvIfcStore.file = file
        return SvIfcStore.file

    @staticmethod
    def get_file() -> ifcopenshell.file:
        if SvIfcStore.file is None:
            SvIfcStore.create_boilerplate()
        return SvIfcStore.file
