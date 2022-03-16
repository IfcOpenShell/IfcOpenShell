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
from pathlib import Path
from blenderbim.bim.prop import StrProperty
from blenderbim.bim.module.root.prop import get_ifc_classes
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

scenarios_enum = []


def purge():
    global scenarios_enum
    scenarios_enum = []


def getScenarios(self, context):
    global scenarios_enum
    if len(scenarios_enum) < 1:
        scenarios_enum.clear()

        if context.scene.BimTesterProperties.feature != "":
            with open(context.scene.BimTesterProperties.feature, "r") as feature_file:
                lines = feature_file.readlines()
                for line in lines:
                    if "Scenario:" in line:
                        s = line.strip()[len("Scenario: ") :]
                        scenarios_enum.append((s, s, ""))
    return scenarios_enum


def refreshScenarios(self, context):
    global scenarios_enum
    scenarios_enum.clear()
    getScenarios(self, context)


class BimTesterProperties(PropertyGroup):
    feature: StringProperty(default="", name="Feature / IDS", update=refreshScenarios)
    steps: StringProperty(default="", name="Custom Steps")
    ifc_file: StringProperty(default="", name="IFC File")
    audit_ifc_class: EnumProperty(items=get_ifc_classes, name="Audit Class")
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")
    scenario: EnumProperty(items=getScenarios, name="Scenario")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
