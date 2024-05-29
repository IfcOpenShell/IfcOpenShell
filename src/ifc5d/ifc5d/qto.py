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
from typing import Optional


def get_rules(name: str):
    cwd = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(cwd, name + ".json"), "r") as f:
        return json.load(f)


def quantify(ifc_file: ifcopenshell.file, elements: set[ifcopenshell.entity_instance], rules: dict):
    results = {}
    for calculator, queries in rules["calculators"].items():
        calculator = calculators[calculator]
        for query, qtos in queries.items():
            filtered_elements = ifcopenshell.util.selector.filter_elements(ifc_file, query, elements)
            if filtered_elements:
                calculator.calculate(ifc_file, filtered_elements, qtos, results)
    return results


def edit_qtos(ifc_file, results):
    for element, qtos in results.items():
        for name, quantities in qtos.items():
            qto = ifcopenshell.util.element.get_pset(element, name, should_inherit=False)
            if qto:
                qto = ifc_file.by_id(qto["id"])
            else:
                qto = ifcopenshell.api.pset.add_qto(ifc_file, element, name)
            ifcopenshell.api.pset.edit_qto(ifc_file, qto=qto, properties=quantities)


class IOSTriangulation:
    @staticmethod
    def calculate(
        ifc_file: ifcopenshell.file,
        elements: set[ifcopenshell.entity_instance],
        qtos: dict,
        results: dict,
    ):
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
            tasks.append((IOSTriangulation.create_iterator(ifc_file, gross_settings, elements), gross_qtos))

        if net_qtos:
            tasks.append((IOSTriangulation.create_iterator(ifc_file, net_settings, elements), net_qtos))

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
    def create_iterator(ifc_file, settings, elements):
        return ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count(), include=elements)


class Blender:
    @staticmethod
    def calculate(ifc_file: ifcopenshell.file, elements: set[ifcopenshell.entity_instance], qtos: dict, results: dict):
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


calculators = {"Blender": Blender, "IOSTriangulation": IOSTriangulation}
