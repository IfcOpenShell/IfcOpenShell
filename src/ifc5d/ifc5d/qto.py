# Ifc5D - IFC costing utility
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Ifc5D.
#
# Ifc5D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc5D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc5D.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.util.selector
import multiprocessing
from collections import namedtuple
from typing import Iterable


Function = namedtuple("Function", ["id", "name", "description"])
rules = {}

cwd = os.path.dirname(os.path.realpath(__file__))
for name in ("IFC4QtoBaseQuantities", "IFC4QtoBaseQuantitiesBlender"):
    with open(os.path.join(cwd, name + ".json"), "r") as f:
        rules[name] = json.load(f)


def quantify(ifc_file: ifcopenshell.file, elements: set[ifcopenshell.entity_instance], rules: dict) -> dict:
    results = {}
    for calculator, queries in rules["calculators"].items():
        calculator = calculators[calculator]
        for query, qtos in queries.items():
            filtered_elements = ifcopenshell.util.selector.filter_elements(ifc_file, query, elements)
            if filtered_elements:
                calculator.calculate(ifc_file, filtered_elements, qtos, results)
    return results


def edit_qtos(ifc_file, results) -> None:
    for element, qtos in results.items():
        for name, quantities in qtos.items():
            qto = ifcopenshell.util.element.get_pset(element, name, should_inherit=False)
            if qto:
                qto = ifc_file.by_id(qto["id"])
            else:
                qto = ifcopenshell.api.pset.add_qto(ifc_file, element, name)
            ifcopenshell.api.pset.edit_qto(ifc_file, qto=qto, properties=quantities)


class IfcOpenShell:
    """Calculates Model body context geometry using the default IfcOpenShell
    iterator on triangulation elements."""

    @staticmethod
    def calculate(
        ifc_file: ifcopenshell.file,
        elements: set[ifcopenshell.entity_instance],
        qtos: dict,
        results: dict,
    ) -> None:
        import ifcopenshell
        import ifcopenshell.geom
        import ifcopenshell.util.shape

        formula_functions = {}

        gross_settings = ifcopenshell.geom.settings()
        gross_settings.set(gross_settings.DISABLE_OPENING_SUBTRACTIONS, True)
        net_settings = ifcopenshell.geom.settings()

        gross_qtos = {}
        net_qtos = {}

        for name, quantities in qtos.items():
            for quantity, formula in quantities.items():
                if not formula:
                    continue
                if formula.startswith("gross_"):
                    formula = formula[6:]
                    gross_qtos.setdefault(name, {})[quantity] = formula
                    formula_functions[formula] = getattr(ifcopenshell.util.shape, formula)
                elif formula.startswith("net_"):
                    formula = formula[4:]
                    net_qtos.setdefault(name, {})[quantity] = formula
                    formula_functions[formula] = getattr(ifcopenshell.util.shape, formula)

        tasks = []

        if gross_qtos:
            tasks.append((IfcOpenShell.create_iterator(ifc_file, gross_settings, list(elements)), gross_qtos))

        if net_qtos:
            tasks.append((IfcOpenShell.create_iterator(ifc_file, net_settings, list(elements)), net_qtos))

        for iterator, qtos in tasks:
            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    element = ifc_file.by_id(shape.id)
                    results.setdefault(element, {})
                    for name, quantities in qtos.items():
                        results[element].setdefault(name, {})
                        for quantity, formula in quantities.items():
                            results[element][name][quantity] = formula_functions[formula](shape.geometry)
                    if not iterator.next():
                        break

    @staticmethod
    def create_iterator(
        ifc_file: ifcopenshell.file, settings: ifcopenshell.geom.settings, elements: list[ifcopenshell.entity_instance]
    ) -> ifcopenshell.geom.iterator:
        return ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count(), include=elements)

    @staticmethod
    def get_functions() -> list[Function]:
        return [
            Function("get_area", "Area", "The total surface area of the element"),
            Function("get_bottom_elevation", "Bottom Elevation", "The local minimum Z ordinate"),
            Function(
                "get_footprint_area",
                "Footprint Area",
                "The area if the object's faces were projected along the Z-axis and seen top down",
            ),
            Function(
                "get_footprint_perimeter",
                "Footprint Perimeter",
                "The perimeter if the object's faces were projected along the Z-axis and seen top down",
            ),
            Function(
                "get_max_side_area",
                "Max Side Area",
                "The maximum side area when seen from either X, Y, or Z directions",
            ),
            Function("get_max_xyz", "Max XYZ", "The maximum X, Y, or Z local dimension"),
            Function("get_min_xyz", "Min XYZ", "The minimum X, Y, or Z local dimension"),
            Function(
                "get_outer_surface_area",
                "Outer Surface Area",
                "The total surface area except for the top or bottom, such as the ends of columns or beams",
            ),
            Function(
                "get_side_area", "Side area", "The side (non-projected) are of the shape as seen from the local Y-axis"
            ),
            Function("get_top_elevation", "Top elevation", "The local maximum Z ordinate"),
            Function("get_volume", "Volume", "Calculates the volume of a manifold shape"),
            Function("get_x", "X", "Calculates the length along the local X axis"),
            Function("get_y", "Y", "Calculates the length along the local Y axis"),
            Function("get_z", "Z", "Calculates the length along the local Z axis"),
        ]


