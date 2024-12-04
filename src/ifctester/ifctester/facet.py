# IfcTester - IDS based model auditing
# Copyright (C) 2021 Artur Tomczak <artomczak@gmail.com>, Thomas Krijnen <mail@thomaskrijnen.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
import re
import builtins
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.classification
from functools import lru_cache
from xmlschema.validators import identities
from typing import Union, Optional, Any, Literal, TYPE_CHECKING, TypedDict
from logging import Logger

if TYPE_CHECKING:
    from .ids import Specification


def cast_to_value(from_value, to_value):
    try:
        target_type = type(to_value).__name__
        if target_type == "int":
            # Casting str -> float means that notation like '1e3' is preserved
            # We do not cast to int because 42.0 == 42 and 42.3 != 42
            return float(from_value)
        elif target_type == "bool":
            if from_value in ("true", "1"):
                return True
            elif from_value in ("false", "0"):
                return False
        return builtins.__dict__[target_type](from_value)
    except ValueError:
        pass


# See bug 4716.
def is_x(value, cast_value):
    if cast_value >= 0:
        if value < cast_value * (1.0 - 1e-6) or value > cast_value * (1.0 + 1e-6):
            return False
    elif value > cast_value * (1.0 - 1e-6) or value < cast_value * (1.0 + 1e-6):
        return False
    return True


@lru_cache
def get_pset(element, pset):
    return ifcopenshell.util.element.get_pset(element, pset)


@lru_cache
def get_psets(element):
    return ifcopenshell.util.element.get_psets(element)


Cardinality = Literal["required", "optional", "prohibited"]


class FacetFailure(TypedDict):
    element: ifcopenshell.entity_instance
    reason: str


class Facet:
    cardinality: Cardinality

    def __init__(self, *parameters):
        self.status = None
        self.passed_entities: set[ifcopenshell.entity_instance] = set()
        self.failures: list[FacetFailure] = []
        for i, name in enumerate(self.parameters):
            setattr(self, name.replace("@", ""), parameters[i])

    def asdict(self, clause_type: str) -> dict[str, Any]:
        results = {}
        for name in self.parameters:
            value = getattr(self, name.replace("@", ""))
            if value is not None:
                if name == "@dataType":
                    value = value.upper()
                results[name] = value if "@" in name else self.to_ids_value(value)
        if clause_type == "applicability":
            for key in ["@uri", "@instructions", "@cardinality"]:
                results.pop(key, None)
        return results

    def parse(self, xml):
        setattr(self, "cardinality", "required")
        for name, value in xml.items():
            name = name.replace("@", "")
            if isinstance(value, dict) and "simpleValue" in value.keys():
                setattr(self, name, value["simpleValue"])
            elif isinstance(value, dict) and "restriction" in value.keys():
                setattr(self, name, Restriction().parse(value["restriction"]))
            else:
                setattr(self, name, value)
        return self

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]]
    ) -> list[ifcopenshell.entity_instance]:
        if not elements:
            return []
        return [e for e in elements if self(e)]

    def to_string(
        self,
        clause_type: str,
        specification: Optional[Specification] = None,
        requirement: Optional[Facet] = None,
    ) -> str:
        if clause_type == "applicability":
            templates = self.applicability_templates
        elif clause_type == "requirement":
            is_prohibited = False
            if specification.maxOccurs == 0:
                is_prohibited = not is_prohibited
            if requirement.cardinality == "prohibited":
                is_prohibited = not is_prohibited
            templates = self.prohibited_templates if is_prohibited else self.requirement_templates
            if requirement.cardinality == "optional":
                templates = [
                    t.replace("shall", "may").replace("Shall", "May").replace("must", "may") for t in templates
                ]

        for template in templates:
            total_variables = len(template) - len(template.replace("{", ""))
            total_replacements = 0
            for key in self.parameters:
                key = key.replace("@", "")
                value = getattr(self, key)
                key_variable = "{" + key + "}"
                if value is not None and key_variable in template:
                    template = template.replace(key_variable, str(value))
                    total_replacements += 1
                if total_replacements == total_variables:
                    return template
        return "This facet cannot be interpreted"

    def to_ids_value(self, parameter: Union[str, Restriction, list]) -> dict[str, Any]:
        if isinstance(parameter, (int, float, str)):
            parameter_dict = {"simpleValue": str(parameter)}
        elif isinstance(parameter, Restriction):
            parameter_dict = {"xs:restriction": [parameter.asdict()]}
        elif isinstance(parameter, list):
            restrictions = {"@base": "xs:" + parameter[0].base}
            for p in parameter:
                x = p.asdict()
                restrictions[list(x)[1]] = x[list(x)[1]]
            parameter_dict = {"xs:restriction": [restrictions]}
        else:
            raise Exception(str(parameter) + " was not able to be converted into 'Parameter_dict'")
        return parameter_dict

    def get_usage(self) -> Cardinality:
        return self.cardinality

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> Result:
        raise NotImplementedError


