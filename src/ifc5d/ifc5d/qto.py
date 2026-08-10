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

import functools
import itertools
import json
import multiprocessing
import os
import types
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Literal, NamedTuple, Optional, Union, get_args

import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.selector
import ifcopenshell.util.shape
import ifcopenshell.util.unit


class Function(NamedTuple):
    measure: str
    name: str
    description: str


RULE_SET = Literal[
    "IFC4QtoBaseQuantities",
    "IFC4QtoBaseQuantitiesBlender",
    "IFC4X3QtoBaseQuantities",
    "IFC4X3QtoBaseQuantitiesBlender",
]
rules: dict[RULE_SET, dict[str, Any]] = {}
ResultsDict = dict[ifcopenshell.entity_instance, dict[str, dict[str, float]]]
QtosFormulas = dict[str, dict[str, str]]

cwd = os.path.dirname(os.path.realpath(__file__))
for name in get_args(RULE_SET):
    with open(os.path.join(cwd, name + ".json"), "r") as f:
        rules[name] = json.load(f)


@functools.cache
def lower_case_entity_names(schema_iden: str):
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_iden)
    return set(n.name().lower() for n in schema.entities())


@functools.cache
def entity_supertypes(schema_iden: str, entity_name: str):
    def visit(decl):
        yield decl.name().lower()
        if ty := decl.supertype():
            yield from visit(ty)

    decl = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_iden).declaration_by_name(entity_name)
    return list(visit(decl))


def quantify(ifc_file: ifcopenshell.file, elements: set[ifcopenshell.entity_instance], rules: dict) -> ResultsDict:
    """Quantify elements from a rules using preset quantification rules

    Rules placed as a JSON configuration file in the ``ifc5d`` folder will be
    autodetected and loaded with the module for convenience.

    :param rules: Set of rules from `ifc5d.qto.rules`.
    """
    results: ResultsDict = {}
    elements_by_classes: defaultdict[str, set[ifcopenshell.entity_instance]] = defaultdict(set)
    for element in elements:
        elements_by_classes[element.is_a()].add(element)

    for calculator, queries in rules["calculators"].items():
        calculator = calculators[calculator]
        # Cache schema entity names once per file
        schema_entity_names = lower_case_entity_names(ifc_file.schema_identifier)

        # Fast path: all queries are simple entity names
        if not set(m.lower() for m in queries.keys()) - schema_entity_names:
            casenorm = {k.lower(): k for k in queries.keys()}
            pred = lambda inst: inst.is_a().lower()

            for ty, group in itertools.groupby(sorted(elements, key=pred), key=pred):
                group_elements = list(group)
                # check entity type and its supertypes for matching QTO rules
                for sty in entity_supertypes(ifc_file.schema_identifier, ty):
                    if qtos := queries.get(casenorm.get(sty)):
                        calculator.calculate(ifc_file, group_elements, qtos, results)
            continue  # Skip general path to avoid duplicate calculations

        # Fallback: per-query evaluation
        for query, qtos in queries.items():
            # Simple entity name: use by_type but restrict to incoming elements
            if query.lower() in schema_entity_names:
                by_type_all = ifc_file.by_type(query)
                # ensure we don't expand beyond provided elements subset
                if isinstance(elements, set):
                    filtered_elements = [e for e in by_type_all if e in elements]
                else:
                    elements_set = set(elements)
                    filtered_elements = [e for e in by_type_all if e in elements_set]
            else:
                filtered_elements = ifcopenshell.util.selector.filter_elements(ifc_file, query, elements)

            if filtered_elements:
                calculator.calculate(ifc_file, filtered_elements, qtos, results)

    return results


def get_quantity_measures(rules: dict) -> dict[str, dict[str, str]]:
    """Statically derive each quantity's measure class from the rule set that defines it,
    reading it straight from the calculator's own Function table (the same source the
    calculator itself used to compute the value) -- not guessed from the quantity name.

    :param rules: A rule set as accepted by :func:`quantify`, e.g. from `ifc5d.qto.rules`.
    :return: `qto_name -> quantity_name -> measure class` (e.g. "IfcLengthMeasure"), matching
        the keys used by `SI2ProjectUnitConverter.project_units`.
    """
    measures: dict[str, dict[str, str]] = {}
    for calculator_name, queries in rules.get("calculators", {}).items():
        calculator = calculators[calculator_name]
        for _entity_or_query, qtos in queries.items():
            for qto_name, quantities in qtos.items():
                for quantity_name, formula in quantities.items():
                    if not formula:
                        continue
                    function = calculator.functions.get(formula)
                    if function is None:
                        continue
                    measures.setdefault(qto_name, {})[quantity_name] = function.measure
    return measures


