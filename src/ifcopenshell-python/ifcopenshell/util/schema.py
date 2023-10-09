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

import os
import json
import time
import inspect
import types
import importlib
from typing import Any, Optional, Callable, TypeVar
from dataclasses import dataclass, field, fields
from functools import reduce
import ifcopenshell
import ifcopenshell.util.attribute

# This is highly experimental and incomplete, however, it may work for simple datasets.
# In this simple implementation, we only support 2X3<->4 right now

cwd = os.path.dirname(os.path.realpath(__file__))
wrapper = ifcopenshell.ifcopenshell_wrapper
Usecase = TypeVar('Usecase')


def is_a(entity, ifc_class):
    ifc_class = ifc_class.upper()
    if entity.name_uc() == ifc_class:
        return True
    if entity.supertype():
        return is_a(entity.supertype(), ifc_class)
    return False


def get_subtypes(entity):
    def get_classes(declaration):
        results = []
        if not declaration.is_abstract():
            results.append(declaration)
        for subtype in declaration.subtypes():
            results.extend(get_classes(subtype))
        return results

    return get_classes(entity)


def reassign_class(ifc_file, element, new_class):
    """
    Attempts to change the class (entity name) of `element` to `new_class` by
    removing element and recreating a similar instance of type `new_class`
    with the same id.
    
    In certain cases it may affect the structure of inversely related instances:
    - Multiple occurrences of reassigned instance within the same aggregate
      (such as start and end-point of polyline)
    - Occurrences of reassigned instance within an ordered aggregate
      (such as IfcRelNests)
    
    It's unlikely that this affects real-world usage of this function.
    """
    
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema)
    try:
        declaration = schema.declaration_by_name(new_class)
    except:
        raise Exception(f"Class of {element} could not be changed to {new_class} as the class does not exist")

    info = element.get_info()

    new_attributes = {}
    for attribute in declaration.all_attributes():
        name = attribute.name()
        old_attribute = info.get(name, None)
        if old_attribute:
            if ifcopenshell.util.attribute.get_primitive_type(attribute) == "enum":
                if old_attribute in ifcopenshell.util.attribute.get_enum_items(attribute):
                    new_attributes[name] = old_attribute
            else:
                new_attributes[name] = old_attribute

    inverse_pairs = ifc_file.get_inverse(element, allow_duplicate=True, with_attribute_indices=True)
    ifc_file.remove(element)

    try:
        new_element = ifc_file.create_entity(new_class, id=info["id"], **new_attributes)
    except:
        print(f"Class of {element} could not be changed to {new_class}")
        old_class = info.pop("type")
        return ifc_file.create_entity(old_class, **info)

    for inverse_pair in inverse_pairs:
        inverse, index = inverse_pair
        if inverse[index] is None:
            inverse[index] = new_element
        elif isinstance(inverse[index], tuple):
            item = list(inverse[index])
            item.append(new_element)
            inverse[index] = item

    return new_element


class BatchReassignClass:
    def __init__(self, file):
        self.file = file
        self.purge()

    def reassign(self, element, new_class):
        try:
            new_element = self.file.create_entity(new_class)
        except:
            print(f"Class of {element} could not be changed to {new_class}")
            return element
        new_attributes = [new_element.attribute_name(i) for i, attribute in enumerate(new_element)]
        for i, attribute in enumerate(element):
            try:
                new_element[new_attributes.index(element.attribute_name(i))] = attribute
            except:
                continue
        for inverse_pair in self.file.get_inverse(element, allow_duplicate=True, with_attribute_indices=True):
            inverse, index = inverse_pair
            self.replacements.setdefault(inverse, {}).setdefault(index, {})[element] = new_element
        self.to_delete.add(element)
        return new_element

    def unbatch(self):
        for inverse, replacements in self.replacements.items():
            for index, element_map in replacements.items():
                value = inverse[index]
                new = inverse.walk(lambda x : True, lambda v: element_map.get(v, v), value)
                if value != new:
                    inverse[index] = new

        for element in self.to_delete:
            self.file.remove(element)
        self.purge()

    def purge(self):
        self.replacements = {}
        self.to_delete = set()