class Entity(Facet):
    def __init__(self, name="IFCWALL", predefinedType=None, instructions=None):
        self.parameters = ["name", "predefinedType", "@instructions"]
        self.applicability_templates = [
            "All {name} data of type {predefinedType}",
            "All {name} data",
        ]
        self.requirement_templates = [
            "Shall be {name} data of type {predefinedType}",
            "Shall be {name} data",
        ]
        self.prohibited_templates = [
            "Shall not be {name} data of type {predefinedType}",
            "Shall not be {name} data",
        ]
        super().__init__(name, predefinedType, instructions)

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]] = None
    ) -> list[ifcopenshell.entity_instance]:
        if isinstance(elements, list):
            return super().filter(ifc_file, elements)

        if isinstance(self.name, str):
            try:
                results = ifc_file.by_type(self.name, include_subtypes=False)
            except:
                # If the user has specified a class that doesn't exist in the version
                results = []
        else:
            results = []
            ifc_classes = [t for t in ifc_file.wrapped_data.types() if t.upper() == self.name]
            for ifc_class in ifc_classes:
                try:
                    results.extend(ifc_file.by_type(ifc_class, include_subtypes=False))
                except:
                    # If the user has specified a class that doesn't exist in the version
                    continue
        if self.predefinedType:
            return [r for r in results if self(r)]
        return results

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> EntityResult:
        is_pass = inst.is_a().upper() == self.name
        reason = None

        if not is_pass:
            reason = {"type": "NAME", "actual": inst.is_a().upper()}

        if is_pass and self.predefinedType:
            predefined_type = ifcopenshell.util.element.get_predefined_type(inst)
            is_pass = predefined_type == self.predefinedType

            if not is_pass:
                reason = {"type": "PREDEFINEDTYPE", "actual": predefined_type}

        return EntityResult(is_pass, reason)


class Attribute(Facet):
    def __init__(self, name="Name", value=None, cardinality: Cardinality = "required", instructions=None):
        self.parameters = ["name", "value", "@cardinality", "@instructions"]
        self.applicability_templates = [
            "Data where the {name} is {value}",
            "Data where the {name} is provided",
        ]
        self.requirement_templates = [
            "The {name} shall be {value}",
            "The {name} shall be provided",
        ]
        self.prohibited_templates = [
            "The {name} shall not be {value}",
            "The {name} shall not be provided",
        ]
        super().__init__(name, value, cardinality, instructions)

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]]
    ) -> list[ifcopenshell.entity_instance]:
        if isinstance(elements, list):
            return super().filter(ifc_file, elements)

        results = []
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema)
        entities = {entity.name(): entity for entity in schema.entities()}

        def ignore_subtypes(entity):
            for subentity in entity.subtypes():
                # entity might be already removed as .entities() order is not hierarchical
                if entities.pop(subentity.name(), None):
                    ignore_subtypes(subentity)

        while entities:
            entity_name, entity = entities.popitem()
            for attribute in entity.attributes():
                if attribute.name() == self.name:
                    results.extend(ifc_file.by_type(entity_name, include_subtypes=True))
                    # e.g. if IfcRoot already has .Name, it's safe not to check all it's subtypes attributes
                    ignore_subtypes(entity)

        # TODO: perhaps we should consider value in the filter

        return results

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> AttributeResult:
        if self.cardinality == "optional":
            return AttributeResult(True)

        if isinstance(self.name, str):
            names = [self.name]
            attribute_type = inst.wrapped_data.get_attribute_category(self.name)
            if attribute_type == 1:  # Forward attribute
                values = [getattr(inst, self.name, None)]
            else:
                values = [None]
        else:
            info = inst.get_info()
            names = []
            values = []
            for k, v in info.items():
                if k == self.name:
                    attribute_type = inst.wrapped_data.get_attribute_category(k)
                    if attribute_type == 1:  # Forward attribute
                        names.append(k)
                        values.append(v)

        is_pass = bool(values)
        reason = None

        if not is_pass:
            reason = {"type": "NOVALUE"}

        if is_pass:
            non_empty_values = []
            for i, value in enumerate(values):
                is_empty = False
                if value is None:
                    is_empty = True
                elif value == "":
                    is_empty = True
                elif value == tuple():
                    is_empty = True
                else:
                    argument_index = inst.wrapped_data.get_argument_index(names[i])
                    try:
                        attribute_type = inst.attribute_type(argument_index)
                        if attribute_type == "LOGICAL" and value == "UNKNOWN":
                            is_empty = True
                    except:
                        if names[i] in inst.wrapped_data.get_inverse_attribute_names():
                            is_empty = True
                if not is_empty:
                    non_empty_values.append(value)
            if non_empty_values:
                values = non_empty_values
            else:
                is_pass = False
                reason = {"type": "FALSEY", "actual": values if len(values) > 1 else values[0]}

        if is_pass and self.value:
            for value in values:
                if isinstance(value, ifcopenshell.entity_instance):
                    is_pass = False
                    reason = {"type": "VALUE", "actual": value}
                    break
                elif isinstance(self.value, str) and isinstance(value, str):
                    if value != self.value:
                        is_pass = False
                        reason = {"type": "VALUE", "actual": value}
                        break
                elif isinstance(self.value, str):
                    cast_value = cast_to_value(self.value, value)
                    if isinstance(value, float) and isinstance(cast_value, float):
                        if not is_x(value, cast_value):
                            is_pass = False
                            reason = {"type": "VALUE", "actual": value}
                            break
                    elif value != cast_value:
                        is_pass = False
                        reason = {"type": "VALUE", "actual": value}
                        break
                elif value != self.value:
                    is_pass = False
                    reason = {"type": "VALUE", "actual": value}
                    break

        if self.cardinality == "prohibited":
            return AttributeResult(not is_pass, {"type": "PROHIBITED"})
        return AttributeResult(is_pass, reason)


