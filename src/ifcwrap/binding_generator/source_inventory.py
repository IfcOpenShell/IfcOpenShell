# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .clang_discovery import (
    DiscoveredBase,
    DiscoveredConstructor,
    DiscoveredField,
    DiscoveredFunction,
    DiscoveredMethod,
    DiscoveryEnvironment,
    discover_base_types,
    discover_namespace_functions,
    discover_public_constructors,
    discover_public_fields,
    discover_public_methods,
)
from .semantic_types import (
    RecordSemanticType,
    SemanticCppType,
    VoidSemanticType,
    analyze_cpp_type,
)


@dataclass(frozen=True)
class SourceClassRequest:
    cpp_name: str
    translation_unit: Path
    include_methods: bool = True
    include_constructors: bool = True
    include_fields: bool = True
    include_bases: bool = True
    include_inherited_methods: bool = False
    include_inherited_fields: bool = False
    selected_methods: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SourceNamespaceRequest:
    namespace: str
    translation_unit: Path
    selected_functions: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SourceInventoryRequest:
    environment: DiscoveryEnvironment
    classes: tuple[SourceClassRequest, ...] = ()
    namespaces: tuple[SourceNamespaceRequest, ...] = ()


@dataclass(frozen=True)
class SourceTypeInventory:
    cpp_type: str
    semantic: SemanticCppType
    ownership_hint: str


@dataclass(frozen=True)
class SourceParamInventory:
    name: str
    type: SourceTypeInventory


@dataclass(frozen=True)
class SourceCallableInventory:
    cpp_name: str
    return_type: SourceTypeInventory | None
    params: tuple[SourceParamInventory, ...]


@dataclass(frozen=True)
class SourceClassInventory:
    cpp_name: str
    translation_unit: Path
    methods: dict[str, tuple[DiscoveredMethod, ...]]
    constructors: tuple[DiscoveredConstructor, ...]
    fields: dict[str, DiscoveredField]
    bases: tuple[DiscoveredBase, ...]
    method_semantics: dict[str, tuple[SourceCallableInventory, ...]]
    constructor_semantics: tuple[SourceCallableInventory, ...]
    field_semantics: dict[str, SourceTypeInventory]
    base_semantics: tuple[SourceTypeInventory, ...]


@dataclass(frozen=True)
class SourceNamespaceInventory:
    namespace: str
    translation_unit: Path
    functions: dict[str, tuple[DiscoveredFunction, ...]]
    function_semantics: dict[str, tuple[SourceCallableInventory, ...]]


@dataclass(frozen=True)
class SourceInventory:
    classes: dict[tuple[str, Path], SourceClassInventory]
    namespaces: dict[tuple[str, Path], SourceNamespaceInventory]


def _selected_names(names: Iterable[str] | None) -> tuple[str, ...] | None:
    if names is None:
        return None
    return tuple(sorted(set(names)))


def _ownership_hint(cpp_type) -> str:
    semantic = analyze_cpp_type(cpp_type)
    if isinstance(semantic, VoidSemanticType):
        return "void"
    if (
        isinstance(semantic, RecordSemanticType)
        and semantic.pointer_wrapper is not None
    ):
        return semantic.pointer_wrapper
    pointer_depth = getattr(cpp_type, "pointer_depth", 0)
    if pointer_depth:
        return "raw_pointer"
    if getattr(cpp_type, "is_lvalue_reference", False):
        return "borrowed_reference"
    if getattr(cpp_type, "is_rvalue_reference", False):
        return "rvalue_reference"
    return "value"


def _source_type(cpp_type) -> SourceTypeInventory:
    semantic = analyze_cpp_type(cpp_type)
    return SourceTypeInventory(
        cpp_type=getattr(cpp_type, "storage_spelling", None)
        or getattr(cpp_type, "cpp_type", None)
        or str(cpp_type),
        semantic=semantic,
        ownership_hint=_ownership_hint(cpp_type),
    )


