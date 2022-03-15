# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
import bpy
import json
import importlib
import ifcopenshell
import ifcopenshell.util.pset
import blenderbim.bim.handler
import blenderbim.bim.schema
from blenderbim.bim.ifc import IfcStore
from collections import defaultdict
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

cwd = os.path.dirname(os.path.realpath(__file__))

materialpsetnames_enum = []


def update_preset(self, context):
    from blenderbim.bim.data.ui.presets import presets

    module_visibility = context.scene.BIMProperties.module_visibility
    chosen_preset = context.scene.BIMProperties.ui_preset

    for module in module_visibility:
        module.is_visible = module.name in presets[chosen_preset]


def load_presets(self, context):
    from blenderbim.bim.data.ui.presets import presets

    return [(preset, preset, "") for preset in presets.keys()]


def update_is_visible(self, context):
    from blenderbim.bim import modules

    # TODO: Pset depends on sequence module as an edge case.
    if self.name == "sequence" and not self.is_visible:
        context.scene.BIMProperties.module_visibility["pset"].is_visible = False

    for cls in modules[self.name].classes:
        if not issubclass(cls, bpy.types.Panel):
            continue

        if self.is_visible:
            try:
                bpy.utils.register_class(cls)
            except:
                pass
        else:
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass


# If we don't cache strings, accents get mangled due to a Blender bug
# https://blender.stackexchange.com/questions/216230/is-there-a-workaround-for-the-known-bug-in-dynamic-enumproperty
# https://github.com/IfcOpenShell/IfcOpenShell/pull/1945
# https://github.com/IfcOpenShell/IfcOpenShell/issues/1941
def cache_string(s):
    s = str(s)
    if not hasattr(cache_string, "data"):  # Another way to define a function attribute
        cache_string.data = defaultdict(str)
    cache_string.data[s] = s
    return cache_string.data[s]


cache_string.data = {}


def getAttributeEnumValues(prop, context):
    # Support weird buildingSMART dictionary mappings which behave like enums
    items = []
    data = json.loads(prop.enum_items)

    if isinstance(data, dict):
        for k, v in data.items():
            items.append(
                (
                    cache_string(k),
                    cache_string(v),
                    "",
                )
            )
    else:
        for e in data:
            items.append(
                (
                    cache_string(e),
                    cache_string(e),
                    "",
                )
            )

    return items


def update_schema_dir(self, context):
    import blenderbim.bim.schema

    blenderbim.bim.schema.ifc.schema_dir = context.scene.BIMProperties.schema_dir


def update_data_dir(self, context):
    import blenderbim.bim.schema

    blenderbim.bim.schema.ifc.data_dir = context.scene.BIMProperties.data_dir


def update_ifc_file(self, context):
    if context.scene.BIMProperties.ifc_file:
        blenderbim.bim.handler.loadIfcStore(context.scene)


def getMaterialPsetNames(self, context):
    global materialpsetnames_enum
    materialpsetnames_enum.clear()
    psetqto = ifcopenshell.util.pset.get_template("IFC4")
    pset_names = psetqto.get_applicable_names("IfcMaterial", pset_only=True)
    materialpsetnames_enum.extend([(p, p, "") for p in pset_names])
    return materialpsetnames_enum


def update_section_color(self, context):
    section_node_group = bpy.data.node_groups.get("Section Override")
    if section_node_group is None:
        return
    try:
        emission_node = next(n for n in section_node_group.nodes if isinstance(n, bpy.types.ShaderNodeEmission))
        emission_node.inputs[0].default_value = list(self.section_plane_colour) + [1]
    except StopIteration:
        pass


class StrProperty(PropertyGroup):
    pass


class ObjProperty(PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)


def updateAttributeValue(self, context):
    value_name = self.get_value_name()
    if value_name:
        value_names = [value_name]
    else:
        # We may not have a value name in <select> data types, so let's check everything
        value_names = ["string_value", "bool_value", "int_value", "float_value", "enum_value"]
    for name in value_names:
        if name == "enum_value" and not self.enum_items:
            continue
        if getattr(self, name, None):
            self.is_null = False


class Attribute(PropertyGroup):
    name: StringProperty(name="Name")
    data_type: StringProperty(name="Data Type")
    string_value: StringProperty(name="Value", update=updateAttributeValue)
    bool_value: BoolProperty(name="Value", update=updateAttributeValue)
    int_value: IntProperty(name="Value", update=updateAttributeValue)
    float_value: FloatProperty(name="Value", update=updateAttributeValue)
    enum_items: StringProperty(name="Value")
    enum_value: EnumProperty(items=getAttributeEnumValues, name="Value", update=updateAttributeValue)
    is_null: BoolProperty(name="Is Null")
    is_optional: BoolProperty(name="Is Optional")
    is_uri: BoolProperty(name="Is Uri", default=False)

    def get_value(self):
        if self.is_null:
            return None
        return getattr(self, str(self.get_value_name()), None)

    def get_value_default(self):
        if self.data_type == "string":
            return ""
        elif self.data_type == "integer":
            return 0
        elif self.data_type == "float":
            return 0.0
        elif self.data_type == "boolean":
            return False
        elif self.data_type == "enum":
            return "0"

    def get_value_name(self):
        if self.data_type == "string":
            return "string_value"
        elif self.data_type == "boolean":
            return "bool_value"
        elif self.data_type == "integer":
            return "int_value"
        elif self.data_type == "float":
            return "float_value"
        elif self.data_type == "enum":
            return "enum_value"

    def set_value(self, value):
        if isinstance(value, str):
            self.data_type = "string"
        elif isinstance(value, float):
            self.data_type = "float"
        elif isinstance(value, bool):  # Make sure this is evaluated BEFORE integer
            self.data_type = "boolean"
        elif isinstance(value, int):
            self.data_type = "integer"
        else:
            self.data_type = "string"
            value = str(value)
        setattr(self, self.get_value_name(), value)