class Blender:
    """Calculates geometry based on currently loaded Blender objects."""

    @staticmethod
    def calculate(
        ifc_file: ifcopenshell.file, elements: set[ifcopenshell.entity_instance], qtos: dict, results: dict
    ) -> None:
        import blenderbim.tool as tool
        import blenderbim.bim.module.qto.calculator as calculator

        formula_functions = {}

        for element in elements:
            obj = tool.Ifc.get_object(element)
            if not obj:
                continue
            results.setdefault(element, {})
            for name, quantities in qtos.items():
                results[element].setdefault(name, {})
                for quantity, formula in quantities.items():
                    if not (formula_function := formula_functions.get(formula)):
                        formula_function = formula_functions[formula] = getattr(calculator, formula)
                    results[element][name][quantity] = formula_function(obj)

    @staticmethod
    def get_functions() -> list[Function]:
        return [
            Function("get_covering_gross_area", "Covering Gross Area", ""),
            Function("get_covering_net_area", "Covering Net Area", ""),
            Function("get_covering_width", "Covering Width", ""),
            Function("get_cross_section_area", "Cross Section Area", ""),
            Function("get_finish_ceiling_height", "Finish Ceiling Height", ""),
            Function("get_finish_floor_height", "Finish Floor Height", ""),
            Function("get_gross_ceiling_area", "Gross Ceiling Area", ""),
            Function("get_gross_footprint_area", "Gross Footprint Area", ""),
            Function("get_gross_perimeter", "Gross Perimeter", ""),
            Function("get_gross_side_area", "Gross Side Area", ""),
            Function("get_gross_stair_area", "Gross Stair Area", ""),
            Function("get_gross_surface_area", "Gross Surface Area", ""),
            Function("get_gross_top_area", "Gross Top Area", ""),
            Function("get_gross_volume", "Gross Volume", ""),
            Function("get_gross_weight", "Gross Weight", ""),
            Function("get_height", "Height", ""),
            Function("get_length", "Length", ""),
            Function("get_net_ceiling_area", "Net Ceiling Area", ""),
            Function("get_net_floor_area", "Net Floor Area", ""),
            Function("get_net_footprint_area", "Net Footprint Area", ""),
            Function("get_net_side_area", "Net Side Area", ""),
            Function("get_net_stair_area", "Net Stair Area", ""),
            Function("get_net_surface_area", "Net Surface Area", ""),
            Function("get_net_top_area", "Net Top Area", ""),
            Function("get_net_volume", "Net Volume", ""),
            Function("get_net_weight", "Net Weight", ""),
            Function("get_opening_depth", "Opening Depth", ""),
            Function("get_opening_height", "Opening Height", ""),
            Function("get_opening_mapping_area", "Opening Mapping Area", ""),
            Function("get_outer_surface_area", "Outer Surface Area", ""),
            Function("get_rectangular_perimeter", "Rectangular Perimeter", ""),
            Function("get_space_net_volume", "Space Net Volume", ""),
            Function("get_stair_length", "Stair Length", ""),
            Function("get_width", "Width", ""),
        ]


calculators = {"Blender": Blender, "IfcOpenShell": IfcOpenShell}
