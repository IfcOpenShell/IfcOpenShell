from __future__ import annotations
import ast
import os
import inspect
from enum import Enum, auto
import warnings
from pathlib import Path
from dataclasses import dataclass, field
from functools import reduce
from typing import cast, Optional, Union, Any
import ifcopenshell
from ifcopenshell.api import list_actions

wrapper = ifcopenshell.ifcopenshell_wrapper


class PythonArgType(Enum):  # See PEP 570 and PEP 3102 for reference
    POS_ONLY = auto()       # positional-only, before / in signature
    POS_OR_KW = auto()      # either positional or keyword argument, Python default
    KW_ONLY = auto()        # keyword-only argument, after * in signature
    VARARG = auto()         # *args, variational positional
    KWARG = auto()          # **kwargs, variational keyword


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


def is_dataclass(node: ast.ClassDef) -> bool:
    return any([dec for dec in node.decorator_list if isinstance(dec, ast.Name) and dec.id == "dataclass"])


@dataclass(slots=True)
class PythonArg:
    argtype: PythonArgType = PythonArgType.POS_OR_KW
    name: Optional[str] = None
    annotation: Optional[AstAnnotation] = None
    default: Optional[Any] = None

    @property
    def ast_arg(self) -> ast.arg:
        arg_data = {"arg": self.name}
        if self.annotation:
            arg_data["annotation"] = self.annotation()
        return ast.arg(**arg_data)

    @property
    def ast_default(self) -> Optional[ast.Constant]:
        return ast.Constant(value=self.default) if self.default else None

    @property
    def ast_annassign(self) -> ast.AnnAssign:
        kwargs = {
            "target": ast.Name(id=self.name, ctx=ast.Store()),
            "simple": 1
        }
        if self.annotation:
            kwargs["annotation"] = self.annotation()
        if self.default:
            kwargs["value"] = ast.Constant(value=self.default)
        return ast.AnnAssign(**kwargs)


@dataclass(slots=True)
class InitArguments:
    posonlyargs: list[ast.arg] = field(default_factory=list)
    args: list[ast.arg] = field(default_factory=list)
    kwonlyargs: list[ast.arg] = field(default_factory=list)
    vararg: Optional[ast.arg] = None
    kwarg: Optional[ast.arg] = None
    defaults: list[ast.expr] = field(default_factory=list)
    kw_defaults: list[Optional[ast.Constant]] = field(default_factory=list)

    @classmethod
    def from_ast_node(cls, init_args: ast.arguments) -> InitArguments:
        return cls(
            posonlyargs=init_args.posonlyargs,
            args=init_args.args,
            kwonlyargs=init_args.kwonlyargs,
            vararg=init_args.vararg,
            kwarg=init_args.kwarg,
            defaults=init_args.defaults,
            kw_defaults=init_args.kw_defaults
        )
    
    def to_ast_node(self) -> ast.arguments:
        return ast.arguments(
            posonlyargs=self.posonlyargs,
            args=self.args,
            kwonlyargs=self.kwonlyargs,
            vararg=self.vararg,
            kwarg=self.kwarg,
            defaults=self.defaults,
            kw_defaults=self.kw_defaults
        )

    def add(self, new_arg: PythonArg) -> None:
        position, default_position = self.resolve_insertion_position(new_arg)

        if new_arg.argtype == PythonArgType.POS_ONLY:
            self.posonlyargs.insert(position, new_arg.ast_arg)
            if new_arg.default:
                self.defaults.insert(default_position, new_arg.ast_default)
        elif new_arg.argtype == PythonArgType.POS_OR_KW:
            self.args.insert(position, new_arg.ast_arg)
            if new_arg.default:
                self.defaults.insert(default_position, new_arg.ast_default)
        elif new_arg.argtype == PythonArgType.KW_ONLY:
            self.kwonlyargs.insert(position, new_arg.ast_arg)
            self.kw_defaults.insert(default_position, new_arg.ast_default)
        elif new_arg.argtype == PythonArgType.VARARG:
            if self.vararg:
                raise ValueError(f"Trying to add {new_arg.name}, but vararg already exists")
            self.vararg = new_arg.ast_arg
        elif new_arg.argtype == PythonArgType.KWARG:
            if self.kwarg:
                raise ValueError(f"Trying to add {new_arg.name}, but kwargs already exists")
            self.kwarg = new_arg.ast_arg

    def resolve_insertion_position(self, new_arg: PythonArg) -> tuple[int, int]:
        position, default_position = -1, -1
        num_defaults = len(self.defaults)
        num_kw_defaults = len(self.kw_defaults)
        num_pos_only = len(self.posonlyargs)
        num_pos_or_kw = len(self.args)
        num_kw_only = len(self.kwonlyargs)
        if new_arg.argtype in (PythonArgType.VARARG, PythonArgType.KWARG):
            raise TypeError(f"*args and **kwargs are single node arguments")
        elif new_arg.argtype == PythonArgType.KW_ONLY:
            if new_arg.default:
                position = num_kw_only
                default_position = num_kw_defaults
            else:
                position = num_kw_only - num_kw_defaults
                default_position = position  # default will be None, and kwarg required
                if position < 0:
                    raise ValueError(f"Invalid number of keyword-only default values")
        elif new_arg.argtype == PythonArgType.POS_OR_KW:
            if new_arg.default:
                position = num_pos_or_kw
                default_position = num_defaults
            else:
                position = num_pos_or_kw - num_defaults
                if position < 0:
                    error_txt = f"Positional or keyword argument {new_arg.name} without default value "
                    error_txt += f"cannot be inserted while positional-only arguments with default exist"
                    raise ValueError(error_txt)
        elif new_arg.argtype == PythonArgType.POS_ONLY:
            if new_arg.default:
                position = num_pos_only
                default_position = num_defaults - num_pos_or_kw
                if default_position < 0:
                    error_txt = f"Positional-only argument {new_arg.name} with default value {new_arg.default} "
                    error_txt += f"cannot be inserted while positional or keyword arguments without default exist"
                    raise ValueError(error_txt)
            else:
                position = num_pos_only - max(num_defaults - num_pos_or_kw, 0)
        return position, default_position


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

    def __call__(self) -> list[PythonArg]:
        return self.retrieve_parameters()

    @property
    def schema(self) -> wrapper.schema_definition:
        return wrapper.schema_by_name(self.version)

    def retrieve_parameters(self) -> list[PythonArg]:
        entity = self.schema.declaration_by_name(self.ifc_class)
        parsed_attrs = []
        for attribute in entity.all_attributes():
            if parameter := self.parse_attribute(attribute):
                parsed_attrs.append(parameter)
        return parsed_attrs

    def parse_attribute(self, attribute: wrapper.attribute) -> Optional[PythonArg]:
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
        return PythonArg(name=name, annotation=annotation, default=default)

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

    @classmethod
    def from_decorator(cls, decorator: ast.Call, version: str = "IFC4") -> SchemaAttrParser:
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
        return cls(ifc_class, defaults, exclude, version)


