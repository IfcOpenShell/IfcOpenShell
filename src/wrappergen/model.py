from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ParameterModel:
    name: str
    cpp_name: str
    cpp_type: str
    adapter: str
    has_default: bool = False
    default_cpp_value: str | None = None
    default_python_value: str | None = None


@dataclass(slots=True)
class CallableModel:
    kind: str
    owner_cpp_name: str
    owner_py_name: str
    cpp_name: str
    py_name: str
    c_name: str
    return_cpp_type: str
    return_adapter: str
    parameters: list[ParameterModel] = field(default_factory=list)

    @property
    def minimum_arity(self) -> int:
        defaults = 0
        for parameter in reversed(self.parameters):
            if not parameter.has_default:
                break
            defaults += 1
        return len(self.parameters) - defaults


@dataclass(slots=True)
class EnumValueModel:
    name: str
    c_name: str
    value: int


@dataclass(slots=True)
class EnumModel:
    cpp_name: str
    py_name: str
    c_name: str
    values: list[EnumValueModel]


@dataclass(slots=True)
class ClassModel:
    cpp_name: str
    py_name: str
    handle_kind: str
    owner_cpp_name: str | None = None
    owner_py_name: str | None = None
    callables: list[CallableModel] = field(default_factory=list)


@dataclass(slots=True)
class ModuleModel:
    module_name: str
    c_prefix: str
    api_header_name: str
    api_implementation_name: str
    extension_source_name: str
    python_source_name: str
    source_headers: list[str]
    classes: list[ClassModel]
    enums: list[EnumModel]
