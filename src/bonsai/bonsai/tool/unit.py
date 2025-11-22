# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import bpy
import json
import math
import ifcopenshell
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from lark import Lark, Transformer
from typing import Union, Literal, Any, TYPE_CHECKING, assert_never

if TYPE_CHECKING:
    from bonsai.bim.module.unit.prop import BIMUnitProperties


def parse_distance_string(input_string: str, use_project_unit: bool = True) -> tuple[bool, float]:
    """
    Parse a distance string with optional unit suffixes and convert to meters.

    This function parses distance inputs with units (e.g., "5m", "10ft", "3.5cm")
    and converts them to meters (SI units) for use in IFC models.

    Supports:
    - Metric units: mm, cm, dm, m
    - Imperial units: ft/feet ('), in/inches (")
    - Arithmetic expressions: +, -, *, /
    - Fractions for imperial units (e.g., 1/2")
    - Formula mode: values starting with "="

    :param input_string: The string to parse (e.g., "5m", "10ft", "10'6\"", "3.5cm", "12in")
    :param use_project_unit: If True, uses project unit scale; if False, uses Blender unit scale
    :return: Tuple (is_valid, value_in_meters) where is_valid indicates successful parsing
             and value_in_meters is the converted value in meters

    Examples:
        >>> parse_distance_string("5m")
        (True, 5.0)
        >>> parse_distance_string("30cm")
        (True, 0.3)
        >>> parse_distance_string("10ft")
        (True, 3.048)
        >>> parse_distance_string("12in")
        (True, 0.3048)
        >>> parse_distance_string("5'6\"")
        (True, 1.6764)
        >>> parse_distance_string("invalid")
        (False, 0.0)
    """

    grammar_imperial = """
    start: (FORMULA dim expr) | dim
    dim: imperial

    FORMULA: "="

    imperial: feet_inches | feet_only | inches_only | plain_number
    feet_only: NUMBER (FEET_SYM | FEET_TEXT)
    inches_only: (NUMBER | fraction) (INCH_SYM | INCH_TEXT)
    feet_inches: NUMBER (FEET_SYM | FEET_TEXT) "-"? (NUMBER | fraction) (INCH_SYM | INCH_TEXT)
    plain_number: NUMBER
    fraction: NUMBER "/" NUMBER

    expr: (ADD | SUB) dim | (MUL | DIV) NUMBER

    NUMBER: /-?\\d+(?:\\.\\d+)?/
    FEET_SYM: "'"
    FEET_TEXT: "ft"
    INCH_SYM: "\\""
    INCH_TEXT: "in"
    ADD: "+"
    SUB: "-"
    MUL: "*"
    DIV: "/"

    %ignore " "
    """

    grammar_metric = """
    start: FORMULA? dim expr?
    dim: metric

    FORMULA: "="

    metric: NUMBER (MM | CM | DM | M | DEG)?

    expr: (ADD | SUB | MUL | DIV) dim

    NUMBER: /-?\\d+(?:\\.\\d+)?/
    MM: "mm"
    CM: "cm"
    DM: "dm"
    M: "m"
    DEG: "°"
    ADD: "+"
    SUB: "-"
    MUL: "*"
    DIV: "/"

    %ignore " "
    """

    class InputTransform(Transformer):
        def NUMBER(self, n):
            return float(n)

        def fraction(self, numbers):
            return numbers[0] / numbers[1]

        def plain_number(self, args):
            # A plain number in imperial context is assumed to be feet
            feet = args[0]
            # Convert feet to meters (1 foot = 0.3048 meters)
            return feet * 0.3048

        def feet_only(self, args):
            # args[0] is the number of feet, args[1] is the unit token (we can ignore it)
            feet = args[0]
            # Convert feet to meters (1 foot = 0.3048 meters)
            return feet * 0.3048

        def inches_only(self, args):
            # args[0] is the number (or fraction) of inches, args[1] is the unit token
            inches = args[0]
            # Convert inches to meters (1 inch = 0.0254 meters)
            return inches * 0.0254

        def feet_inches(self, args):
            # Grammar: NUMBER (FEET_SYM | FEET_TEXT) "-"? (NUMBER | fraction) (INCH_SYM | INCH_TEXT)
            # args will be: [feet_number, feet_unit_token, inches_number, inch_unit_token]
            # or with optional dash: [feet_number, feet_unit_token, dash_token, inches_number, inch_unit_token]
            # We need to extract just the numbers
            feet = args[0]
            # Find the inches value - it's the first number after the feet number
            inches = None
            for arg in args[1:]:
                if isinstance(arg, (int, float)):
                    inches = arg
                    break
            if inches is None:
                inches = 0
            # Convert to meters
            total_meters = (feet * 0.3048) + (inches * 0.0254)
            return total_meters

        def imperial(self, args):
            # Just return the value from the sub-rule (feet_only, inches_only, or feet_inches)
            return args[0]

        def metric(self, args):
            # args[0] is the NUMBER, args[1] if present is the unit
            value = args[0]
            if len(args) > 1:
                unit = str(args[1])
                # Convert to meters based on unit
                if unit == "mm":
                    value = value / 1000.0
                elif unit == "cm":
                    value = value / 100.0
                elif unit == "dm":
                    value = value / 10.0
                elif unit == "m":
                    value = value  # already in meters
                elif unit == "°":
                    value = value  # degrees, pass through
            # If no unit specified, assume it's already in the project's unit system
            return value

        def dim(self, args):
            return args[0]

        def expr(self, args):
            op = args[0]
            value = float(args[1])
            if op == "+":
                return lambda x: x + value
            elif op == "-":
                return lambda x: x - value
            elif op == "*":
                return lambda x: x * value
            elif op == "/":
                return lambda x: x / value

        def FORMULA(self, args):
            return args[0]

        def start(self, args):
            i = 0
            if args[0] == "=":
                i += 1
            else:
                if len(args) > 1:
                    raise ValueError("Invalid input.")
            dimension = args[i]
            if len(args) > i + 1:
                expression = args[i + 1]
                return expression(dimension)
            else:
                return dimension

    try:
        # Determine unit scale
        if use_project_unit and tool.Ifc.get():
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        else:
            unit_scale = tool.Blender.get_unit_scale()

        # Try to parse with the project's default grammar first
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            primary_parser = Lark(grammar_imperial)
            fallback_parser = Lark(grammar_metric)
        else:
            primary_parser = Lark(grammar_metric)
            fallback_parser = Lark(grammar_imperial)

        # Try parsing with primary grammar
        parse_tree = None
        try:
            parse_tree = primary_parser.parse(input_string)
            print(f"Primary parser succeeded for '{input_string}'")
        except Exception as e:
            print(f"Primary parser failed for '{input_string}': {e}")
            # If primary fails, try fallback grammar (allows metric in imperial projects and vice versa)
            try:
                parse_tree = fallback_parser.parse(input_string)
                print(f"Fallback parser succeeded for '{input_string}'")
            except Exception as e2:
                print(f"Fallback parser failed for '{input_string}': {e2}")
                pass

        if parse_tree is None:
            print(f"No parse tree for '{input_string}'")
            return False, 0.0

        # Transform the parse tree to get the numeric result
        transformer = InputTransform()
        result = transformer.transform(parse_tree)
        print(f"Parsed '{input_string}' -> {result} meters (unit_scale={unit_scale})")
        result = round(result, 4)

        return True, result
    except Exception as e:
        print(f"Parse exception for '{input_string}': {e}")
        return False, 0.0


