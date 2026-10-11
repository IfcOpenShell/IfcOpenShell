# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import importlib
import inspect
import re
from functools import lru_cache
from typing import NamedTuple, Union

import ifcopenshell
import ifcopenshell.util.schema


class ApplicableOccurrence(NamedTuple):
    ifc_class: str
    predefined_type: Union[str, None]


def parse_applicable_occurrence(applicable_occurrence: str) -> list[ApplicableOccurrence]:
    """Parse an IfcTypeObject.ApplicableOccurrence string.

    The spec's convention is a comma separated list of occurrence classes,
    each optionally followed by "/" and a predefined type, e.g.
    "IfcWall/STANDARD, IfcWallStandardCase".
    """
    items: list[ApplicableOccurrence] = []
    for item in applicable_occurrence.split(","):
        ifc_class, _, predefined_type = item.strip().partition("/")
        if ifc_class:
            items.append(ApplicableOccurrence(ifc_class, predefined_type.strip() or None))
    return items


@lru_cache
def get_correct_type_assigned_rules(schema_name: str) -> dict[str, str]:
    """Map each occurrence class with a CorrectTypeAssigned rule to the type class it names.

    The rules are read from their transpiled form in ifcopenshell.express.rules,
    where the type class survives as a lowercased literal such as
    'ifc4.ifcwalltype' in typeof(...).
    """
    schema = ifcopenshell.schema_by_name(schema_name)
    rules = {}
    module = importlib.import_module(f"ifcopenshell.express.rules.{schema.name()}")
    for _, rule in inspect.getmembers(module, inspect.isclass):
        if getattr(rule, "RULE_NAME", None) != "CorrectTypeAssigned":
            continue
        type_class = re.search(r"'ifc\w+\.(ifc\w+)' in typeof", inspect.getsource(rule))
        if not type_class:
            continue  # IfcEvent's rule is about event triggers, not IfcTypeObject.
        type_class = type_class.group(1)
        if type_class == "ifctranformertype":  # IFC4 misspells it in IfcTransformer.CorrectTypeAssigned.
            type_class = "ifctransformertype"
        rules[rule.TYPE_NAME] = schema.declaration_by_name(type_class).name()
    return rules


def get_same_named_types(
    schema: ifcopenshell.ifcopenshell_wrapper.schema_definition, name: str
) -> list[ifcopenshell.ifcopenshell_wrapper.entity]:
    """The type class declarations named after the occurrence class, abstract or not."""
    if name in ("IfcProduct", "IfcObject"):
        return [schema.declaration_by_name("IfcType" + name[3:])]
    declarations = []
    for suffix in ("Type", "Style"):
        try:
            declaration = schema.declaration_by_name(name + suffix)
        except RuntimeError:
            continue
        if ifcopenshell.util.schema.is_a(declaration, "IfcTypeObject"):
            declarations.append(declaration)
    return declarations


def get_applicable_schema_types(
    schema: ifcopenshell.ifcopenshell_wrapper.schema_definition, declaration: ifcopenshell.ifcopenshell_wrapper.entity
) -> list[str]:
    """The type classes the schema lets type the occurrence class, most specific first."""
    rules = get_correct_type_assigned_rules(schema.name())
    occurrence_class = declaration.name()
    ancestors = ifcopenshell.util.schema.get_supertypes(declaration)

    # Check for both direct and inherited WRs.
    # e.g. IfcWallStandardCase has none of its own and takes IfcWall's
    for ancestor in [declaration] + ancestors:
        if ancestor.name() in rules:
            return [rules[ancestor.name()]]

    # Try to guess via name
    types = []
    for type_declaration in get_same_named_types(schema, occurrence_class):
        types.extend([d.name() for d in ifcopenshell.util.schema.get_subtypes(type_declaration)])
    if types:
        return types

    # Still can't find anything? Find the nearest concrete typed ancestor.
    for ancestor in ancestors:
        for type_declaration in get_same_named_types(schema, ancestor.name()):
            if not type_declaration.is_abstract():
                types.append(type_declaration.name())
        if types:
            return types

    assert False, f"could not find matching type for {occurrence_class}"