class Classification(Facet):
    def __init__(self, value=None, system=None, uri=None, cardinality: Cardinality = "required", instructions=None):
        self.parameters = ["value", "system", "@uri", "@cardinality", "@instructions"]
        self.applicability_templates = [
            "Data having a {system} reference of {value}",
            "Data classified using {system}",
            "Data classified as {value}",
        ]
        self.requirement_templates = [
            "Shall have a {system} reference of {value}",
            "Shall be classified using {system}",
            "Shall be classified as {value}",
        ]
        self.prohibited_templates = [
            "Shall not have a {system} reference of {value}",
            "Shall not be classified using {system}",
            "Shall not be classified as {value}",
        ]

        super().__init__(value, system, uri, cardinality, instructions)

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]]
    ) -> list[ifcopenshell.entity_instance]:
        if isinstance(elements, list):
            return super().filter(ifc_file, elements)
        return ifc_file.by_type("IfcObjectDefinition")

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> ClassificationResult:
        if self.cardinality == "optional":
            return ClassificationResult(True)  # Is this really the correct behaviour?

        leaf_references = ifcopenshell.util.classification.get_references(inst)

        references = leaf_references.copy()
        for leaf_reference in leaf_references:
            references.update(ifcopenshell.util.classification.get_inherited_references(leaf_reference))

        is_pass = bool(references)
        reason = None

        if not is_pass:
            reason = {"type": "NOVALUE"}

        if is_pass and self.value:
            values = [getattr(r, "Identification", getattr(r, "ItemReference", None)) for r in references]
            is_pass = any([self.value == v for v in values])
            if not is_pass:
                reason = {"type": "VALUE", "actual": values}

        if is_pass:
            systems = [ifcopenshell.util.classification.get_classification(r).Name for r in references]
            is_pass = any([self.system == s for s in systems])
            if not is_pass:
                reason = {"type": "SYSTEM", "actual": systems}

        if self.cardinality == "prohibited":
            return ClassificationResult(not is_pass, {"type": "PROHIBITED"})
        return ClassificationResult(is_pass, reason)