def _params(params) -> tuple[SourceParamInventory, ...]:
    return tuple(
        SourceParamInventory(name=param.name, type=_source_type(param.cpp_type_ref))
        for param in params
    )


def _method_semantics(
    methods: dict[str, tuple[DiscoveredMethod, ...]],
) -> dict[str, tuple[SourceCallableInventory, ...]]:
    return {
        name: tuple(
            SourceCallableInventory(
                cpp_name=method.cpp_name,
                return_type=_source_type(method.return_type_ref),
                params=_params(method.params),
            )
            for method in overloads
        )
        for name, overloads in methods.items()
    }


def _constructor_semantics(
    constructors: tuple[DiscoveredConstructor, ...],
) -> tuple[SourceCallableInventory, ...]:
    return tuple(
        SourceCallableInventory(
            cpp_name=constructor.cpp_name,
            return_type=None,
            params=_params(constructor.params),
        )
        for constructor in constructors
    )


def _field_semantics(
    fields: dict[str, DiscoveredField],
) -> dict[str, SourceTypeInventory]:
    return {name: _source_type(field.cpp_type_ref) for name, field in fields.items()}


def _base_semantics(
    bases: tuple[DiscoveredBase, ...],
) -> tuple[SourceTypeInventory, ...]:
    return tuple(_source_type(base.cpp_type_ref) for base in bases)


def _function_semantics(
    functions: dict[str, tuple[DiscoveredFunction, ...]],
) -> dict[str, tuple[SourceCallableInventory, ...]]:
    return {
        name: tuple(
            SourceCallableInventory(
                cpp_name=function.cpp_name,
                return_type=_source_type(function.return_type_ref),
                params=_params(function.params),
            )
            for function in overloads
        )
        for name, overloads in functions.items()
    }


def discover_source_inventory(request: SourceInventoryRequest) -> SourceInventory:
    classes: dict[tuple[str, Path], SourceClassInventory] = {}
    namespaces: dict[tuple[str, Path], SourceNamespaceInventory] = {}

    for item in request.classes:
        key = (item.cpp_name, item.translation_unit.resolve())
        selected_methods = _selected_names(item.selected_methods)
        methods = (
            discover_public_methods(
                request.environment,
                item.translation_unit,
                item.cpp_name,
                include_inherited=item.include_inherited_methods,
                selected_names=selected_methods,
            )
            if item.include_methods
            else {}
        )
        constructors = (
            discover_public_constructors(
                request.environment, item.translation_unit, item.cpp_name
            )
            if item.include_constructors
            else ()
        )
        fields = (
            discover_public_fields(
                request.environment,
                item.translation_unit,
                item.cpp_name,
                include_inherited=item.include_inherited_fields,
            )
            if item.include_fields
            else {}
        )
        bases = (
            discover_base_types(
                request.environment, item.translation_unit, item.cpp_name
            )
            if item.include_bases
            else ()
        )
        classes[key] = SourceClassInventory(
            cpp_name=item.cpp_name,
            translation_unit=item.translation_unit,
            methods=methods,
            constructors=constructors,
            fields=fields,
            bases=bases,
            method_semantics=_method_semantics(methods),
            constructor_semantics=_constructor_semantics(constructors),
            field_semantics=_field_semantics(fields),
            base_semantics=_base_semantics(bases),
        )

    for item in request.namespaces:
        key = (item.namespace, item.translation_unit.resolve())
        functions = discover_namespace_functions(
            request.environment,
            item.translation_unit,
            item.namespace,
            selected_names=_selected_names(item.selected_functions),
        )
        namespaces[key] = SourceNamespaceInventory(
            namespace=item.namespace,
            translation_unit=item.translation_unit,
            functions=functions,
            function_semantics=_function_semantics(functions),
        )

    return SourceInventory(classes=classes, namespaces=namespaces)
