import ast
import os
import importlib
import inspect
import warnings
from pathlib import Path
from dataclasses import dataclass, field
from functools import reduce
from typing import Optional, Any, TypeVar
from types import ModuleType, UnionType, GenericAlias
import ifcopenshell
from ifcopenshell.api import list_actions

wrapper = ifcopenshell.ifcopenshell_wrapper


def pascal_to_snake(txt: str) -> str:
    txt = "".join([f"_{char.lower()}" if char.isupper() else char for char in txt]).lstrip("_")
    return txt[1:] if txt[0] == "_" else txt


def snake_to_pascal(txt: str) -> str:
    return txt.replace("_", " ").title().replace(" ", "")


@dataclass(slots=True)
class SchemaAttrParser:
    """Parses IFC Schema attributes"""
    ifc_class: str
    defaults: dict[str, Any] = field(default_factory=dict)
    exclude: list[str] = field(default_factory=list)
    version: str = "IFC4"

    def __call__(self) -> list[ast.AnnAssign]:
        return self.retrieve_parameters()

    @property
    def schema(self) -> wrapper.schema_definition:
        return wrapper.schema_by_name(self.version)

    @staticmethod
    def ast_definition(name: str, annotation: str, value: Optional[Any] = None) -> ast.AnnAssign:
        kwargs = {
            "target": ast.Name(id=name, ctx=ast.Store()),
            "annotation": ast.Name(id=annotation, ctx=ast.Load())
        }
        if value:
            kwargs["value"] = ast.Constant(value=value)
        return ast.AnnAssign(**kwargs)

    def retrieve_parameters(self) -> list[ast.AnnAssign]:
        entity = self.schema.declaration_by_name(self.ifc_class)
        parsed_attrs = []
        for attribute in entity.all_attributes():
            if parameter := self.parse_attribute(attribute):
                parsed_attrs.append(parameter)
        return parsed_attrs

    def parse_attribute(self, attribute: wrapper.attribute) -> Optional[ast.AnnAssign]:
        name_pascal: str = attribute.name()
        name: str = pascal_to_snake(name_pascal)
        if name in self.exclude:
            return
        # optional: bool = attribute.optional()
        default = self.defaults[name_pascal] if name_pascal in self.defaults else None
        type_of_attribute = attribute.type_of_attribute()
        if isinstance(type_of_attribute, wrapper.simple_type):
            annotation = self.parse_simple_type(type_of_attribute)
        elif isinstance(type_of_attribute, wrapper.named_type):
            annotation = self.parse_named_type(type_of_attribute)
        elif isinstance(type_of_attribute, wrapper.aggregation_type):
            annotation = self.parse_aggregation_type(type_of_attribute)
        else:
            warnings.warn(f"Unexpected type of attribute {type(type_of_attribute)}")
            annotation = Any
        return self.ast_definition(name, annotation, default)

    @staticmethod
    def parse_simple_type(simple: wrapper.simple_type) -> type | UnionType:
        return {
            "string": str,
            "logical": bool | None,
            "boolean": bool,
            "real": float,
            "number": int | float,
            "integer": int,
            "binary": bytes
        }[simple.declared_type()]

    def parse_named_type(self, named: wrapper.named_type) -> type | UnionType | GenericAlias:
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
    ) -> type | UnionType | GenericAlias:

        declared_type = declaration.declared_type()
        if isinstance(declared_type, wrapper.simple_type):
            return self.parse_simple_type(declared_type)
        elif isinstance(declared_type, wrapper.named_type):
            return self.parse_named_type(declared_type)
        elif isinstance(declared_type, wrapper.aggregation_type):
            return self.parse_aggregation_type(declared_type)
        elif isinstance(declared_type, wrapper.type_declaration):
            return self.parse_type_declaration(declared_type)

    def parse_aggregation_type(self, aggregation: wrapper.aggregation_type) -> UnionType | GenericAlias:
        type_of_element = aggregation.type_of_element()
        type_of_aggregation = aggregation.type_of_aggregation_string()

        if isinstance(type_of_element, wrapper.simple_type):
            element_annotation = self.parse_simple_type(type_of_element)
        elif isinstance(type_of_element, wrapper.named_type):
            element_annotation = self.parse_named_type(type_of_element)
        elif isinstance(type_of_element, wrapper.aggregation_type):
            element_annotation = self.parse_aggregation_type(type_of_element)
        else:
            warnings.warn(f"Unexpected type of element {type(type_of_element)}")
            element_annotation = Any

        if type_of_aggregation == "list":  # ordered w/o repetition, flexible size
            return list[element_annotation]
        elif type_of_aggregation == "set":  # unordered w/o repetition
            return set[element_annotation]
        elif type_of_aggregation == "array":  # ordered and fixed size
            min_size: int = aggregation.bound1()
            max_size: int = aggregation.bound2()
            annotations = [tuple[(element_annotation, ) * size] for size in (min_size, max_size) if size != -1]
            return reduce(lambda a, b: a | b, annotations)

    def parse_select_type(self, select: wrapper.select_type) -> type | UnionType | GenericAlias:
        annotations = set()
        for item in select.select_list():
            if isinstance(item, wrapper.entity):
                annotations.add(ifcopenshell.entity_instance)
            elif isinstance(item, wrapper.type_declaration):
                annotations.add(self.parse_type_declaration(item))
            elif isinstance(item, wrapper.select_type):
                annotations.union(set(self.parse_select_type(item).__args__))
        return reduce(lambda a, b: a | b, annotations)