class PartOf(Facet):
    def __init__(
        self,
        name="IFCWALL",
        predefinedType=None,
        relation=None,
        cardinality: Cardinality = "required",
        instructions=None,
    ):
        self.parameters = ["name", "predefinedType", "@relation", "@cardinality", "@instructions"]
        self.applicability_templates = [
            "An element with an {relation} relationship with an {name}",
            "An element with an {relation} relationship",
        ]
        self.requirement_templates = [
            "An element must have an {relation} relationship with an {name} of predefined type {predefinedType}",
            "An element must have an {relation} relationship with an {name}",
            "An element must have an {relation} relationship",
        ]
        self.prohibited_templates = [
            "An element must not have an {relation} relationship with an {name}",
            "An element must not have an {relation} relationship",
        ]
        super().__init__(name, predefinedType, relation, cardinality, instructions)

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]]
    ) -> list[ifcopenshell.entity_instance]:
        if isinstance(elements, list):
            return super().filter(ifc_file, elements)
        return list(ifc_file)  # Lazy

    def asdict(self, clause_type: str) -> dict[str, Any]:
        results = super().asdict(clause_type)
        entity = {}
        if "name" in results:
            entity["name"] = results["name"]
            del results["name"]
        if "predefinedType" in results:
            entity["predefinedType"] = results["predefinedType"]
            del results["predefinedType"]
        if entity:
            results["entity"] = entity
        return results

    def parse(self, xml):
        if "entity" in xml:
            super().parse(xml["entity"])
            del xml["entity"]
        return super().parse(xml)

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> PartOfResult:
        reason = None
        if not self.relation:
            is_pass = False
            ancestors = []
            parent = self.get_parent(inst)
            while parent:
                ancestors.append(parent.is_a().upper())
                if parent.is_a().upper() == self.name:
                    if self.predefinedType:
                        predefined_type = ifcopenshell.util.element.get_predefined_type(parent)
                        ancestors[-1] += f".{predefined_type}"
                        if predefined_type == self.predefinedType:
                            is_pass = True
                    else:
                        is_pass = True
                    break
                parent = self.get_parent(parent)
            if not is_pass:
                reason = {"type": "ENTITY", "actual": ancestors}
        elif self.relation == "IFCRELAGGREGATES":
            aggregate = ifcopenshell.util.element.get_aggregate(inst)
            is_pass = aggregate is not None
            if not is_pass:
                reason = {"type": "NOVALUE"}
            if is_pass and self.name:
                is_pass = False
                ancestors = []
                while aggregate is not None:
                    ancestors.append(aggregate.is_a().upper())
                    if aggregate.is_a().upper() == self.name:
                        if self.predefinedType:
                            predefined_type = ifcopenshell.util.element.get_predefined_type(aggregate)
                            ancestors[-1] += f".{predefined_type}"
                            if predefined_type == self.predefinedType:
                                is_pass = True
                        else:
                            is_pass = True
                        break
                    aggregate = ifcopenshell.util.element.get_aggregate(aggregate)
                if not is_pass:
                    reason = {"type": "ENTITY", "actual": ancestors}
        elif self.relation == "IFCRELASSIGNSTOGROUP":
            group = None
            for rel in getattr(inst, "HasAssignments", []) or []:
                if rel.is_a("IfcRelAssignsToGroup"):
                    group = rel.RelatingGroup
                    break
            is_pass = group is not None
            if not is_pass:
                reason = {"type": "NOVALUE"}
            if is_pass and self.name:
                if group.is_a().upper() != self.name:
                    is_pass = False
                    reason = {"type": "ENTITY", "actual": group.is_a().upper()}
                if self.predefinedType:
                    predefined_type = ifcopenshell.util.element.get_predefined_type(group)
                    if predefined_type != self.predefinedType:
                        is_pass = False
                        reason = {"type": "PREDEFINEDTYPE", "actual": predefined_type}
        elif self.relation == "IFCRELCONTAINEDINSPATIALSTRUCTURE":
            container = ifcopenshell.util.element.get_container(inst)
            is_pass = container is not None
            if not is_pass:
                reason = {"type": "NOVALUE"}
            if is_pass and self.name:
                if container.is_a().upper() != self.name:
                    is_pass = False
                    reason = {"type": "ENTITY", "actual": container.is_a().upper()}
                if is_pass and self.predefinedType:
                    predefined_type = ifcopenshell.util.element.get_predefined_type(container)
                    if predefined_type != self.predefinedType:
                        is_pass = False
                        reason = {"type": "PREDEFINEDTYPE", "actual": predefined_type}
        elif self.relation == "IFCRELNESTS":
            nest = ifcopenshell.util.element.get_nest(inst)
            is_pass = nest is not None
            if not is_pass:
                reason = {"type": "NOVALUE"}
            if is_pass and self.name:
                is_pass = False
                ancestors = []
                while nest is not None:
                    ancestors.append(nest.is_a().upper())
                    if nest.is_a().upper() == self.name:
                        if self.predefinedType:
                            predefined_type = ifcopenshell.util.element.get_predefined_type(nest)
                            ancestors[-1] += f".{predefined_type}"
                            if predefined_type == self.predefinedType:
                                is_pass = True
                        else:
                            is_pass = True
                        break
                    nest = ifcopenshell.util.element.get_nest(nest)
                if not is_pass:
                    reason = {"type": "ENTITY", "actual": ancestors}
        elif self.relation == "IFCRELVOIDSELEMENT IFCRELFILLSELEMENT":
            if inst.is_a("IfcOpeningElement"):
                building_element = ifcopenshell.util.element.get_voided_element(inst)
            else:
                building_element = None
                opening = ifcopenshell.util.element.get_filled_void(inst)
                if opening:
                    building_element = ifcopenshell.util.element.get_voided_element(opening)
            is_pass = building_element is not None
            if not is_pass:
                reason = {"type": "NOVALUE"}
            if is_pass and self.name:
                if building_element.is_a().upper() != self.name:
                    is_pass = False
                    reason = {"type": "ENTITY", "actual": building_element.is_a().upper()}
                if is_pass and self.predefinedType:
                    predefined_type = ifcopenshell.util.element.get_predefined_type(building_element)
                    if predefined_type != self.predefinedType:
                        is_pass = False
                        reason = {"type": "PREDEFINEDTYPE", "actual": predefined_type}

        if self.cardinality == "prohibited":
            return PartOfResult(not is_pass, {"type": "PROHIBITED"})
        return PartOfResult(is_pass, reason)

    def get_parent(self, element):
        parent = ifcopenshell.util.element.get_parent(element)
        if not parent:
            for rel in getattr(element, "HasAssignments", []) or []:
                if rel.is_a("IfcRelAssignsToGroup"):
                    parent = rel.RelatingGroup
                    break
        return parent


