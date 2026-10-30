# This file was generated with the assistance of an AI coding tool.
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Small AST pattern matcher; target-language knowledge lives in the selected YAML rules."""

import argparse
import ast
import copy
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined, pass_context

PACKAGE = Path(__file__).parent.parent / "ifcopenshell-python" / "ifcopenshell"


def match(pattern, value, captures):
    if isinstance(pattern, str) and pattern.startswith("$"):
        key = pattern[1:]
        if key in captures:
            describe = lambda v: ast.dump(v) if isinstance(v, ast.AST) else repr(v)
            return describe(value) == describe(captures[key])
        captures[key] = value
        return True
    if isinstance(pattern, dict):
        return isinstance(value, ast.AST) and all(
            type(value).__name__ == expected
            if key == "node"
            else hasattr(value, key) and match(expected, getattr(value, key), captures)
            for key, expected in pattern.items()
        )
    if isinstance(pattern, list):
        return (
            isinstance(value, list)
            and len(pattern) == len(value)
            and all(match(p, v, captures) for p, v in zip(pattern, value))
        )
    return pattern == value


def module_name(path, package=PACKAGE):
    """Python module path relative to ifcopenshell, e.g. util.unit or api.root.create_entity."""
    return ".".join(path.relative_to(package).with_suffix("").parts)


def build_index(package=PACKAGE):
    """Top-level functions and module data of ifcopenshell.util and ifcopenshell.api, by qualified name."""
    index = {}
    for path in sorted([*package.glob("util/*.py"), *package.glob("api/*/*.py")]):
        if path.stem == "__init__":
            continue
        name = module_name(path, package)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                index[f"{name}.{node.name}"] = node
                # Usecases are re-exported by their package: ifcopenshell.api.root.create_entity.
                if name.startswith("api.") and node.name == path.stem:
                    index[f"{name.rsplit('.', 1)[0]}.{node.name}"] = node
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                for target in node.targets if isinstance(node, ast.Assign) else [node.target]:
                    if isinstance(target, ast.Name):
                        index[f"{name}.{target.id}"] = None
            elif isinstance(node, ast.ClassDef):
                # Classes are constructed with `new`; NamedTuples and TypedDicts are not classes in TS.
                special = any(ast.unparse(b).endswith(("NamedTuple", "TypedDict")) for b in node.bases)
                index[f"{name}.{node.name}"] = None if special else node
    return index


TYPE_NAMES = {"Union", "Optional", "tuple", "list", "dict", "set", "Literal", "Callable", "Sequence", "Iterable", "Any"}


def is_type(node):
    """Whether a module-level value is a type expression (an implicit type alias)."""
    if isinstance(node, ast.Subscript):
        return isinstance(node.value, ast.Name) and node.value.id in TYPE_NAMES or ast.unparse(node.value) in ("npt.NDArray", "NDArray")
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return all(is_type(n) or is_type_name(n) or isinstance(n, ast.Constant) and n.value is None for n in (node.left, node.right))
    return False


def is_type_name(node):
    """A bare type used in a union: builtins and ifcopenshell classes."""
    if isinstance(node, ast.Name):
        return node.id in {"float", "int", "str", "bool", "bytes", "object", "dict", "list", "set", "tuple", "entity_instance"}
    return isinstance(node, ast.Attribute) and node.attr in {"entity_instance", "file"}


def is_dataclass(node):
    return any(ast.unparse(d.func if isinstance(d, ast.Call) else d) in ("dataclass", "dataclasses.dataclass") for d in node.decorator_list)


def static_classmethods(tree):
    """Classmethods become static methods whose `cls` is the class itself (`this` in a TS static method)."""
    for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        for method in [m for m in cls.body if isinstance(m, ast.FunctionDef)]:
            if any(ast.unparse(d) == "classmethod" for d in method.decorator_list) and method.args.args:
                first = method.args.args[0].arg
                method.args.args = method.args.args[1:]
                method.decorator_list = [ast.Name("staticmethod", ast.Load()) if ast.unparse(d) == "classmethod" else d for d in method.decorator_list]
                for node in ast.walk(method):
                    if isinstance(node, ast.Name) and node.id == first:
                        node.id = cls.name


def untyped_overloads(tree):
    """Implementations of @overload functions return any: their union return type is narrowed per call in Python."""
    for body in [tree.body] + [n.body for n in tree.body if isinstance(n, ast.ClassDef)]:
        overloaded = {
            n.name
            for n in body
            if isinstance(n, ast.FunctionDef) and any(ast.unparse(d) in ("overload", "typing.overload") for d in n.decorator_list)
        }
        for n in body:
            if isinstance(n, ast.FunctionDef) and n.name in overloaded:
                n.returns = None


def flatten_type_checking(body):
    """Module statements with `if TYPE_CHECKING:` blocks (imports and type aliases) inlined; their else branches dropped."""
    return [
        statement
        for node in body
        for statement in (
            node.body if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING" else [node]
        )
    ]


def value_path(node):
    """Key of a dict value in symbols: `d[]` for d[k], d.get(k) and d.setdefault(k, v); `d[][]` one level down."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return f"self.{node.attr}"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("get", "setdefault", "pop"):
        inner = value_path(node.func.value)
        return f"{inner}[]" if inner else None
    if isinstance(node, ast.Subscript):
        inner = value_path(node.value)
        return f"{inner}[]" if inner else None
    return None


