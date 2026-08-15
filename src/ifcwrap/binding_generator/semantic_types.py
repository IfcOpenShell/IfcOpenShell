# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

import re
from dataclasses import dataclass

from .clang_discovery import DiscoveredCppType


def _normalize_cpp_type(text: str) -> str:
    return " ".join(
        text.replace(" &", "&")
        .replace(" *", "*")
        .replace("< ", "<")
        .replace(" >", ">")
        .split()
    )


def _strip_qualifiers(text: str) -> str:
    normalized = _normalize_cpp_type(text)
    while normalized.startswith("const "):
        normalized = normalized[len("const ") :].strip()
    while normalized.endswith("&") or normalized.endswith("*"):
        normalized = normalized[:-1].strip()
    return normalized


def _split_template_args(text: str) -> tuple[str, ...]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        if char == "<":
            depth += 1
            current.append(char)
            continue
        if char == ">":
            depth = max(0, depth - 1)
            current.append(char)
            continue
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return tuple(parts)


def _template_match(text: str, template_name: str) -> tuple[str, ...] | None:
    normalized = _strip_qualifiers(text)
    prefix = f"{template_name}<"
    if not normalized.startswith(prefix) or not normalized.endswith(">"):
        return None
    inner = normalized[len(prefix) : -1].strip()
    return _split_template_args(inner)


@dataclass(frozen=True)
class VoidSemanticType:
    cpp_type: str


@dataclass(frozen=True)
class ScalarSemanticType:
    family: str
    cpp_type: str


@dataclass(frozen=True)
class StringSemanticType:
    cpp_type: str


@dataclass(frozen=True)
class EnumSemanticType:
    cpp_type: str
    enum_qualified_name: str | None
    values: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class RecordSemanticType:
    cpp_type: str
    base_name: str
    base_record_names: tuple[str, ...]
    pointee: SemanticCppType | None = None
    pointer_wrapper: str | None = None


@dataclass(frozen=True)
class SequenceSemanticType:
    cpp_type: str
    container_kind: str
    element: SemanticCppType
    fixed_length: int | None = None
    alias: str | None = None


@dataclass(frozen=True)
class OptionalSemanticType:
    cpp_type: str
    element: SemanticCppType


@dataclass(frozen=True)
class VariantSemanticType:
    cpp_type: str
    alternatives: tuple[SemanticCppType, ...]


@dataclass(frozen=True)
class UnsupportedSemanticType:
    cpp_type: str
    reason: str


SemanticCppType = (
    VoidSemanticType
    | ScalarSemanticType
    | StringSemanticType
    | EnumSemanticType
    | RecordSemanticType
    | SequenceSemanticType
    | OptionalSemanticType
    | VariantSemanticType
    | UnsupportedSemanticType
)


def _scalar_family_from_base(base_name: str, *, normalized: str) -> str | None:
    if base_name == "void":
        return "void"
    if base_name == "bool":
        return "bool"
    if base_name in {"int", "int32_t", "ptrdiff_t"}:
        return "int32"
    if base_name in {"int64_t", "std::int64_t", "long long"}:
        return "int64"
    if base_name in {"unsigned", "unsigned int", "uint32_t"}:
        return "uint32"
    if base_name in {"size_t", "std::size_t", "unsigned long"}:
        return "size"
    if base_name in {"double", "float"}:
        return "double"
    if base_name in {"uint8_t", "std::uint8_t", "unsigned char"}:
        return "uint8"
    if (base_name == "char" and normalized.endswith("*")) or base_name == "std::string":
        return "string"
    return None


def _from_discovered(cpp_type: DiscoveredCppType) -> SemanticCppType:
    cpp_text = (
        cpp_type.storage_spelling
        or cpp_type.canonical_spelling
        or cpp_type.normalized_spelling
        or cpp_type.spelling
    )
    normalized = _normalize_cpp_type(cpp_text)

    if cpp_type.is_enum:
        return EnumSemanticType(
            cpp_type=cpp_text,
            enum_qualified_name=cpp_type.enum_qualified_name,
            values=cpp_type.enum_values,
        )

    if (
        cpp_type.template_name in {"std::vector", "std::set", "std::array"}
        and cpp_type.template_args
    ):
        return SequenceSemanticType(
            cpp_type=cpp_text,
            container_kind=cpp_type.template_name,
            element=analyze_cpp_type(cpp_type.template_args[0]),
            fixed_length=(
                int(cpp_type.template_args[1].spelling)
                if cpp_type.template_name == "std::array"
                and len(cpp_type.template_args) > 1
                and cpp_type.template_args[1].spelling.isdigit()
                else None
            ),
            alias=(
                _strip_qualifiers(cpp_type.normalized_spelling)
                if cpp_type.normalized_desugared_spelling
                and cpp_type.normalized_spelling
                != cpp_type.normalized_desugared_spelling
                and "<" not in _strip_qualifiers(cpp_type.normalized_spelling)
                else None
            ),
        )

    if cpp_type.template_name == "std::optional" and cpp_type.template_args:
        return OptionalSemanticType(
            cpp_type=cpp_text,
            element=analyze_cpp_type(cpp_type.template_args[0]),
        )

    if cpp_type.template_name == "std::variant" and cpp_type.template_args:
        return VariantSemanticType(
            cpp_type=cpp_text,
            alternatives=tuple(analyze_cpp_type(arg) for arg in cpp_type.template_args),
        )

    if (
        cpp_type.template_name
        in {"std::shared_ptr", "boost::shared_ptr", "std::unique_ptr"}
        and cpp_type.template_args
    ):
        pointee = analyze_cpp_type(cpp_type.template_args[0])
        return RecordSemanticType(
            cpp_type=cpp_text,
            base_name=cpp_type.base_name,
            base_record_names=cpp_type.base_record_names,
            pointee=pointee,
            pointer_wrapper="unique_ptr"
            if cpp_type.template_name == "std::unique_ptr"
            else "shared_ptr",
        )

    family = _scalar_family_from_base(cpp_type.base_name, normalized=normalized)
    if family == "void":
        if normalized != "void":
            return UnsupportedSemanticType(
                cpp_type=cpp_text, reason="opaque void pointer/reference"
            )
        return VoidSemanticType(cpp_type=cpp_text)
    if family == "string":
        return StringSemanticType(cpp_type=cpp_text)
    if family is not None:
        return ScalarSemanticType(family=family, cpp_type=cpp_text)

    return RecordSemanticType(
        cpp_type=cpp_text,
        base_name=cpp_type.base_name,
        base_record_names=cpp_type.base_record_names,
    )