def _reconvert(ifc_file: ifcopenshell.file, value: float, to_unit: ifcopenshell.entity_instance) -> float:
    """Re-express `value` (as computed by `SI2ProjectUnitConverter` -- the project's default
    unit for its dimension, or, if the project has none, raw SI, mirroring `convert()`'s own
    fallback below) in `to_unit`, which shares `to_unit`'s dimension (`UnitType`).
    """
    unit_type = getattr(to_unit, "UnitType", None)
    from_unit = ifcopenshell.util.unit.get_project_unit(ifc_file, unit_type) if unit_type else None
    from_scale = ifcopenshell.util.unit.get_unit_scale(from_unit) if from_unit else 1.0  # already SI
    return value * from_scale / ifcopenshell.util.unit.get_unit_scale(to_unit)


def edit_qtos(
    ifc_file: ifcopenshell.file,
    results: ResultsDict,
    target_units: Optional[dict[str, ifcopenshell.entity_instance]] = None,
    rules: Optional[dict] = None,
) -> None:
    """Apply quantification results as quantity sets.

    :param target_units: Optional map of measure class (e.g. "IfcLengthMeasure", matching
        `SI2ProjectUnitConverter.project_units`'s keys) to a unit to express *newly created*
        quantities of that measure in, instead of the project default. Ignored unless `rules`
        is also given (needed to resolve each quantity's measure class -- see
        `get_quantity_measures`). Has no effect on quantities that already exist -- those are
        always re-expressed in whatever Unit they already carry (see below), regardless of
        `target_units`.
    :param rules: The rule set used to produce `results` (the same object passed to
        `quantify()`), used only to resolve `target_units` via `get_quantity_measures()`.
    """
    quantity_measures = get_quantity_measures(rules) if (target_units and rules) else {}

    for element, qtos in results.items():
        for name, quantities in qtos.items():
            qto = ifcopenshell.util.element.get_pset(element, name, should_inherit=False)
            if qto:
                qto = ifc_file.by_id(qto["id"])
            else:
                qto = ifcopenshell.api.pset.add_qto(ifc_file, element, name)

            existing_by_name = {q.Name: q for q in (qto.Quantities or ())}
            wrapped_quantities: dict[str, Any] = {}

            for quantity_name, value in quantities.items():
                existing_unit = getattr(existing_by_name.get(quantity_name), "Unit", None)

                if existing_unit is not None:
                    # A quantity that already carries its own Unit override must be
                    # re-expressed in that unit, not overwritten with a value computed in
                    # the project default while the stale Unit label stays put.
                    wrapped_quantities[quantity_name] = {
                        "NominalValue": _reconvert(ifc_file, value, existing_unit),
                        "Unit": existing_unit,
                    }
                    continue

                measure = quantity_measures.get(name, {}).get(quantity_name)
                target_unit = target_units.get(measure) if (target_units and measure) else None
                if target_unit is not None:
                    # Brand new quantity, proactively expressed in the chosen target unit.
                    wrapped_quantities[quantity_name] = {
                        "NominalValue": _reconvert(ifc_file, value, target_unit),
                        "Unit": target_unit,
                    }
                    continue

                wrapped_quantities[quantity_name] = value  # unchanged bare-float path

            ifcopenshell.api.pset.edit_qto(ifc_file, qto=qto, properties=wrapped_quantities)


class SI2ProjectUnitConverter:
    def __init__(self, ifc_file: ifcopenshell.file):
        self.project_units = {
            "IfcAreaMeasure": ifcopenshell.util.unit.get_project_unit(ifc_file, "AREAUNIT"),
            "IfcLengthMeasure": ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT"),
            "IfcMassMeasure": ifcopenshell.util.unit.get_project_unit(ifc_file, "MASSUNIT"),
            "IfcTimeMeasure": ifcopenshell.util.unit.get_project_unit(ifc_file, "TIMEUNIT"),
            "IfcVolumeMeasure": ifcopenshell.util.unit.get_project_unit(ifc_file, "VOLUMEUNIT"),
        }
        for key, value in self.project_units.items():
            if value:
                self.project_units[key] = (getattr(value, "Prefix", "None"), value.Name)

        self.si_names = {
            "IfcAreaMeasure": "SQUARE_METRE",
            "IfcLengthMeasure": "METRE",
            "IfcMassMeasure": "GRAM",
            "IfcTimeMeasure": "SECOND",
            "IfcVolumeMeasure": "CUBIC_METRE",
        }

    def convert(self, value: float, measure: str) -> float:
        if measure_unit := self.project_units.get(measure, None):
            return ifcopenshell.util.unit.convert(value, None, self.si_names[measure], *measure_unit)
        return value


