# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from dataclasses import dataclass

from .binding_model import ImplementationSpec, ParamSpec, TypeSpec


@dataclass(frozen=True)
class DirectFunctionPolicyOp:
    cpp_name: str | None


@dataclass(frozen=True)
class DirectMethodPolicyOp:
    cpp_name: str | None


@dataclass(frozen=True)
class SpecMethodFunctionPolicyOp:
    cpp_name: str
    receiver_cpp_type: str


@dataclass(frozen=True)
class BoolOutParamPolicyOp:
    cpp_name: str
    out_param_cpp_type: str


@dataclass(frozen=True)
class DirectFieldPolicyOp:
    field_name: str


@dataclass(frozen=True)
class ValueHandleFieldPolicyOp:
    field_name: str


@dataclass(frozen=True)
class ConstructorPolicyOp:
    cpp_class: str | None = None
    compile_guard: str | None = None
    compile_guard_message: str | None = None


@dataclass(frozen=True)
class InlineAdapterPolicyOp:
    implementation: ImplementationSpec


@dataclass(frozen=True)
class ChildrenCountPolicyOp:
    field_name: str


@dataclass(frozen=True)
class ChildrenAtPolicyOp:
    field_name: str


@dataclass(frozen=True)
class ChildrenAddPolicyOp:
    field_name: str
    cast_cpp_type: str | None


@dataclass(frozen=True)
class OptionalHasPolicyOp:
    field_name: str


@dataclass(frozen=True)
class OptionalGetPolicyOp:
    field_name: str


@dataclass(frozen=True)
class PointerPresencePolicyOp:
    field_name: str


@dataclass(frozen=True)
class FieldSetterPolicyOp:
    field_name: str


@dataclass(frozen=True)
class MethodSizePolicyOp:
    method_name: str


@dataclass(frozen=True)
class MethodAtPolicyOp:
    method_name: str
    item_cpp_type: str
    out_of_range_message: str
    exception_type: str


@dataclass(frozen=True)
class ListCountPolicyOp:
    list_param: str


@dataclass(frozen=True)
class ListAtPolicyOp:
    list_param: str
    item_cpp_type: str
    out_of_range_message: str


@dataclass(frozen=True)
class ArrayElementFieldPolicyOp:
    expression: str


@dataclass(frozen=True)
class AsItemCastPolicyOp:
    pass


@dataclass(frozen=True)
class CcomponentsAccessorPolicyOp:
    access_via: str
    dimensions: int


@dataclass(frozen=True)
class VariantGetPolicyOp:
    method_name: str
    cpp_type: str
    getter_types: tuple[str, ...]


@dataclass(frozen=True)
class VariantSetPolicyOp:
    method_name: str
    variant_type: str
    cpp_type: str


PolicyOperation = (
    DirectFunctionPolicyOp
    | DirectMethodPolicyOp
    | SpecMethodFunctionPolicyOp
    | DirectFieldPolicyOp
    | ValueHandleFieldPolicyOp
    | ConstructorPolicyOp
    | InlineAdapterPolicyOp
    | ChildrenCountPolicyOp
    | ChildrenAtPolicyOp
    | ChildrenAddPolicyOp
    | OptionalHasPolicyOp
    | OptionalGetPolicyOp
    | PointerPresencePolicyOp
    | FieldSetterPolicyOp
    | MethodSizePolicyOp
    | MethodAtPolicyOp
    | ListCountPolicyOp
    | ListAtPolicyOp
    | ArrayElementFieldPolicyOp
    | AsItemCastPolicyOp
    | CcomponentsAccessorPolicyOp
    | VariantGetPolicyOp
    | VariantSetPolicyOp
)


@dataclass(frozen=True)
class PolicyCallSpec:
    expose_as: str
    receiver: str | None
    returns: TypeSpec
    params: tuple[ParamSpec, ...]
    operation: PolicyOperation