def _from_string(cpp_type: str) -> SemanticCppType:
    normalized = _normalize_cpp_type(cpp_type)
    for template_name in ("std::vector", "std::set", "std::array"):
        args = _template_match(normalized, template_name)
        if args:
            return SequenceSemanticType(
                cpp_type=normalized,
                container_kind=template_name,
                element=analyze_cpp_type(args[0]),
                fixed_length=(
                    int(args[1])
                    if template_name == "std::array"
                    and len(args) > 1
                    and args[1].isdigit()
                    else None
                ),
            )

    args = _template_match(normalized, "std::optional")
    if args:
        return OptionalSemanticType(
            cpp_type=normalized,
            element=analyze_cpp_type(args[0]),
        )

    args = _template_match(normalized, "std::variant")
    if args:
        return VariantSemanticType(
            cpp_type=normalized,
            alternatives=tuple(analyze_cpp_type(arg) for arg in args),
        )

    for pointer_name, wrapper_kind in (
        ("std::shared_ptr", "shared_ptr"),
        ("boost::shared_ptr", "shared_ptr"),
        ("std::unique_ptr", "unique_ptr"),
    ):
        pointer_args = _template_match(normalized, pointer_name)
        if pointer_args:
            pointee = analyze_cpp_type(pointer_args[0])
            return RecordSemanticType(
                cpp_type=normalized,
                base_name=pointer_name,
                base_record_names=(),
                pointee=pointee,
                pointer_wrapper=wrapper_kind,
            )

    core = _strip_qualifiers(normalized)
    family = _scalar_family_from_base(core, normalized=normalized)
    if family == "void":
        if normalized != "void":
            return UnsupportedSemanticType(
                cpp_type=normalized, reason="opaque void pointer/reference"
            )
        return VoidSemanticType(cpp_type=normalized)
    if family == "string":
        return StringSemanticType(cpp_type=normalized)
    if family is not None:
        return ScalarSemanticType(family=family, cpp_type=normalized)

    return RecordSemanticType(cpp_type=normalized, base_name=core, base_record_names=())


def analyze_cpp_type(cpp_type: str | DiscoveredCppType) -> SemanticCppType:
    if isinstance(cpp_type, DiscoveredCppType):
        return _from_discovered(cpp_type)
    return _from_string(cpp_type)


def semantic_record_match_names(semantic: RecordSemanticType) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()

    def push(value: str | None) -> None:
        if value and value not in seen:
            seen.add(value)
            names.append(value)

    push(_strip_qualifiers(semantic.cpp_type))
    push(semantic.base_name)
    for base in semantic.base_record_names:
        push(base)
    if isinstance(semantic.pointee, RecordSemanticType):
        push(_strip_qualifiers(semantic.pointee.cpp_type))
        push(semantic.pointee.base_name)
        for base in semantic.pointee.base_record_names:
            push(base)
    return tuple(names)


def semantic_sequence_depth(semantic: SemanticCppType) -> int:
    depth = 0
    current = semantic
    while isinstance(current, SequenceSemanticType):
        depth += 1
        current = current.element
    return depth


def semantic_sequence_lengths(
    semantic: SemanticCppType,
) -> tuple[int | None, ...]:
    lengths: list[int | None] = []
    current = semantic
    while isinstance(current, SequenceSemanticType):
        lengths.append(current.fixed_length)
        current = current.element
    return tuple(lengths)


def semantic_sequence_alias(semantic: SemanticCppType) -> str | None:
    current = semantic
    while isinstance(current, SequenceSemanticType):
        if current.alias:
            return current.alias.rsplit("::", 1)[-1]
        current = current.element
    return None


def semantic_leaf_type(semantic: SemanticCppType) -> SemanticCppType:
    current = semantic
    while isinstance(current, SequenceSemanticType):
        current = current.element
    return current
