from __future__ import annotations

import pytest

from src.ifcwrap.binding_generator.abi_ir import finalize_abi
from src.ifcwrap.binding_generator.binding_ir import (
    BindingIR,
    CallIR,
    DirectCallOp,
    lower_binding_spec,
)
from src.ifcwrap.binding_generator.binding_model import (
    CallSpec,
    HandleSpec,
    ParamSpec,
    ResultStructFieldSpec,
    ResultStructSpec,
    TypeSpec,
)
from src.ifcwrap.binding_generator.discovery_policy import MergedBindingSpec
from src.ifcwrap.binding_generator.policy_ir import (
    ConstructorPolicyOp,
    DirectFunctionPolicyOp,
    DirectMethodPolicyOp,
)


def test_finalized_abi_derives_layouts_and_signatures() -> None:
    handles = {
        name: HandleSpec(
            name=name,
            cpp_type=f"Demo::{name.title()}",
            c_type=f"ifcopenshell_demo_{name}_t",
            destructor="delete",
        )
        for name in ("file", "item")
    }
    functions = (
        CallSpec(
            expose_as="create_file",
            c_name="ifcopenshell_demo_create_file",
            receiver=None,
            returns=TypeSpec(kind="handle", handle="file", ownership="owned"),
            params=(ParamSpec("schema", TypeSpec(kind="string")),),
            policy_operation=ConstructorPolicyOp(),
        ),
        CallSpec(
            expose_as="schema_names",
            c_name="ifcopenshell_demo_schema_names",
            receiver=None,
            returns=TypeSpec(kind="string", sequence_depth=1),
            params=(),
            policy_operation=DirectFunctionPolicyOp("schema_names"),
        ),
    )
    methods = tuple(
        CallSpec(
            expose_as=name,
            c_name=f"ifcopenshell_demo_{receiver}_{name}",
            receiver=receiver,
            returns=returns,
            params=(ParamSpec(param_name, param_type),),
            policy_operation=DirectMethodPolicyOp(name),
        )
        for receiver, name, returns, param_name, param_type in (
            (
                "file",
                "by_type",
                TypeSpec(
                    kind="handle", handle="item", ownership="owned", sequence_depth=1
                ),
                "type_name",
                TypeSpec(kind="string"),
            ),
            (
                "item",
                "set_values",
                TypeSpec(kind="void"),
                "values",
                TypeSpec(kind="double", sequence_depth=1),
            ),
            (
                "item",
                "set_counts",
                TypeSpec(kind="void"),
                "values",
                TypeSpec(kind="int64", sequence_depth=1),
            ),
        )
    )
    metadata = finalize_abi(
        lower_binding_spec(
            MergedBindingSpec(
                module="demo",
                c_prefix="ifcopenshell_demo",
                public_headers=("demo.h",),
                handles=handles,
                result_structs={},
                functions=functions,
                methods=methods,
            )
        )
    )

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
        ("CANCELLED", 4),
    ]
    assert [(entry.name, entry.value) for entry in metadata.error_catalog.codes] == [
        ("NONE", 0),
        ("UNSPECIFIED", 1),
        ("INVALID_ARGUMENT", 2),
        ("DOMAIN_ERROR", 3),
        ("OPERATION_CANCELLED", 4),
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
    assert "demo_item_list_list" not in metadata.value_types

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


def test_finalized_abi_preserves_result_field_docs() -> None:
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
        )
    )

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
