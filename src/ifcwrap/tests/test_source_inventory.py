# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src.ifcwrap.binding_generator import (
    CompilationConfig,
    DiscoveryEnvironment,
    SourceClassRequest,
    SourceInventoryRequest,
    SourceNamespaceRequest,
    discover_source_inventory,
)
from src.ifcwrap.binding_generator.semantic_types import (
    RecordSemanticType,
    ScalarSemanticType,
)


def test_source_inventory_discovers_classes_and_namespaces(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "inventory.h"
    source = tmp_path / "inventory.cpp"
    header.write_text(
        """
namespace Demo {
struct Base {
public:
    int inherited() const;
};

struct Widget : Base {
public:
    Widget();
    int value() const;
    int field;
};

int make_count(int value);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "inventory.h"\n', encoding="utf-8")
    environment = DiscoveryEnvironment(
        compilation=CompilationConfig(
            compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
        )
    )

    inventory = discover_source_inventory(
        SourceInventoryRequest(
            environment=environment,
            classes=(
                SourceClassRequest(
                    cpp_name="Demo::Widget",
                    translation_unit=source,
                    include_inherited_methods=True,
                    selected_methods=("value", "inherited"),
                ),
            ),
            namespaces=(
                SourceNamespaceRequest(
                    namespace="Demo",
                    translation_unit=source,
                    selected_functions=("make_count",),
                ),
            ),
        )
    )

    widget = inventory.classes[("Demo::Widget", source.resolve())]
    assert set(widget.methods) == {"value", "inherited"}
    assert widget.constructors[0].class_name == "Demo::Widget"
    assert set(widget.fields) == {"field"}
    assert widget.bases[0].cpp_type_ref.base_name == "Demo::Base"
    assert set(inventory.namespaces[("Demo", source.resolve())].functions) == {
        "make_count"
    }
    assert isinstance(
        widget.method_semantics["value"][0].return_type.semantic, ScalarSemanticType
    )
    assert widget.method_semantics["value"][0].return_type.semantic.family == "int32"
    assert widget.constructor_semantics[0].return_type is None
    assert isinstance(widget.field_semantics["field"].semantic, ScalarSemanticType)
    assert widget.field_semantics["field"].ownership_hint == "value"
    assert isinstance(widget.base_semantics[0].semantic, RecordSemanticType)
    make_count = inventory.namespaces[("Demo", source.resolve())].function_semantics[
        "make_count"
    ][0]
    assert isinstance(make_count.return_type.semantic, ScalarSemanticType)
    assert make_count.params[0].type.ownership_hint == "value"
