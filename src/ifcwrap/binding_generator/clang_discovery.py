from __future__ import annotations

import re
import tempfile
import threading
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .debug import debug_log, debug_path

_RECORD_KINDS = {"CXXRecordDecl", "ClassTemplateSpecializationDecl"}
_TYPE_PREFIXES = ("class ", "struct ", "union ", "enum ")
_EXTERNAL_NAMESPACE_PREFIXES = ("std::", "boost::", "Eigen::", "po::")
_SKIP_QUALIFIED_ROOTS = frozenset({"Eigen", "boost", "ifcopenshell", "po", "std"})
_BUILTIN_TYPE_NAMES = {
    "bool",
    "char",
    "double",
    "float",
    "int",
    "int8_t",
    "int16_t",
    "int32_t",
    "int64_t",
    "long",
    "long double",
    "long long",
    "ptrdiff_t",
    "short",
    "signed",
    "size_t",
    "ssize_t",
    "std::int64_t",
    "std::size_t",
    "uint8_t",
    "uint16_t",
    "uint32_t",
    "uint64_t",
    "unsigned",
    "unsigned char",
    "unsigned int",
    "unsigned long",
    "unsigned long long",
    "unsigned short",
    "void",
    "wchar_t",
}


def _is_external_qualified_type(text: str) -> bool:
    normalized = text.strip()
    return normalized.startswith(_EXTERNAL_NAMESPACE_PREFIXES)


def _should_skip_clang_type_resolution(text: str) -> bool:
    normalized = text.strip()
    return bool(re.fullmatch(r"ifcopenshell_[A-Za-z0-9_]+_t", normalized))


def _has_skipped_qualified_root(text: str) -> bool:
    if "::" not in text:
        return False
    return text.split("::", 1)[0] in _SKIP_QUALIFIED_ROOTS


def _should_skip_qualified_resolution(
    index: TranslationUnitIndex | None, text: str
) -> bool:
    return index is None and _has_skipped_qualified_root(text)


def _selected_key(selected_names: Iterable[str] | None) -> tuple[str, ...] | None:
    return tuple(sorted(set(selected_names))) if selected_names is not None else None


def _selected_set(selected_names: Iterable[str] | None) -> set[str] | None:
    return set(selected_names) if selected_names is not None else None


@dataclass(frozen=True)
class DiscoveredParam:
    name: str
    cpp_type: str
    cpp_type_ref: DiscoveredCppType


@dataclass(frozen=True)
class DiscoveredCppType:
    spelling: str
    desugared_spelling: str | None
    normalized_spelling: str
    normalized_desugared_spelling: str | None
    canonical_spelling: str
    storage_spelling: str
    base_name: str
    base_record_names: tuple[str, ...]
    template_name: str | None
    template_args: tuple[DiscoveredCppType, ...]
    is_enum: bool
    enum_qualified_name: str | None
    enum_values: tuple[tuple[str, int], ...]
    is_const: bool
    pointer_depth: int
    is_lvalue_reference: bool
    is_rvalue_reference: bool


@dataclass(frozen=True)
class DiscoveredMethod:
    class_name: str
    cpp_name: str
    return_cpp_type: str
    return_type_ref: DiscoveredCppType
    params: tuple[DiscoveredParam, ...]
    is_const: bool


@dataclass(frozen=True)
class DiscoveredConstructor:
    class_name: str
    cpp_name: str
    params: tuple[DiscoveredParam, ...]


@dataclass(frozen=True)
class DiscoveredField:
    class_name: str
    cpp_name: str
    cpp_type: str
    cpp_type_ref: DiscoveredCppType
    doc: str | None = None
    has_initializer: bool = False


@dataclass(frozen=True)
class DiscoveredBase:
    class_name: str
    cpp_type: str
    cpp_type_ref: DiscoveredCppType


@dataclass(frozen=True)
class DiscoveredFunction:
    namespace: str
    cpp_name: str
    return_cpp_type: str
    return_type_ref: DiscoveredCppType
    params: tuple[DiscoveredParam, ...]


@dataclass(frozen=True)
class CompileCommand:
    directory: Path
    file: Path
    arguments: tuple[str, ...]
    project_root: Path | None = None


@dataclass(frozen=True)
class CompilationConfig:
    compiler: str = "clang++"
    clang_args: tuple[str, ...] = ("-x", "c++", "-std=c++17")
    include_dirs: tuple[Path, ...] = ()
    defines: tuple[str, ...] = ()
    working_directory: Path | None = None


@dataclass(frozen=True)
class DiscoveryEnvironment:
    compilation: CompilationConfig = field(default_factory=CompilationConfig)
    _translation_unit_indexes: dict[Path, TranslationUnitIndex] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )
    _cache_lock: threading.RLock = field(
        default_factory=threading.RLock, init=False, repr=False, compare=False
    )


@dataclass(frozen=True)
class IndexedRecord:
    qualified_name: str
    simple_name: str
    node: dict


@dataclass(frozen=True)
class IndexedEnum:
    qualified_name: str
    simple_name: str
    node: dict


