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

import json
import math
from typing import TYPE_CHECKING, Any, Literal, Union

import bpy
import ifcopenshell
import ifcopenshell.util.unit
from lark import Lark, Transformer

import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.unit.prop import BIMUnitProperties


class Unit(bonsai.core.tool.Unit):
    UNIT_TYPE = Literal["LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT", "MASSUNIT", "TIMEUNIT"]

    @staticmethod
    def format_distance(meters: float, use_imperial: bool = None, **kwargs) -> str:
        """
        Format a distance value in meters to a string in the project's unit system.

        :param meters: The distance value in meters
        :param use_imperial: If True, format as imperial; if False, format as metric; if None, auto-detect from scene
        :param kwargs: Additional arguments to pass to the underlying format_distance function
                    (hide_units, precision, decimal_places, etc.)
        :return: Formatted string with units
        """
        # Import the comprehensive format_distance from the helper module
        from bonsai.bim.module.drawing import helper

        # The comprehensive function expects value in scene units, not meters
        # So we pass meters directly since it handles unit conversion internally
        return helper.format_distance(
            meters,
            hide_units=kwargs.get("hide_units", False),
            precision=kwargs.get("precision"),
            decimal_places=kwargs.get("decimal_places"),
            **kwargs,
        )

    @classmethod
    def parse_distance_string(cls, input_string: str, use_project_unit: bool = True) -> tuple[bool, float]:
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

        grammar_imperial = r"""
        start: (FORMULA dim expr) | dim
        dim: imperial

        FORMULA: "="

        imperial: feet_inches | feet_only | inches_only | plain_number
        feet_only: NUMBER (FEET_SYM | FEET_TEXT)
        inches_only: inch_value (INCH_SYM | INCH_TEXT)
        feet_inches: NUMBER (FEET_SYM | FEET_TEXT) DASH? inch_value (INCH_SYM | INCH_TEXT)?
        plain_number: NUMBER

        inch_value: NUMBER fraction | fraction | NUMBER

        fraction: NUMBER "/" NUMBER

        expr: (ADD | SUB) dim | (MUL | DIV) NUMBER

        NUMBER: /-?(?:\d+\.?\d*|\.\d+)/
        FEET_SYM: "'"
        FEET_TEXT: "ft"
        INCH_SYM: "\""
        INCH_TEXT: "in"
        DASH: "-"
        ADD: "+"
        SUB: "-"
        MUL: "*"
        DIV: "/"

        %ignore " "
        """

        grammar_metric = r"""
        start: FORMULA? dim expr?
        dim: metric

        FORMULA: "="

        metric: NUMBER (MM | CM | DM | M | DEG)?

        expr: (ADD | SUB | MUL | DIV) dim

        NUMBER: /-?(?:\d+\.?\d*|\.\d+)/
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

            def inch_value(self, args):
                # Can be: NUMBER fraction, fraction, or NUMBER
                if len(args) == 2:
                    # NUMBER fraction (e.g., "9 1/64")
                    return args[0] + args[1]
                else:
                    # Just fraction or just NUMBER
                    return args[0]

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
                # args[0] is the inch_value, args[1] is the unit token
                inches = args[0]
                # Convert inches to meters (1 inch = 0.0254 meters)
                return inches * 0.0254

            def feet_inches(self, args):
                # Extract feet and inches values
                feet = args[0]
                # Find the inch_value (it's a number, not a token)
                inches = None
                for arg in args[1:]:
                    if isinstance(arg, (int, float)):
                        inches = arg
                        break
                if inches is None:
                    inches = 0

                # If feet is negative (including -0), inches should also be negative (subtractive)
                if math.copysign(1, feet) < 0:
                    inches = -inches

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
            except Exception as e:
                # If primary fails, try fallback grammar (allows metric in imperial projects and vice versa)
                try:
                    parse_tree = fallback_parser.parse(input_string)
                except Exception as e2:
                    pass

            if parse_tree is None:
                return False, 0.0

            # Transform the parse tree to get the numeric result
            transformer = InputTransform()
            result = transformer.transform(parse_tree)
            result = round(result, 6)

            return True, result

        except Exception as e:
            return False, 0.0

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
    def get_scene_unit_name(cls, unit_type: UNIT_TYPE) -> str | None:
        if unit_type == "LENGTHUNIT":
            name = bpy.context.scene.unit_settings.length_unit
            if name == "ADAPTIVE":
                if bpy.context.scene.unit_settings.system == "IMPERIAL":
                    name = "foot"
                else:
                    name = "METRE"
            name = (
                {"MILES": "mile", "FEET": "foot", "INCHES": "inch", "THOU": "thou", "ADAPTIVE": "METERS"}
                .get(name, name)
                .replace("METERS", "METRE")
            )
            if len(name) > len("METRE") and name.endswith("METRE"):
                return f"{name[:-5]}/METRE"
            return name
        bim_props = tool.Blender.get_bim_props()
        if (name := getattr(bim_props, f"{unit_type[:-4].lower()}_unit")) != "NONE":
            return name

    @classmethod
    def is_si_unit(cls, name: str) -> bool:
        return name[0].isupper()

    @classmethod
    def get_scene_unit_si_prefix(cls, name: str) -> str | None:
        return name.split("/")[0] if "/" in name else None

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
