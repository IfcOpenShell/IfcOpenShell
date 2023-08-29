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

from pathlib import Path
import os
import bpy
import json
import importlib
import ifcopenshell
import ifcopenshell.util.pset
from ifcopenshell.util.doc import (
    get_entity_doc,
    get_attribute_doc,
    get_property_set_doc,
    get_property_doc,
    get_predefined_type_doc,
)
import blenderbim.bim
import blenderbim.bim.schema
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore
import blenderbim.tool as tool
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


def update_tab(self, context):
    self.alt_tab = self.previous_tab
    self.previous_tab = self.tab


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


def get_attribute_enum_values(prop, context):
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

    if prop.enum_descriptions:
        items = [(identifier, name, prop.enum_descriptions[i].name) for i, (identifier, name, _) in enumerate(items)]

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


def update_section_line_decorator(self, context):
    compare_node_group = bpy.data.node_groups.get("Section Compare")
    if compare_node_group is None:
        return
    for node in compare_node_group.nodes:
        if not hasattr(node, "operation"):
            continue
        if node.operation == "COMPARE":
            node.inputs[2].default_value = self.section_line_decorator_width
            break


class StrProperty(PropertyGroup):
    pass


class ObjProperty(PropertyGroup):
    obj: bpy.props.PointerProperty(type=bpy.types.Object)


def update_attribute_value(self, context):
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


def set_int_value(self, new_value):
    set_numerical_value(self, "int_value", new_value)


def set_float_value(self, new_value):
    set_numerical_value(self, "float_value", new_value)


def set_numerical_value(self, value_name, new_value):
    if self.value_min_constraint and new_value < self.value_min:
        new_value = self.value_min
    elif self.value_max_constraint and new_value > self.value_max:
        new_value = self.value_max
    self[value_name] = new_value


def get_length_value(self):
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    return self.float_value * si_conversion


def set_length_value(self, value):
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    self.float_value = value / si_conversion


def get_display_name(self):
    name = self.name
    if not self.special_type or self.special_type == "LENGTH":
        return name

    unit_type = f"{self.special_type}UNIT"
    project_unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), unit_type)
    unit_symbol = ifcopenshell.util.unit.get_unit_symbol(project_unit)
    return f"{name}, {unit_symbol}"


class Attribute(PropertyGroup):
    tooltip = "`Right Click > IFC Description` to read the attribute description and online documentation"
    name: StringProperty(name="Name")
    display_name: StringProperty(name="Display Name", get=get_display_name)
    description: StringProperty(name="Description")
    ifc_class: StringProperty(name="Ifc Class")
    data_type: StringProperty(name="Data Type")
    string_value: StringProperty(name="Value", update=update_attribute_value, description=tooltip)
    bool_value: BoolProperty(name="Value", update=update_attribute_value, description=tooltip)
    int_value: IntProperty(
        name="Value",
        description=tooltip,
        update=update_attribute_value,
        get=lambda self: int(self.get("int_value", 0)),
        set=set_int_value,
    )
    float_value: FloatProperty(
        name="Value",
        description=tooltip,
        update=update_attribute_value,
        get=lambda self: float(self.get("float_value", 0.0)),
        set=set_float_value,
    )
    length_value: FloatProperty(
        name="Value", description=tooltip, get=get_length_value, set=set_length_value, unit="LENGTH"
    )
    enum_items: StringProperty(name="Value")
    enum_descriptions: CollectionProperty(type=StrProperty)
    enum_value: EnumProperty(items=get_attribute_enum_values, name="Value", update=update_attribute_value)
    is_null: BoolProperty(name="Is Null")
    is_optional: BoolProperty(name="Is Optional")
    is_uri: BoolProperty(name="Is Uri", default=False)
    is_selected: BoolProperty(name="Is Selected", default=False)
    has_calculator: BoolProperty(name="Has Calculator", default=False)
    value_min: FloatProperty(description="This is used to validate int_value and float_value")
    value_min_constraint: BoolProperty(default=False, description="True if the numerical value has a lower bound")
    value_max: FloatProperty(description="This is used to validate int_value and float_value")
    value_max_constraint: BoolProperty(default=False, description="True if the numerical value has an upper bound")
    special_type: StringProperty(name="Special Value Type", default="")

    def get_value(self):
        if self.is_optional and self.is_null:
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

    def get_value_name(self, display_only=False):
        if self.data_type == "string":
            return "string_value"
        elif self.data_type == "boolean":
            return "bool_value"
        elif self.data_type == "integer":
            return "int_value"
        elif self.data_type == "float":
            if display_only and self.special_type == "LENGTH":
                return "length_value"
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


