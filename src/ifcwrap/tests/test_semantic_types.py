from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src.ifcwrap.binding_generator.clang_discovery import (
    CompilationConfig,
    DiscoveryEnvironment,
    discover_public_fields,
)
from src.ifcwrap.binding_generator.semantic_types import (
    OptionalSemanticType,
    RecordSemanticType,
    ScalarSemanticType,
    SequenceSemanticType,
    StringSemanticType,
    UnsupportedSemanticType,
    analyze_cpp_type,
)


def test_analyze_cpp_type_parses_recursive_standard_sequences() -> None:
    semantic = analyze_cpp_type("const std::vector<std::vector<int>>&")
    assert isinstance(semantic, SequenceSemanticType)
    assert semantic.container_kind == "std::vector"
    assert isinstance(semantic.element, SequenceSemanticType)
    assert semantic.element.container_kind == "std::vector"
    assert isinstance(semantic.element.element, ScalarSemanticType)
    assert semantic.element.element.family == "int32"

    string_set = analyze_cpp_type("const std::set<std::string>&")
    assert isinstance(string_set, SequenceSemanticType)
    assert string_set.container_kind == "std::set"
    assert isinstance(string_set.element, StringSemanticType)


def test_analyze_cpp_type_rejects_void_pointers() -> None:
    semantic = analyze_cpp_type("void*")
    assert isinstance(semantic, UnsupportedSemanticType)
    assert semantic.reason == "opaque void pointer/reference"


def test_analyze_cpp_type_parses_optional_string() -> None:
    semantic = analyze_cpp_type("std::optional<std::string>")

    assert isinstance(semantic, OptionalSemanticType)
    assert isinstance(semantic.element, StringSemanticType)


def test_analyze_cpp_type_parses_shared_ptr_aliases_from_discovery(
    tmp_path: Path,
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "shared_ptr_alias.h"
    source = tmp_path / "shared_ptr_alias.cpp"

    header.write_text(
        """
#include <memory>

namespace Demo {
struct Node {
    using ptr = std::shared_ptr<Node>;
};

struct Holder {
    Node::ptr axis;
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "shared_ptr_alias.h"\n', encoding="utf-8")

    environment = DiscoveryEnvironment(
        compilation=CompilationConfig(
            compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
        )
    )
    fields = discover_public_fields(environment, source, "Demo::Holder")
    semantic = analyze_cpp_type(fields["axis"].cpp_type_ref)

    assert isinstance(semantic, RecordSemanticType)
    assert semantic.pointer_wrapper == "shared_ptr"
    assert isinstance(semantic.pointee, RecordSemanticType)
    assert semantic.pointee.base_name == "Demo::Node"
