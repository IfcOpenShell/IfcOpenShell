from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .abi_ir import BindingABI

from .binding_model import (
    CallSpec,
    HandleSpec,
    ImplementationSpec,
    OptionStructSpec,
    ParamSpec,
    ResultStructSpec,
    TypeSpec,
)
from .debug import debug_log
from .discovery_policy import MergedBindingSpec
from .policy_ir import (
    ArrayElementFieldPolicyOp,
    AsItemCastPolicyOp,
    BoolOutParamPolicyOp,
    CcomponentsAccessorPolicyOp,
    ChildrenAddPolicyOp,
    ChildrenAtPolicyOp,
    ChildrenCountPolicyOp,
    ConstructorPolicyOp,
    DirectFieldPolicyOp,
    DirectFunctionPolicyOp,
    DirectMethodPolicyOp,
    FieldSetterPolicyOp,
    InlineAdapterPolicyOp,
    ListAtPolicyOp,
    ListCountPolicyOp,
    MethodAtPolicyOp,
    MethodSizePolicyOp,
    OptionalGetPolicyOp,
    OptionalHasPolicyOp,
    PointerPresencePolicyOp,
    SpecMethodFunctionPolicyOp,
    ValueHandleFieldPolicyOp,
    VariantGetPolicyOp,
    VariantSetPolicyOp,
)

SourceBindingSpec = MergedBindingSpec


@dataclass(frozen=True)
class DirectCallOp:
    cpp_name: str


@dataclass(frozen=True)
class SpecMethodFunctionCallOp:
    cpp_name: str
    receiver_cpp_type: str


@dataclass(frozen=True)
class BoolOutParamCallOp:
    cpp_name: str
    out_param_cpp_type: str


@dataclass(frozen=True)
class FieldGetOp:
    field_name: str
    null_check: bool
    array_element_cpp_type: str | None = None


@dataclass(frozen=True)
class ValueHandleFieldGetOp:
    field_name: str


@dataclass(frozen=True)
class PointerPresenceCheckOp:
    field_name: str


@dataclass(frozen=True)
class ChildrenCountOp:
    field_name: str


@dataclass(frozen=True)
class ChildrenAtOp:
    field_name: str


@dataclass(frozen=True)
class ChildrenAddOp:
    field_name: str
    cast_cpp_type: str | None


@dataclass(frozen=True)
class FieldSetterOp:
    field_name: str


@dataclass(frozen=True)
class MethodSizeOp:
    method_name: str


@dataclass(frozen=True)
class MethodAtOp:
    method_name: str
    item_cpp_type: str
    out_of_range_message: str
    exception_type: str


@dataclass(frozen=True)
class ListCountOp:
    list_param: str


@dataclass(frozen=True)
class ListAtOp:
    list_param: str
    item_cpp_type: str
    out_of_range_message: str


@dataclass(frozen=True)
class ArrayElementFieldOp:
    expression: str


@dataclass(frozen=True)
class OptionalPresenceCheckOp:
    field_name: str


@dataclass(frozen=True)
class OptionalGetOp:
    field_name: str


@dataclass(frozen=True)
class StaticCastOp:
    expression: str


@dataclass(frozen=True)
class CcomponentsAccessorOp:
    access_via: str
    dimensions: int


@dataclass(frozen=True)
class VariantGetOp:
    method_name: str
    cpp_type: str
    getter_types: tuple[str, ...]


@dataclass(frozen=True)
class VariantSetOp:
    method_name: str
    variant_type: str
    cpp_type: str


@dataclass(frozen=True)
class ConstructorOp:
    cpp_class: str | None
    compile_guard: str | None
    compile_guard_message: str | None


@dataclass(frozen=True)
class InlineImplementationOp:
    implementation: ImplementationSpec


