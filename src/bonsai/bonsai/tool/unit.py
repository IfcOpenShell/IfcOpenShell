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
from functools import cache
from typing import TYPE_CHECKING, Any, Literal, Union

import bpy
import ifcopenshell
import ifcopenshell.api.unit
import ifcopenshell.util.attribute
import ifcopenshell.util.unit
from lark import Lark, Transformer

import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.unit.prop import BIMUnitProperties


@cache
def _get_distance_parser(grammar: str) -> Lark:
    """Return a cached Lark parser for ``grammar``, compiling it on first use."""
    return Lark(grammar)


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
                primary_parser = _get_distance_parser(grammar_imperial)
                fallback_parser = _get_distance_parser(grammar_metric)
            else:
                primary_parser = _get_distance_parser(grammar_metric)
                fallback_parser = _get_distance_parser(grammar_imperial)

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
            name = {"MILES": "mile", "FEET": "foot", "INCHES": "inch", "THOU": "thou", "ADAPTIVE": "METERS"}.get(
                name, name
            ).replace("METERS", "METRE")
            if len(name) > len("METRE") and name.endswith("METRE"):
                return f"{name[:-5]}/METRE"
            return name
        bim_props = tool.Blender.get_bim_props()
        if (name := getattr(bim_props, f"{unit_type[:-4].lower()}_unit")) != "NONE":
            return name

    # How each IfcDerivedUnitEnum type is composed from named unit types, for building it out
    # of the project's own units (see add_derived_unit). Pairs rather than a dict because some
    # repeat a unit type (kN.m/m), mirroring add_structural_units. Section properties are
    # composed from length alone so they follow the project length unit (mm4, not m4).
    # Dimensionless/logarithmic types (pH, sound levels, compound plane angle) are omitted.
    DERIVED_UNIT_COMPOSITIONS: dict[str, tuple[tuple[str, int], ...]] = {
        "ACCELERATIONUNIT": (("LENGTHUNIT", 1), ("TIMEUNIT", -2)),
        "ANGULARVELOCITYUNIT": (("PLANEANGLEUNIT", 1), ("TIMEUNIT", -1)),
        "AREADENSITYUNIT": (("MASSUNIT", 1), ("AREAUNIT", -1)),
        "CURVATUREUNIT": (("PLANEANGLEUNIT", 1), ("LENGTHUNIT", -1)),
        "DYNAMICVISCOSITYUNIT": (("PRESSUREUNIT", 1), ("TIMEUNIT", 1)),
        "HEATFLUXDENSITYUNIT": (("POWERUNIT", 1), ("AREAUNIT", -1)),
        "HEATINGVALUEUNIT": (("ENERGYUNIT", 1), ("MASSUNIT", -1)),
        "INTEGERCOUNTRATEUNIT": (("TIMEUNIT", -1),),
        "IONCONCENTRATIONUNIT": (("MASSUNIT", 1), ("VOLUMEUNIT", -1)),
        "ISOTHERMALMOISTURECAPACITYUNIT": (("VOLUMEUNIT", 1), ("MASSUNIT", -1)),
        "KINEMATICVISCOSITYUNIT": (("AREAUNIT", 1), ("TIMEUNIT", -1)),
        "LINEARFORCEUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -1)),
        "LINEARMOMENTUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", 1), ("LENGTHUNIT", -1)),
        "LINEARSTIFFNESSUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -1)),
        "LINEARVELOCITYUNIT": (("LENGTHUNIT", 1), ("TIMEUNIT", -1)),
        "LUMINOUSINTENSITYDISTRIBUTIONUNIT": (("LUMINOUSINTENSITYUNIT", 1), ("LUMINOUSFLUXUNIT", -1)),
        "MASSDENSITYUNIT": (("MASSUNIT", 1), ("VOLUMEUNIT", -1)),
        "MASSFLOWRATEUNIT": (("MASSUNIT", 1), ("TIMEUNIT", -1)),
        "MASSPERLENGTHUNIT": (("MASSUNIT", 1), ("LENGTHUNIT", -1)),
        "MODULUSOFELASTICITYUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -2)),
        "MODULUSOFLINEARSUBGRADEREACTIONUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -2)),
        "MODULUSOFROTATIONALSUBGRADEREACTIONUNIT": (
            ("FORCEUNIT", 1),
            ("LENGTHUNIT", 1),
            ("LENGTHUNIT", -1),
            ("PLANEANGLEUNIT", -1),
        ),
        "MODULUSOFSUBGRADEREACTIONUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -3)),
        "MOISTUREDIFFUSIVITYUNIT": (("VOLUMEUNIT", 1), ("TIMEUNIT", -1)),
        "MOLECULARWEIGHTUNIT": (("MASSUNIT", 1), ("AMOUNTOFSUBSTANCEUNIT", -1)),
        "MOMENTOFINERTIAUNIT": (("LENGTHUNIT", 4),),
        "PLANARFORCEUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -2)),
        "ROTATIONALFREQUENCYUNIT": (("TIMEUNIT", -1),),
        "ROTATIONALMASSUNIT": (("MASSUNIT", 1), ("LENGTHUNIT", 2)),
        "ROTATIONALSTIFFNESSUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", 1), ("PLANEANGLEUNIT", -1)),
        "SECTIONAREAINTEGRALUNIT": (("LENGTHUNIT", 5),),
        "SECTIONMODULUSUNIT": (("LENGTHUNIT", 3),),
        "SHEARMODULUSUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -2)),
        # IfcDerivedUnit WR1 forbids a lone element with exponent 1, so W and Pa are spelled out.
        "SOUNDPOWERUNIT": (("ENERGYUNIT", 1), ("TIMEUNIT", -1)),
        "SOUNDPRESSUREUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", -2)),
        "SPECIFICHEATCAPACITYUNIT": (("ENERGYUNIT", 1), ("MASSUNIT", -1), ("THERMODYNAMICTEMPERATUREUNIT", -1)),
        "TEMPERATUREGRADIENTUNIT": (("THERMODYNAMICTEMPERATUREUNIT", 1), ("LENGTHUNIT", -1)),
        "TEMPERATURERATEOFCHANGEUNIT": (("THERMODYNAMICTEMPERATUREUNIT", 1), ("TIMEUNIT", -1)),
        "THERMALADMITTANCEUNIT": (("POWERUNIT", 1), ("AREAUNIT", -1), ("THERMODYNAMICTEMPERATUREUNIT", -1)),
        "THERMALCONDUCTANCEUNIT": (("POWERUNIT", 1), ("LENGTHUNIT", -1), ("THERMODYNAMICTEMPERATUREUNIT", -1)),
        "THERMALEXPANSIONCOEFFICIENTUNIT": (("THERMODYNAMICTEMPERATUREUNIT", -1),),
        "THERMALRESISTANCEUNIT": (("AREAUNIT", 1), ("THERMODYNAMICTEMPERATUREUNIT", 1), ("POWERUNIT", -1)),
        "THERMALTRANSMITTANCEUNIT": (("POWERUNIT", 1), ("AREAUNIT", -1), ("THERMODYNAMICTEMPERATUREUNIT", -1)),
        "TORQUEUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", 1)),
        "VAPORPERMEABILITYUNIT": (
            ("MASSUNIT", 1),
            ("TIMEUNIT", -1),
            ("LENGTHUNIT", -1),
            ("PRESSUREUNIT", -1),
        ),
        "VOLUMETRICFLOWRATEUNIT": (("VOLUMEUNIT", 1), ("TIMEUNIT", -1)),
        "WARPINGCONSTANTUNIT": (("LENGTHUNIT", 6),),
        "WARPINGMOMENTUNIT": (("FORCEUNIT", 1), ("LENGTHUNIT", 2)),
    }

    @classmethod
    def get_derived_unit_types(cls) -> list[str]:
        """IfcDerivedUnitEnum values in the current schema that `add_derived_unit` can build."""
        entity = tool.Ifc.schema().declaration_by_name("IfcDerivedUnit").as_entity()
        assert entity
        values = ifcopenshell.util.attribute.get_enum_items(entity.attribute_by_index(1))
        return sorted(v for v in values if v in cls.DERIVED_UNIT_COMPOSITIONS)

    # SI prefixes offered, beyond units already in the file, when picking a derived unit's
    # components (see get_component_unit_choices). Types not listed offer the bare SI unit.
    COMPONENT_SI_PREFIXES: dict[str, tuple[Union[str, None], ...]] = {
        "LENGTHUNIT": (None, "MILLI", "CENTI", "KILO"),
        "AREAUNIT": (None, "MILLI", "CENTI"),
        "VOLUMEUNIT": (None, "MILLI", "CENTI"),
        "MASSUNIT": ("KILO", "MEGA"),
        "FORCEUNIT": (None, "KILO", "MEGA"),
        "PRESSUREUNIT": (None, "KILO", "MEGA", "GIGA"),
        "ENERGYUNIT": (None, "KILO", "MEGA"),
        "POWERUNIT": (None, "KILO", "MEGA"),
    }

    @classmethod
    def get_unit_label(cls, unit: ifcopenshell.entity_instance) -> str:
        """Picker label for a unit, e.g. "inch (in)" or "MILLIMETRE (mm)"."""
        name = getattr(unit, "Name", None) or unit.is_a()
        if unit.is_a("IfcSIUnit") and unit.Prefix:
            name = f"{unit.Prefix}{name}"
        symbol = ifcopenshell.util.unit.get_unit_symbol(unit)
        return f"{name} ({symbol})" if symbol else name

    @classmethod
    def get_distinct_units(
        cls, units: list[ifcopenshell.entity_instance], preferred_id: int = 0
    ) -> list[ifcopenshell.entity_instance]:
        """Collapse units a user can't tell apart -- same class, type, label and scale -- to one.

        Files routinely hold such copies: every conversion-based unit (foot, inch, ...) carries
        its own METRE as its conversion factor's unit. The lowest STEP id represents each group,
        so the choice is stable across redraws, unless `preferred_id` (e.g. a property's current
        Unit) is in the group, in which case it is kept so that selection stays representable.
        The caller's order is preserved.
        """
        groups: dict[tuple, ifcopenshell.entity_instance] = {}
        for unit in sorted(units, key=lambda u: u.id()):
            try:
                scale = f"{ifcopenshell.util.unit.get_unit_scale(unit):.12g}"
            except Exception:
                scale = str(unit.id())  # Unscalable: never merge it with anything.
            key = (unit.is_a(), getattr(unit, "UnitType", None), cls.get_unit_label(unit), scale)
            if key not in groups or unit.id() == preferred_id:
                groups[key] = unit
        kept = set(groups.values())
        return [u for u in units if u in kept]

    @classmethod
    def get_derived_unit_component_types(cls, unit_type: str) -> list[str]:
        """The distinct named unit types a derived `unit_type` is built from, in order, e.g.
        ["FORCEUNIT", "LENGTHUNIT"] for MODULUSOFELASTICITYUNIT."""
        return list(dict.fromkeys(t for t, _ in cls.DERIVED_UNIT_COMPOSITIONS.get(unit_type, ())))

    @classmethod
    def get_component_unit_choices(cls, unit_type: str) -> list[tuple[str, str, str]]:
        """Choices for one component (a named `unit_type`, e.g. "FORCEUNIT") of a derived unit.

        Identifiers: "0" for the project's unit (or a new SI unit if it has none), a STEP id for
        a unit already in the file, "+SI:<prefix>" or "+CONV:<name>" for a unit not in the file
        yet, created on demand by `resolve_unit_choice` -- so e.g. kip/in2 needs no setup.
        """
        ifc_file = tool.Ifc.get()
        si_name = ifcopenshell.util.unit.si_type_names[unit_type]

        def si_symbol(prefix: Union[str, None]) -> str:
            return ifcopenshell.util.unit.prefix_symbols.get(prefix, "") + ifcopenshell.util.unit.unit_symbols.get(
                si_name, "?"
            )

        project_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, unit_type)
        if project_unit and project_unit.is_a("IfcNamedUnit"):
            symbol = ifcopenshell.util.unit.get_unit_symbol(project_unit)
            choices = [("0", f"Default ({symbol})", "The project's unit")]
        else:
            fallback = "KILO" if unit_type == "MASSUNIT" else None
            choices = [
                ("0", f"SI ({si_symbol(fallback)})", "The project has no unit of this type, so an SI unit is used")
            ]

        existing = [
            u for u in ifcopenshell.util.unit.get_candidate_units(ifc_file, unit_type) if u.is_a("IfcNamedUnit")
        ]
        for unit in cls.get_distinct_units(existing):
            choices.append((str(unit.id()), cls.get_unit_label(unit), ""))
        choices.extend(cls.get_new_unit_choices(unit_type, "created when the derived unit is added"))
        return choices

    @classmethod
    def get_new_unit_choices(cls, unit_type: str, when: str) -> list[tuple[str, str, str]]:
        """Choices for catalog units of a named `unit_type` that aren't in the file yet: SI with
        common prefixes and the conversion-based (imperial/US) units, e.g. "+ psf (psf)".
        Identifiers are "+SI:<prefix>" / "+CONV:<name>"; see `resolve_unit_choice`.

        :param when: Completes the description "Not in the file yet: ...".
        """
        if unit_type not in ifcopenshell.util.unit.si_type_names or unit_type == "USERDEFINED":
            return []  # Not a named unit type (e.g. a derived one): there is no catalog.
        ifc_file = tool.Ifc.get()
        si_name = ifcopenshell.util.unit.si_type_names[unit_type]

        def si_symbol(prefix: Union[str, None]) -> str:
            return ifcopenshell.util.unit.prefix_symbols.get(prefix, "") + ifcopenshell.util.unit.unit_symbols.get(
                si_name, "?"
            )

        existing = [u for u in ifc_file.by_type("IfcNamedUnit") if getattr(u, "UnitType", None) == unit_type]
        choices: list[tuple[str, str, str]] = []
        new = f"Not in the file yet: {when}"
        present_si = {(u.Prefix, u.Name) for u in existing if u.is_a("IfcSIUnit")}
        for prefix in cls.COMPONENT_SI_PREFIXES.get(unit_type, (None,)):
            if (prefix, si_name) not in present_si:
                choices.append((f"+SI:{prefix or ''}", f"+ {prefix or ''}{si_name} ({si_symbol(prefix)})", new))
        present_names = {u.Name for u in existing if u.is_a("IfcConversionBasedUnit")}
        for name, conversion_type in ifcopenshell.util.unit.imperial_types.items():
            if (
                conversion_type == unit_type
                and name not in present_names
                and name in ifcopenshell.util.unit.si_conversions
                and name not in ifcopenshell.util.unit.si_offsets  # e.g. fahrenheit: no use in a ratio.
            ):
                symbol = ifcopenshell.util.unit.unit_symbols.get(name, name)
                choices.append((f"+CONV:{name}", f"+ {name} ({symbol})", new))
        return choices

    @classmethod
    def resolve_unit_choice(cls, unit_type: str, choice: str) -> Union[ifcopenshell.entity_instance, None]:
        """The unit a `get_component_unit_choices` / `get_new_unit_choices` identifier names,
        creating it if it's new. None for "0" (or empty): use the project's unit."""
        ifc_file = tool.Ifc.get()
        if choice.startswith("+SI:"):
            prefix = choice.removeprefix("+SI:") or None
            return ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type=unit_type, prefix=prefix)
        if choice.startswith("+CONV:"):
            return ifcopenshell.api.unit.add_conversion_based_unit(ifc_file, name=choice.removeprefix("+CONV:"))
        if choice and choice != "0":
            return ifc_file.by_id(int(choice))
        return None

    @classmethod
    def add_derived_unit(
        cls, unit_type: str, component_units: Union[dict[str, ifcopenshell.entity_instance], None] = None
    ) -> ifcopenshell.entity_instance:
        """Create an IfcDerivedUnit of `unit_type` composed from the project's assigned units,
        e.g. MOMENTOFINERTIAUNIT becomes mm4 in a millimetre project and LINEARFORCEUNIT kN/m
        with kN and m assigned. A component type the project has no unit for falls back to a
        new, unassigned SI unit (kilogram for mass) so the result is always well defined.

        :param component_units: Units to use instead of the project's, by named unit type,
            e.g. {"FORCEUNIT": kip, "LENGTHUNIT": inch} for a kip/in2 modulus in a foot project.
        """
        ifc_file = tool.Ifc.get()
        components: dict[str, ifcopenshell.entity_instance] = dict(component_units or {})
        elements: list[ifcopenshell.entity_instance] = []
        for named_type, exponent in cls.DERIVED_UNIT_COMPOSITIONS[unit_type]:
            if named_type not in components:
                component = ifcopenshell.util.unit.get_project_unit(ifc_file, named_type)
                if component is None or not component.is_a("IfcNamedUnit"):
                    prefix = "KILO" if named_type == "MASSUNIT" else None
                    component = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type=named_type, prefix=prefix)
                components[named_type] = component
            elements.append(
                ifc_file.create_entity("IfcDerivedUnitElement", Unit=components[named_type], Exponent=exponent)
            )
        return ifc_file.create_entity("IfcDerivedUnit", Elements=elements, UnitType=unit_type)

    @classmethod
    def add_structural_units(cls) -> list[ifcopenshell.entity_instance]:
        """Units for the forces, stiffnesses and material values of structural analysis.

        Without them a millimetre project reads a load of 5 meant as kN/m2 as 5 N/mm2.
        These are the units engineers write, whatever the length unit: kN, kN/m, kN/m2,
        kN.m, N/mm2 and kg/m3 in a metric scene; kip, kip/ft, psf, kip.ft, ksi and pcf
        in an imperial one. Pressure is left alone, as building services use it too.
        """
        ifc_file = tool.Ifc.get()

        def derived(
            unit_type: str, *elements: tuple[ifcopenshell.entity_instance, int]
        ) -> ifcopenshell.entity_instance:
            # Built element by element: kN.m/m repeats the metre, which a dict cannot hold.
            return ifc_file.create_entity(
                "IfcDerivedUnit",
                Elements=[ifc_file.create_entity("IfcDerivedUnitElement", Unit=u, Exponent=e) for u, e in elements],
                UnitType=unit_type,
            )

        radian = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="PLANEANGLEUNIT")
        if bpy.context.scene.unit_settings.system == "IMPERIAL":
            force = ifcopenshell.api.unit.add_conversion_based_unit(ifc_file, name="kip")
            lbf = ifcopenshell.api.unit.add_conversion_based_unit(ifc_file, name="lbf")
            length = ifcopenshell.api.unit.add_conversion_based_unit(ifc_file, name="foot")
            inch = ifcopenshell.api.unit.add_conversion_based_unit(ifc_file, name="inch")
            pound = ifcopenshell.api.unit.add_conversion_based_unit(ifc_file, name="pound")
            area_force = (lbf, 1), (length, -2)  # psf
            stiffness = (force, 1), (inch, -1)
            modulus = (force, 1), (inch, -2)  # ksi
            density = (pound, 1), (length, -3)  # pcf
        else:
            force = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="FORCEUNIT", prefix="KILO")
            length = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT")
            newton = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="FORCEUNIT")
            millimetre = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="LENGTHUNIT", prefix="MILLI")
            kilogram = ifcopenshell.api.unit.add_si_unit(ifc_file, unit_type="MASSUNIT", prefix="KILO")
            area_force = (force, 1), (length, -2)
            stiffness = (force, 1), (length, -1)
            modulus = (newton, 1), (millimetre, -2)
            density = (kilogram, 1), (length, -3)
        return [
            force,
            derived("TORQUEUNIT", (force, 1), (length, 1)),
            derived("LINEARFORCEUNIT", (force, 1), (length, -1)),
            derived("LINEARMOMENTUNIT", (force, 1), (length, 1), (length, -1)),
            derived("PLANARFORCEUNIT", *area_force),
            derived("LINEARSTIFFNESSUNIT", *stiffness),
            derived("ROTATIONALSTIFFNESSUNIT", (force, 1), (length, 1), (radian, -1)),
            derived("MODULUSOFLINEARSUBGRADEREACTIONUNIT", (force, 1), (length, -2)),
            derived("MODULUSOFROTATIONALSUBGRADEREACTIONUNIT", (force, 1), (length, 1), (length, -1), (radian, -1)),
            derived("MODULUSOFSUBGRADEREACTIONUNIT", (force, 1), (length, -3)),
            derived("MODULUSOFELASTICITYUNIT", *modulus),
            derived("SHEARMODULUSUNIT", *modulus),
            derived("MASSDENSITYUNIT", *density),
        ]

    @classmethod
    def is_si_unit(cls, name: str) -> bool:
        return name[0].isupper()

    @classmethod
    def get_scene_unit_si_prefix(cls, name: str) -> str | None:
        return name.split("/")[0] if "/" in name else None

    @classmethod
    def get_unit_si_scale(cls, unit: ifcopenshell.entity_instance) -> float | None:
        """Get a named unit's magnitude in SI units, or None if it cannot be determined."""
        scale = 1.0
        while unit.is_a("IfcConversionBasedUnit"):
            value = unit.ConversionFactor.ValueComponent.wrappedValue
            if not isinstance(value, (int, float)):
                return None
            scale *= value
            unit = unit.ConversionFactor.UnitComponent
        if unit.is_a("IfcSIUnit"):
            return scale * ifcopenshell.util.unit.get_prefix_multiplier(unit.Prefix)
        return None

    @classmethod
    def get_project_rescale_factor(cls, new_si_scale: float | None) -> float | None:
        """Get the factor by which stored lengths would physically rescale, or None if they wouldn't.

        Compares the prospective SI scale of the project length unit against the
        current one. Returns None when the scale is unknown, unchanged, or the
        project has no length-bearing data worth warning about yet.
        """
        if new_si_scale is None or not new_si_scale:
            return None
        ifc_file = tool.Ifc.get()
        if not ifc_file.by_type("IfcShapeRepresentation") and not ifc_file.by_type("IfcMaterialLayer"):
            return None
        old_si_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        if not old_si_scale or math.isclose(new_si_scale, old_si_scale, rel_tol=1e-9):
            return None
        return new_si_scale / old_si_scale

    @classmethod
    def is_project_unit(cls, unit: ifcopenshell.entity_instance) -> bool:
        assignment = ifcopenshell.util.unit.get_unit_assignment(tool.Ifc.get())
        return bool(assignment) and unit in (assignment.Units or ())

    @classmethod
    def get_assign_unit_rescale_factor(cls, unit: ifcopenshell.entity_instance) -> float | None:
        """Get the rescale factor assigning this unit as project default would cause, or None."""
        if getattr(unit, "UnitType", None) != "LENGTHUNIT":
            return None
        return cls.get_project_rescale_factor(cls.get_unit_si_scale(unit))

    @classmethod
    def get_edit_unit_rescale_factor(cls, unit: ifcopenshell.entity_instance) -> float | None:
        """Get the rescale factor applying the currently edited unit attributes would cause, or None."""
        if not unit.is_a("IfcSIUnit") or unit.UnitType != "LENGTHUNIT" or not cls.is_project_unit(unit):
            return None
        attributes = cls.export_unit_attributes()
        if attributes.get("UnitType") != "LENGTHUNIT" or attributes.get("Name") != "METRE":
            return None
        return cls.get_project_rescale_factor(ifcopenshell.util.unit.get_prefix_multiplier(attributes.get("Prefix")))

    @classmethod
    def get_scene_units_rescale_factor(cls) -> float | None:
        """Get the rescale factor assigning the Blender scene length unit would cause, or None."""
        if not (name := cls.get_scene_unit_name("LENGTHUNIT")):
            return None
        if cls.is_si_unit(name):
            new_scale = ifcopenshell.util.unit.get_prefix_multiplier(cls.get_scene_unit_si_prefix(name))
        else:
            new_scale = ifcopenshell.util.unit.si_conversions.get(name)
        return cls.get_project_rescale_factor(new_scale)

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
            elif unit.is_a("IfcDerivedUnit"):
                # Derived units have no Name; their symbol (e.g. "kN/m") identifies them.
                name = ifcopenshell.util.unit.get_unit_symbol(unit) if unit.Elements else ""
            else:
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
    def get_assigned_unit_of_type(cls, unit: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        """Get the project's assigned unit of the same unit type as the given unit, if any."""
        return ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), unit.UnitType)

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