def get_tab(self, context):
    return [
        ("PROJECT", "Project Overview", "", blenderbim.bim.icons["IFC"].icon_id, 0),
        ("OBJECT", "Object Information", "", "FILE_3D", 1),
        ("GEOMETRY", "Geometry and Materials", "", "MATERIAL", 2),
        ("DRAWINGS", "Drawings and Documents", "", "DOCUMENTS", 3),
        ("SERVICES", "Services and Systems", "", "NETWORK_DRIVE", 4),
        ("STRUCTURE", "Structural Analysis", "", "EDITMODE_HLT", 5),
        ("SCHEDULING", "Costing and Scheduling", "", "NLA", 6),
        ("FM", "Facility Management", "", "PACKAGE", 7),
        ("QUALITY", "Quality and Coordination", "", "COMMUNITY", 8),
        ("BLENDER", "Blender Properties", "", "BLENDER", 9),
    ]


class BIMAreaProperties(PropertyGroup):
    tab: EnumProperty(default=0, items=get_tab, name="Tab", update=update_tab)
    previous_tab: StringProperty(default="PROJECT", name="Previous Tab")
    alt_tab: StringProperty(default="OBJECT", name="Alt Tab")
    active_tab: BoolProperty(default=True, name="Active Tab")
    inactive_tab: BoolProperty(default=False, name="Inactive Tab")


class BIMProperties(PropertyGroup):
    schema_dir: StringProperty(
        default=os.path.join(cwd, "schema") + os.path.sep, name="Schema Directory", update=update_schema_dir
    )
    data_dir: StringProperty(
        default=os.path.join(cwd, "data") + os.path.sep, name="Data Directory", update=update_data_dir
    )
    pset_dir: StringProperty(default=os.path.join("psets") + os.path.sep, name="Default Psets Directory")
    ifc_file: StringProperty(name="IFC File", update=update_ifc_file)
    last_transaction: StringProperty(name="Last Transaction")
    should_section_selected_objects: BoolProperty(name="Section Selected Objects", default=False)
    section_plane_colour: FloatVectorProperty(
        name="Cutaway Colour",
        subtype="COLOR",
        default=(1, 0, 0),
        min=0.0,
        max=1.0,
        update=update_section_color,
    )
    section_line_decorator_width: FloatProperty(
        name="Line Decorator Width",
        default=0.04,
        min=0.0,
        soft_max=1.0,
        update=update_section_line_decorator,
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


class BIMCollectionProperties(PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object)


class BIMObjectProperties(PropertyGroup):
    collection: PointerProperty(type=bpy.types.Collection)
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
    ifc_coordinate_id: IntProperty(name="IFC Coordinate ID")
    shading_checksum: StringProperty(name="Shading Checksum")


class BIMMeshProperties(PropertyGroup):
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    ifc_boolean_id: IntProperty(name="IFC Boolean ID")
    obj: bpy.props.PointerProperty(type=bpy.types.Object)
    has_openings_applied: BoolProperty(name="Has Openings Applied", default=True)
    is_native: BoolProperty(name="Is Native", default=False)
    is_swept_solid: BoolProperty(name="Is Swept Solid")
    is_parametric: BoolProperty(name="Is Parametric", default=False)
    subshape_type: StringProperty(name="Subshape Type")
    ifc_definition: StringProperty(name="IFC Definition")
    ifc_parameters: CollectionProperty(name="IFC Parameters", type=IfcParameter)
    material_checksum: StringProperty(name="Material Checksum", default="[]")
    mesh_checksum: StringProperty(name="Mesh Checksum", default="")