class ModuleVisibility(PropertyGroup):
    name: StringProperty(name="Name")
    is_visible: BoolProperty(name="Value", default=True, update=update_is_visible)


class BIMProperties(PropertyGroup):
    ui_preset: EnumProperty(
        name="UI Preset",
        description="Select from one of the available UI presets, or configure the modules to your preference below",
        update=update_preset,
        items=load_presets,
    )
    module_visibility: CollectionProperty(name="Module Visibility", type=ModuleVisibility)
    schema_dir: StringProperty(
        default=os.path.join(cwd, "schema") + os.path.sep, name="Schema Directory", update=update_schema_dir
    )
    data_dir: StringProperty(
        default=os.path.join(cwd, "data") + os.path.sep, name="Data Directory", update=update_data_dir
    )
    ifc_file: StringProperty(name="IFC File", update=update_ifc_file)
    last_transaction: StringProperty(name="Last Transaction")
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    section_plane_colour: FloatVectorProperty(
        name="Temporary Section Cutaway Colour",
        subtype="COLOR",
        default=(1, 0, 0),
        min=0.0,
        max=1.0,
        update=update_section_color,
    )
    area_unit: EnumProperty(
        default="SQUARE_METRE",
        items=[
            ("NANO/SQUARE_METRE", "Square Nanometre", ""),
            ("MICRO/SQUARE_METRE", "Square Micrometre", ""),
            ("MILLI/SQUARE_METRE", "Square Millimetre", ""),
            ("DECI/SQUARE_METRE", "Square Decimetre", ""),
            ("CENTI/SQUARE_METRE", "Square Centimetre", ""),
            ("SQUARE_METRE", "Square Metre", ""),
            ("KILO/SQUARE_METRE", "Square Kilometre", ""),
            ("square inch", "Square Inch", ""),
            ("square foot", "Square Foot", ""),
            ("square yard", "Square Yard", ""),
            ("square mile", "Square Mile", ""),
        ],
        name="IFC Area Unit",
    )
    volume_unit: EnumProperty(
        default="CUBIC_METRE",
        items=[
            ("NANO/CUBIC_METRE", "Cubic Nanometre", ""),
            ("MICRO/CUBIC_METRE", "Cubic Micrometre", ""),
            ("MILLI/CUBIC_METRE", "Cubic Millimetre", ""),
            ("DECI/CUBIC_METRE", "Cubic Decimetre", ""),
            ("CENTI/CUBIC_METRE", "Cubic Centimetre", ""),
            ("CUBIC_METRE", "Cubic Metre", ""),
            ("KILO/CUBIC_METRE", "Cubic Kilometre", ""),
            ("cubic inch", "Cubic Inch", ""),
            ("cubic foot", "Cubic Foot", ""),
            ("cubic yard", "Cubic Yard", ""),
        ],
        name="IFC Volume Unit",
    )
    metric_precision: FloatProperty(default=0, name="Drawing Metric Precision")
    imperial_precision: EnumProperty(
        items=[
            ("NONE", "No rounding", ""),
            ("1", 'Nearest 1"', ""),
            ("1/2", 'Nearest 1/2"', ""),
            ("1/4", 'Nearest 1/4"', ""),
            ("1/8", 'Nearest 1/8"', ""),
            ("1/16", 'Nearest 1/16"', ""),
            ("1/32", 'Nearest 1/32"', ""),
            ("1/64", 'Nearest 1/64"', ""),
            ("1/128", 'Nearest 1/128"', ""),
            ("1/256", 'Nearest 1/256"', ""),
        ],
        name="Drawing Imperial Precision",
    )


class IfcParameter(PropertyGroup):
    name: StringProperty(name="Name")
    step_id: IntProperty(name="STEP ID")
    index: IntProperty(name="Index")
    value: FloatProperty(name="Value")  # For now, only floats
    type: StringProperty(name="Type")


class PsetQto(PropertyGroup):
    name: StringProperty(name="Name")
    properties: CollectionProperty(name="Properties", type=Attribute)
    is_expanded: BoolProperty(name="Is Expanded", default=True)
    is_editable: BoolProperty(name="Is Editable")


class GlobalId(PropertyGroup):
    name: StringProperty(name="Name")


class BIMObjectProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    blender_offset_type: EnumProperty(
        items=[(o, o, "") for o in ["NONE", "OBJECT_PLACEMENT", "CARTESIAN_POINT"]],
        name="Blender Offset",
        default="NONE",
    )
    is_reassigning_class: BoolProperty(name="Is Reassigning Class")
    location_checksum: StringProperty(name="Location Checksum")
    rotation_checksum: StringProperty(name="Rotation Checksum")


class BIMMaterialProperties(PropertyGroup):
    is_external: BoolProperty(name="Has External Definition")
    location: StringProperty(name="Location")
    identification: StringProperty(name="Identification")
    name: StringProperty(name="Name")
    pset_name: EnumProperty(items=getMaterialPsetNames, name="Pset Name")
    psets: CollectionProperty(name="Psets", type=PsetQto)
    attributes: CollectionProperty(name="Attributes", type=Attribute)
    # In Blender, a material object can map to an IFC material, IFC surface style, or both
    ifc_style_id: IntProperty(name="IFC Style ID")


class BIMMeshProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    is_native: BoolProperty(name="Is Native", default=False)
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    is_parametric: BoolProperty(name="Is Parametric", default=False)
    ifc_definition: StringProperty(name="IFC Definition")
    ifc_parameters: CollectionProperty(name="IFC Parameters", type=IfcParameter)
    material_checksum: StringProperty(name="Material Checksum", default="[]")
