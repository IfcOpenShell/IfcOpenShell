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


def update_active_specification_index(self, context):
    TesterData.load()


class Specification(PropertyGroup):
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    status: BoolProperty(default=False, name="Status")


class FailedEntities(PropertyGroup):
    ifc_id: IntProperty(name="IFC ID")
    element: StringProperty(name="Element")
    reason: StringProperty(name="Reason")


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
    old_index: IntProperty(name="", default=0)
    active_failed_entity_index: IntProperty(name="Active Failed Entity Index")
    specifications: CollectionProperty(name="Specifications", type=Specification)
    failed_entities: CollectionProperty(name="FailedEntities", type=FailedEntities)
    has_entities: BoolProperty(default=False, name="")
    n_entities: IntProperty(name="", default=0)