class Unit(bonsai.core.tool.Unit):
    UNIT_TYPE = Literal["LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT"]

    @staticmethod
    def format_distance(meters: float, use_imperial: bool = None) -> str:
        """
        Format a distance value in meters to a string in the project's unit system.

        :param meters: The distance value in meters
        :param use_imperial: If True, format as imperial; if False, format as metric; if None, auto-detect from scene
        :return: Formatted string with units
        """
        if use_imperial is None:
            use_imperial = bpy.context.scene.unit_settings.system == "IMPERIAL"

        if use_imperial:
            # Convert meters to feet
            total_feet = meters / 0.3048
            feet = int(total_feet)
            inches = (total_feet - feet) * 12

            # If inches is very close to 0, just show feet
            if abs(inches) < 0.01:
                if feet == 0:
                    return "0'"
                return f"{feet}'"
            # If feet is 0, just show inches
            elif feet == 0:
                return f'{inches:.4g}"'
            # Show both feet and inches
            else:
                return f"{feet}'{inches:.4g}\""
        else:
            # Use metric - choose appropriate unit
            if abs(meters) >= 1.0:
                return f"{meters:.4g}m"
            elif abs(meters) >= 0.01:
                return f"{meters * 100:.4g}cm"
            else:
                return f"{meters * 1000:.4g}mm"

    @classmethod
    def get_unit_props(cls) -> BIMUnitProperties:
        return bpy.context.scene.BIMUnitProperties

    @classmethod
    def clear_active_unit(cls) -> None:
        props = cls.get_unit_props()
        props.active_unit_id = 0

    @classmethod
    def disable_editing_units(cls) -> None:
        props = cls.get_unit_props()
        props.is_editing = False

    @classmethod
    def enable_editing_units(cls) -> None:
        props = cls.get_unit_props()
        props.is_editing = True

    @classmethod
    def export_unit_attributes(cls) -> dict[str, Any]:
        def callback(attributes, prop):
            if prop.name == "Dimensions":
                try:
                    attributes[prop.name] = json.loads(prop.get_value())
                except:
                    attributes[prop.name] = (0, 0, 0, 0, 0, 0, 0)
                return True

        props = cls.get_unit_props()
        return bonsai.bim.helper.export_attributes(props.unit_attributes, callback=callback)

    @classmethod
    def get_scene_unit_name(cls, unit_type: UNIT_TYPE) -> str:
        bim_props = tool.Blender.get_bim_props()
        if unit_type == "LENGTHUNIT":
            assert bpy.context.scene
            props = bpy.context.scene.unit_settings
            if props.length_unit == "MILES":
                return "mile"
            elif props.length_unit == "FEET" or props.length_unit == "ADAPTIVE":
                return "foot"
            elif props.length_unit == "INCHES":
                return "inch"
            elif props.length_unit == "THOU":
                return "thou"
            return "foot"
        elif unit_type == "AREAUNIT":
            return bim_props.area_unit
        elif unit_type == "VOLUMEUNIT":
            return bim_props.volume_unit
        else:
            assert_never(unit_type)

    @classmethod
    def get_scene_unit_si_prefix(cls, unit_type: UNIT_TYPE) -> Union[str, None]:
        bim_props = tool.Blender.get_bim_props()
        if unit_type == "LENGTHUNIT":
            assert bpy.context.scene
            props = bpy.context.scene.unit_settings
            if props.length_unit == "ADAPTIVE" or props.length_unit == "METERS":
                return
            return props.length_unit.replace("METERS", "")
        elif unit_type == "AREAUNIT":
            unit = bim_props.area_unit
        elif unit_type == "VOLUMEUNIT":
            unit = bim_props.volume_unit
        else:
            assert_never(unit_type)
        if "/" in unit:
            return unit.split("/")[0]

    @classmethod
    def import_unit_attributes(cls, unit: ifcopenshell.entity_instance) -> None:
        props = cls.get_unit_props()

        def callback(name, prop, data):
            if name == "Dimensions" and data["type"] != "IfcSIUnit":
                new = props.unit_attributes.add()
                new.name = name
                new.is_null = data[name] is None
                new.is_optional = False
                new.data_type = "string"
                new.string_value = json.dumps([e for e in tool.Ifc.get().by_id(data["id"]).Dimensions])
                return True

        props.unit_attributes.clear()
        bonsai.bim.helper.import_attributes(unit, props.unit_attributes, callback=callback)

    @classmethod
    def import_units(cls) -> None:
        props = tool.Unit.get_unit_props()
        props.units.clear()

        units: list[ifcopenshell.entity_instance] = []
        for unit_class in ["IfcDerivedUnit", "IfcMonetaryUnit", "IfcNamedUnit"]:
            units += tool.Ifc.get().by_type(unit_class)

        assigned_units = []
        if assignment := tool.Ifc.get().by_type("IfcProject")[0].UnitsInContext:
            assigned_units = assignment.Units

        for unit in units:
            name = ""
            if unit.is_a("IfcMonetaryUnit"):
                name = unit.Currency
            elif not unit.is_a("IfcDerivedUnit"):
                name = unit.Name or ""

            if unit.is_a("IfcSIUnit") and unit.Prefix:
                if "_" in name:
                    name_components = name.split("_")
                    name = f"{name_components[0]} {unit.Prefix}{name_components[1]}"
                else:
                    name = f"{unit.Prefix}{name}"

            if unit.is_a("IfcMonetaryUnit"):
                unit_type = "CURRENCY"
            else:
                unit_type = getattr(unit, "UserDefinedType", None)
                if not unit_type:
                    unit_type = getattr(unit, "UnitType", None)

            new = props.units.add()
            new.ifc_definition_id = unit.id()
            new.name = name
            new.unit_type = unit_type
            new.is_assigned = unit in assigned_units
            new.ifc_class = unit.is_a()

    @classmethod
    def is_scene_unit_metric(cls) -> bool:
        assert bpy.context.scene
        return bpy.context.scene.unit_settings.system in ["METRIC", "NONE"]

    @classmethod
    def is_unit_class(cls, unit: ifcopenshell.entity_instance, ifc_class: str) -> bool:
        return unit.is_a(ifc_class)

    @classmethod
    def set_active_unit(cls, unit: ifcopenshell.entity_instance) -> None:
        props = cls.get_unit_props()
        props.active_unit_id = unit.id()

    @classmethod
    def get_project_currency_unit(cls) -> Union[ifcopenshell.entity_instance, None]:
        if assignment := tool.Ifc.get().by_type("IfcProject")[0].UnitsInContext:
            for unit in assignment.Units:
                if unit.is_a("IfcMonetaryUnit"):
                    return unit

    @classmethod
    def get_currency_name(cls) -> Union[str, None]:
        unit = cls.get_project_currency_unit()
        if unit:
            return unit.Currency

    @classmethod
    def blender_format_unit(cls, value: float) -> str:
        assert bpy.context.scene
        return bpy.utils.units.to_string(
            bpy.context.scene.unit_settings.system,
            "LENGTH",
            value,
            precision=4,
            split_unit=bpy.context.scene.unit_settings.system == "IMPERIAL",
        )

    @classmethod
    def format_value(cls, value: float) -> str:
        context = next(iter(tool.Ifc.get().by_type("IfcGeometricRepresentationContext")), None)
        if context and (precision := context.Precision):
            decimal_places = math.ceil(math.log10(1 / precision))
        else:
            precision = 1e-5
            decimal_places = 5
        return str(round(precision * round(value / precision), decimal_places))

    @classmethod
    def get_icon_for_unit_class(cls, ifc_class: str) -> str:
        if ifc_class == "IfcSIUnit":
            return "SNAP_GRID"
        elif ifc_class == "IfcMonetaryUnit":
            return "COPY_ID"
        return "MOD_MESHDEFORM"