class Property(Facet):
    def __init__(
        self,
        propertySet="Property_Set",
        baseName="PropertyName",
        value=None,
        dataType=None,
        uri=None,
        cardinality: Cardinality = "required",
        instructions=None,
    ):
        self.parameters = [
            "propertySet",
            "baseName",
            "value",
            "@dataType",
            "@uri",
            "@cardinality",
            "@instructions",
        ]
        self.applicability_templates = [
            "Elements with {baseName} data of {value} in the dataset {propertySet}",
            "Elements with {baseName} data in the dataset {propertySet}",
        ]
        self.requirement_templates = [
            "{baseName} data shall be {value} and in the dataset {propertySet}",
            "{baseName} data shall be provided in the dataset {propertySet}",
        ]
        self.prohibited_templates = [
            "{baseName} data shall not be {value} and in the dataset {propertySet}",
            "{baseName} data shall not be provided in the dataset {propertySet}",
        ]
        super().__init__(propertySet, baseName, value, dataType, uri, cardinality, instructions)

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]]
    ) -> list[ifcopenshell.entity_instance]:
        if isinstance(elements, list):
            return super().filter(ifc_file, elements)
        if ifc_file.schema == "IFC2X3":
            return ifc_file.by_type("IfcObjectDefinition")
        return (
            ifc_file.by_type("IfcObjectDefinition")
            + ifc_file.by_type("IfcMaterialDefinition")
            + ifc_file.by_type("IfcProfileDef")
        )

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> PropertyResult:
        if self.cardinality == "optional":
            return PropertyResult(True)

        if isinstance(self.propertySet, str):
            pset = get_pset(inst, self.propertySet)
            psets = {self.propertySet: pset} if pset else {}
        else:
            all_psets = get_psets(inst)
            psets = {k: v for k, v in all_psets.items() if k == self.propertySet}

        is_pass = bool(psets)
        reason = None

        if not is_pass:
            reason = {"type": "NOPSET"}

        if is_pass:
            props = {}
            for pset_name, pset_props in psets.items():
                props[pset_name] = {}
                if isinstance(self.baseName, str):
                    prop = pset_props.get(self.baseName)
                    if prop == "UNKNOWN" and [
                        p
                        for p in self.get_properties(inst.wrapped_data.file.by_id(pset_props["id"]))
                        if p.Name == self.baseName
                    ][0].NominalValue.is_a("IfcLogical"):
                        pass
                    elif prop is not None and prop != "":
                        props[pset_name][self.baseName] = prop
                else:
                    props[pset_name] = {k: v for k, v in pset_props.items() if k == self.baseName}

                if not bool(props[pset_name]):
                    is_pass = False
                    reason = {"type": "NOVALUE"}
                    break

                pset_entity = inst.wrapped_data.file.by_id(pset_props["id"])

                is_property_supported_class = True
                for prop_entity in self.get_properties(pset_entity):
                    if prop_entity.Name not in props[pset_name].keys():
                        continue
                    if not isinstance(prop_entity, ifcopenshell.entity_instance):
                        # Predefined properties are special :(
                        pass
                    elif prop_entity.is_a("IfcPropertySingleValue"):
                        data_type = prop_entity.NominalValue.is_a()

                        if self.dataType and data_type.lower() != self.dataType.lower():
                            is_pass = False
                            reason = {"type": "DATATYPE", "actual": data_type, "dataType": self.dataType}
                            break

                        unit = ifcopenshell.util.unit.get_property_unit(prop_entity, inst.wrapped_data.file)
                        if unit and getattr(unit, "Name", None):
                            # TODO support unnamed derived units
                            props[pset_name][prop_entity.Name] = ifcopenshell.util.unit.convert(
                                prop_entity.NominalValue.wrappedValue,
                                getattr(unit, "Prefix", None),
                                unit.Name,
                                None,
                                ifcopenshell.util.unit.si_type_names[unit.UnitType],
                            )
                    elif prop_entity.is_a("IfcPhysicalSimpleQuantity"):
                        prop_schema = prop_entity.wrapped_data.declaration().as_entity()
                        data_type = prop_schema.attribute_by_index(3).type_of_attribute().declared_type().name()

                        if self.dataType and data_type.lower() != self.dataType.lower():
                            is_pass = False
                            reason = {"type": "DATATYPE", "actual": data_type, "dataType": self.dataType}
                            break

                        unit = ifcopenshell.util.unit.get_property_unit(prop_entity, inst.wrapped_data.file)
                        if unit:
                            props[pset_name][prop_entity.Name] = ifcopenshell.util.unit.convert(
                                prop_entity[3],
                                getattr(unit, "Prefix", None),
                                unit.Name,
                                None,
                                ifcopenshell.util.unit.si_type_names[unit.UnitType],
                            )
                    elif prop_entity.is_a("IfcPropertyEnumeratedValue"):
                        if not prop_entity.EnumerationValues:
                            is_pass = False
                            reason = {"type": "NOVALUE"}
                            break
                        data_type = prop_entity.EnumerationValues[0].is_a()
                        if self.dataType and data_type.lower() != self.dataType.lower():
                            is_pass = False
                            reason = {"type": "DATATYPE", "actual": data_type, "dataType": self.dataType}
                            break
                    elif prop_entity.is_a("IfcPropertyListValue"):
                        if not prop_entity.ListValues:
                            is_pass = False
                            reason = {"type": "NOVALUE"}
                            break
                        data_type = prop_entity.ListValues[0].is_a()
                        if self.dataType and data_type.lower() != self.dataType.lower():
                            is_pass = False
                            reason = {"type": "DATATYPE", "actual": data_type, "dataType": self.dataType}
                            break
                        unit = ifcopenshell.util.unit.get_property_unit(prop_entity, inst.wrapped_data.file)
                        if unit:
                            props[pset_name][prop_entity.Name] = [
                                ifcopenshell.util.unit.convert(
                                    v,
                                    getattr(unit, "Prefix", None),
                                    unit.Name,
                                    None,
                                    ifcopenshell.util.unit.si_type_names[unit.UnitType],
                                )
                                for v in props[pset_name][prop_entity.Name]
                            ]
                    elif prop_entity.is_a("IfcPropertyBoundedValue"):
                        values = []
                        for attribute in ["UpperBoundValue", "LowerBoundValue", "SetPointValue"]:
                            value = getattr(prop_entity, attribute)
                            if value is not None:
                                data_type = value.is_a()
                                values.append(value.wrappedValue)
                        if self.dataType and data_type.lower() != self.dataType.lower():
                            is_pass = False
                            reason = {"type": "DATATYPE", "actual": data_type, "dataType": self.dataType}
                            break
                        unit = ifcopenshell.util.unit.get_property_unit(prop_entity, inst.wrapped_data.file)
                        if unit:
                            values = [
                                ifcopenshell.util.unit.convert(
                                    v,
                                    getattr(unit, "Prefix", None),
                                    unit.Name,
                                    None,
                                    ifcopenshell.util.unit.si_type_names[unit.UnitType],
                                )
                                for v in values
                            ]
                        props[pset_name][prop_entity.Name] = values
                    elif prop_entity.is_a("IfcPropertyTableValue"):
                        values = []
                        units = ifcopenshell.util.unit.get_property_unit(prop_entity, inst.wrapped_data.file)
                        for attribute in ["Defining", "Defined"]:
                            column_values = props[pset_name][prop_entity.Name][f"{attribute}Values"]
                            if not column_values:
                                continue
                            data_type = column_values[0].is_a()
                            if self.dataType and data_type.lower() == self.dataType.lower():
                                column_values = [v.wrappedValue for v in column_values]
                                unit = units[f"{attribute}Unit"]
                                if unit:
                                    column_values = [
                                        ifcopenshell.util.unit.convert(
                                            v,
                                            getattr(unit, "Prefix", None),
                                            unit.Name,
                                            None,
                                            ifcopenshell.util.unit.si_type_names[unit.UnitType],
                                        )
                                        for v in column_values
                                    ]
                                values.extend(column_values)
                        if not values:
                            is_pass = False
                            reason = {"type": "DATATYPE", "actual": data_type, "dataType": self.dataType}
                            break
                        props[pset_name][prop_entity.Name] = values
                    else:
                        is_property_supported_class = False

                if not is_property_supported_class:
                    is_pass = False
                    reason = {"type": "NOVALUE"}

                if not is_pass:
                    break

                if self.value:
                    for value in props[pset_name].values():
                        if isinstance(self.value, str) and isinstance(value, str):
                            # "i_require_foo" = "i_have_bar"
                            if value != self.value:
                                is_pass = False
                                reason = {"type": "VALUE", "actual": value}
                                break
                        elif isinstance(self.value, str) and isinstance(value, list):
                            # "i_require_foo" = ["a", "b"] such as in enumerated properties
                            cast_value = cast_to_value(self.value, value[0])
                            if cast_value not in value:
                                is_pass = False
                                reason = {"type": "VALUE", "actual": value}
                                break
                        elif not isinstance(self.value, str) and isinstance(value, list):
                            # XSD restriction = ["a", "b"] such as in enumerated properties
                            does_any_pass = [v for v in value if v == self.value]
                            if not does_any_pass:
                                is_pass = False
                                reason = {"type": "VALUE", "actual": value}
                                break
                        elif isinstance(self.value, str):
                            # "42" = 42
                            cast_value = cast_to_value(self.value, value)
                            if isinstance(value, float) and isinstance(cast_value, float):
                                if not is_x(value, cast_value):
                                    is_pass = False
                                    reason = {"type": "VALUE", "actual": value}
                                    break
                            elif value != cast_value:
                                is_pass = False
                                reason = {"type": "VALUE", "actual": value}
                                break
                        elif value != self.value:
                            # XSD restriction = whatever
                            is_pass = False
                            reason = {"type": "VALUE", "actual": value}
                            break

        if self.cardinality == "prohibited":
            return PropertyResult(not is_pass, {"type": "PROHIBITED"})
        return PropertyResult(is_pass, reason)

    def get_properties(self, pset):
        if pset.is_a("IfcPropertySet"):
            return pset.HasProperties
        elif pset.is_a("IfcElementQuantity"):
            return pset.Quantities
        elif pset.is_a("IfcMaterialProperties") or pset.is_a("IfcProfileProperties"):
            return pset.Properties
        elif pset.is_a("IfcPreDefinedPropertySet"):
            return [
                type("", (object,), {"Name": k, "Value": v})()
                for k, v in pset.get_info().items()
                if not isinstance(v, ifcopenshell.entity_instance)
            ]