class Migrator:
    def __init__(self):
        self.migrated_ids = {}
        self.class_4_to_2x3 = json.load(open(os.path.join(cwd, "class_4_to_2x3.json"), "r"))
        self.class_2x3_to_4 = json.load(open(os.path.join(cwd, "class_2x3_to_4.json"), "r"))

        # IFC4 classes, and their IFC4 attribute : IFC2X3 attributes
        self.attribute_4_to_2x3 = json.load(open(os.path.join(cwd, "attribute_4_to_2x3.json"), "r"))

        self.default_values = {
            "ChangeAction": "NOCHANGE",
            "CompositionType": "ELEMENT",
            "CrossSectionArea": 1,
            "DataValue": 0,
            "DefinedValues": [0],
            "DefiningValues": [0],
            "DestabilizingLoad": False,
            "Edition": "",
            "EndParam": 1.0,
            "EnumerationValues": [0],
            "GeodeticDatum": "",
            "Intent": "",
            "IsHeading": False,
            "ListValues": [0],
            "LongitudinalBarCrossSectionArea": 1,
            "LongitudinalBarNominalDiameter": 1,
            "LongitudinalBarSpacing": 1,
            "Name": "",
            "NominalDiameter": 1,
            "PredefinedType": "NOTDEFINED",
            "RowCells": [0],
            "SequenceType": "NOTDEFINED",
            "Source": "",
            "StartParam": 0.0,
            "TransverseBarCrossSectionArea": 1,
            "TransverseBarNominalDiameter": 1,
            "TransverseBarSpacing": 1,
            # Manual additions from experience
            "InteriorOrExteriorSpace": "NOTDEFINED",
            "AssemblyPlace": "NOTDEFINED",  # See bug https://github.com/Autodesk/revit-ifc/issues/395
        }
        self.default_entities = {
            "CurrentValue": None,
            "DepreciatedValue": None,
            "Jurisdiction": None,
            "OriginalValue": None,
            "Owner": None,
            "OwnerHistory": None,
            "Position": None,
            "PropertyReference": None,
            "RepresentationContexts": None,
            "ResponsiblePerson": None,
            "ResponsiblePersons": None,
            "Rows": None,
            "TotalReplacementCost": None,
            "UnitsInContext": None,
            "User": None,
        }

    def migrate(self, element, new_file):
        if element.id() == 0:
            return new_file.create_entity(element.is_a(), element.wrappedValue)
        try:
            return new_file.by_id(self.migrated_ids[element.id()])
        except:
            pass
        # print("Migrating", element)
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(new_file.schema)
        new_element = self.migrate_class(element, new_file)
        # print("Migrated class from {} to {}".format(element, new_element))
        new_element_schema = schema.declaration_by_name(new_element.is_a())
        if not hasattr(new_element_schema, "all_attributes"):
            return element  # The element has no attributes, so migration is done
        new_element = self.migrate_attributes(element, new_file, new_element, new_element_schema)
        self.migrated_ids[element.id()] = new_element.id()
        return new_element

    def migrate_class(self, element, new_file):
        try:
            new_element = new_file.create_entity(element.is_a())
        except:
            # The element does not exist in this schema
            # Complex migration is not yet supported (e.g. polygonal face set to faceted brep)
            if new_file.schema == "IFC2X3":
                new_element = new_file.create_entity(self.class_4_to_2x3[element.is_a()])
            elif new_file.schema == "IFC4":
                new_element = new_file.create_entity(self.class_2x3_to_4[element.is_a()])
        return new_element

    def migrate_attributes(self, element, new_file, new_element, new_element_schema):
        for i, attribute in enumerate(new_element_schema.all_attributes()):
            if new_element_schema.derived()[i]:
                continue
            self.migrate_attribute(attribute, element, new_file, new_element, new_element_schema)
        return new_element

    def migrate_attribute(self, attribute, element, new_file, new_element, new_element_schema):
        # print("Migrating attribute", element, new_element, attribute.name())
        if hasattr(element, attribute.name()):
            value = getattr(element, attribute.name())
            # print("Attribute names matched", value)
        elif new_file.schema == "IFC2X3":
            # IFC4 to IFC2X3: We know the IFC2X3 attribute name, but not its IFC4 equivalent
            # print("Searching for an equivalent", new_element, attribute.name())
            try:
                equivalent_map = self.attribute_4_to_2x3[new_element.is_a()]
                equivalent = list(equivalent_map.keys())[list(equivalent_map.values()).index(attribute.name())]
                if hasattr(element, equivalent):
                    # print("Equivalent found", equivalent)
                    value = getattr(element, equivalent)
                else:
                    return
            except:
                print(
                    "Unable to find equivalent attribute of {} to migrate from {} to {}".format(
                        attribute.name(), element, new_element
                    )
                )
                return  # We tried our best
        elif new_file.schema == "IFC4":
            # IFC2X3 to IFC4: We know the IFC4 attribute name, but not its IFC2X3 equivalent
            # print("Searching for an equivalent", element, new_element, attribute.name())
            try:
                equivalent = self.attribute_4_to_2x3[new_element.is_a()][attribute.name()]
                # print("Searching for equivalent", equivalent)
                if hasattr(element, equivalent):
                    value = getattr(element, equivalent)
                else:
                    return
            except:
                print(
                    "Unable to find equivalent attribute of {} to migrate from {} to {}".format(
                        attribute.name(), element, new_element
                    )
                )
                return  # We tried our best

        # print("Continuing migration of {} to migrate from {} to {}".format(attribute.name(), element, new_element))
        if value is None and not attribute.optional():
            value = self.generate_default_value(attribute, new_file)
            if value is None:
                print("Failed to generate default value for {} on {}".format(attribute.name(), element))
        elif isinstance(value, ifcopenshell.entity_instance):
            value = self.migrate(value, new_file)
        elif isinstance(value, (list, tuple)):
            if value and isinstance(value[0], ifcopenshell.entity_instance):
                new_value = []
                for item in value:
                    new_value.append(self.migrate(item, new_file))
                value = new_value
        if value is not None:
            setattr(new_element, attribute.name(), value)

    def generate_default_value(self, attribute, new_file):
        if attribute.name() in self.default_values:
            return self.default_values[attribute.name()]
        elif attribute.name() == "OwnerHistory":
            self.default_entities[attribute.name()] = new_file.create_entity(
                "IfcOwnerHistory",
                **{
                    "OwningUser": new_file.create_entity(
                        "IfcPersonAndOrganization",
                        **{
                            "ThePerson": new_file.create_entity("IfcPerson"),
                            "TheOrganization": new_file.create_entity(
                                "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
                            ),
                        },
                    ),
                    "OwningApplication": new_file.create_entity(
                        "IfcApplication",
                        **{
                            "ApplicationDeveloper": new_file.create_entity(
                                "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
                            ),
                            "Version": "Works for me",
                            "ApplicationFullName": "IfcOpenShell Migrator",
                            "ApplicationIdentifier": "IfcOpenShell Migrator",
                        },
                    ),
                    "ChangeAction": "NOCHANGE",
                    "CreationDate": int(time.time()),
                },
            )
        return self.default_entities.get(attribute.name(), None)


