import inspect
import types
import importlib
from typing import Any, Optional, Callable, TypeVar
from dataclasses import dataclass, field, fields
from functools import reduce
import ifcopenshell

wrapper = ifcopenshell.ifcopenshell_wrapper
Usecase = TypeVar('Usecase')


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
        name: str = attribute.name()
        if name in self.exclude:
            return
        optional: bool = attribute.optional()
        kind = inspect.Parameter.VAR_KEYWORD if optional else inspect.Parameter.KEYWORD_ONLY
        default = self.defaults[name] if name in self.defaults else inspect.Parameter.empty
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
            return {key: getattr(self, key) for key in keys if key in self.__schema_attr_keys__[ifc_class]}

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