@lru_cache
def get_type_maps(schema_name: str) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """The occurrence to type map and its inverse for a schema, derived once and cached."""
    schema = ifcopenshell.schema_by_name(schema_name)
    rules = get_correct_type_assigned_rules(schema.name())
    entity_to_type_map = {
        declaration.name(): get_applicable_schema_types(schema, declaration)
        for declaration in ifcopenshell.util.schema.get_subtypes(schema.declaration_by_name("IfcObject"))
    }

    # An occurrence is the primary one of a type class when its own rule or
    # same-named type names it. Primaries come first in the inverse map, then
    # the most specific classes, so callers asking for "the" occurrence class
    # of IfcPumpType get IfcPump, and IfcFlowMovingDevice before
    # IfcDistributionElement.
    def is_primary(entity: str, type_class: str) -> bool:
        return rules.get(entity) == type_class or type_class in {d.name() for d in get_same_named_types(schema, entity)}

    def depth(entity: str) -> int:
        declaration = schema.declaration_by_name(entity)
        return 0 if declaration.supertype() is None else 1 + depth(declaration.supertype().name())

    type_to_entity_map: dict[str, list[str]] = {}
    for primary in (True, False):
        for entity, types in sorted(entity_to_type_map.items(), key=lambda item: (-depth(item[0]), item[0])):
            for type_class in types:
                if is_primary(entity, type_class) == primary:
                    type_to_entity_map.setdefault(type_class, []).append(entity)
    return entity_to_type_map, type_to_entity_map


def get_applicable_types(
    ifc_class: Union[str, ifcopenshell.entity_instance], schema: ifcopenshell.util.schema.IFC_SCHEMA = "IFC4"
) -> list[str]:
    """Get the type classes that may type the occurrence class.

    E.g. "IfcWindow" -> ["IfcWindowType"]. The first class is the primary
    pairing. An occurrence instance may be passed instead of a class name, in
    which case its file's schema is used.
    """
    if isinstance(ifc_class, ifcopenshell.entity_instance):
        schema = ifc_class.file.schema_identifier
        ifc_class = ifc_class.is_a()
    return list(get_type_maps(schema.upper())[0].get(ifc_class, []))


def get_applicable_entities(
    ifc_type_class: Union[str, ifcopenshell.entity_instance], schema: ifcopenshell.util.schema.IFC_SCHEMA = "IFC4"
) -> list[ApplicableOccurrence]:
    """Get the occurrence classes that the type class may type.

    E.g. "IfcWindowType" -> [ApplicableOccurrence("IfcWindow", None)]. The
    first class is the primary pairing.

    A type instance may be passed instead of a class name, in which case its
    file's schema is used and its ApplicableOccurrence attribute narrows the
    result to the classes it names, carrying their predefined types. The
    attribute can never widen the schema's answer: classes the schema does
    not allow are dropped, and if nothing it names is allowed it is ignored.
    """
    relating_type = None
    if isinstance(ifc_type_class, ifcopenshell.entity_instance):
        relating_type = ifc_type_class
        schema = relating_type.file.schema_identifier
        ifc_type_class = relating_type.is_a()
    entities = get_type_maps(schema.upper())[1].get(ifc_type_class, [])
    if relating_type is not None and (applicable_occurrence := getattr(relating_type, "ApplicableOccurrence", None)):
        narrowed = [o for o in parse_applicable_occurrence(applicable_occurrence) if o.ifc_class in entities]
        if narrowed:
            return narrowed
    return [ApplicableOccurrence(entity, None) for entity in entities]


def is_applicable(relating_type: ifcopenshell.entity_instance, occurrence: ifcopenshell.entity_instance) -> bool:
    """Whether the type may type the occurrence, see :func:`get_applicable_entities`."""
    return any(occurrence.is_a() == o.ifc_class for o in get_applicable_entities(relating_type))
