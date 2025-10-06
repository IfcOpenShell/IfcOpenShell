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

from typing import TYPE_CHECKING

import bpy
from bonsai.bim.module.tester.data import TesterData
from bonsai.bim.prop import StrProperty, MultipleFileSelect
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


def update_active_specification_index(self: "IfcTesterProperties", context: bpy.types.Context) -> None:
    TesterData.load()


class Specification(PropertyGroup):
    description: StringProperty(name="Description")
    status: BoolProperty(default=False, name="Status")

    if TYPE_CHECKING:
        description: str
        status: bool


class FailedEntities(PropertyGroup):
    ifc_id: IntProperty(name="IFC ID")
    element: StringProperty(name="Element")
    reason: StringProperty(name="Reason")

    if TYPE_CHECKING:
        ifc_id: int
        element: str
        reason: str


class IfcTesterProperties(PropertyGroup):
    specs: PointerProperty(type=MultipleFileSelect)
    ifc_files: PointerProperty(type=MultipleFileSelect)
    should_load_from_memory: BoolProperty(
        default=False,
        name="Load from Memory",
        description="Use IFC file currently loaded in Bonsai",
        options=set(),
    )
    generate_html_report: BoolProperty(default=False, name="Generate HTML report", options=set())
    generate_ods_report: BoolProperty(default=False, name="Generate ODS report", options=set())
    flag: BoolProperty(default=False, name="Flag Failed Entities", options=set())
    active_specification_index: IntProperty(name="Active Specification Index", update=update_active_specification_index)
    active_requirement_index: IntProperty(name="Active Requirement Index")

    old_index: IntProperty(name="", default=0)
    active_failed_entity_index: IntProperty(name="Active Failed Entity Index")
    specifications: CollectionProperty(name="Specifications", type=Specification)
    failed_entities: CollectionProperty(name="FailedEntities", type=FailedEntities)
    has_entities: BoolProperty(default=False, name="")
    n_entities: IntProperty(name="", default=0)
    webapp_server_port: IntProperty(name="Webapp Server Port", default=0)
    webapp_is_running: BoolProperty(default=False, name="Webapp Is Running", options=set())
    websocket_server_port: IntProperty(name="WebSocket Server Port", default=0)
    hide_skipped_specs: BoolProperty(default=False, name="Hide skipped Specifications", options=set())

    if TYPE_CHECKING:
        specs: MultipleFileSelect
        ifc_files: MultipleFileSelect
        should_load_from_memory: bool
        generate_html_report: bool
        generate_ods_report: bool
        flag: bool
        active_specification_index: int
        active_requirement_index: int
        old_index: int
        active_failed_entity_index: int
        specifications: bpy.types.bpy_prop_collection_idprop[Specification]
        failed_entities: bpy.types.bpy_prop_collection_idprop[FailedEntities]
        has_entities: bool
        n_entities: int
        webapp_server_port: int
        webapp_is_running: bool
        websocket_server_port: int