class Material(Facet):
    def __init__(self, value=None, uri=None, cardinality: Cardinality = "required", instructions=None):
        self.parameters = ["value", "@uri", "@cardinality", "@instructions"]
        self.applicability_templates = [
            "All data with a {value} material",
            "All data with a material",
        ]
        self.requirement_templates = [
            "Shall have a material of {value}",
            "Shall have a material",
        ]
        self.prohibited_templates = [
            "Shall not have a material of {value}",
            "Shall not have a material",
        ]
        super().__init__(value, uri, cardinality, instructions)

    def filter(
        self, ifc_file: ifcopenshell.file, elements: Optional[list[ifcopenshell.entity_instance]]
    ) -> list[ifcopenshell.entity_instance]:
        if isinstance(elements, list):
            return super().filter(ifc_file, elements)
        return ifc_file.by_type("IfcObjectDefinition")

    def __call__(self, inst: ifcopenshell.entity_instance, logger: Optional[Logger] = None) -> MaterialResult:
        if self.cardinality == "optional":
            return MaterialResult(True)

        material = ifcopenshell.util.element.get_material(inst, should_skip_usage=True)

        is_pass = material is not None
        reason = None

        if not is_pass:
            reason = {"type": "NOVALUE"}

        if is_pass and self.value:
            if material.is_a("IfcMaterial"):
                values = {material.Name, getattr(material, "Category", None)}
            elif material.is_a("IfcMaterialList"):
                values = set()
                for mat in material.Materials or []:
                    values.update([mat.Name, getattr(mat, "Category", None)])
            elif material.is_a("IfcMaterialLayerSet"):
                values = {material.LayerSetName}
                for item in material.MaterialLayers or []:
                    values.update(
                        [
                            getattr(item, "Name", None),
                            getattr(item, "Category", None),
                            item.Material.Name,
                            getattr(item.Material, "Category", None),
                        ]
                    )
            elif material.is_a("IfcMaterialProfileSet"):
                values = {material.Name}
                for item in material.MaterialProfiles or []:
                    values.update(
                        [item.Name, item.Category, item.Material.Name, getattr(item.Material, "Category", None)]
                    )
            elif material.is_a("IfcMaterialConstituentSet"):
                values = {material.Name}
                for item in material.MaterialConstituents or []:
                    values.update(
                        [item.Name, item.Category, item.Material.Name, getattr(item.Material, "Category", None)]
                    )

            is_pass = False
            for value in values:
                if value == self.value:
                    is_pass = True
                    break

            if not is_pass:
                reason = {"type": "VALUE", "actual": values}

        if self.cardinality == "prohibited":
            return MaterialResult(not is_pass, {"type": "PROHIBITED"})
        return MaterialResult(is_pass, reason)


