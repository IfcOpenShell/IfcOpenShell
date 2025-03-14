# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import bonsai.tool as tool
import ifc5d.qto
from bonsai.bim.prop import StrProperty, Attribute
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
from typing import TYPE_CHECKING, Union


CALCULATOR_FUNCTION_ENUM_ITEMS: list[Union[tuple[str, str, str], None]] = []


def get_qto_rule(self: "BIMQtoProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []
    for rule_id, rule in tool.Qto.get_qto_rules().items():
        results.append((rule_id, rule["name"], rule["description"]))
    return results


def get_calculator(self: "BIMQtoProperties", context: bpy.types.Context) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []
    for name, calculator in ifc5d.qto.calculators.items():
        results.append((name, name, calculator.__doc__ or ""))
    # Make IfcOpenShell appear first.
    results.sort(key=lambda x: x[0] == "IfcOpenShell", reverse=True)
    return results


def get_calculator_function(
    self: "BIMQtoProperties", context: bpy.types.Context
) -> list[Union[tuple[str, str, str], None]]:
    global CALCULATOR_FUNCTION_ENUM_ITEMS
    calculator = ifc5d.qto.calculators[self.calculator]
    CALCULATOR_FUNCTION_ENUM_ITEMS = []
    previous_measure = None
    for function_id, function in calculator.functions.items():
        measure = function.measure.split("Measure")[0][3:]
        if previous_measure is not None and measure != previous_measure:
            CALCULATOR_FUNCTION_ENUM_ITEMS.append(None)
        description = function.description
        description += f"\n\nInternal function id: '{function_id}'."
        CALCULATOR_FUNCTION_ENUM_ITEMS.append((function_id, f"{measure}: {function.name}", function.description))
        previous_measure = measure
    return CALCULATOR_FUNCTION_ENUM_ITEMS


class BIMQtoProperties(PropertyGroup):
    qto_rule: EnumProperty(items=get_qto_rule, name="Qto Rule")
    calculator: EnumProperty(items=get_calculator, name="Calculator")
    calculator_function: EnumProperty(
        items=get_calculator_function,
        name="Calculator Function",
        description=(
            "Gross functions calculate the measure for the original element's geometry, without openings.\n"
            "Net functions include the openings substractions.\n\nCurrently selected function"
        ),
    )
    qto_result: StringProperty(default="", name="Qto Result")
    qto_name: StringProperty(name="Qto Name", default="My_Qto")
    prop_name: StringProperty(name="Prop Name", default="MyDimension")
    fallback: BoolProperty(
        name="Fallback To Other Calculators",
        description=(
            "If currently selected calculator does not support quantification "
            "of some class/property, to try other available calculators."
        ),
        default=False,
    )

    if TYPE_CHECKING:
        qto_rule: str
        calculator: str
        calculator_function: str
        qto_result: str
        qto_name: str
        prop_name: str
        fallback: bool