@dataclass(slots=True)
class SchemaApiActionBuilder(ast.NodeTransformer):
    module: str
    action: str
    version: str
    output_dir: Path

    def __post_init__(self) -> None:
        python_module: ModuleType = importlib.import_module(f"ifcopenshell.api.{self.module}.{self.action}")
        source: str = inspect.getsource(python_module)
        tree: ast.Module = ast.parse(source)
        updated_tree: ast.Module = self.visit(tree)
        # print(ast.dump(updated_tree, indent=4))
        updated_source = ast.unparse(updated_tree)
        (self.output_dir / self.module).mkdir(exist_ok=True)
        with open(self.output_dir / self.module / f"{self.action}.py", "w") as f:
            f.write(updated_source)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        attrs_decorator = self.get_schema_attrs_decorator(node)
        if attrs_decorator is None:
            return node

        ifc_class, exclude, defaults = self.parse_decorated_attrs(attrs_decorator)
        attr_parser = SchemaAttrParser(ifc_class=ifc_class, defaults=defaults, exclude=exclude, version=self.version)
        attr_nodes: list[ast.AnnAssign] = attr_parser()

        num_assigns = 0
        for idx, child in enumerate(ast.iter_child_nodes(node)):
            if not isinstance(child, ast.AnnAssign):
                num_assigns = idx
                break
        for attr_node in attr_nodes:
            node.body.insert(num_assigns, attr_node)
            num_assigns += 1
        return node

    @staticmethod
    def get_schema_attrs_decorator(node: ast.ClassDef) -> Optional[ast.Call]:
        attrs_decorator: Optional[ast.Call] = None
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Name):
                continue
            if decorator.func.id == "with_schema_attrs":
                attrs_decorator = decorator
                break
        return attrs_decorator

    @staticmethod
    def parse_decorated_attrs(decorator: ast.Call) -> tuple[Optional[str], list[str], dict[str, Any]]:
        ifc_class: Optional[str] = None
        exclude: list[str] = []
        defaults: dict[str, Any] = {}
        for keyword in decorator.keywords:
            if keyword.arg == "ifc_class":
                if not isinstance(keyword.value, ast.Constant):
                    warnings.warn(f"Unexpected ifc_class[{type(keyword.value)}]. Expected ast.Constant")
                    break
                ifc_class = keyword.value.value
            if keyword.arg == "exclude":
                if not isinstance(keyword.value, ast.List):
                    warnings.warn(f"Ignoring exclude[{type(keyword.value)}]. Expected ast.List")
                    continue
                for element in keyword.value.elts:
                    if not isinstance(element, ast.Constant):
                        warnings.warn(f"Ignoring exclude[{type(element)}]. Expected ast.Constant")
                        continue
                    exclude.append(element.value)
            if keyword.arg == "defaults":
                if not isinstance(keyword.value, ast.Dict):
                    warnings.warn(f"Ignoring defaults[{type(keyword.value)}]. Expected ast.Dict")
                    continue
                for key, value in zip(keyword.value.keys, keyword.value.values):
                    if not isinstance(key, ast.Constant):
                        warnings.warn(f"Ignoring default key[{type(key)}]. Expected ast.Constant")
                        continue
                    if not isinstance(value, ast.Constant):
                        warnings.warn(f"Ignoring default value[{type(key)}] for key {key.value}. Expected ast.Constant")
                        continue
                    defaults[key.value] = value.value
        return ifc_class, exclude, defaults


@dataclass(slots=True)
class SchemaApiBuilder:
    version: str
    output_dir: Path

    def __post_init__(self):
        for module, actions in list_actions().items():
            for action in actions:
                SchemaApiActionBuilder(module, action, self.version, self.output_dir)


if __name__ == "__main__":
    api_dir = Path(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

    for version in ["IFC2X3", "IFC4", "IFC4X3"]:  # TODO: include every version
        output_dir = api_dir / version
        output_dir.mkdir(exist_ok=True)
        SchemaApiBuilder(version=version, output_dir=output_dir)
