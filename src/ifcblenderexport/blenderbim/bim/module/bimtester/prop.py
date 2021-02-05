import os
from pathlib import Path
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty
from blenderbim.bim.module.root.prop import getIfcClasses
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
classes_enum = []


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
    feature: StringProperty(default="", name="Feature File", update=refreshScenarios)
    steps: StringProperty(default="", name="Custom Steps")
    ifc_file: StringProperty(default="", name="IFC File")
    audit_ifc_class: EnumProperty(items=getIfcClasses, name="Audit Class")
    qa_reject_element_reason: StringProperty(name="Element Rejection Reason")
    scenario: EnumProperty(items=getScenarios, name="Scenario")
    should_load_from_memory: BoolProperty(default=False, name="Load from Memory")