OperationIR = Union[
    DirectCallOp,
    SpecMethodFunctionCallOp,
    BoolOutParamCallOp,
    FieldGetOp,
    ValueHandleFieldGetOp,
    PointerPresenceCheckOp,
    ChildrenCountOp,
    ChildrenAtOp,
    ChildrenAddOp,
    FieldSetterOp,
    MethodSizeOp,
    MethodAtOp,
    ListCountOp,
    ListAtOp,
    ArrayElementFieldOp,
    OptionalPresenceCheckOp,
    OptionalGetOp,
    StaticCastOp,
    CcomponentsAccessorOp,
    VariantGetOp,
    VariantSetOp,
    ConstructorOp,
    InlineImplementationOp,
]


@dataclass(frozen=True)
class CallIR:
    expose_as: str
    c_name: str
    receiver: str | None
    returns: TypeSpec
    params: tuple[ParamSpec, ...]
    operation: OperationIR
    doc: str | None = None
    public_module: str | None = None


@dataclass(frozen=True)
class BindingIR:
    module: str
    c_prefix: str
    public_headers: tuple[str, ...]
    handles: dict[str, HandleSpec]
    result_structs: dict[str, ResultStructSpec]
    calls: tuple[CallIR, ...]
    option_structs: dict[str, OptionStructSpec] = field(default_factory=dict)
    abi: BindingABI | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "handles", MappingProxyType(dict(self.handles)))
        object.__setattr__(
            self, "result_structs", MappingProxyType(dict(self.result_structs))
        )
        object.__setattr__(
            self, "option_structs", MappingProxyType(dict(self.option_structs))
        )

    @property
    def functions(self) -> tuple[CallIR, ...]:
        return tuple(call for call in self.calls if call.receiver is None)

    @property
    def methods(self) -> tuple[CallIR, ...]:
        return tuple(call for call in self.calls if call.receiver is not None)


def _array_element_cpp_type(cpp_type: str | None) -> str | None:
    if not cpp_type or "std::array<" not in cpp_type:
        return None
    match = re.match(r".*std::array<\s*([^,>]+)", cpp_type)
    if match is None:
        return None
    return match.group(1).strip()