def camel(name):
    """snake_case to camelCase; CONSTANT_CASE and leading underscores are kept."""
    stripped = name.lstrip("_")
    if not stripped or stripped.upper() == stripped:
        return name
    head, *rest = stripped.split("_")
    return name[: len(name) - len(stripped)] + head + "".join(part[:1].upper() + part[1:] for part in rest)


class Transpiler:
    def __init__(self, rules, index=None, precomputed=None):
        self.rules = yaml.safe_load(Path(rules).read_text(encoding="utf-8"))
        self.index = index or {}
        self.precomputed = precomputed or {}
        self.module = None
        self.scope = {}
        self.depth = 0
        self.unsupported = []
        self.functions = {}
        self.classes = {}
        self.current_class = None
        self.symbols = {}
        self.aliases = {}
        self.imports = {}
        self.import_aliases = {}
        self.runtime_names = {}
        self.type_aliases = {}
        self.reassigned = set()
        self.typed_dicts = set()
        self.nested = {}
        self.globals = set()
        self.shadowed = set()
        self.return_annotation = None
        self.generator = False
        self.loops = []
        self.declared = []
        self.env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
        self.cache = {}
        self.env.tests["startswith"] = lambda value, prefix: str(value).startswith(prefix)
        self.env.filters.update(
            emit=self.emit,
            emit_in=lambda n, context: self.emit(n, context=context),
            type=lambda n: self.emit(n, "types"),
            kind=lambda n: self.emit(n, "inference"),
            condition=lambda n: self.emit(n, context="condition"),
            iterable=lambda n: self.emit(n, context="iterable"),
            literal=json.dumps,
            is_generator=self.is_generator,
            source=lambda n: ast.unparse(n.func if isinstance(n, ast.Call) else n),
            path=value_path,
            code=ast.unparse,
            module_alias=lambda name: self.import_aliases.get(name),
            camel=camel,
            is_type=is_type,
            ident=lambda name: f"{name}_" if name in self.rules.get("reserved", ()) else name,
            resolve=self.resolve,
            defining_module=self.defining_module,
            signature=self.signature,
            bind=self.bind,
            runtime_path=self.runtime_path,
            alias_value=self.alias_value,
            api_run=self.api_run,
            is_class=self.is_class,
            is_static=self.is_static,
            # Context-dependent, so Jinja does not constant-fold it into a cached template.
            use=pass_context(lambda _, module, alias=None: self.use(module, alias)),
        )

    def compiled(self, source, expression=False):
        """Rule templates and conditions are compiled once."""
        key = (source, expression)
        if key not in self.cache:
            self.cache[key] = self.env.compile_expression(source) if expression else self.env.from_string(source)
        return self.cache[key]

    def render(self, template, captures):
        return self.compiled(template).render(self.context(captures))

    def context(self, captures):
        return dict(
            self.rules,
            functions=self.functions,
            classes=self.classes,
            current_class=self.current_class,
            symbols=self.symbols,
            aliases=self.aliases,
            this_module=self.module,
            module_globals=self.globals,
            shadowed=self.shadowed,
            return_annotation=self.return_annotation,
            generator=self.generator,
            break_label=self.loops[-1] if self.loops else None,
            declared=self.declared,
            runtime_names=self.runtime_names,
            reassigned=self.reassigned,
            typed_dicts=self.typed_dicts,
            # Python operators may dispatch to runtime objects (arrays, dates) in this module.
            overloading=any(m in self.rules.get("overloading_modules", ()) for m, _ in self.runtime_names.values()),
            **captures,
        )

    def api_run(self, call):
        """`ifcopenshell.api.run("package.usecase", file, **settings)` as a direct call of the usecase, or None."""
        package, _, usecase = call.args[0].value.partition(".")
        if f"api.{package}.{usecase}" not in self.index:
            return None
        api = ast.Attribute(value=ast.Name("ifcopenshell", ast.Load()), attr="api", ctx=ast.Load())
        func = ast.Attribute(value=ast.Attribute(value=api, attr=package, ctx=ast.Load()), attr=usecase, ctx=ast.Load())
        return ast.Call(func=func, args=call.args[1:], keywords=call.keywords, lineno=call.lineno)

    def alias_value(self, node):
        """The type expression a module-level type alias (`MatrixType = npt.NDArray[...]`) names, or None."""
        if not isinstance(node, (ast.Name, ast.Attribute)):
            return None
        qualified = self.resolve(node)
        if not qualified:
            return None
        module, name = qualified.rsplit(".", 1)
        if module not in self.type_aliases:
            path = PACKAGE.joinpath(*module.split(".")).with_suffix(".py")
            tree = ast.parse(path.read_text(encoding="utf-8")) if path.exists() else ast.Module(body=[])
            self.type_aliases[module] = {
                n.targets[0].id: n.value
                for n in flatten_type_checking(tree.body)
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and is_type(n.value)
            }
        return self.type_aliases[module].get(name)

    def runtime_path(self, node):
        """{"module", "parts"} of a name or attribute chain rooted at an import of a runtime module, or None."""
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if not isinstance(node, ast.Name) or node.id in self.shadowed or node.id not in self.runtime_names:
            return None
        module, member = self.runtime_names[node.id]
        return {"module": module, "parts": ([member] if member else []) + parts[::-1]}

    def resolve(self, node):
        """Qualified name (relative to ifcopenshell) of a module-level function or value, or None."""
        if isinstance(node, ast.Name):
            if node.id in self.shadowed:
                return None
            if node.id in self.import_aliases:
                return self.import_aliases[node.id]
            if node.id in self.globals and self.module:
                return f"{self.module}.{node.id}"
            return None
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if not isinstance(node, ast.Name) or node.id in self.shadowed:
            return None
        root = self.import_aliases.get(node.id, "" if node.id == "ifcopenshell" else None)
        if root is None:
            return None
        qualified = ".".join(filter(None, [root, *reversed(parts)]))
        return qualified if qualified in self.index or qualified.rsplit(".", 1)[0] in self.packages() else None

    def packages(self):
        return {name.rsplit(".", 1)[0] for name in self.index}

    def method(self, class_name, name):
        """A method of a module class (or ClassDef), with its self parameter removed."""
        cls = class_name if isinstance(class_name, ast.ClassDef) else self.classes[class_name]
        if name == "__init__" and is_dataclass(cls) and not any(isinstance(i, ast.FunctionDef) and i.name == name for i in cls.body):
            # The generated constructor: fields without defaults are required, in order.
            fields = [i for i in cls.body if isinstance(i, ast.AnnAssign) and isinstance(i.target, ast.Name)]
            required = [f for f in fields if f.value is None]
            optional = [f for f in fields if f.value is not None]
            arguments = ast.arguments(
                posonlyargs=[], args=[ast.arg(f.target.id, f.annotation) for f in required + optional], vararg=None,
                kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[f.value for f in optional],
            )
            return ast.FunctionDef(name="__init__", args=arguments, body=[], decorator_list=[], returns=None)
        for item in cls.body:
            if isinstance(item, ast.FunctionDef) and item.name == name:
                if any(ast.unparse(d) == "staticmethod" for d in item.decorator_list):
                    return item
                method = copy.copy(item)
                method.args = copy.copy(item.args)
                method.args.args = item.args.args[1:]
                return method
        return None

    def signature(self, node):
        """FunctionDef of a resolvable callee: local, a method of a module class, or in the index."""
        if isinstance(node, ast.Name) and node.id in self.nested:
            return self.nested[node.id]
        if isinstance(node, ast.Name) and node.id in self.functions and node.id not in self.shadowed:
            return self.functions[node.id]
        if isinstance(node, ast.Name) and node.id in self.classes and node.id not in self.shadowed:
            return self.method(node.id, "__init__")
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            owner = self.current_class if node.value.id == "self" else None
            kind = self.symbols.get(node.value.id, "")
            if owner is None and kind.startswith("class:"):
                owner = kind.removeprefix("class:")
            if owner in self.classes:
                return self.method(owner, node.attr)
        qualified = self.resolve(node)
        found = self.index.get(qualified) if qualified else None
        if isinstance(found, ast.ClassDef):
            return self.method(found, "__init__") or ast.FunctionDef(name="__init__", args=ast.arguments([], [], None, [], [], None, []), body=[], decorator_list=[], returns=None)
        return found

    def is_static(self, node):
        """Whether a callee is `self.method` for a static method of the current class."""
        if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"):
            return False
        cls = self.classes.get(self.current_class)
        return cls is not None and any(
            isinstance(i, ast.FunctionDef) and i.name == node.attr and any(ast.unparse(d) == "staticmethod" for d in i.decorator_list)
            for i in cls.body
        )

    def is_class(self, node):
        """Whether a callee is a class of another util or api module."""
        qualified = self.resolve(node)
        return isinstance(self.index.get(qualified), ast.ClassDef) if qualified else False

    def bind(self, call, function):
        """Bind call arguments to parameters with Python semantics.

        Returns {"positional": [arg nodes for required parameters], "options": [(name, node)],
        "error": reason or None}. Parameters with defaults and keyword-only parameters are options.
        """
        parameters = function.args.posonlyargs + function.args.args
        required = parameters[: len(parameters) - len(function.args.defaults)]
        positional, options = [], []
        if function.args.vararg and not function.args.defaults and not function.args.kwonlyargs and not call.keywords:
            # def f(a, *args): every argument is positional; starred ones are spread.
            if len(call.args) < len(parameters) or any(isinstance(a, ast.Starred) for a in call.args[: len(parameters)]):
                return {"positional": [], "options": [], "error": "variadic call"}
            return {"positional": list(call.args), "options": [], "error": None}
        starred = [a for a in call.args if isinstance(a, ast.Starred)]
        if starred == call.args[-1:] and not function.args.vararg and not call.keywords and len(call.args) > len(required):
            # f(a, *rest): rest fills the optional parameters after a, as an options object built at runtime.
            head = call.args[:-1]
            names = [ast.Constant(p.arg) for p in parameters[len(head) :]]
            spread = ast.Call(ast.Name("__positional_options__", ast.Load()), [ast.List(names, ast.Load()), starred[0].value], [])
            result = self.bind(ast.Call(call.func, head, []), function)
            if result["error"] is None:
                result["options"].append((None, spread))
            return result
        if starred and starred == call.args[-1:] and len(parameters) == len(required) and not function.args.vararg and not function.args.kwonlyargs and not call.keywords:
            # f(*xy) for def f(x, y): the starred value fills the remaining parameters, as a tuple of that length.
            head = call.args[:-1]
            count = ast.Constant(len(required) - len(head))
            return {"positional": head + [ast.Starred(ast.Call(ast.Name("__fixed_tuple__", ast.Load()), [starred[0].value, count], []), ast.Load())], "options": [], "error": None}
        if function.args.vararg or starred:
            return {"positional": [], "options": [], "error": "variadic call"}
        if len(call.args) > len(parameters):
            return {"positional": [], "options": [], "error": "too many arguments"}
        given = dict(zip((p.arg for p in parameters), call.args))
        for keyword in call.keywords:
            if keyword.arg == "should_run_listeners" and "should_run_listeners" not in [a.arg for a in parameters + function.args.kwonlyargs]:
                continue  # Accepted by ifcopenshell.api's wrapper, not by the usecase; there are no listeners in TS.
            if keyword.arg is None:
                return {"positional": [], "options": [], "error": "**kwargs call"}
            given[keyword.arg] = keyword.value
        for parameter in required:
            if parameter.arg not in given:
                return {"positional": [], "options": [], "error": f"missing {parameter.arg}"}
            positional.append(given.pop(parameter.arg))
        optional = [p.arg for p in parameters[len(required) :]] + [a.arg for a in function.args.kwonlyargs]
        for name in optional:
            if name in given:
                options.append((name, given.pop(name)))
        if given and not function.args.kwarg:
            return {"positional": [], "options": [], "error": f"unknown argument {next(iter(given))}"}
        options += list(given.items())
        return {"positional": positional, "options": options, "error": None}

    @staticmethod
    def is_generator(function):
        """Whether a function body yields, ignoring nested functions and lambdas."""
        pending = list(function.body)
        while pending:
            node = pending.pop()
            if isinstance(node, (ast.Yield, ast.YieldFrom)):
                return True
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                pending.extend(ast.iter_child_nodes(node))
        return False

    def defining_module(self, qualified):
        """Module that defines a qualified function: an API usecase's own file rather than its package."""
        module, name = qualified.rsplit(".", 1)
        return f"{module}.{name}" if f"{module}.{name}.{name}" in self.index else module

    def foreign_names(self, tree):
        """Names bound by imports of modules other than ifcopenshell, which generated code drops."""
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {(a.asname or a.name).split(".")[0] for a in node.names if not a.name.startswith("ifcopenshell")}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and not node.module.startswith("ifcopenshell"):
                supported = set(self.rules.get("type_only_modules", ())) | set(self.rules.get("supported_modules", ()))
                if node.module not in supported:
                    names |= {a.asname or a.name for a in node.names}
        return names - set(self.rules.get("supported_modules", ())) - set(self.runtime_names)

    def check_foreign(self, node, foreign):
        """Reject code that uses a dropped import, rather than emit a reference that fails at runtime."""
        bound = {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        # isinstance(x, datetime.date) is translated without the module.
        type_positions = {
            id(n)
            for call in ast.walk(node)
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "isinstance" and len(call.args) == 2
            for n in ast.walk(call.args[1])
        }
        # Annotations become TS types, so modules used only there are not needed at runtime.
        annotations = [n.annotation for n in ast.walk(node) if isinstance(n, (ast.arg, ast.AnnAssign)) and n.annotation]
        annotations += [n.returns for n in ast.walk(node) if isinstance(n, ast.FunctionDef) and n.returns]
        type_positions |= {id(n) for annotation in annotations for n in ast.walk(annotation)}
        for name in ast.walk(node):
            if id(name) in type_positions:
                continue
            if isinstance(name, ast.Name) and isinstance(name.ctx, ast.Load) and name.id in foreign - bound:
                raise ValueError(f"No rules rule at line {name.lineno}: uses module {name.id}")

    def annotate(self, name, annotation, values_only=False):
        """Record the kind of an annotated name, and of its values (`name[]`) for dict[K, V]."""
        if not values_only:
            self.symbols[name] = self.emit(annotation, "annotation_kinds")
        if (
            isinstance(annotation, ast.Subscript)
            and isinstance(annotation.value, ast.Name)
            and annotation.value.id in ("dict", "defaultdict")
            and isinstance(annotation.slice, ast.Tuple)
        ):
            self.annotate(f"{name}[]", annotation.slice.elts[1])

    def use(self, qualified_module, alias=None):
        """Record an import of another module and return its local alias."""
        alias = alias or qualified_module.replace(".", "_")
        if qualified_module != self.module:
            self.imports[qualified_module] = alias
        return alias

    def emit(self, node, mode="rules", context="expression"):
        if isinstance(node, list):
            return "\n".join(filter(None, (self.emit(n, mode) for n in node)))
        for rule in self.rules[mode]:
            if rule.get("context", "expression") != context:
                continue
            captures = {"node": node, "top_level": self.depth == 0}
            if match(rule["input"], node, captures) and all(
                isinstance(captures[name], ast.Name) and self.scope.get(captures[name].id) == expected
                for name, expected in rule.get("where", {}).items()
            ):
                if "when" in rule and not self.compiled(rule["when"], expression=True)(**self.context(captures)):
                    continue
                if isinstance(node, (ast.FunctionDef, ast.Lambda)):
                    # Binding discovery is shared by targets; declaration syntax remains in YAML.
                    bindings = {
                        n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
                    }
                    # Names declared nonlocal or global refer to the enclosing scope's variable.
                    bindings -= {
                        name for n in ast.walk(node) if isinstance(n, (ast.Nonlocal, ast.Global)) for name in n.names
                    }
                    nested = {n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef) and n is not node}
                    arguments = node.args
                    parameters = {
                        a.arg
                        for a in arguments.posonlyargs + arguments.args + arguments.kwonlyargs
                        + [a for a in (arguments.vararg, arguments.kwarg) if a]
                    }
                    captures["locals"] = sorted(bindings - parameters - set(self.declared))
                    previous = self.shadowed
                    self.shadowed = previous | bindings | parameters | nested
                    # Functions defined inside this one, for binding calls to them.
                    outer_nested = self.nested
                    self.nested = {**{k: v for k, v in outer_nested.items() if k not in bindings | parameters}, **{
                        n.name: n for n in ast.walk(node) if isinstance(n, ast.FunctionDef) and n is not node
                    }}
                outer_class = self.current_class
                outer_generator = self.generator
                loop = isinstance(node, (ast.For, ast.While))
                if loop:
                    # A loop with an else clause is a labelled block; break leaves the block.
                    captures["label"] = f"loop{node.lineno}" if node.orelse else None
                    self.loops.append(captures["label"])
                elif isinstance(node, (ast.FunctionDef, ast.Lambda)):
                    outer_loops, self.loops = self.loops, []
                if isinstance(node, ast.ClassDef):
                    self.current_class = node.name
                if isinstance(node, (ast.FunctionDef, ast.Lambda)):
                    self.generator = isinstance(node, ast.FunctionDef) and self.is_generator(node)
                self.depth += 1
                try:
                    return self.render(rule["output"], captures)
                finally:
                    self.depth -= 1
                    self.current_class = outer_class
                    self.generator = outer_generator
                    if loop:
                        self.loops.pop()
                    elif isinstance(node, (ast.FunctionDef, ast.Lambda)):
                        self.loops = outer_loops
                    if isinstance(node, (ast.FunctionDef, ast.Lambda)):
                        self.shadowed = previous
                        self.nested = outer_nested
        code = ast.unparse(node) if isinstance(node, ast.AST) else repr(node)
        raise ValueError(f"No {mode} rule at line {getattr(node, 'lineno', '?')}: {code[:180]}")

    def discover_imports(self, module):
        """Local names bound by imports of other ifcopenshell modules."""
        self.import_aliases = {}
        self.runtime_names = {}
        runtime = self.rules.get("runtime_modules", {})
        for node in ast.walk(module):
            # Python modules with a hand-written TypeScript counterpart: local name -> (module, member).
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in runtime and (alias.asname or "." not in alias.name) and runtime[alias.name].get("plain_import", True):
                        self.runtime_names[alias.asname or alias.name] = (alias.name, None)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module in runtime:
                for alias in node.names:
                    self.runtime_names[alias.asname or alias.name] = (node.module, alias.name)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname and alias.name.startswith("ifcopenshell."):
                        self.import_aliases[alias.asname] = alias.name.removeprefix("ifcopenshell.")
            elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("ifcopenshell."):
                for alias in node.names:
                    qualified = f"{node.module.removeprefix('ifcopenshell.')}.{alias.name}"
                    self.import_aliases[alias.asname or alias.name] = qualified

    def translate(self, source, module=None):
        self.module = module
        tree = ast.parse(source)
        static_classmethods(tree)
        untyped_overloads(tree)
        tree.body = flatten_type_checking(tree.body)
        self.functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        named_tuples = {
            n.name
            for n in tree.body
            if isinstance(n, ast.ClassDef) and any(ast.unparse(b) in ("NamedTuple", "typing.NamedTuple") for b in n.bases)
        }
        typed_dicts = {
            n.name
            for n in tree.body
            if isinstance(n, ast.ClassDef) and any(ast.unparse(b).endswith("TypedDict") for b in n.bases)
        }
        self.classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef) and n.name not in named_tuples | typed_dicts}
        self.typed_dicts = typed_dicts
        self.globals = set(self.functions) | named_tuples | {
            t.id
            for n in tree.body
            if isinstance(n, (ast.Assign, ast.AnnAssign))
            for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
            if isinstance(t, ast.Name)
        }
        self.discover_imports(tree)
        self.aliases = {
            n.targets[0].id: [e.value for e in n.value.slice.elts]
            for n in tree.body
            if isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Subscript)
            and isinstance(n.value.value, ast.Name)
            and n.value.value.id == "Literal"
        }
        # Module-level names assigned more than once (e.g. a default, then data read in a with block).
        assigned = [
            n.id
            for statement in tree.body
            if not isinstance(statement, (ast.FunctionDef, ast.ClassDef))
            for n in ast.walk(statement)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
        ]
        self.reassigned = {name for name in assigned if assigned.count(name) > 1} | {
            name for n in ast.walk(tree) if isinstance(n, ast.Global) for name in n.names
        }
        self.unsupported = []
        self.symbols = {}
        self.imports = {}
        foreign = self.foreign_names(tree)
        output = []
        for node in tree.body:
            functions = [node] if isinstance(node, ast.FunctionDef) else []
            if isinstance(node, ast.ClassDef):
                functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            self.scope = {
                a.arg: ast.unparse(a.annotation)
                for f in functions
                for a in f.args.args + f.args.kwonlyargs
                if a.annotation
            }
            globals_ = self.symbols.copy()
            imports = dict(self.imports)
            self.declared = []
            self.shadowed = set()
            self.return_annotation = node.returns if isinstance(node, ast.FunctionDef) else None
            if isinstance(node, ast.ClassDef):
                # Annotated attributes, at class level or as self.x: T in methods.
                for n in ast.walk(node):
                    if isinstance(n, ast.AnnAssign) and (
                        n in node.body and isinstance(n.target, ast.Name)
                        or isinstance(n.target, ast.Attribute) and isinstance(n.target.value, ast.Name) and n.target.value.id == "self"
                    ):
                        self.annotate(f"self.{n.target.id if isinstance(n.target, ast.Name) else n.target.attr}", n.annotation)
            for n in ast.walk(node):
                if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
                    self.annotate(n.target.id, n.annotation, values_only=True)
            for function in functions:
                self.symbols.update(
                    {
                        a.arg: self.emit(a.annotation, "annotation_kinds")
                        for a in function.args.args + function.args.kwonlyargs
                    }
                )
            # Resolve local data shapes without embedding target-language decisions here.
            bindings = [n for n in ast.walk(node) if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr))]
            for _ in range(len(bindings) + 1):
                previous = self.symbols.copy()
                seen = {}
                for binding in bindings:
                    value = binding.value
                    if value is None:
                        continue
                    kind = self.emit(value, "inference")
                    if isinstance(binding, ast.AnnAssign):
                        # The annotation decides where the value does not; dict[int, X] makes {} a Map.
                        annotated = self.emit(binding.annotation, "annotation_kinds")
                        if kind == "unknown" or kind == "dict" and annotated == "map":
                            kind = annotated
                    targets = binding.targets if isinstance(binding, ast.Assign) else [binding.target]
                    if kind == "unknown" and not (isinstance(value, ast.Constant) and value.value is None):
                        for target in targets:
                            if isinstance(target, ast.Name):
                                seen.setdefault(target.id, set()).add("unknown")
                    for target in targets:
                        # An empty {} does not make a non-string-keyed dict a string-keyed one.
                        if isinstance(target, ast.Name) and kind != "unknown" and not (kind == "dict" and self.symbols.get(target.id) == "map"):
                            self.symbols[target.id] = kind
                            seen.setdefault(target.id, set()).add(kind)
                # A name bound to values of different kinds (a dict here, a list there) has no single kind.
                for name, kinds in seen.items():
                    if len(kinds - {"dict"} if "map" in kinds else kinds) > 1:
                        self.symbols[name] = "unknown"
                # A dict indexed by tuples or entities needs non-string keys.
                for subscript in ast.walk(node):
                    if (
                        isinstance(subscript, ast.Subscript)
                        and isinstance(subscript.value, ast.Name)
                        and self.symbols.get(subscript.value.id) in ("dict", None, "unknown")
                        and (
                            isinstance(subscript.slice, ast.Tuple)
                            or self.emit(subscript.slice, "inference") in ("entity", "number")
                        )
                        and self.symbols.get(subscript.value.id) == "dict"
                    ):
                        self.symbols[subscript.value.id] = "map"
                # Likewise d.setdefault(entity, ...) and d.get(entity).
                for call in ast.walk(node):
                    if (
                        isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Attribute)
                        and call.func.attr in ("setdefault", "get", "pop")
                        and isinstance(call.func.value, ast.Name)
                        and self.symbols.get(call.func.value.id) == "dict"
                        and call.args
                        and (isinstance(call.args[0], ast.Tuple) or self.emit(call.args[0], "inference") in ("entity", "number"))
                    ):
                        self.symbols[call.func.value.id] = "map"
                # Loop variables over an annotated dict's values: for k, v in d.items() and for v in d.values().
                for loop in ast.walk(node):
                    if isinstance(loop, ast.For) and isinstance(loop.iter, ast.Call) and isinstance(loop.iter.func, ast.Attribute):
                        method, target = loop.iter.func.attr, loop.target
                        if method == "items" and isinstance(target, ast.Tuple) and len(target.elts) == 2:
                            target = target.elts[1]
                        elif method != "values":
                            continue
                        prefix = f"{value_path(loop.iter.func.value)}[]"
                        if isinstance(target, ast.Name) and prefix in self.symbols:
                            for key in [k for k in self.symbols if k == prefix or k.startswith(prefix + "[]")]:
                                self.symbols[target.id + key[len(prefix):]] = self.symbols[key]
                if previous == self.symbols:
                    break
            # A parameter rebound to another kind of value (products = set(products)) is typed any, as is
            # one of unknown kind (a union) that the function narrows, by rebinding it (thickness = [thickness] * 4)
            # or with isinstance/hasattr, which TypeScript does not follow.
            for function in functions:
                narrowed = {n.id for n in ast.walk(function) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)} | {
                    n.args[0].id
                    for n in ast.walk(function)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("isinstance", "hasattr")
                    and n.args and isinstance(n.args[0], ast.Name)
                }
                for a in function.args.args + function.args.kwonlyargs:
                    annotated = self.emit(a.annotation, "annotation_kinds") if a.annotation else None
                    if a.annotation and (self.symbols.get(a.arg) != annotated or a.arg in narrowed and annotated == "unknown"):
                        a.widened = True
            qualified = f"{module}.{getattr(node, 'name', '')}"
            try:
                if isinstance(node, ast.FunctionDef) and qualified in self.precomputed:
                    parameter = node.args.args[0].arg
                    data = self.precomputed[qualified]
                    result = self.render(self.rules["precomputed_function"], {"name": node.name, "parameter": parameter, "data": data})
                    output.append(result.rstrip())
                    continue
                locates_module = isinstance(node, ast.Assign) and "__file__" in ast.unparse(node.value)
                type_alias = isinstance(node, ast.Assign) and is_type(node.value)
                if not isinstance(node, (ast.Import, ast.ImportFrom)) and not locates_module and not type_alias:
                    self.check_foreign(node, foreign)
                result = self.emit(node).rstrip()
            except Exception as error:
                name = getattr(node, "name", f"line {node.lineno}")
                reason = str(error) if isinstance(error, ValueError) else f"{type(error).__name__}: {error}"
                self.unsupported.append(f"{name}: {reason}")
                if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    raise ValueError(reason) from error  # Never silently discard module data.
                self.imports = imports  # Drop imports only the failed function needed.
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                result = self.render(self.rules["unsupported"], {"name": name, "reason": reason, "kind": kind})
            if result:
                output.append(result)
            if functions:
                self.symbols = globals_
        header = [self.render(self.rules["header"], {})] if "header" in self.rules else []
        imports = [
            self.render(self.rules["import"], {"target": target, "alias": alias})
            for target, alias in sorted(self.imports.items())
        ]
        return "\n\n".join(header + (["\n".join(imports)] if imports else []) + output) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--rules", type=Path, default=Path(__file__).with_name("ts.yaml"))
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    compiler = Transpiler(args.rules, build_index())
    source = args.source.resolve()
    name = module_name(source) if source.is_relative_to(PACKAGE) else None
    result = compiler.translate(source.read_text(encoding="utf-8"), name)
    for diagnostic in compiler.unsupported:
        print(diagnostic, file=sys.stderr)
    print(
        f"Translated {len(compiler.functions) - len(compiler.unsupported)}/{len(compiler.functions)} functions",
        file=sys.stderr,
    )
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
