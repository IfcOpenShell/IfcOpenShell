# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from src.ifcwrap.binding_generator.abi_ir import finalize_abi
from src.ifcwrap.binding_generator.authored_spec import load_authored_spec
from src.ifcwrap.binding_generator.binding_ir import (
    BindingIR,
    CallIR,
    DirectCallOp,
    lower_binding_spec,
)
from src.ifcwrap.binding_generator.binding_model import (
    HandleSpec,
    OptionStructFieldSpec,
    OptionStructSpec,
    ParamSpec,
    ResultStructFieldSpec,
    ResultStructSpec,
    TypeSpec,
)


def test_finalized_abi_derives_layouts_and_signatures(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo.yml"
    spec_path.write_text(
        dedent(
            """
            schema_version: 1
            module: demo
            slice: demo
            c_prefix: ifcopenshell_demo
            public_headers:
              - demo.h
            handles:
              - name: file
                cpp_type: Demo::File
                c_type: ifcopenshell_demo_file_t
                destructor: delete
              - name: item
                cpp_type: Demo::Item
                c_type: ifcopenshell_demo_item_t
                destructor: delete
            functions:
              - expose_as: create_file
                handle: file
                params:
                  - name: schema
                    type:
                      kind: string
              - expose_as: schema_names
                cpp_name: schema_names
                returns:
                  kind: string_list
                params: []
            methods:
              - receiver: file
                expose_as: by_type
                cpp_name: by_type
                returns:
                  kind: handle_list
                  handle: item
                  ownership: owned
                params:
                  - name: type_name
                    type:
                      kind: string
              - receiver: item
                expose_as: set_values
                cpp_name: set_values
                returns:
                  kind: void
                params:
                  - name: values
                    type:
                      kind: double_list
              - receiver: item
                expose_as: set_counts
                cpp_name: set_counts
                returns:
                  kind: void
                params:
                  - name: values
                    type:
                      kind: int64_list
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    metadata = finalize_abi(lower_binding_spec(load_authored_spec(spec_path)))

    assert metadata.error_functions == {
        "clear_error": "ifcopenshell_demo_clear_error",
        "last_error_message": "ifcopenshell_demo_last_error_message",
        "last_error_kind": "ifcopenshell_demo_last_error_kind",
        "last_error_code": "ifcopenshell_demo_last_error_code",
    }
    assert [(entry.name, entry.value) for entry in metadata.error_catalog.kinds] == [
        ("NONE", 0),
        ("RUNTIME", 1),
        ("VALUE", 2),
        ("TYPE", 3),
    ]
    assert [(entry.name, entry.value) for entry in metadata.error_catalog.codes] == [
        ("NONE", 0),
        ("UNSPECIFIED", 1),
        ("INVALID_ARGUMENT", 2),
        ("DOMAIN_ERROR", 3),
    ]
    assert metadata.handles["file"].layout == "ptr_owned"
    assert metadata.handles["file"].fields[0].c_type == "void*"
    assert metadata.handles["file"].destroy_function == "ifcopenshell_demo_file_destroy"

    assert metadata.value_types["string"].fields[0].name == "data"
    assert (
        metadata.value_types["string_list"].destroy_function
        == "ifcopenshell_string_list_destroy"
    )
    assert metadata.value_types["double_list"].fields[0].c_type == "double*"
    assert metadata.value_types["int64_list"].fields[0].c_type == "int64_t*"
    assert (
        metadata.value_types["demo_item_list"].fields[0].c_type
        == "ifcopenshell_demo_item_t**"
    )
    assert (
        metadata.value_types["demo_item_list_list"].fields[0].c_type
        == "ifcopenshell_demo_item_list_t*"
    )

    create = metadata.functions["ifcopenshell_demo_create_file"]
    assert create.restype == "bool"
    assert [param.c_type for param in create.params] == [
        "const char*",
        "ifcopenshell_demo_file_t**",
    ]
    assert create.params[-1].role == "out_result"
    assert create.error_policy == "bool_return_last_error"

    by_type = metadata.functions["ifcopenshell_demo_file_by_type"]
    assert [param.role for param in by_type.params] == [
        "receiver",
        "param",
        "out_result",
    ]
    assert [param.c_type for param in by_type.params] == [
        "ifcopenshell_demo_file_t*",
        "const char*",
        "ifcopenshell_demo_item_list_t*",
    ]

    set_values = metadata.functions["ifcopenshell_demo_item_set_values"]
    assert [param.c_type for param in set_values.params] == [
        "ifcopenshell_demo_item_t*",
        "const ifcopenshell_double_list_t*",
    ]

    set_counts = metadata.functions["ifcopenshell_demo_item_set_counts"]
    assert [param.c_type for param in set_counts.params] == [
        "ifcopenshell_demo_item_t*",
        "const ifcopenshell_int64_list_t*",
    ]


def test_finalized_abi_includes_sequences_used_only_by_option_structs() -> None:
    metadata = finalize_abi(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={
                "item": HandleSpec(
                    name="item",
                    cpp_type="Demo::Item",
                    c_type="ifcopenshell_demo_item_t",
                    destructor="delete",
                ),
            },
            result_structs={},
            calls=(
                CallIR(
                    expose_as="add_mesh",
                    c_name="ifcopenshell_demo_add_mesh",
                    receiver=None,
                    returns=TypeSpec(kind="void"),
                    params=(
                        ParamSpec(
                            "options", TypeSpec(kind="option", struct="AddMeshOptions")
                        ),
                    ),
                    operation=DirectCallOp(cpp_name="Demo::add_mesh"),
                ),
            ),
            option_structs={
                "AddMeshOptions": OptionStructSpec(
                    name="AddMeshOptions",
                    cpp_type="Demo::AddMeshOptions",
                    c_type="ifcopenshell_demo_add_mesh_options_t",
                    fields=(
                        OptionStructFieldSpec(
                            "faces", TypeSpec(kind="int32", sequence_depth=4)
                        ),
                        OptionStructFieldSpec(
                            "grouped_items",
                            TypeSpec(kind="handle", handle="item", sequence_depth=2),
                        ),
                    ),
                ),
            },
        )
    )

    assert "int32_list" in metadata.value_types
    assert "int32_list_list_list_list" in metadata.value_types
    assert metadata.value_types["int32_list_list_list_list"].sequence_depth == 4
    assert "demo_item_list" in metadata.value_types
    assert "demo_item_list_list" in metadata.value_types


def test_finalized_abi_preserves_option_and_result_field_docs() -> None:
    metadata = finalize_abi(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={},
            result_structs={
                "DemoResult": ResultStructSpec(
                    name="DemoResult",
                    cpp_type="Demo::Result",
                    c_type="ifcopenshell_demo_result_t",
                    fields=(
                        ResultStructFieldSpec(
                            "value",
                            TypeSpec(kind="double"),
                            doc="Result value in model units.",
                        ),
                        ResultStructFieldSpec("undocumented", TypeSpec(kind="bool")),
                    ),
                )
            },
            calls=(),
            option_structs={
                "DemoOptions": OptionStructSpec(
                    name="DemoOptions",
                    cpp_type="Demo::Options",
                    c_type="ifcopenshell_demo_options_t",
                    fields=(
                        OptionStructFieldSpec(
                            "enabled",
                            TypeSpec(kind="bool", nullable=True),
                            doc="Whether the feature is enabled.\n\nOptional in the input.",
                        ),
                        OptionStructFieldSpec("undocumented", TypeSpec(kind="string")),
                    ),
                )
            },
        )
    )

    option_fields = {
        field.name: field for field in metadata.option_structs["DemoOptions"].fields
    }
    assert (
        option_fields["enabled"].doc
        == "Whether the feature is enabled.\n\nOptional in the input."
    )
    assert option_fields["undocumented"].doc is None

    result_fields = {
        field.name: field for field in metadata.value_types["DemoResult"].fields
    }
    assert result_fields["value"].doc == "Result value in model units."
    assert result_fields["undocumented"].doc is None


def test_finalization_rejects_unresolved_types_with_call_context() -> None:
    ir = BindingIR(
        module="demo",
        c_prefix="ifcopenshell_demo",
        public_headers=(),
        handles={},
        result_structs={},
        calls=(
            CallIR(
                expose_as="inspect",
                c_name="ifcopenshell_demo_inspect",
                receiver=None,
                returns=TypeSpec(kind="void"),
                params=(ParamSpec("item", TypeSpec(kind="handle", handle="item")),),
                operation=DirectCallOp(cpp_name="Demo::inspect"),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="call ifcopenshell_demo_inspect parameter 'item': unknown handle 'item'",
    ):
        finalize_abi(ir)


def test_finalization_rejects_empty_variants_with_field_context() -> None:
    ir = BindingIR(
        module="demo",
        c_prefix="ifcopenshell_demo",
        public_headers=(),
        handles={},
        result_structs={
            "DemoResult": ResultStructSpec(
                name="DemoResult",
                cpp_type="Demo::Result",
                c_type="ifcopenshell_demo_result_t",
                fields=(ResultStructFieldSpec("value", TypeSpec(kind="variant")),),
            )
        },
        calls=(),
    )

    with pytest.raises(
        ValueError,
        match="result struct DemoResult field 'value': variant has no alternatives",
    ):
        finalize_abi(ir)


def test_finalization_rejects_unsupported_types_with_call_context() -> None:
    ir = BindingIR(
        module="demo",
        c_prefix="ifcopenshell_demo",
        public_headers=(),
        handles={},
        result_structs={},
        calls=(
            CallIR(
                expose_as="inspect",
                c_name="ifcopenshell_demo_inspect",
                receiver=None,
                returns=TypeSpec(kind="void"),
                params=(ParamSpec("item", TypeSpec(kind="mystery")),),
                operation=DirectCallOp(cpp_name="Demo::inspect"),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="call ifcopenshell_demo_inspect: Unsupported parameter kind: mystery",
    ):
        finalize_abi(ir)