@dataclass
class TranslationUnitIndex:
    command: CompileCommand
    _parsed: bool = False
    _records_by_qualified: dict[str, IndexedRecord] = field(default_factory=dict)
    _record_names_by_simple: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _enums_by_qualified: dict[str, IndexedEnum] = field(default_factory=dict)
    _enum_names_by_simple: dict[str, list[str]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _namespace_function_cache: dict[
        tuple[str, tuple[str, ...] | None],
        dict[str, tuple[DiscoveredFunction, ...]],
    ] = field(default_factory=dict)
    _functions_by_namespace: dict[str, tuple[dict, ...]] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def _ensure_compact_index(self) -> None:
        if self._parsed:
            return
        from .libclang_index import parse_translation_unit

        debug_log("clang.tu_parse.start", f"tu={debug_path(self.command.file)}")
        parsed = parse_translation_unit(self.command)
        self._index_records((*parsed.records, *parsed.enums))
        self._functions_by_namespace = parsed.functions
        self._parsed = True
        debug_log(
            "clang.tu_parse.done",
            f"tu={debug_path(self.command.file)} records={len(parsed.records)} enums={len(parsed.enums)} functions={sum(len(items) for items in parsed.functions.values())}",
        )

    def resolve_record(
        self, class_name: str, current_scope: str = ""
    ) -> IndexedRecord | None:
        lookup_name = _normalize_record_lookup_name(class_name)
        if not lookup_name:
            return None
        self._ensure_compact_index()

        for candidate in _scoped_lookup_candidates(lookup_name, current_scope):
            record = self._records_by_qualified.get(candidate)
            if record is not None:
                return record
            if (
                current_scope
                and "::" not in lookup_name
                and candidate.startswith(f"{current_scope}::")
                and candidate != lookup_name
                and not self._record_declares_nested_name(
                    current_scope, lookup_name, kinds=_RECORD_KINDS
                )
            ):
                continue
            if "::" not in candidate:
                continue
            simple = _simple_name(candidate)
            simple_candidates = self._record_names_by_simple.get(simple, [])
            if "::" in candidate:
                simple_candidates = [
                    name
                    for name in simple_candidates
                    if name == candidate
                    or name.endswith(f"::{candidate}")
                    or candidate.endswith(f"::{name}")
                ]
            if simple_candidates:
                resolved = (
                    self._records_by_qualified[simple_candidates[0]]
                    if len(simple_candidates) == 1
                    else self._resolve_best_scoped_decl(
                        candidate,
                        current_scope=current_scope,
                        qualified=self._records_by_qualified,
                        simple=self._record_names_by_simple,
                    )
                )
                if "::" not in resolved.qualified_name:
                    return IndexedRecord(
                        qualified_name=candidate,
                        simple_name=resolved.simple_name,
                        node=resolved.node,
                    )

        if "::" in lookup_name and not any(
            name == lookup_name
            or name.endswith(f"::{lookup_name}")
            or lookup_name.endswith(f"::{name}")
            for name in self._record_names_by_simple.get(_simple_name(lookup_name), [])
        ):
            return None
        return self._resolve_scoped_decl(
            lookup_name,
            current_scope=current_scope,
            qualified=self._records_by_qualified,
            simple=self._record_names_by_simple,
        )

    def resolve_enum(
        self, enum_name: str, current_scope: str = ""
    ) -> IndexedEnum | None:
        lookup_name = _normalize_record_lookup_name(enum_name)
        if not lookup_name:
            return None
        self._ensure_compact_index()

        for candidate in _scoped_lookup_candidates(lookup_name, current_scope):
            enum = self._enums_by_qualified.get(candidate)
            if enum is not None:
                return enum
            if (
                current_scope
                and "::" not in lookup_name
                and candidate.startswith(f"{current_scope}::")
                and candidate != lookup_name
                and not self._record_declares_nested_name(
                    current_scope, lookup_name, kinds={"EnumDecl"}
                )
            ):
                continue
            if "::" in candidate:
                simple = _simple_name(candidate)
                simple_candidates = self._enum_names_by_simple.get(simple, [])
                if "::" in candidate:
                    simple_candidates = [
                        name
                        for name in simple_candidates
                        if name == candidate
                        or name.endswith(f"::{candidate}")
                        or candidate.endswith(f"::{name}")
                    ]
                if simple_candidates:
                    resolved = (
                        self._enums_by_qualified[simple_candidates[0]]
                        if len(simple_candidates) == 1
                        else self._resolve_best_scoped_decl(
                            candidate,
                            current_scope=current_scope,
                            qualified=self._enums_by_qualified,
                            simple=self._enum_names_by_simple,
                        )
                    )
                    if "::" not in resolved.qualified_name:
                        return IndexedEnum(
                            qualified_name=candidate,
                            simple_name=resolved.simple_name,
                            node=resolved.node,
                        )
        if "::" in lookup_name and not any(
            name == lookup_name
            or name.endswith(f"::{lookup_name}")
            or lookup_name.endswith(f"::{name}")
            for name in self._enum_names_by_simple.get(_simple_name(lookup_name), [])
        ):
            return None
        return self._resolve_scoped_decl(
            lookup_name,
            current_scope=current_scope,
            qualified=self._enums_by_qualified,
            simple=self._enum_names_by_simple,
        )

    def discover_namespace_functions(
        self,
        namespace_name: str,
        selected_names: Iterable[str] | None = None,
    ) -> dict[str, tuple[DiscoveredFunction, ...]]:
        with self._lock:
            return self._discover_namespace_functions(
                namespace_name, selected_names=selected_names
            )

    def _discover_namespace_functions(
        self,
        namespace_name: str,
        selected_names: Iterable[str] | None = None,
    ) -> dict[str, tuple[DiscoveredFunction, ...]]:
        selected_key = _selected_key(selected_names)
        selected_set = _selected_set(selected_key)
        cached = self._namespace_function_cache.get((namespace_name, selected_key))
        if cached is not None:
            return cached

        self._ensure_compact_index()
        functions: dict[str, list[DiscoveredFunction]] = defaultdict(list)
        namespace_nodes = self._functions_by_namespace.get(namespace_name, ())
        if not namespace_nodes and "::" in namespace_name:
            namespace_nodes = self._functions_by_namespace.get(
                _simple_name(namespace_name), ()
            )
        for node in namespace_nodes:
            for func_name, overloads in _extract_namespace_functions(
                node, namespace_name, self, selected_names=selected_set
            ).items():
                functions[func_name].extend(overloads)

        if not functions:
            msg = f"Namespace '{namespace_name}' not found in AST for '{self.command.file}'"
            raise ValueError(msg)

        result = {
            func_name: _dedupe_discovered_functions(overloads)
            for func_name, overloads in functions.items()
        }
        self._namespace_function_cache[(namespace_name, selected_key)] = result
        return result

    def _index_records(self, nodes: tuple[dict, ...]) -> None:
        def visit(node: dict, current_scope: str) -> None:
            kind = node.get("kind")
            name = node.get("name", "")
            next_scope = current_scope

            if kind == "NamespaceDecl":
                next_scope = _qualified_name(current_scope, name)
            elif kind in _RECORD_KINDS and name and node.get("completeDefinition"):
                qualified_name = node.get("qualifiedName") or _qualified_name(
                    current_scope, name
                )
                if qualified_name not in self._records_by_qualified:
                    self._records_by_qualified[qualified_name] = IndexedRecord(
                        qualified_name=qualified_name,
                        simple_name=name,
                        node=node,
                    )
                    if qualified_name not in self._record_names_by_simple[name]:
                        self._record_names_by_simple[name].append(qualified_name)
                next_scope = qualified_name
            elif kind == "EnumDecl" and name:
                qualified_name = node.get("qualifiedName") or _qualified_name(
                    current_scope, name
                )
                if qualified_name not in self._enums_by_qualified:
                    self._enums_by_qualified[qualified_name] = IndexedEnum(
                        qualified_name=qualified_name,
                        simple_name=name,
                        node=node,
                    )
                    if qualified_name not in self._enum_names_by_simple[name]:
                        self._enum_names_by_simple[name].append(qualified_name)
            elif kind == "TypedefDecl" and name:
                enum_child = next(
                    (
                        child
                        for child in node.get("inner", [])
                        if child.get("kind") == "EnumDecl"
                    ),
                    None,
                )
                if enum_child is None:
                    enum_child = next(
                        (
                            child.get("ownedTagDecl")
                            for child in node.get("inner", [])
                            if child.get("kind") == "ElaboratedType"
                            and child.get("ownedTagDecl", {}).get("kind") == "EnumDecl"
                        ),
                        None,
                    )
                if enum_child is not None:
                    type_info = node.get("type", {})
                    qualified_name = type_info.get("desugaredQualType", "")
                    if not qualified_name or _simple_name(qualified_name) != name:
                        qualified_name = _qualified_name(current_scope, name)
                    if qualified_name not in self._enums_by_qualified:
                        self._enums_by_qualified[qualified_name] = IndexedEnum(
                            qualified_name=qualified_name,
                            simple_name=name,
                            node=enum_child,
                        )
                        if qualified_name not in self._enum_names_by_simple[name]:
                            self._enum_names_by_simple[name].append(qualified_name)

            for child in node.get("inner", []):
                visit(child, next_scope)

        for node in nodes:
            visit(node, "")

    def _resolve_scoped_decl(
        self,
        name: str,
        current_scope: str,
        qualified: dict[str, object],
        simple: dict[str, list[str]],
    ):
        if name in qualified:
            return qualified[name]
        if "::" not in name and current_scope:
            scope = current_scope
            while scope:
                candidate = f"{scope}::{name}"
                if candidate in qualified:
                    return qualified[candidate]
                scope = scope.rsplit("::", 1)[0] if "::" in scope else ""
        candidates = simple.get(_simple_name(name), [])
        if not candidates:
            return None
        return self._resolve_best_scoped_decl(
            name, current_scope=current_scope, qualified=qualified, simple=simple
        )

    def _resolve_best_scoped_decl(
        self,
        name: str,
        current_scope: str,
        qualified: dict[str, object],
        simple: dict[str, list[str]],
    ):
        candidates = simple.get(_simple_name(name), [])
        if not candidates:
            return None
        if len(candidates) == 1:
            return qualified[candidates[0]]

        wanted_simple = _simple_name(name)

        def scope_score(candidate: str) -> tuple[int, int, str]:
            if candidate == name:
                return (0, 0, candidate)
            scope = current_scope
            depth = 1
            while scope:
                if candidate == f"{scope}::{wanted_simple}":
                    return (1, depth, candidate)
                scope = scope.rsplit("::", 1)[0] if "::" in scope else ""
                depth += 1
            if "::" in name and name.endswith(candidate):
                return (2, -candidate.count("::"), candidate)
            if "::" in name and candidate.endswith(f"::{name}"):
                return (3, 0, candidate)
            if "::" not in candidate:
                return (4, 0, candidate)
            return (5, 0, candidate)

        ranked = sorted(candidates, key=scope_score)
        best = ranked[0]
        if scope_score(best)[:2] == scope_score(ranked[1])[:2]:
            msg = f"Ambiguous declaration lookup for '{name}': {ranked}"
            raise ValueError(msg)
        return qualified[best]

    def _record_declares_nested_name(
        self, record_name: str, nested_name: str, *, kinds: set[str]
    ) -> bool:
        record = self._records_by_qualified.get(record_name)
        if record is None:
            return False
        for child in record.node.get("inner", []):
            if child.get("kind") not in kinds or child.get("name") != nested_name:
                continue
            if child.get("kind") in _RECORD_KINDS and not child.get(
                "completeDefinition"
            ):
                continue
            return True
        return False


def _resolve_path(path: Path, base_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()


def _compile_command_from_config(
    config: CompilationConfig, translation_unit: Path
) -> CompileCommand:
    tu_resolved = translation_unit.resolve()
    directory = (config.working_directory or tu_resolved.parent).resolve()
    arguments: list[str] = [config.compiler]
    arguments.extend(config.clang_args)
    arguments.extend(
        f"-I{include_dir.resolve()}" for include_dir in config.include_dirs
    )
    arguments.extend(f"-D{define}" for define in config.defines)
    arguments.extend(["-c", str(tu_resolved)])
    return CompileCommand(
        directory=directory, file=tu_resolved, arguments=tuple(arguments)
    )


def _translation_unit_index(
    environment: DiscoveryEnvironment, translation_unit: Path
) -> TranslationUnitIndex:
    tu_resolved = translation_unit.resolve()

    with environment._cache_lock:  # noqa: SLF001
        cached = environment._translation_unit_indexes.get(tu_resolved)  # noqa: SLF001
        if cached is not None:
            return cached

        command = _compile_command_from_config(environment.compilation, tu_resolved)
        debug_context = "compilation_config"

        index = TranslationUnitIndex(command=command)
        environment._translation_unit_indexes[tu_resolved] = index  # noqa: SLF001
        debug_log(
            "clang.tu_index.create", f"{debug_context} tu={debug_path(tu_resolved)}"
        )
        return index


def _choose_reference_compile_command(
    environment: DiscoveryEnvironment,
    reference_source_root: Path | None,
) -> CompileCommand:
    source_root = (
        reference_source_root.resolve()
        if reference_source_root is not None
        else Path.cwd().resolve()
    )
    return _compile_command_from_config(
        CompilationConfig(
            compiler=environment.compilation.compiler,
            clang_args=environment.compilation.clang_args,
            include_dirs=environment.compilation.include_dirs,
            defines=environment.compilation.defines,
            working_directory=environment.compilation.working_directory or source_root,
        ),
        source_root / "contract_discovery.cpp",
    )


def _is_compile_source_token(token: str, command: CompileCommand) -> bool:
    if token == str(command.file):
        return True
    if token.startswith("-"):
        return False
    try:
        return _resolve_path(Path(token), command.directory) == command.file
    except RuntimeError:
        return False


def _synthetic_compile_arguments(
    command: CompileCommand, synthetic_source: Path
) -> tuple[str, ...]:
    synthetic = str(synthetic_source)
    replaced = False
    arguments: list[str] = []
    for token in command.arguments:
        if _is_compile_source_token(token, command):
            arguments.append(synthetic)
            replaced = True
        else:
            arguments.append(token)
    if not replaced:
        arguments.extend(["-c", synthetic])
    return tuple(arguments)


def _default_access(record: dict) -> str:
    return "public" if record.get("tagUsed") == "struct" else "private"


def _return_type_discovery_input(
    declaration: dict,
    fallback: str,
    *,
    index: TranslationUnitIndex,
    current_scope: str,
) -> dict | str:
    type_info = declaration.get("returnType")
    if not isinstance(type_info, dict) or not type_info.get("desugaredQualType"):
        return fallback
    parsed = _parse_discovered_cpp_type(
        type_info,
        index=index,
        current_scope=current_scope,
    )
    return (
        type_info
        if parsed.template_name
        in {"std::array", "std::optional", "std::set", "std::variant", "std::vector"}
        else fallback
    )


def _extract_public_methods(
    record: dict,
    index: TranslationUnitIndex,
    current_scope: str,
    selected_names: set[str] | None = None,
) -> dict[str, tuple[DiscoveredMethod, ...]]:
    methods: dict[str, list[DiscoveredMethod]] = defaultdict(list)
    access = _default_access(record)
    for child in record.get("inner", []):
        if child.get("kind") == "AccessSpecDecl":
            access = child.get("access", access)
            continue
        if access != "public":
            continue
        if child.get("kind") != "CXXMethodDecl":
            continue
        if child.get("name") in {"operator=", "operator[]"}:
            continue
        if selected_names is not None and child.get("name") not in selected_names:
            continue

        params = tuple(
            DiscoveredParam(
                name=param.get("name") or f"arg_{param_index}",
                cpp_type=param.get("type", {}).get("qualType", ""),
                cpp_type_ref=_parse_discovered_cpp_type(
                    param.get("type", {}), index=index, current_scope=current_scope
                ),
            )
            for param_index, param in enumerate(
                item
                for item in child.get("inner", [])
                if item.get("kind") == "ParmVarDecl"
            )
        )
        return_cpp_type = (
            child.get("type", {}).get("qualType", "").rsplit("(", 1)[0].strip()
        )
        return_type_info = _return_type_discovery_input(
            child,
            return_cpp_type,
            index=index,
            current_scope=current_scope,
        )
        methods[child["name"]].append(
            DiscoveredMethod(
                class_name=record.get("name", ""),
                cpp_name=child["name"],
                return_cpp_type=return_cpp_type,
                return_type_ref=_parse_discovered_cpp_type(
                    return_type_info, index=index, current_scope=current_scope
                ),
                params=params,
                is_const=child.get("type", {}).get("qualType", "").endswith(" const"),
            )
        )
    return {name: tuple(overloads) for name, overloads in methods.items()}


def _is_copy_or_move_constructor(
    child: dict, record_name: str, current_scope: str
) -> bool:
    params = [
        item for item in child.get("inner", []) if item.get("kind") == "ParmVarDecl"
    ]
    if len(params) != 1:
        return False
    param_type = params[0].get("type", {}).get("qualType", "")
    lookup_name = _normalize_record_lookup_name(param_type)
    return lookup_name in {
        record_name,
        _qualified_name(_enclosing_scope(current_scope), record_name),
        current_scope,
    }


def _is_implicit_default_constructor(child: dict) -> bool:
    return bool(child.get("isImplicit")) and not any(
        item.get("kind") == "ParmVarDecl" for item in child.get("inner", [])
    )


def _comment_node_parts(node: dict) -> list[str]:
    kind = node.get("kind")
    if kind == "TextComment":
        return [node.get("text", "")]
    if kind == "InlineCommandComment":
        return [
            " ".join(
                argument.get("text", "")
                for argument in node.get("args", [])
                if argument.get("text")
            )
        ]
    if kind == "ParagraphComment":
        return [
            "\n".join(
                part
                for child in node.get("inner", [])
                for part in _comment_node_parts(child)
            )
        ]
    if kind == "FullComment":
        return [
            part
            for child in node.get("inner", [])
            for part in _comment_node_parts(child)
        ]

    parts = [
        part for child in node.get("inner", []) for part in _comment_node_parts(child)
    ]
    if parts:
        return ["\n".join(parts)]
    text = node.get("text")
    return [text] if isinstance(text, str) else []


def _normalize_comment_parts(parts: Iterable[str]) -> str | None:
    paragraphs: list[str] = []
    for part in parts:
        lines = [line.strip() for line in part.splitlines()]
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        paragraph = "\n".join(lines)
        if paragraph:
            paragraphs.append(paragraph)
    doc = "\n\n".join(paragraphs).strip()
    return doc or None


def _extract_documentation(node: dict) -> str | None:
    if node.get("doc"):
        return node["doc"]
    for child in node.get("inner", []):
        if child.get("kind") == "FullComment":
            return _normalize_comment_parts(_comment_node_parts(child))
    return None


def _extract_public_constructors(
    record: dict,
    index: TranslationUnitIndex,
    current_scope: str,
) -> tuple[DiscoveredConstructor, ...]:
    constructors: list[DiscoveredConstructor] = []
    access = _default_access(record)
    record_name = record.get("name", "")
    saw_non_copy_move_constructor_decl = False
    for child in record.get("inner", []):
        if child.get("kind") == "AccessSpecDecl":
            access = child.get("access", access)
            continue
        if child.get("kind") != "CXXConstructorDecl":
            continue
        if _is_copy_or_move_constructor(child, record_name, current_scope):
            continue
        saw_non_copy_move_constructor_decl = True
        implicit_default = _is_implicit_default_constructor(child)
        if access != "public" and not implicit_default:
            continue
        if (child.get("isImplicit") and not implicit_default) or child.get("isDeleted"):
            continue

        params = tuple(
            DiscoveredParam(
                name=param.get("name") or f"arg_{param_index}",
                cpp_type=param.get("type", {}).get("qualType", ""),
                cpp_type_ref=_parse_discovered_cpp_type(
                    param.get("type", {}), index=index, current_scope=current_scope
                ),
            )
            for param_index, param in enumerate(
                item
                for item in child.get("inner", [])
                if item.get("kind") == "ParmVarDecl"
            )
        )
        constructors.append(
            DiscoveredConstructor(
                class_name=current_scope,
                cpp_name=current_scope,
                params=params,
            )
        )
    if not constructors and not saw_non_copy_move_constructor_decl:
        constructors.append(
            DiscoveredConstructor(
                class_name=current_scope, cpp_name=current_scope, params=()
            )
        )
    return tuple(constructors)


def _extract_public_fields(
    record: dict, index: TranslationUnitIndex, current_scope: str
) -> dict[str, DiscoveredField]:
    fields: dict[str, DiscoveredField] = {}
    access = _default_access(record)
    for child in record.get("inner", []):
        if child.get("kind") == "AccessSpecDecl":
            access = child.get("access", access)
            continue
        if access != "public":
            continue
        if child.get("kind") != "FieldDecl":
            continue
        name = child.get("name")
        if not name:
            continue
        fields[name] = DiscoveredField(
            class_name=record.get("name", ""),
            cpp_name=name,
            cpp_type=child.get("type", {}).get("qualType", ""),
            cpp_type_ref=_parse_discovered_cpp_type(
                child.get("type", {}), index=index, current_scope=current_scope
            ),
            doc=_extract_documentation(child),
            has_initializer=bool(child.get("hasInitializer", False)),
        )
    return fields


def _qualified_name(prefix: str, name: str) -> str:
    if not prefix:
        return name
    if not name:
        return prefix
    return f"{prefix}::{name}"


def _simple_name(name: str) -> str:
    return name.rsplit("::", 1)[-1]


def _enclosing_scope(current_scope: str) -> str:
    if "::" not in current_scope:
        return ""
    return current_scope.rsplit("::", 1)[0]


def _looks_like_named_type(text: str) -> bool:
    if text in _BUILTIN_TYPE_NAMES:
        return False
    return re.fullmatch(r"[A-Za-z_]\w*(?:::[A-Za-z_]\w*)*", text) is not None


def _scoped_lookup_candidates(name: str, current_scope: str) -> tuple[str, ...]:
    if "::" in name or not current_scope:
        return (name,)
    candidates: list[str] = []
    scope = current_scope
    while scope:
        candidates.append(f"{scope}::{name}")
        scope = scope.rsplit("::", 1)[0] if "::" in scope else ""
    candidates.append(name)
    return tuple(candidates)


def _strip_template_args(text: str) -> str:
    chars: list[str] = []
    depth = 0
    for char in text:
        if char == "<":
            depth += 1
            continue
        if char == ">":
            depth = max(0, depth - 1)
            continue
        if depth == 0:
            chars.append(char)
    return "".join(chars)


def _normalize_record_lookup_name(name: str) -> str:
    normalized = " ".join(name.replace(" &", "&").replace(" *", "*").split())
    while normalized.startswith("const "):
        normalized = normalized[len("const ") :].strip()
    for prefix in _TYPE_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :].strip()
            break
    while normalized.endswith("&") or normalized.endswith("*"):
        normalized = normalized[:-1].strip()
    normalized = _strip_template_args(normalized).strip()
    return normalized


def _base_record_lookup_names(record: dict) -> list[str]:
    base_names: list[str] = []
    for base in record.get("bases", []):
        type_info = base.get("type", {})
        raw_name = type_info.get("desugaredQualType") or type_info.get("qualType", "")
        lookup_name = _normalize_record_lookup_name(raw_name)
        if lookup_name:
            base_names.append(lookup_name)
    return base_names


def _extract_bases(
    record: dict, index: TranslationUnitIndex, current_scope: str
) -> tuple[DiscoveredBase, ...]:
    bases: list[DiscoveredBase] = []
    for base in record.get("bases", []):
        type_info = base.get("type", {})
        cpp_type = type_info.get("desugaredQualType") or type_info.get("qualType", "")
        if not cpp_type:
            continue
        bases.append(
            DiscoveredBase(
                class_name=record.get("name", ""),
                cpp_type=cpp_type,
                cpp_type_ref=_parse_discovered_cpp_type(
                    type_info, index=index, current_scope=current_scope
                ),
            )
        )
    return tuple(bases)


def _extract_namespace_functions(
    node: dict,
    namespace_name: str,
    index: TranslationUnitIndex,
    current_namespace: str = "",
    selected_names: set[str] | None = None,
) -> dict[str, tuple[DiscoveredFunction, ...]]:
    functions: dict[str, list[DiscoveredFunction]] = defaultdict(list)

    kind = node.get("kind")
    name = node.get("name", "")
    declaration_namespace = node.get("namespace", current_namespace)
    next_namespace = declaration_namespace
    if kind == "NamespaceDecl":
        next_namespace = _qualified_name(current_namespace, name)

    if (
        kind == "FunctionDecl"
        and _namespace_matches(declaration_namespace, namespace_name)
        and (selected_names is None or name in selected_names)
    ):
        params = tuple(
            DiscoveredParam(
                name=param.get("name") or f"arg_{param_index}",
                cpp_type=param.get("type", {}).get("qualType", ""),
                cpp_type_ref=_parse_discovered_cpp_type(
                    param.get("type", {}),
                    index=index,
                    current_scope=declaration_namespace,
                ),
            )
            for param_index, param in enumerate(
                item
                for item in node.get("inner", [])
                if item.get("kind") == "ParmVarDecl"
            )
        )
        return_cpp_type = (
            node.get("type", {}).get("qualType", "").rsplit("(", 1)[0].strip()
        )
        return_type_info = _return_type_discovery_input(
            node,
            return_cpp_type,
            index=index,
            current_scope=declaration_namespace,
        )
        functions[name].append(
            DiscoveredFunction(
                namespace=declaration_namespace,
                cpp_name=name,
                return_cpp_type=return_cpp_type,
                return_type_ref=_parse_discovered_cpp_type(
                    return_type_info,
                    index=index,
                    current_scope=declaration_namespace,
                ),
                params=params,
            )
        )

    for child in node.get("inner", []):
        for func_name, overloads in _extract_namespace_functions(
            child, namespace_name, index, next_namespace, selected_names=selected_names
        ).items():
            functions[func_name].extend(overloads)

    return {func_name: tuple(overloads) for func_name, overloads in functions.items()}


def _namespace_matches(current_namespace: str, target_namespace: str) -> bool:
    if current_namespace == target_namespace:
        return True
    return "::" in target_namespace and current_namespace == _simple_name(
        target_namespace
    )


def _dedupe_discovered_functions(
    functions: Iterable[DiscoveredFunction],
) -> tuple[DiscoveredFunction, ...]:
    result: list[DiscoveredFunction] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for function in functions:
        key = (
            function.cpp_name,
            function.return_cpp_type,
            tuple(param.cpp_type for param in function.params),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(function)
    return tuple(result)


def discover_public_methods(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    class_name: str,
    include_inherited: bool = False,
    selected_names: Iterable[str] | None = None,
) -> dict[str, tuple[DiscoveredMethod, ...]]:
    index = _translation_unit_index(environment, translation_unit)
    record = index.resolve_record(class_name)
    if record is None:
        msg = f"Class '{class_name}' not found in AST for '{translation_unit}'"
        raise ValueError(msg)

    selected_set = set(selected_names) if selected_names is not None else None
    methods = _extract_public_methods(
        record.node, index, record.qualified_name, selected_names=selected_set
    )

    if include_inherited:
        visited: set[str] = {record.qualified_name}
        queue = _base_record_lookup_names(record.node)
        while queue:
            base_name = queue.pop(0)
            base_record = index.resolve_record(base_name)
            if base_record is None or base_record.qualified_name in visited:
                continue
            visited.add(base_record.qualified_name)
            base_methods = _extract_public_methods(
                base_record.node,
                index,
                base_record.qualified_name,
                selected_names=selected_set,
            )
            for method_name, overloads in base_methods.items():
                if method_name not in methods:
                    methods[method_name] = overloads
            queue.extend(_base_record_lookup_names(base_record.node))

    return methods


def discover_public_constructors(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    class_name: str,
) -> tuple[DiscoveredConstructor, ...]:
    index = _translation_unit_index(environment, translation_unit)
    record = index.resolve_record(class_name)
    if record is None:
        msg = f"Class '{class_name}' not found in AST for '{translation_unit}'"
        raise ValueError(msg)
    return _extract_public_constructors(record.node, index, record.qualified_name)


def discover_public_fields(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    class_name: str,
    include_inherited: bool = False,
) -> dict[str, DiscoveredField]:
    index = _translation_unit_index(environment, translation_unit)
    record = index.resolve_record(class_name)
    if record is None:
        msg = f"Class '{class_name}' not found in AST for '{translation_unit}'"
        raise ValueError(msg)

    fields = _extract_public_fields(record.node, index, record.qualified_name)

    if include_inherited:
        visited: set[str] = {record.qualified_name}
        queue = _base_record_lookup_names(record.node)
        while queue:
            base_name = queue.pop(0)
            base_record = index.resolve_record(base_name)
            if base_record is None or base_record.qualified_name in visited:
                continue
            visited.add(base_record.qualified_name)
            base_fields = _extract_public_fields(
                base_record.node, index, base_record.qualified_name
            )
            for field_name, field_value in base_fields.items():
                if field_name not in fields:
                    fields[field_name] = field_value
            queue.extend(_base_record_lookup_names(base_record.node))

    return fields


def discover_base_types(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    class_name: str,
) -> tuple[DiscoveredBase, ...]:
    index = _translation_unit_index(environment, translation_unit)
    record = index.resolve_record(class_name)
    if record is None:
        msg = f"Class '{class_name}' not found in AST for '{translation_unit}'"
        raise ValueError(msg)
    return _extract_bases(record.node, index, record.qualified_name)


def discover_namespace_functions(
    environment: DiscoveryEnvironment,
    translation_unit: Path,
    namespace_name: str,
    selected_names: Iterable[str] | None = None,
) -> dict[str, tuple[DiscoveredFunction, ...]]:
    index = _translation_unit_index(environment, translation_unit)
    return index.discover_namespace_functions(
        namespace_name, selected_names=selected_names
    )


def discover_namespace_functions_with_synthetic_source(
    environment: DiscoveryEnvironment,
    source_text: str,
    namespace_name: str,
    selected_names: Iterable[str] | None = None,
    *,
    reference_source_root: Path | None = None,
) -> dict[str, tuple[DiscoveredFunction, ...]]:
    reference_command = _choose_reference_compile_command(
        environment, reference_source_root
    )
    with tempfile.TemporaryDirectory(prefix="ifcwrap-bindgen-") as tmp_dir:
        synthetic_source = Path(tmp_dir) / "contract_discovery.cpp"
        synthetic_source.write_text(source_text, encoding="utf-8")
        command = CompileCommand(
            directory=reference_command.directory,
            file=synthetic_source,
            arguments=_synthetic_compile_arguments(reference_command, synthetic_source),
            project_root=reference_source_root.resolve()
            if reference_source_root is not None
            else None,
        )
        debug_log(
            "clang.synthetic_tu_index.create",
            f"reference={debug_path(reference_command.file)}",
        )
        index = TranslationUnitIndex(command=command)
        return index.discover_namespace_functions(
            namespace_name, selected_names=selected_names
        )


def _normalize_cpp_type_text(text: str) -> str:
    return " ".join(text.replace(" &", "&").replace(" *", "*").split())


def _split_template_args(text: str) -> tuple[str, ...]:
    args: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char == "<":
            depth += 1
        elif char == ">":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            arg = "".join(current).strip()
            if arg:
                args.append(arg)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        args.append(tail)
    return tuple(args)


def _parse_type_core(text: str) -> tuple[bool, int, bool, bool, str]:
    core = _normalize_cpp_type_text(text)
    is_const = False
    while core.startswith("const "):
        is_const = True
        core = core[len("const ") :].strip()

    pointer_depth = 0
    is_lvalue_reference = False
    is_rvalue_reference = False
    while True:
        if core.endswith("&&"):
            is_rvalue_reference = True
            core = core[:-2].strip()
            continue
        if core.endswith("&"):
            is_lvalue_reference = True
            core = core[:-1].strip()
            continue
        if core.endswith("*"):
            pointer_depth += 1
            core = core[:-1].strip()
            continue
        break
    return is_const, pointer_depth, is_lvalue_reference, is_rvalue_reference, core


def _rebuild_type_text(
    *,
    is_const: bool,
    pointer_depth: int,
    is_lvalue_reference: bool,
    is_rvalue_reference: bool,
    core: str,
) -> str:
    text = core.strip()
    if is_const:
        text = f"const {text}"
    text += "*" * pointer_depth
    if is_lvalue_reference:
        text += "&"
    if is_rvalue_reference:
        text += "&&"
    return text


def _parse_template_name_and_args(
    text: str,
    *,
    index: TranslationUnitIndex | None = None,
    current_scope: str = "",
) -> tuple[str | None, tuple[DiscoveredCppType, ...]]:
    if not text.endswith(">"):
        return None, ()
    start = text.find("<")
    if start == -1:
        return None, ()
    template_name = text[:start].strip()
    inner = text[start + 1 : -1].strip()
    if not inner:
        return template_name, ()
    return template_name, tuple(
        _parse_discovered_cpp_type(arg, index=index, current_scope=current_scope)
        for arg in _split_template_args(inner)
    )


def _qualified_type_core(
    text: str, *, index: TranslationUnitIndex | None = None, current_scope: str = ""
) -> str:
    template_name, template_args = _parse_template_name_and_args(
        text, index=index, current_scope=current_scope
    )
    if template_name is not None:
        if template_args:
            rendered_args = ", ".join(arg.storage_spelling for arg in template_args)
            return f"{template_name}<{rendered_args}>"
        return f"{template_name}<>"

    if _is_external_qualified_type(text):
        return text

    if _should_skip_clang_type_resolution(text):
        return text

    if _should_skip_qualified_resolution(index, text):
        return text

    if index is not None:
        if _looks_like_named_type(text):
            record = index.resolve_record(text, current_scope=current_scope)
            if record is not None:
                if "::" in text and "::" not in record.qualified_name:
                    return text
                if "::" in text and record.qualified_name.endswith(f"::{text}"):
                    return text
                if "::" not in record.qualified_name and "::" not in text:
                    enclosing_scope = _enclosing_scope(current_scope)
                    if enclosing_scope:
                        return f"{enclosing_scope}::{text}"
                return record.qualified_name

            enum = index.resolve_enum(text, current_scope)
            if enum is not None:
                if "::" in text and "::" not in enum.qualified_name:
                    return text
                if "::" not in enum.qualified_name and "::" not in text:
                    enclosing_scope = _enclosing_scope(current_scope)
                    if enclosing_scope:
                        return f"{enclosing_scope}::{text}"
                return enum.qualified_name

            if "::" in text:
                root, suffix = text.split("::", 1)
                root_record = index.resolve_record(root, current_scope=current_scope)
                if root_record is not None and "::" not in root:
                    qualified_root = root_record.qualified_name
                    if "::" not in qualified_root:
                        enclosing_scope = _enclosing_scope(current_scope)
                        if enclosing_scope:
                            qualified_root = f"{enclosing_scope}::{root}"
                    if "::" in qualified_root:
                        return f"{qualified_root}::{suffix}"

    if "::" not in text and _looks_like_named_type(text):
        enclosing_scope = _enclosing_scope(current_scope)
        if enclosing_scope:
            return f"{enclosing_scope}::{text}"
    return text


def _with_requested_enum_name(
    enum: IndexedEnum, text: str, current_scope: str
) -> IndexedEnum:
    if (
        "::" in text
        and enum.qualified_name != text
        and _simple_name(text) == enum.simple_name
        and (
            "::" not in enum.qualified_name or text.endswith(f"::{enum.qualified_name}")
        )
    ):
        return IndexedEnum(
            qualified_name=text,
            simple_name=enum.simple_name,
            node=enum.node,
        )
    if "::" not in enum.qualified_name and "::" not in text:
        enclosing_scope = _enclosing_scope(current_scope)
        if enclosing_scope:
            return IndexedEnum(
                qualified_name=f"{enclosing_scope}::{text}",
                simple_name=enum.simple_name,
                node=enum.node,
            )
    return enum


def _resolved_enum(
    index: TranslationUnitIndex | None, text: str, current_scope: str
) -> IndexedEnum | None:
    if (
        index is None
        or not _looks_like_named_type(text)
        or _is_external_qualified_type(text)
        or _should_skip_clang_type_resolution(text)
    ):
        return None
    enum = index._resolve_scoped_decl(  # noqa: SLF001
        text,
        current_scope=current_scope,
        qualified=index._enums_by_qualified,  # noqa: SLF001
        simple=index._enum_names_by_simple,  # noqa: SLF001
    )
    if enum is not None:
        return _with_requested_enum_name(enum, text, current_scope)
    if _should_skip_qualified_resolution(index, text):
        return None
    return index.resolve_enum(text, current_scope)


def _parse_discovered_cpp_type(
    raw: dict | str,
    *,
    index: TranslationUnitIndex | None = None,
    current_scope: str = "",
) -> DiscoveredCppType:
    if isinstance(raw, dict):
        spelling = raw.get("qualType", "")
        desugared_spelling = raw.get("desugaredQualType")
    else:
        spelling = raw
        desugared_spelling = None

    normalized_spelling = _normalize_cpp_type_text(spelling)
    normalized_desugared = (
        _normalize_cpp_type_text(desugared_spelling) if desugared_spelling else None
    )
    canonical_input = normalized_desugared or normalized_spelling
    is_const, pointer_depth, is_lvalue_reference, is_rvalue_reference, core = (
        _parse_type_core(canonical_input)
    )
    template_name, template_args = _parse_template_name_and_args(
        core, index=index, current_scope=current_scope
    )
    base_name = template_name or core
    canonical = _rebuild_type_text(
        is_const=is_const,
        pointer_depth=pointer_depth,
        is_lvalue_reference=is_lvalue_reference,
        is_rvalue_reference=is_rvalue_reference,
        core=base_name,
    )
    storage_core = _qualified_type_core(core, index=index, current_scope=current_scope)
    storage_spelling = _rebuild_type_text(
        is_const=is_const,
        pointer_depth=pointer_depth,
        is_lvalue_reference=is_lvalue_reference,
        is_rvalue_reference=is_rvalue_reference,
        core=storage_core,
    )
    resolved_record = None
    if (
        index is not None
        and template_name is None
        and _looks_like_named_type(base_name)
        and not _is_external_qualified_type(base_name)
        and not _should_skip_qualified_resolution(index, base_name)
    ):
        candidates = index._record_names_by_simple.get(  # noqa: SLF001
            _simple_name(base_name), []
        )
        if "::" not in base_name or any(
            name == base_name
            or name.endswith(f"::{base_name}")
            or base_name.endswith(f"::{name}")
            for name in candidates
        ):
            resolved_record = index._resolve_scoped_decl(  # noqa: SLF001
                base_name,
                current_scope=current_scope,
                qualified=index._records_by_qualified,  # noqa: SLF001
                simple=index._record_names_by_simple,  # noqa: SLF001
            )
    resolved_enum = (
        None
        if resolved_record is not None or template_name is not None
        else _resolved_enum(index, base_name, current_scope)
    )
    is_enum = resolved_enum is not None
    enum_values = (
        tuple(
            (
                child.get("literal") or child.get("name", ""),
                int(child.get("value", 0)),
            )
            for child in resolved_enum.node.get("inner", ())
            if child.get("kind") == "EnumConstantDecl" and child.get("name")
        )
        if resolved_enum is not None
        else ()
    )
    return DiscoveredCppType(
        spelling=spelling,
        desugared_spelling=desugared_spelling,
        normalized_spelling=normalized_spelling,
        normalized_desugared_spelling=normalized_desugared,
        canonical_spelling=canonical,
        storage_spelling=storage_spelling,
        base_name=base_name,
        base_record_names=tuple(_base_record_lookup_names(resolved_record.node))
        if resolved_record is not None
        else (),
        template_name=template_name,
        template_args=template_args,
        is_enum=is_enum,
        enum_qualified_name=resolved_enum.qualified_name
        if resolved_enum is not None
        else None,
        enum_values=enum_values,
        is_const=is_const,
        pointer_depth=pointer_depth,
        is_lvalue_reference=is_lvalue_reference,
        is_rvalue_reference=is_rvalue_reference,
    )