class Restriction:
    def __init__(self, options=None, base="string"):
        self.base = base
        self.options = options or {}

    def parse(self, ids_dict):
        if not ids_dict:
            return self
        self.base = ids_dict.get("@base", "xs:string")[3:]
        for key, value in ids_dict.items():
            key = key.split(":")[-1]
            if key in ["@base", "annotation"]:
                continue
            if key == "enumeration" and isinstance(value, dict):
                self.options[key] = [value["@value"]]  # A single enumeration value which is pretty meaningless
            elif isinstance(value, dict):
                self.options[key] = value["@value"]
            else:
                self.options[key] = [v["@value"] for v in value]
        return self

    def asdict(self) -> dict[str, Any]:
        result = {"@base": "xs:" + self.base}
        for constraint, value in self.options.items():
            value = [value] if not isinstance(value, list) else value
            for v in value:
                if constraint in ["length", "minLength", "maxLength"]:
                    value_dict = {"@value": v}
                else:
                    value_dict = {"@value": str(v)}
                result.setdefault(f"xs:{constraint}", []).append(value_dict)
        return result

    def __eq__(self, other):
        if other is None:
            return False
        for constraint, value in self.options.items():
            try:
                if constraint == "enumeration":
                    if other not in [cast_to_value(v, other) for v in value]:
                        return False
                elif constraint == "pattern":
                    if not isinstance(other, str):
                        return False
                    value = value if isinstance(value, list) else [value]
                    for pattern in value:
                        if re.compile(identities.translate_pattern(pattern)).fullmatch(other) is None:
                            return False
                elif constraint == "length":
                    if len(str(other)) != int(value):
                        return False
                elif constraint == "maxLength":
                    if len(str(other)) > int(value):
                        return False
                elif constraint == "minLength":
                    if len(str(other)) < int(value):
                        return False
                elif constraint == "maxExclusive":
                    if float(other) >= float(value):
                        return False
                elif constraint == "maxInclusive":
                    if float(other) > float(value):
                        return False
                elif constraint == "minExclusive":
                    if float(other) <= float(value):
                        return False
                elif constraint == "minInclusive":
                    if float(other) < float(value):
                        return False
            except ValueError:
                return False
        return True

    def __str__(self):
        return str(self.options)