class IteratorForTypes:
    """Currently ifcopenshell.geom.iterator support only IfcProducts, so this
    class is mimicking the iterator interface but works for IfcTypeProducts."""

    element: Union[ifcopenshell.entity_instance, None] = None
    shape: Union[ifcopenshell.geom.ShapeType, None] = None

    def __init__(
        self,
        ifc_file: ifcopenshell.file,
        settings: ifcopenshell.geom.settings,
        elements: Iterable[ifcopenshell.entity_instance],
    ):
        self.settings = settings
        self.elements = list(elements)
        self.element = None
        self.file = ifc_file
        model = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        assert model
        self.context = model

    def initialize(self) -> bool:
        return bool(self.next())

    def get_element_and_geometry(self) -> tuple[ifcopenshell.entity_instance, ifcopenshell.geom.ShapeType]:
        # get() is not implemented so it won't be confused with iteartor.get().
        # The difference is important since create_shape for product types
        # doesn't ouput SpapeElementType, only ShapeTypes.
        assert self.element and self.shape
        return (self.element, self.shape)

    def next(self) -> bool:
        if not self.elements:
            return False
        while self.elements:
            element = self.elements.pop()
            if self.process_shape(element):
                return True
        return False

    def process_shape(self, element: ifcopenshell.entity_instance):
        representation = ifcopenshell.util.representation.get_representation(element, self.context)
        if not representation:
            return False
        self.shape = ifcopenshell.geom.create_shape(self.settings, representation)
        self.element = element
        return True


class QtoCalculator:
    """Abstract class for Qto calculators."""

    functions: dict[str, Function]

    @classmethod
    def calculate(
        cls,
        ifc_file: ifcopenshell.file,
        elements: set[ifcopenshell.entity_instance],
        qtos: dict[str, dict[str, Union[str, None]]],
        results: ResultsDict,
    ) -> None:
        raise NotImplementedError