def _lower_policy_operation(call: CallSpec, operation: object) -> OperationIR:
    if isinstance(operation, DirectFunctionPolicyOp | DirectMethodPolicyOp):
        if operation.cpp_name is None:
            raise ValueError(f"{call.c_name} is missing cpp_name")
        return DirectCallOp(cpp_name=operation.cpp_name)
    if isinstance(operation, SpecMethodFunctionPolicyOp):
        return SpecMethodFunctionCallOp(
            cpp_name=operation.cpp_name,
            receiver_cpp_type=operation.receiver_cpp_type,
        )
    if isinstance(operation, BoolOutParamPolicyOp):
        return BoolOutParamCallOp(
            cpp_name=operation.cpp_name,
            out_param_cpp_type=operation.out_param_cpp_type,
        )
    if isinstance(operation, DirectFieldPolicyOp):
        return FieldGetOp(
            field_name=operation.field_name,
            null_check=call.returns.kind == "handle"
            and call.returns.sequence_depth == 0,
            array_element_cpp_type=_array_element_cpp_type(call.returns.cpp_type),
        )
    if isinstance(operation, ValueHandleFieldPolicyOp):
        return ValueHandleFieldGetOp(field_name=operation.field_name)
    if isinstance(operation, ConstructorPolicyOp):
        return ConstructorOp(
            cpp_class=operation.cpp_class,
            compile_guard=operation.compile_guard,
            compile_guard_message=operation.compile_guard_message,
        )
    if isinstance(operation, InlineAdapterPolicyOp):
        return InlineImplementationOp(implementation=operation.implementation)
    if isinstance(operation, PointerPresencePolicyOp):
        return PointerPresenceCheckOp(field_name=operation.field_name)
    if isinstance(operation, ChildrenCountPolicyOp):
        return ChildrenCountOp(field_name=operation.field_name)
    if isinstance(operation, ChildrenAtPolicyOp):
        return ChildrenAtOp(field_name=operation.field_name)
    if isinstance(operation, ChildrenAddPolicyOp):
        return ChildrenAddOp(
            field_name=operation.field_name, cast_cpp_type=operation.cast_cpp_type
        )
    if isinstance(operation, FieldSetterPolicyOp):
        return FieldSetterOp(field_name=operation.field_name)
    if isinstance(operation, MethodSizePolicyOp):
        return MethodSizeOp(method_name=operation.method_name)
    if isinstance(operation, MethodAtPolicyOp):
        return MethodAtOp(
            method_name=operation.method_name,
            item_cpp_type=operation.item_cpp_type,
            out_of_range_message=operation.out_of_range_message,
            exception_type=operation.exception_type,
        )
    if isinstance(operation, ListCountPolicyOp):
        return ListCountOp(list_param=operation.list_param)
    if isinstance(operation, ListAtPolicyOp):
        return ListAtOp(
            list_param=operation.list_param,
            item_cpp_type=operation.item_cpp_type,
            out_of_range_message=operation.out_of_range_message,
        )
    if isinstance(operation, ArrayElementFieldPolicyOp):
        return ArrayElementFieldOp(expression=operation.expression)
    if isinstance(operation, OptionalHasPolicyOp):
        return OptionalPresenceCheckOp(field_name=operation.field_name)
    if isinstance(operation, OptionalGetPolicyOp):
        return OptionalGetOp(field_name=operation.field_name)
    if isinstance(operation, AsItemCastPolicyOp):
        return StaticCastOp(expression="self->ptr")
    if isinstance(operation, CcomponentsAccessorPolicyOp):
        return CcomponentsAccessorOp(
            access_via=operation.access_via, dimensions=operation.dimensions
        )
    if isinstance(operation, VariantGetPolicyOp):
        return VariantGetOp(
            method_name=operation.method_name,
            cpp_type=operation.cpp_type,
            getter_types=operation.getter_types,
        )
    if isinstance(operation, VariantSetPolicyOp):
        return VariantSetOp(
            method_name=operation.method_name,
            variant_type=operation.variant_type,
            cpp_type=operation.cpp_type,
        )
    raise ValueError(f"Unsupported policy operation for {call.c_name}")


def lower_call(call: CallSpec) -> CallIR:
    if call.policy_operation is None:
        raise ValueError(f"{call.c_name} is missing typed policy_operation")
    operation = _lower_policy_operation(call, call.policy_operation)

    return CallIR(
        expose_as=call.expose_as,
        c_name=call.c_name,
        receiver=call.receiver,
        returns=call.returns,
        params=call.params,
        operation=operation,
        doc=call.doc,
        public_module=call.public_module,
    )


def lower_binding_spec(spec: SourceBindingSpec) -> BindingIR:
    debug_log(
        "binding_ir.lower.start",
        f"module={spec.module} functions={len(spec.functions)} methods={len(spec.methods)} handles={len(spec.handles)}",
    )
    semantic_ir = BindingIR(
        module=spec.module,
        c_prefix=spec.c_prefix,
        public_headers=spec.public_headers,
        handles=spec.handles,
        result_structs=getattr(spec, "result_structs", {}),
        option_structs=getattr(spec, "option_structs", {}),
        calls=tuple(lower_call(call) for call in (*spec.functions, *spec.methods)),
    )
    result = finalize_binding_ir(semantic_ir)
    debug_log(
        "binding_ir.finalize.done",
        f"module={result.module} functions={len(result.functions)} methods={len(result.methods)} handles={len(result.handles)}",
    )
    return result


def finalize_binding_ir(semantic_ir: BindingIR) -> BindingIR:
    if semantic_ir.abi is not None:
        return semantic_ir
    from .abi_ir import finalize_abi

    debug_log("binding_ir.finalize.start", f"module={semantic_ir.module}")
    return replace(semantic_ir, abi=finalize_abi(semantic_ir))
