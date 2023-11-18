from __future__ import annotations
import ast
import os
import inspect
import warnings
from pathlib import Path
from dataclasses import dataclass, field
from functools import reduce
from typing import Optional, Any
import ifcopenshell
from ifcopenshell.api import list_actions

wrapper = ifcopenshell.ifcopenshell_wrapper


def pascal_to_snake(txt: str) -> str:
    txt = "".join([f"_{char.lower()}" if char.isupper() else char for char in txt]).lstrip("_")
    return txt[1:] if txt[0] == "_" else txt


def snake_to_pascal(txt: str) -> str:
    return txt.replace("_", " ").title().replace(" ", "")


def type_to_str(builtin_type: type) -> str:
    candidates: list[str] = [el for el in dir(__builtins__) if getattr(__builtins__, el) == builtin_type]
    if len(candidates) != 1:
        raise ValueError(f"Type {builtin_type} not found on __builtins__")
    return candidates[0]


@dataclass(slots=True)
class AstAnnotation:
    def __call__(self) -> ast.expr:
        ...

    def __or__(self, other: AstAnnotation) -> AstAnnotation:
        if self.__class__.__name__ == other.__class__.__name__ and self == other:
            return self
        return AstAnnotationUnion([self, other])


@dataclass(slots=True)
class AstAnnotationEntityInstance(AstAnnotation):
    def __call__(self) -> ast.Attribute:
        return ast.Attribute(
            value=ast.Name(id="ifcopenshell", ctx=ast.Load()),
            attr="entity_instance",
            ctx=ast.Load()
        )


@dataclass(slots=True)
class AstAnnotationName(AstAnnotation):
    annotation_type: type

    def __call__(self) -> ast.Name:
        return ast.Name(id=type_to_str(self.annotation_type), ctx=ast.Load())


@dataclass(slots=True)
class AstAnnotationConstant(AstAnnotation):
    annotation_value: Any

    def __call__(self) -> ast.Constant:
        return ast.Constant(value=self.annotation_value)


@dataclass(slots=True)
class AstAnnotationAggregation(AstAnnotation):
    aggregation_type: type
    aggregation_content: AstAnnotation

    def __call__(self) -> ast.Subscript:
        return ast.Subscript(
            value=ast.Name(id=type_to_str(self.aggregation_type), ctx=ast.Load()),
            slice=self.aggregation_content(),
            ctx=ast.Load()
        )