class IfcOpenShell(QtoCalculator):
    """Calculates Model body context geometry using the default IfcOpenShell
    iterator on triangulation elements."""

    # Implementations are located in ifcopenshell.util.shape.
    raw_functions = {
        # IfcLengthMeasure
        "get_x": Function("IfcLengthMeasure", "X", "Calculates the length along the local X axis"),
        "get_y": Function("IfcLengthMeasure", "Y", "Calculates the length along the local Y axis"),
        "get_z": Function("IfcLengthMeasure", "Z", "Calculates the length along the local Z axis"),
        "get_max_xy": Function("IfcLengthMeasure", "Max XY", "The maximum X or Y local dimension"),
        "get_max_xyz": Function("IfcLengthMeasure", "Max XYZ", "The maximum X, Y, or Z local dimension"),
        "get_min_xyz": Function("IfcLengthMeasure", "Min XYZ", "The minimum X, Y, or Z local dimension"),
        "get_top_elevation": Function("IfcLengthMeasure", "Top elevation", "The local maximum Z ordinate"),
        "get_bottom_elevation": Function("IfcLengthMeasure", "Bottom Elevation", "The local minimum Z ordinate"),
        "get_footprint_perimeter": Function(
            "IfcLengthMeasure",
            "Footprint Perimeter",
            "The perimeter if the object's faces were projected along the Z-axis and seen top down",
        ),
        "get_segment_length": Function(
            "IfcLengthMeasure", "Segment Length", "Intelligently guesses the length of flow segments"
        ),
        "get_opening_width": Function(
            "IfcLengthMeasure", "Opening Width", "The width of an opening, guessing the opening orientation"
        ),
        "get_opening_height": Function(
            "IfcLengthMeasure", "Opening Height", "The height of an opening, guessing the opening orientation"
        ),
        "get_opening_depth": Function(
            "IfcLengthMeasure",
            "Opening Depth",
            "The depth of an opening (through the voided element), guessing the opening orientation",
        ),
        "get_footing_length": Function(
            "IfcLengthMeasure",
            "Footing Length",
            "The footing length. For beam-like footings (STRIP_FOOTING, FOOTING_BEAM) this is the "
            "extruded run along the local Z axis. For slab-like footings (PAD_FOOTING, PILE_CAP) and "
            "other predefined types it is the longer footprint side (the larger of local X or Y).",
        ),
        "get_footing_width": Function(
            "IfcLengthMeasure",
            "Footing Width",
            "The footing width. For beam-like footings (STRIP_FOOTING, FOOTING_BEAM) this is the "
            "cross section width along the local X axis. For slab-like footings (PAD_FOOTING, PILE_CAP) "
            "and other predefined types it is the shorter footprint side (the smaller of local X or Y).",
        ),
        "get_footing_height": Function(
            "IfcLengthMeasure",
            "Footing Height",
            "The footing height. For beam-like footings (STRIP_FOOTING, FOOTING_BEAM) this is the "
            "cross section height along the local Y axis. For slab-like footings (PAD_FOOTING, PILE_CAP) "
            "and other predefined types it is the thickness along the local Z axis.",
        ),
        "get_covering_width": Function(
            "IfcLengthMeasure",
            "Covering Width",
            "The covering's thickness: the side area axis for AXIS2 (e.g. wall finishes), "
            "otherwise the local Z depth (e.g. floor or ceiling finishes)",
        ),
        # IfcAreaMeasure
        "get_area": Function("IfcAreaMeasure", "Area", "The total surface area of the element"),
        "get_covering_area": Function(
            "IfcAreaMeasure",
            "Covering Area",
            "The covering's side area for AXIS2 (e.g. wall finishes), otherwise its footprint "
            "area (e.g. floor or ceiling finishes)",
        ),
        "get_footprint_area": Function(
            "IfcAreaMeasure",
            "Footprint Area",
            "The area if the object's faces were projected along the Z-axis and seen top down",
        ),
        "get_max_side_area": Function(
            "IfcAreaMeasure",
            "Max Side Area",
            "The maximum side area when seen from either X, Y, or Z directions",
        ),
        "get_outer_surface_area": Function(
            "IfcAreaMeasure",
            "Outer Surface Area",
            "The total surface area except for the top or bottom, such as the ends of columns or beams",
        ),
        "get_side_area": Function(
            "IfcAreaMeasure",
            "Side area",
            "The side (non-projected) are of the shape as seen from the local Y-axis",
        ),
        "get_opening_area": Function(
            "IfcAreaMeasure", "Opening Area", "The area of an opening, guessing the opening orientation"
        ),
        "get_top_area": Function(
            "IfcAreaMeasure",
            "Top area",
            "The total surface area deviating by no more than 45 degrees from the local Z+ axis.",
        ),
        # IfcVolumeMeasure
        "get_volume": Function("IfcVolumeMeasure", "Volume", "Calculates the volume of a manifold shape"),
        # IfcMassMeasure
        "get_weight": Function(
            "IfcMassMeasure",
            "Weight",
            "The weight of the object based on it's length and Pset_ProfileMechanical.MassPerLength "
            "(for profile based objects, though objects with openings are not supported for net calculations)"
            "or it's volume and material density (from Pset_MaterialCommon.MassDensity).",
        ),
    }

    functions = {}
    for k, v in raw_functions.items():
        functions[f"gross_{k}"] = Function(v.measure, f"Gross {v.name}", v.description)
        functions[f"net_{k}"] = Function(v.measure, f"Net {v.name}", v.description)

    # Predefined-type-aware footing functions. They read the element's predefined type to
    # pick the correct local axis, so they receive the element (not just the geometry) and
    # cannot live in ifcopenshell.util.shape.
    footing_functions = (
        "get_footing_length",
        "get_footing_width",
        "get_footing_height",
    )

    internal_functions = (
        "get_segment_length",
        "get_weight",
        "get_opening_width",
        "get_opening_height",
        "get_opening_depth",
        "get_opening_area",
        "get_covering_width",
        "get_covering_area",
    ) + footing_functions

    @classmethod
    def calculate(cls, ifc_file, elements, qtos, results):
        formula_functions: dict[str, types.FunctionType] = {}

        cls.gross_settings = ifcopenshell.geom.settings()
        cls.gross_settings.set("disable-opening-subtractions", True)
        cls.net_settings = ifcopenshell.geom.settings()
        cls.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

        gross_qtos: QtosFormulas = {}
        net_qtos: QtosFormulas = {}

        for name, quantities in qtos.items():
            for quantity, formula in quantities.items():
                if not formula:
                    continue
                gross_or_net_qtos = gross_qtos if formula.startswith("gross_") else net_qtos
                if formula.endswith(cls.internal_functions):
                    gross_or_net_qtos.setdefault(name, {})[quantity] = formula.partition("_")[2]
                elif formula.startswith(("gross_", "net_")):
                    formula = formula.partition("_")[2]
                    gross_or_net_qtos.setdefault(name, {})[quantity] = formula
                    formula_functions[formula] = getattr(ifcopenshell.util.shape, formula)
                else:
                    print(f"WARNING. Unexpected formula: '{formula}' ({name}.{quantity}).")

        tasks: list[tuple[Union[ifcopenshell.geom.iterator, IteratorForTypes], QtosFormulas]] = []

        if gross_qtos:
            for iterator in IfcOpenShell.create_iterators(ifc_file, cls.gross_settings, list(elements)):
                tasks.append((iterator, gross_qtos))

        if net_qtos:
            for iterator in IfcOpenShell.create_iterators(ifc_file, cls.net_settings, list(elements)):
                tasks.append((iterator, net_qtos))

        cls.unit_converter = SI2ProjectUnitConverter(ifc_file)

        for iterator, qtos_ in tasks:
            if iterator.initialize():
                while True:
                    geometry: ifcopenshell.geom.main.ShapeType
                    if isinstance(iterator, ifcopenshell.geom.iterator):
                        shape = iterator.get()
                        geometry = shape.geometry
                        element = ifc_file.by_id(shape.id)
                    else:
                        element, geometry = iterator.get_element_and_geometry()

                    results.setdefault(element, {})
                    for name, quantities in qtos_.items():
                        results[element].setdefault(name, {})
                        for quantity, formula in quantities.items():
                            if formula == "get_segment_length":
                                value = cls.get_segment_length(element)
                                if value is None:
                                    continue
                            elif formula == "get_weight":
                                calculation_type = "GROSS" if iterator.settings is cls.gross_settings else "NET"
                                value = cls.get_weight(element, geometry, calculation_type)
                                if value is None:
                                    continue
                            elif formula.startswith("get_opening_"):
                                value = cls.get_opening_quantity(geometry, formula)
                                value = cls.unit_converter.convert(value, IfcOpenShell.raw_functions[formula].measure)
                            elif formula in cls.footing_functions:
                                value = getattr(cls, formula)(element, geometry)
                                if value is None:
                                    continue
                                value = cls.unit_converter.convert(value, cls.raw_functions[formula].measure)
                            elif formula == "get_covering_width":
                                value = cls.get_covering_width(element, geometry)
                                value = cls.unit_converter.convert(value, "IfcLengthMeasure")
                            elif formula == "get_covering_area":
                                value = cls.get_covering_area(element, geometry)
                                value = cls.unit_converter.convert(value, "IfcAreaMeasure")
                            else:
                                value = formula_functions[formula](geometry)
                                assert isinstance(value, (float, int))
                                value = cls.unit_converter.convert(value, IfcOpenShell.raw_functions[formula].measure)
                            results[element][name][quantity] = value
                    if not iterator.next():
                        break

    @staticmethod
    def create_iterators(
        ifc_file: ifcopenshell.file, settings: ifcopenshell.geom.settings, elements: list[ifcopenshell.entity_instance]
    ) -> list[Union[ifcopenshell.geom.iterator, IteratorForTypes]]:
        elements_sorted: defaultdict[bool, list[ifcopenshell.entity_instance]] = defaultdict(list)
        iterators = []
        for element in elements:
            elements_sorted[element.is_a("IfcTypeProduct")].append(element)
        if True in elements_sorted:
            iterators.append(IteratorForTypes(ifc_file, settings, elements_sorted[True]))
        if False in elements_sorted:
            iterators.append(
                ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count(), include=elements)
            )
        return iterators

    @classmethod
    def get_opening_quantity(cls, geometry: ifcopenshell.geom.ShapeType, formula: str) -> float:
        """Get an opening dimension or area, guessing the opening orientation.

        Vertical (wall) openings are measured in a Z-up local frame: X along
        the voided element, Y through it, Z vertical. An opening is treated as
        horizontal (e.g. voiding a slab) when its Z extent is smaller than
        both X and Y, matching the Blender calculator's heuristic.

        :param geometry: Geometry output calculated by IfcOpenShell
        :param formula: One of the ``get_opening_*`` internal function names.
        :return: The dimension or area in SI units.
        """
        x = ifcopenshell.util.shape.get_x(geometry)
        y = ifcopenshell.util.shape.get_y(geometry)
        z = ifcopenshell.util.shape.get_z(geometry)
        is_horizontal = z < x and z < y
        if formula == "get_opening_width":
            return x
        if formula == "get_opening_height":
            return min(x, y) if is_horizontal else z
        if formula == "get_opening_depth":
            return z if is_horizontal else y
        assert formula == "get_opening_area"
        if is_horizontal:
            return ifcopenshell.util.shape.get_footprint_area(geometry)
        return ifcopenshell.util.shape.get_side_area(geometry)

    @classmethod
    def get_segment_length(cls, element: ifcopenshell.entity_instance) -> Union[float, None]:
        """Get segment length.

        :param element: IFC element entity.
        :return: ``float`` segment length in project units
            or ``None`` if element doesn't have a representation or it's not supported.
        """
        rep = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if rep and len(rep.Items or []) == 1 and rep.Items[0].is_a("IfcExtrudedAreaSolid"):
            item = rep.Items[0]
            if item.SweptArea.is_a("IfcRectangleProfileDef"):
                # Revit doesn't follow the +Z extrusion rule, so the rectangle isn't the cross section
                x = item.SweptArea.XDim
                y = item.SweptArea.YDim
                z = item.Depth
                return max([x, y, z])
            elif item.SweptArea.is_a("IfcParameterizedProfileDef"):
                return item.Depth
            settings = ifcopenshell.geom.settings()
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            try:
                area_shape = ifcopenshell.geom.create_shape(settings, item.SweptArea)
            except RuntimeError:
                return
            assert isinstance(area_shape, W.Triangulation)
            x = ifcopenshell.util.shape.get_x(area_shape) / cls.unit_scale
            y = ifcopenshell.util.shape.get_y(area_shape) / cls.unit_scale
            z = item.Depth
            return max([x, y, z])

    # Footings are authored two ways, so a single static axis rule cannot be correct for both.
    # Beam-like footings (STRIP_FOOTING, FOOTING_BEAM) are a profile extruded along the local Z
    # axis, so the run (Length) is local Z and the cross section sits on local X (Width) and
    # local Y (Height). Slab-like footings (PAD_FOOTING, PILE_CAP) have their footprint on the
    # local X/Y plane and their thickness (Height) on local Z. These functions branch on the
    # predefined type to pick the right axis. This mirrors the Blender calculator's
    # get_footing_length / get_footing_width / get_footing_height.
    _beam_like_footings = ("STRIP_FOOTING", "FOOTING_BEAM")

    @classmethod
    def get_footing_length(cls, element: ifcopenshell.entity_instance, geometry: ifcopenshell.geom.ShapeType) -> float:
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type in cls._beam_like_footings:
            return ifcopenshell.util.shape.get_z(geometry)
        return max(ifcopenshell.util.shape.get_x(geometry), ifcopenshell.util.shape.get_y(geometry))

    @classmethod
    def get_footing_width(cls, element: ifcopenshell.entity_instance, geometry: ifcopenshell.geom.ShapeType) -> float:
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type in cls._beam_like_footings:
            return ifcopenshell.util.shape.get_x(geometry)
        return min(ifcopenshell.util.shape.get_x(geometry), ifcopenshell.util.shape.get_y(geometry))

    @classmethod
    def get_footing_height(cls, element: ifcopenshell.entity_instance, geometry: ifcopenshell.geom.ShapeType) -> float:
        predefined_type = ifcopenshell.util.element.get_predefined_type(element)
        if predefined_type in cls._beam_like_footings:
            return ifcopenshell.util.shape.get_y(geometry)
        return ifcopenshell.util.shape.get_z(geometry)

    @classmethod
    def get_weight(
        cls,
        element: ifcopenshell.entity_instance,
        geometry: ifcopenshell.geom.ShapeType,
        calculation_type: Literal["GROSS", "NET"],
    ) -> Union[float, None]:
        """Get element's weight.

        :param element: IFC element entity.
        :return: ``float`` weight in project units
            or ``None`` if mass density calculation for this element is not supported.
        """

        if calculation_type == "gross" or not ifcopenshell.util.element.has_openings(element):
            weight = cls.get_weight_profile_based(element)
            if weight is not None:
                return weight

        density = ifcopenshell.util.element.get_element_mass_density(element)
        if density is None:
            return
        volume = ifcopenshell.util.shape.get_volume(geometry)
        return volume * density

    @classmethod
    def get_weight_profile_based(cls, element: ifcopenshell.entity_instance) -> Union[float, None]:
        """Get weight of the profile based element.

        :return: A float weight value if calculation was successful
            or ``None`` if it's either not profile based object
            or it's not supported.
        """
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return None
        items = representation.Items
        if not all(item.is_a("IfcExtrudedAreaSolid") for item in items):
            return None
        mass = 0.0
        for item in items:
            profile = item.SweptArea
            # TODO: there are also bunch of other similar props we will need to consider in the future.
            # Examples:
            # - Pset_CableSegmentTypeBusBarSegment.MassPerLength
            # - Pset_CableCarrierSegmentTypeCatenaryWire.MassPerLength
            mass_per_length = ifcopenshell.util.element.get_pset(profile, "Pset_ProfileMechanical", "MassPerLength")
            if not isinstance(mass_per_length, float):
                return None
            mass += mass_per_length * item.Depth
        return mass

    @staticmethod
    def get_covering_parametric_axis(element: ifcopenshell.entity_instance) -> Union[str, None]:
        """Get an IfcCovering's layer set direction, as authored by Bonsai's covering type.

        :param element: IFC element entity.
        :return: ``"AXIS2"`` for wall-like coverings, ``"AXIS3"`` for slab-like
            coverings (e.g. floors or ceilings), or ``None`` if the covering's
            type has no ``EPset_Parametric.LayerSetDirection``.
        """
        relating_type = ifcopenshell.util.element.get_type(element)
        if not relating_type:
            return None
        parametric = ifcopenshell.util.element.get_psets(relating_type).get("EPset_Parametric")
        if not parametric:
            return None
        return parametric.get("LayerSetDirection")

    @classmethod
    def get_covering_area(cls, element: ifcopenshell.entity_instance, geometry: ifcopenshell.geom.ShapeType) -> float:
        """Get a covering's area, following its layer set direction.

        AXIS2 (wall-like) coverings report the local Y-facing side area,
        while AXIS3 coverings and coverings without a layer set direction
        (e.g. freeform profiles) report the projected footprint area. This
        mirrors how ``gross_get_side_area``/``net_get_side_area`` are
        already used for ``Qto_WallBaseQuantities.*SideArea`` in this same
        rule set.
        """
        if cls.get_covering_parametric_axis(element) == "AXIS2":
            return ifcopenshell.util.shape.get_side_area(geometry)
        return ifcopenshell.util.shape.get_footprint_area(geometry)

    @classmethod
    def get_covering_width(cls, element: ifcopenshell.entity_instance, geometry: ifcopenshell.geom.ShapeType) -> float:
        """Get a covering's width (i.e. thickness), following its layer set direction.

        AXIS2 (wall-like) coverings report the local Y depth, while AXIS3
        coverings and coverings without a layer set direction report the
        local Z depth. This mirrors how ``net_get_y`` is already used for
        ``Qto_WallBaseQuantities.Width`` in this same rule set, rather than
        the ``min(X, Y)`` heuristic used by the Blender-side
        :func:`bonsai.bim.module.qto.calculator.get_width`.
        """
        if cls.get_covering_parametric_axis(element) == "AXIS2":
            return ifcopenshell.util.shape.get_y(geometry)
        return ifcopenshell.util.shape.get_z(geometry)