class Result:
    def __init__(self, is_pass: bool, reason: Optional[dict[str, Any]] = None):
        self.is_pass = is_pass
        self.reason = reason

    def __bool__(self):
        return self.is_pass

    def __str__(self):
        return "" if self.is_pass else self.to_string()

    def to_string(self):
        return str(self.reason) or "The requirements were not met for some inexplicable reason. Good luck!"


class EntityResult(Result):
    def to_string(self):
        if self.reason["type"] == "NAME":
            return f"The entity class \"{self.reason['actual']}\" does not meet the required IFC class"
        elif self.reason["type"] == "PREDEFINEDTYPE":
            return f"The predefined type \"{str(self.reason['actual'])}\" does not meet the required type"


class AttributeResult(Result):
    def to_string(self):
        if self.reason["type"] == "NOVALUE":
            return "The required attribute did not exist"
        elif self.reason["type"] == "FALSEY":
            return f"The attribute value \"{str(self.reason['actual'])}\" is empty"
        elif self.reason["type"] == "INVALID":
            return "An invalid attribute name was specified in the IDS"
        elif self.reason["type"] == "VALUE":
            return f"The attribute value \"{str(self.reason['actual'])}\" does not match the requirement"
        elif self.reason["type"] == "PROHIBITED":
            return "The attribute value should not have met the requirement"


class ClassificationResult(Result):
    def to_string(self):
        if self.reason["type"] == "NOVALUE":
            return "The entity has no classification"
        elif self.reason["type"] == "VALUE":
            return f"The references \"{str(self.reason['actual'])}\" do not match the requirements"
        elif self.reason["type"] == "SYSTEM":
            return f"The systems \"{str(self.reason['actual'])}\" do not match the requirements"
        elif self.reason["type"] == "PROHIBITED":
            return "The classification should not have met the requirement"


class PartOfResult(Result):
    def to_string(self):
        if self.reason["type"] == "NOVALUE":
            return "The entity has no relationship"
        elif self.reason["type"] == "ENTITY":
            return f"The entity has a relationship with incorrect entities: \"{str(self.reason['actual'])}\""
        elif self.reason["type"] == "PREDEFINEDTYPE":
            return f"The entity has a relationship with incorrect predefined type: \"{str(self.reason['actual'])}\""
        elif self.reason["type"] == "PROHIBITED":
            return "The relationship should not have met the requirement"


class PropertyResult(Result):
    def to_string(self):
        if self.reason["type"] == "NOPSET":
            return "The required property set does not exist"
        elif self.reason["type"] == "NOVALUE":
            return "The property set does not contain the required property"
        elif self.reason["type"] == "DATATYPE":
            return f"The property's data type \"{str(self.reason['actual'])}\" does not match the required data type of \"{str(self.reason['dataType'])}\""
        elif self.reason["type"] == "VALUE":
            if isinstance(self.reason["actual"], list):
                if len(self.reason["actual"]) == 1:
                    return f"The property value \"{str(self.reason['actual'][0])}\" does not match the requirements"
                else:
                    return f"The property values \"{str(self.reason['actual'])}\" do not match the requirements"
            else:
                return f"The property value \"{str(self.reason['actual'])}\" does not match the requirements"
        elif self.reason["type"] == "PROHIBITED":
            return f"The property should not have met the requirement"


class MaterialResult(Result):
    def to_string(self):
        if self.reason["type"] == "NOVALUE":
            return "The entity has no material"
        elif self.reason["type"] == "VALUE":
            return (
                f"The material names and categories of \"{str(self.reason['actual'])}\" does not match the requirement"
            )
        elif self.reason["type"] == "PROHIBITED":
            return f"The material should not have met the requirement"