@dataclass
class SchemaApiActionBuilder(ast.NodeTransformer):
    module: str
    action: str
    version: str
    api_dir: Path
    _signature: Optional[Union[list[ast.AnnAssign], ast.arguments]] = field(init=False, default=None)

    def __call__(self) -> tuple[ast.Module, list[ast.AnnAssign]]:
        source: str = open(self.source_path, 'r').read()
        tree: ast.Module = ast.parse(source)  # TODO: Remove with_attrs_decorator
        updated_tree: ast.Module = ast.fix_missing_locations(self.visit(tree))
        return updated_tree, self._signature

    @property
    def source_path(self) -> Path:
        return self.api_dir / self.module / f"{self.action}.py"

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.name != "Usecase":
            return node

        attrs_decorator = self.get_schema_attrs_decorator(node)
        if attrs_decorator is None:
            return node

        attr_parser = SchemaAttrParser.from_decorator(attrs_decorator, version=self.version)
        schema_args: list[PythonArg] = attr_parser()

        if is_dataclass(node):
            annassigns: list[ast.AnnAssign] = [attr_node.ast_annassign for attr_node in schema_args]
            node, self._signature = self.append_schema_attrs_dataclass(node, annassigns)
        else:
            init_node = self.get_init(node)
            init_arguments = InitArguments.from_ast_node(init_node.args)
            for schema_arg in schema_args:
                init_arguments.add(schema_arg)
            self._signature = init_arguments.to_ast_node()
            init_node.args = self._signature
        return node

    @staticmethod
    def find_assign_idxs_dataclass(node: ast.ClassDef) -> tuple[int, int]:  # TODO: smart parameter insertion like init
        found_assigns = False
        idx_assign_min, idx_assign_max = 0, 0
        for idx, child in enumerate(ast.iter_child_nodes(node)):
            if isinstance(child, ast.AnnAssign):
                idx_assign_min = idx
                found_assigns = True
            elif found_assigns:
                idx_assign_max = idx
                break
        return idx_assign_min, idx_assign_max

    def append_schema_attrs_dataclass(
            self, node: ast.ClassDef, attr_nodes: list[ast.AnnAssign]
    ) -> tuple[ast.ClassDef, list[ast.AnnAssign]]:
        idx_assign_min, idx_assign_max = self.find_assign_idxs_dataclass(node)
        for attr_node in attr_nodes:
            node.body.insert(idx_assign_max, cast(ast.stmt, ast.fix_missing_locations(attr_node)))
            idx_assign_max += 1
        signature = [cast(ast.AnnAssign, node.body[idx]) for idx in range(idx_assign_min, idx_assign_max)]
        return node, signature

    @staticmethod
    def get_init(node: ast.ClassDef) -> ast.FunctionDef:
        inits = [
            child for child in ast.iter_child_nodes(node)
            if isinstance(child, ast.FunctionDef) and child.name == "__init__"
        ]
        if len(inits) != 1:
            raise LookupError(f"{len(inits)} __init__ methods were found")
        return inits[0]

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


@dataclass(slots=True)
class SchemaApiBuilder(ast.NodeTransformer):
    version: str
    api_dir: Path

    def __call__(self) -> None:  # TODO: polish static code generation
        preamble = f"# AUTOGENERATED FILE\n"
        preamble += f"# SCHEMA DEFINITION {self.version}\n\n"
        preamble += f"# WARNING: DO NOT EDIT\n"
        preamble += f"# EDIT ifcopenshell.file.py INSTEAD\n"
        preamble += f"# AND RUN ifcopenshell.api.multischema.py TO REGENERATE\n\n\n\n"

        source: str = open(self.file_path, 'r').read()
        tree: ast.Module = ast.parse(source)
        # print(ast.dump(tree, indent=4))
        # updated_tree: ast.Module = self.visit(tree)

        source = preamble + source
        for module, actions in list_actions().items():
            for action in actions:
                builder = SchemaApiActionBuilder(module, action, self.version, self.api_dir)
                node, signature = builder()
                source += ast.unparse(node)

        with open(self.api_dir.parent / f"file_{self.version}.py", "w") as f:
            f.write(source)

    @property
    def file_path(self) -> Path:
        return self.api_dir.parent / "file.py"

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        pass


if __name__ == "__main__":
    api_dir = Path(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

    for version in ["IFC2X3", "IFC4", "IFC4X3"]:  # TODO: include every version
        SchemaApiBuilder(version=version, api_dir=api_dir)()