class Blender(QtoCalculator):
    """Calculates geometry based on currently loaded Blender objects."""

    # Implementations are located in bonsai.bim.module.qto.calculator.
    functions = {
        # IfcLengthMeasure
        "get_x": Function("IfcLengthMeasure", "X", ""),
        "get_y": Function("IfcLengthMeasure", "Y", ""),
        "get_z": Function("IfcLengthMeasure", "Z", ""),
        "get_covering_width": Function("IfcLengthMeasure", "Covering Width", ""),
        "get_finish_ceiling_height": Function("IfcLengthMeasure", "Finish Ceiling Height", ""),
        "get_finish_floor_height": Function("IfcLengthMeasure", "Finish Floor Height", ""),
        "get_gross_perimeter": Function("IfcLengthMeasure", "Gross Perimeter", ""),
        "get_height": Function("IfcLengthMeasure", "Height", ""),
        "get_length": Function("IfcLengthMeasure", "Length", ""),
        "get_opening_depth": Function("IfcLengthMeasure", "Opening Depth", ""),
        "get_opening_height": Function("IfcLengthMeasure", "Opening Height", ""),
        "get_rectangular_perimeter": Function("IfcLengthMeasure", "Rectangular Perimeter", ""),
        "get_stair_length": Function("IfcLengthMeasure", "Stair Length", ""),
        "get_width": Function("IfcLengthMeasure", "Width", ""),
        "get_footing_height": Function("IfcLengthMeasure", "Height", ""),
        "get_footing_length": Function("IfcLengthMeasure", "Length", ""),
        "get_footing_width": Function("IfcLengthMeasure", "Width", ""),
        # IfcAreaMeasure
        "get_covering_gross_area": Function("IfcAreaMeasure", "Covering Gross Area", ""),
        "get_covering_net_area": Function("IfcAreaMeasure", "Covering Net Area", ""),
        "get_cross_section_area": Function("IfcAreaMeasure", "Cross Section Area", ""),
        "get_gross_ceiling_area": Function("IfcAreaMeasure", "Gross Ceiling Area", ""),
        "get_gross_footprint_area": Function("IfcAreaMeasure", "Gross Footprint Area", ""),
        "get_gross_side_area": Function("IfcAreaMeasure", "Gross Side Area", ""),
        "get_gross_stair_area": Function("IfcAreaMeasure", "Gross Stair Area", ""),
        "get_gross_surface_area": Function("IfcAreaMeasure", "Gross Surface Area", ""),
        "get_gross_top_area": Function("IfcAreaMeasure", "Gross Top Area", ""),
        "get_net_ceiling_area": Function("IfcAreaMeasure", "Net Ceiling Area", ""),
        "get_net_floor_area": Function("IfcAreaMeasure", "Net Floor Area", ""),
        "get_net_footprint_area": Function("IfcAreaMeasure", "Net Footprint Area", ""),
        "get_net_side_area": Function("IfcAreaMeasure", "Net Side Area", ""),
        "get_net_stair_area": Function("IfcAreaMeasure", "Net Stair Area", ""),
        "get_net_surface_area": Function("IfcAreaMeasure", "Net Surface Area", ""),
        "get_net_top_area": Function("IfcAreaMeasure", "Net Top Area", ""),
        "get_opening_mapping_area": Function("IfcAreaMeasure", "Opening Mapping Area", ""),
        "get_outer_surface_area": Function("IfcAreaMeasure", "Outer Surface Area", ""),
        # IfcVolumeMeasure
        "get_gross_volume": Function("IfcVolumeMeasure", "Gross Volume", ""),
        "get_net_volume": Function("IfcVolumeMeasure", "Net Volume", ""),
        "get_space_net_volume": Function("IfcVolumeMeasure", "Space Net Volume", ""),
        # IfcMassMeasure
        "get_gross_weight": Function("IfcMassMeasure", "Gross Weight", ""),
        "get_net_weight": Function("IfcMassMeasure", "Net Weight", ""),
    }

    description_populated = False

    @classmethod
    def populate_descriptions(cls) -> None:
        """Populate the descriptions based on the function docstrings.

        The action is postponed to ensure ifc5d package works without Blender.
        """
        if cls.description_populated:
            return

        import bonsai.bim.module.qto.calculator as calculator

        for function in cls.functions:
            doc = getattr(calculator, function).__doc__ or ""
            doc = doc[: doc.find(":param")].strip()
            old_function = cls.functions[function]
            cls.functions[function] = Function(old_function.measure, old_function.name, doc)

    @classmethod
    def calculate(cls, ifc_file, elements, qtos, results):
        import bonsai.bim.module.qto.calculator as calculator
        import bonsai.tool as tool

        unit_converter = SI2ProjectUnitConverter(ifc_file)
        formula_functions: dict[str, types.FunctionType] = {}

        for element in elements:
            obj = tool.Ifc.get_object(element)
            if not obj or obj.type != "MESH":
                continue
            element_results = results.setdefault(element, {})
            for name, quantities in qtos.items():
                qto_results = element_results.setdefault(name, {})
                for quantity, formula in quantities.items():
                    if not formula:
                        continue
                    if not (formula_function := formula_functions.get(formula)):
                        formula_function = formula_functions[formula] = getattr(calculator, formula)
                    if (value := formula_function(obj)) is not None:
                        qto_results[quantity] = unit_converter.convert(value, Blender.functions[formula].measure)
                if qto_results:
                    element_results[name] = qto_results
            # Avoid adding empty qsets if nothing was calculated.
            if not element_results:
                del results[element]


calculators: dict[str, type[QtoCalculator]] = {
    "Blender": Blender,
    "IfcOpenShell": IfcOpenShell,
}
