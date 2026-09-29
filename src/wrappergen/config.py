from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CompilationConfig:
    headers: list[str]
    clang_args: list[str] = field(default_factory=lambda: ["-x", "c++", "-std=c++17"])
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    compile_commands: str | None = None


@dataclass(slots=True)
class IgnoreConfig:
    namespaces: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    enums: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)


@dataclass(slots=True)
class WrapperConfig:
    module_name: str
    c_prefix: str
    api_header_name: str
    api_implementation_name: str
    extension_source_name: str
    python_source_name: str
    compilation: CompilationConfig
    allowed_namespaces: list[str] = field(default_factory=list)
    export_macro: str = "IFC_PARSE_API"
    require_exported_classes: bool = True
    default_class_handle_kind: str = "value"
    class_names: dict[str, str] = field(default_factory=dict)
    enum_names: dict[str, str] = field(default_factory=dict)
    parameter_names: dict[str, str] = field(default_factory=dict)
    class_handle_kinds: dict[str, str] = field(default_factory=dict)
    class_owner_types: dict[str, str] = field(default_factory=dict)
    type_adapters: dict[str, str] = field(default_factory=dict)
    ignore: IgnoreConfig = field(default_factory=IgnoreConfig)