def pascal_to_snake(txt: str) -> str:
    txt = "".join([f"_{char.lower()}" if char.isupper() else char for char in txt]).lstrip("_")
    return txt[1:] if txt[0] == "_" else txt


def snake_to_pascal(txt: str) -> str:
    return txt.replace("_", " ").title().replace(" ", "")


@dataclass(slots=True)
class AttrsFromSchema:
    """Parses IFC Schema attributes and patches them into an API Usecase, decorated with <with_schema_attrs>"""
    ifc_class: str
    defaults: dict[str, Any] = field(default_factory=dict)
    exclude: list[str] = field(default_factory=list)
    version: str = "IFC4"

    @classmethod
    def patch(cls, usecase: Usecase, version: str = "IFC4") -> None:
        cls(version=version, **usecase.__schema_attrs_def__()).patch_to(usecase)

    def patch_to(self, usecase: Usecase) -> None:
        """Patches IFC Schema applicable attributes into __schema_attr_keys__ and updates Usecase signature"""
        init_method = usecase.__raw_init__ if hasattr(usecase, "__raw_init__") else usecase.__init__
        signature = inspect.signature(init_method)
        parameters: list[inspect.Parameter] = list(signature.parameters.values())
        if hasattr(usecase, "__schema_attr_keys__") and self.ifc_class in usecase.__schema_attr_keys__:
            parameters = [p for p in parameters if p.name not in usecase.__schema_attr_keys__[self.ifc_class]]
        schema_parameters = self.retrieve_parameters()
        parameters.extend(schema_parameters)
        parameters = self.sort_parameters(parameters)
        new_signature = signature.replace(parameters=parameters)
        usecase.__init__.__signature__ = new_signature
        if not hasattr(usecase, "__schema_attr_keys__"):
            setattr(usecase, "__schema_attr_keys__", {})
        usecase.__schema_attr_keys__[self.ifc_class] = [param.name for param in schema_parameters]

    @property
    def schema(self) -> wrapper.schema_definition:
        return wrapper.schema_by_name(self.version)

    def retrieve_parameters(self) -> list[inspect.Parameter]:
        entity = self.schema.declaration_by_name(self.ifc_class)
        parsed_attrs = []
        for attribute in entity.all_attributes():
            if parameter := self.parse_attribute(attribute):
                parsed_attrs.append(parameter)
        return parsed_attrs

    @staticmethod
    def sort_parameters(parameters: list[inspect.Parameter]) -> list[inspect.Parameter]:
        P = inspect.Parameter
        first = (P.POSITIONAL_ONLY, P.POSITIONAL_OR_KEYWORD, P.VAR_POSITIONAL)
        second = (P.KEYWORD_ONLY,)
        third = (P.VAR_KEYWORD,)
        return [param for group in (first, second, third) for param in parameters if param.kind in group]

    def parse_attribute(self, attribute: wrapper.attribute) -> Optional[inspect.Parameter]:
        name_pascal: str = attribute.name()
        name: str = pascal_to_snake(name_pascal)
        if name in self.exclude:
            return
        optional: bool = attribute.optional()
        kind = inspect.Parameter.VAR_KEYWORD if optional else inspect.Parameter.KEYWORD_ONLY
        default = self.defaults[name_pascal] if name_pascal in self.defaults else inspect.Parameter.empty
        type_of_attribute = attribute.type_of_attribute()
        if isinstance(type_of_attribute, wrapper.simple_type):
            annotation = self.parse_simple_type(type_of_attribute)
        elif isinstance(type_of_attribute, wrapper.named_type):
            annotation = self.parse_named_type(type_of_attribute)
        elif isinstance(type_of_attribute, wrapper.aggregation_type):
            annotation = self.parse_aggregation_type(type_of_attribute)
        return inspect.Parameter(name=name, kind=kind, default=default, annotation=annotation)

    @staticmethod
    def parse_simple_type(simple: wrapper.simple_type) -> type | types.UnionType:
        return {
            "string": str,
            "logical": bool | None,
            "boolean": bool,
            "real": float,
            "number": int | float,
            "integer": int,
            "binary": bytes
        }[simple.declared_type()]

    def parse_named_type(self, named: wrapper.named_type) -> type | types.UnionType | types.GenericAlias:
        declared_type = named.declared_type()
        if isinstance(declared_type, wrapper.entity):
            return ifcopenshell.entity_instance
        elif isinstance(declared_type, wrapper.type_declaration):
            return self.parse_type_declaration(declared_type)
        elif isinstance(declared_type, wrapper.select_type):
            return self.parse_select_type(declared_type)
        elif isinstance(declared_type, wrapper.enumeration_type):
            return str

    def parse_type_declaration(
            self, declaration: wrapper.type_declaration
    ) -> type | types.UnionType | types.GenericAlias:

        declared_type = declaration.declared_type()
        if isinstance(declared_type, wrapper.simple_type):
            return self.parse_simple_type(declared_type)
        elif isinstance(declared_type, wrapper.named_type):
            return self.parse_named_type(declared_type)
        elif isinstance(declared_type, wrapper.aggregation_type):
            return self.parse_aggregation_type(declared_type)
        elif isinstance(declared_type, wrapper.type_declaration):
            return self.parse_type_declaration(declared_type)

    def parse_aggregation_type(self, aggregation: wrapper.aggregation_type) -> types.UnionType | types.GenericAlias:
        type_of_element = aggregation.type_of_element()
        type_of_aggregation = aggregation.type_of_aggregation_string()

        if isinstance(type_of_element, wrapper.simple_type):
            element_annotation = self.parse_simple_type(type_of_element)
        elif isinstance(type_of_element, wrapper.named_type):
            element_annotation = self.parse_named_type(type_of_element)
        elif isinstance(type_of_element, wrapper.aggregation_type):
            element_annotation = self.parse_aggregation_type(type_of_element)

        if type_of_aggregation == "list":  # ordered w/o repetition, flexible size
            return list[element_annotation]
        elif type_of_aggregation == "set":  # unordered w/o repetition
            return set[element_annotation]
        elif type_of_aggregation == "array":  # ordered and fixed size
            min_size: int = aggregation.bound1()
            max_size: int = aggregation.bound2()
            annotations = [tuple[(element_annotation, ) * size] for size in (min_size, max_size) if size != -1]
            return reduce(lambda a, b: a | b, annotations)

    def parse_select_type(self, select: wrapper.select_type) -> type | types.UnionType | types.GenericAlias:
        annotations = set()
        for item in select.select_list():
            if isinstance(item, wrapper.entity):
                annotations.add(ifcopenshell.entity_instance)
            elif isinstance(item, wrapper.type_declaration):
                annotations.add(self.parse_type_declaration(item))
            elif isinstance(item, wrapper.select_type):
                annotations.union(set(self.parse_select_type(item).__args__))
        return reduce(lambda a, b: a | b, annotations)


