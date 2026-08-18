from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypeSpec:
    kind: str
    handle: str | None = None
    struct: str | None = None
    variants: tuple[TypeSpec, ...] = ()
    ownership: str | None = None
    nullable: bool = False
    cpp_type: str | None = None
    sequence_depth: int = 0
    alias: str | None = None
    fixed_lengths: tuple[int | None, ...] = ()
    enum_values: tuple[str, ...] = ()
    enum_numeric_values: tuple[int, ...] = ()
    literal_value: str | None = None


@dataclass(frozen=True)
class ParamSpec:
    name: str
    type: TypeSpec
    has_default: bool = False


@dataclass(frozen=True)
class HandleSpec:
    name: str
    cpp_type: str
    c_type: str
    destructor: str
    ptr_type: str = "raw"
    empty_check: str | None = None


@dataclass(frozen=True)
class ResultStructFieldSpec:
    name: str
    type: TypeSpec
    cpp_field: str | None = None
    doc: str | None = None


@dataclass(frozen=True)
class ResultStructSpec:
    name: str
    cpp_type: str
    c_type: str
    fields: tuple[ResultStructFieldSpec, ...]


@dataclass(frozen=True)
class OptionStructFieldSpec:
    name: str
    type: TypeSpec
    cpp_field: str | None = None
    doc: str | None = None
    has_default: bool = False


@dataclass(frozen=True)
class OptionStructSpec:
    name: str
    cpp_type: str
    c_type: str
    fields: tuple[OptionStructFieldSpec, ...]


@dataclass(frozen=True)
class ImplementationSpec:
    kind: str
    body: str


@dataclass(frozen=True)
class CallSpec:
    expose_as: str
    c_name: str
    receiver: str | None
    returns: TypeSpec
    params: tuple[ParamSpec, ...]
    policy_operation: object
    doc: str | None = None
    public_module: str | None = None


@dataclass(frozen=True)
class DiscoveryDiagnostic:
    owner: str
    member: str
    code: str
    message: str