@dataclass(slots=True)
class AstAnnotationUnion(AstAnnotation):
    annotations: list[AstAnnotation]
    subscript_name: str = "Union"

    def __call__(self) -> ast.Subscript:
        return ast.Subscript(
            value=ast.Name(id=self.subscript_name, ctx=ast.Load()),
            slice=ast.Tuple(elts=[ann() for ann in self.annotations], ctx=ast.Load()),
            ctx=ast.Load()
        )


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
    def ast_definition(name: str, annotation: AstAnnotation, value: Optional[Any] = None) -> ast.AnnAssign:
        kwargs = {
            "target": ast.Name(id=name, ctx=ast.Store()),
            "annotation": annotation(),
            "simple": 1
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
            annotation = AstAnnotationConstant(Any)
        return self.ast_definition(name, annotation, default)

    @staticmethod
    def parse_simple_type(simple: wrapper.simple_type) -> AstAnnotation:
        return {
            "string": AstAnnotationName(str),
            "logical": AstAnnotationUnion([
                AstAnnotationName(bool),
                AstAnnotationConstant(None)
            ]),
            "boolean": AstAnnotationName(bool),
            "real": AstAnnotationName(float),
            "number": AstAnnotationUnion([
                AstAnnotationName(int),
                AstAnnotationName(float)
            ]),
            "integer": AstAnnotationName(int),
            "binary": AstAnnotationName(bytes)
        }[simple.declared_type()]

    def parse_named_type(self, named: wrapper.named_type) -> AstAnnotation:
        declared_type = named.declared_type()
        if isinstance(declared_type, wrapper.entity):
            return AstAnnotationEntityInstance()
        elif isinstance(declared_type, wrapper.type_declaration):
            return self.parse_type_declaration(declared_type)
        elif isinstance(declared_type, wrapper.select_type):
            return self.parse_select_type(declared_type)
        elif isinstance(declared_type, wrapper.enumeration_type):
            return AstAnnotationName(str)

    def parse_type_declaration(self, declaration: wrapper.type_declaration) -> AstAnnotation:
        declared_type = declaration.declared_type()
        if isinstance(declared_type, wrapper.simple_type):
            return self.parse_simple_type(declared_type)
        elif isinstance(declared_type, wrapper.named_type):
            return self.parse_named_type(declared_type)
        elif isinstance(declared_type, wrapper.aggregation_type):
            return self.parse_aggregation_type(declared_type)
        elif isinstance(declared_type, wrapper.type_declaration):
            return self.parse_type_declaration(declared_type)

    def parse_aggregation_type(self, aggregation: wrapper.aggregation_type) -> AstAnnotation:
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
            element_annotation = AstAnnotationConstant(Any)

        if type_of_aggregation == "list":  # ordered w/o repetition, flexible size
            return AstAnnotationAggregation(list, element_annotation)
        elif type_of_aggregation == "set":  # unordered w/o repetition
            return AstAnnotationAggregation(set, element_annotation)
        elif type_of_aggregation == "array":  # ordered and fixed size
            min_size: int = aggregation.bound1()
            max_size: int = aggregation.bound2()
            return AstAnnotationUnion(
                [AstAnnotationUnion(annotations=[element_annotation for _ in range(size)], subscript_name="tuple")
                 for size in (min_size, max_size) if size != -1]
            )

    def parse_select_type(self, select: wrapper.select_type) -> AstAnnotation:
        annotations: set[AstAnnotation] = set()
        for item in select.select_list():
            if isinstance(item, wrapper.entity):
                annotations.add(AstAnnotationEntityInstance())
            elif isinstance(item, wrapper.type_declaration):
                annotations.add(self.parse_type_declaration(item))
            elif isinstance(item, wrapper.select_type):
                annotations.union({self.parse_select_type(item)})
        return reduce(lambda a, b: a | b, annotations)


@dataclass(slots=True)
class SchemaApiActionBuilder(ast.NodeTransformer):
    module: str
    action: str
    version: str
    api_dir: Path

    def __call__(self) -> str:
        source: str = open(self.source_path, 'r').read()
        tree: ast.Module = ast.parse(source)
        updated_tree: ast.Module = self.visit(tree)
        try:
            updated_source = ast.unparse(updated_tree)
            return f"\n\n{updated_source}\n\n"
        except TypeError:
            print(f"Error unparsing {self.module}.{self.action}")
            return ""

    @property
    def source_path(self) -> Path:
        return self.api_dir / self.module / f"{self.action}.py"

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        attrs_decorator = self.get_schema_attrs_decorator(node)
        if attrs_decorator is None:
            return node

        ifc_class, exclude, defaults = self.parse_decorated_attrs(attrs_decorator)
        attr_parser = SchemaAttrParser(ifc_class=ifc_class, defaults=defaults, exclude=exclude, version=self.version)
        attr_nodes: list[ast.AnnAssign] = attr_parser()

        found_assigns = False
        num_assigns = 0
        for idx, child in enumerate(ast.iter_child_nodes(node)):
            if isinstance(child, ast.AnnAssign):
                found_assigns = True
            if not isinstance(child, ast.AnnAssign) and found_assigns:
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
    api_dir: Path

    def __call__(self) -> None:
        preamble = f"# AUTOGENERATED FILE\n"
        preamble += f"# SCHEMA DEFINITION {self.version}\n\n"
        preamble += f"# WARNING: DO NOT EDIT\n"
        preamble += f"# EDIT ifcopenshell.file.py INSTEAD\n"
        preamble += f"# AND RUN ifcopenshell.api.multischema.py TO REGENERATE\n\n\n\n"

        source: str = open(self.file_path, 'r').read()
        source = preamble + source
        for module, actions in list_actions().items():  # TODO: Use AST to append Usecases as file methods
            for action in actions:
                source += SchemaApiActionBuilder(module, action, self.version, self.api_dir)()
        with open(self.api_dir.parent / f"file_{self.version}.py", "w") as f:
            f.write(source)

    @property
    def file_path(self) -> Path:
        return self.api_dir.parent / "file.py"


if __name__ == "__main__":
    api_dir = Path(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

    for version in ["IFC2X3", "IFC4", "IFC4X3"]:  # TODO: include every version
        SchemaApiBuilder(version=version, api_dir=api_dir)()