def with_schema_attrs(
        ifc_class: str, defaults: dict[str, Any], exclude: Optional[list[str]] = None
) -> Callable[[Usecase], Usecase]:
    """Decorates an API Usecase dataclass, allowing it to be passed IFC schema attributes"""

    def inner(usecase: Usecase) -> Usecase:
        raw_init = usecase.__init__

        def __init__(self, *args, **kwargs):
            """Wraps a generic signature around the dataclass, allowing for kwargs corresponding to Schema attrs"""
            ref_params = inspect.signature(self.__init__).parameters
            base_params = list(inspect.signature(raw_init).parameters.keys())
            base_kwargs = {key: value for key, value in kwargs.items() if key in base_params}
            other_kwargs = {key: value for key, value in kwargs.items() if key not in base_params}
            for name, param in ref_params.items():
                if name not in other_kwargs and name not in base_params and param.default != inspect.Parameter.empty:
                    other_kwargs[name] = param.default
            raw_init(self, *args, **base_kwargs)
            for key, value in other_kwargs.items():
                setattr(self, key, value)

        @staticmethod
        def __schema_attrs_def__() -> dict[str, Any]:
            """Internal configuration for Schema attribute retrieving"""
            return {"ifc_class": ifc_class, "defaults": defaults, "exclude": exclude or []}

        def schema_attrs(self) -> dict[str, Any]:
            """Actual values of Schema attributes, either defaults or passed to __init__"""
            field_keys = [field.name for field in fields(self)]
            ordinary_keys = list(self.__dict__.keys())
            keys = set(field_keys + ordinary_keys)
            return {
                snake_to_pascal(key): getattr(self, key) for key in keys if key in self.__schema_attr_keys__[ifc_class]
            }

        usecase.__init__ = __init__
        usecase.__init__.__doc__ = usecase.__doc__
        usecase.__schema_attrs_def__ = __schema_attrs_def__
        usecase.schema_attrs = schema_attrs
        usecase.__raw_init__ = raw_init
        return usecase
    return inner


def add_schema_attributes_listener(usecase_path: str, add_pre_listener: Callable) -> None:
    def inner(inner_usecase_path: str, ifc_file: ifcopenshell.file, settings: dict[str, Any]) -> None:
        if inner_usecase_path != usecase_path:
            return
        usecase_module: types.ModuleType = importlib.import_module(f"ifcopenshell.api.{usecase_path}")
        AttrsFromSchema.patch(usecase=usecase_module.Usecase, version=ifc_file.schema)

    add_pre_listener(usecase_path, "with_schema_attributes", inner)
