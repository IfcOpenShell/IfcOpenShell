from __future__ import annotations

import keyword
import re

INTEGER_CPP_TYPES = {"int", "size_t", "std::size_t", "unsigned int", "uint32_t"}


def normalize_identifier(name: str) -> str:
    result: list[str] = []
    previous_was_lower = False
    for character in name:
        if character.isupper() and previous_was_lower:
            result.append("_")
        result.append(character.lower() if character.isalnum() else "_")
        previous_was_lower = character.islower() or character.isdigit()
    normalized = "".join(result).strip("_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized


def cpp_leaf_name(cpp_name: str) -> str:
    return cpp_name.rsplit("::", 1)[-1]


def pascal_case(name: str) -> str:
    parts = [part for part in re.split(r"[_\W]+", name) if part]
    if parts:
        return "".join(part[:1].upper() + part[1:] for part in parts)
    return name[:1].upper() + name[1:] if name else name


def safe_python_identifier(name: str) -> str:
    return f"{name}_" if keyword.iskeyword(name) else name


def normalize_cpp_type(cpp_type: str) -> str:
    normalized = cpp_type.replace("class ", "").replace("struct ", "").replace("enum ", "")
    normalized = normalized.replace("std::basic_string<char>", "std::string")
    normalized = normalized.replace("std::__cxx11::basic_string<char>", "std::string")
    normalized = re.sub(r"\b(const|volatile)\b", " ", normalized)
    normalized = normalized.replace("&", " ")
    normalized = re.sub(r"\s+", "", normalized)
    return normalized


def strip_pointer(cpp_type: str) -> str:
    normalized = normalize_cpp_type(cpp_type)
    while normalized.endswith("*"):
        normalized = normalized[:-1]
    return normalized


def c_identifier_from_cpp_name(cpp_name: str, c_prefix: str | None = None) -> str:
    parts = [part for part in cpp_name.split("::") if part]
    if c_prefix and parts and normalize_identifier(parts[0]) == normalize_identifier(c_prefix):
        parts = parts[1:]
    return normalize_identifier("_".join(parts))


def default_enum_c_name(c_prefix: str, py_name: str) -> str:
    return f"{c_prefix}_{normalize_identifier(py_name)}_t"


def default_enum_value_c_name(enum_c_name: str, value_name: str) -> str:
    return f"{enum_c_name.upper()}_{value_name}"


def handle_adapter_name(cpp_name: str) -> str:
    return f"handle:{normalize_cpp_type(cpp_name)}"


def is_handle_adapter(adapter: str) -> bool:
    return adapter.startswith("handle:")


def handle_adapter_target(adapter: str) -> str:
    return adapter.split(":", 1)[1]


def enum_adapter_name(cpp_name: str) -> str:
    return f"enum:{normalize_cpp_type(cpp_name)}"


def is_enum_adapter(adapter: str) -> bool:
    return adapter.startswith("enum:")


def enum_adapter_target(adapter: str) -> str:
    return adapter.split(":", 1)[1]


def sequence_adapter_name(cpp_name: str) -> str:
    return f"sequence:{normalize_cpp_type(cpp_name)}"


def is_sequence_adapter(adapter: str) -> bool:
    return adapter.startswith("sequence:")


def sequence_adapter_target(adapter: str) -> str:
    return adapter.split(":", 1)[1]


def cpp_type_lists_match(actual_types: list[str], expected_types: list[str]) -> bool:
    if len(actual_types) != len(expected_types):
        return False
    return all(cpp_types_equivalent(actual, expected) for actual, expected in zip(actual_types, expected_types))


def cpp_types_equivalent(actual_type: str, expected_type: str) -> bool:
    actual = normalize_cpp_type(actual_type)
    expected = normalize_cpp_type(expected_type)
    if actual == expected:
        return True
    if "<" in actual or "<" in expected:
        return False
    actual_leaf = strip_pointer(actual).rsplit("::", 1)[-1]
    expected_leaf = strip_pointer(expected).rsplit("::", 1)[-1]
    return actual_leaf == expected_leaf


def resolve_cpp_type_key(cpp_type: str, candidates: set[str]) -> str | None:
    canonical = normalize_cpp_type(cpp_type)
    if canonical in candidates:
        return canonical
    leaf = strip_pointer(canonical).rsplit("::", 1)[-1]
    matches = [candidate for candidate in candidates if strip_pointer(candidate).rsplit("::", 1)[-1] == leaf]
    if len(matches) == 1:
        return matches[0]
    return None
