# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from textwrap import dedent

import pytest

from src.ifcwrap.binding_generator.abi_ir import (
    ErrorCatalogEntryIR,
    finalize_abi,
)
from src.ifcwrap.binding_generator.binding_ir import (
    BindingIR,
    CallIR,
    DirectCallOp,
    finalize_binding_ir,
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
from src.ifcwrap.binding_generator.c_backend import _render_cpp, render_c_abi
from src.ifcwrap.binding_generator.c_handle_rendering import _destroy_body
from src.ifcwrap.binding_generator.c_header_rendering import _render_header
from src.ifcwrap.binding_generator.c_internal_header import _render_internal_header
from src.ifcwrap.binding_generator.c_sequence_helpers import (
    _render_common_type_decls,
    _render_common_type_impls,
    _render_handle_list_destroy_impl,
    _render_sequence_helpers,
)
from src.ifcwrap.binding_generator.c_value_rendering import (
    _render_result_struct_destroy,
)
from src.ifcwrap.binding_generator.c_variant_helpers import (
    _render_variant_destroy_impls,
)
from src.ifcwrap.binding_generator.clang_discovery import (
    CompilationConfig,
    DiscoveryEnvironment,
)
from src.ifcwrap.binding_generator.contract_discovery import (
    discover_marked_functions_in_headers,
)
from src.ifcwrap.binding_generator.cpp_spec_frontend import (
    discover_cpp_spec_functions,
    discover_cpp_spec_handles,
    discover_cpp_spec_option_structs,
    discover_cpp_spec_result_structs,
    lower_cpp_spec_functions_to_calls,
    lower_cpp_spec_handles_to_specs,
    lower_cpp_spec_result_structs_to_specs,
)
from src.ifcwrap.binding_generator.pipeline import build_binding_ir
from src.ifcwrap.binding_generator.targets.wasm.typescript import (
    render_typescript_declarations,
)


def _environment(tmp_path: Path) -> DiscoveryEnvironment:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")
    return DiscoveryEnvironment(
        compilation=CompilationConfig(
            compiler=compiler,
            include_dirs=(tmp_path,),
            working_directory=tmp_path,
        )
    )


def _generate_cpp_specs(
    spec_paths: list[Path],
    namespaces: list[str],
    module: str,
    c_prefix: str,
    header_out: Path,
    cpp_out: Path,
    *,
    discovery_include_dirs: tuple[Path, ...],
) -> None:
    artifacts = render_c_abi(
        build_binding_ir(
            (),
            module=module,
            c_prefix=c_prefix,
            discovery_include_dirs=discovery_include_dirs,
            cpp_spec_paths=spec_paths,
            cpp_spec_namespace=namespaces,
            cpp_spec_c_prefix=c_prefix,
        ),
        header_out.name,
    )
    header_out.write_text(artifacts[header_out.name], encoding="utf-8")
    cpp_out.write_text(
        artifacts[header_out.name.removesuffix(".h") + ".cpp"], encoding="utf-8"
    )


def test_cpp_spec_frontend_rejects_mutable_void_pointer_params(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            namespace ifcopenshell::capi_spec {
            inline int ifcopenshell_demo_set_box(void* data) {
                return data ? 1 : 0;
            }
            }
            """
        ),
        encoding="utf-8",
    )

    functions = discover_cpp_spec_functions(
        _environment(tmp_path),
        spec_path,
        "ifcopenshell::capi_spec",
    )

    with pytest.raises(
        ValueError, match="Unsupported discovered parameter type 'void \\*'"
    ):
        lower_cpp_spec_functions_to_calls(functions, {})


def test_contract_discovery_preserves_source_docs(tmp_path: Path) -> None:
    header = tmp_path / "demo.h"
    header.write_text(
        dedent(
            """
            #define IFCAPI_BINDING

            namespace demo {
            /**
             * Create an IFC entity.
             *
             * Initializes identity and ownership metadata.
             */
            IFCAPI_BINDING int root_create_entity(int file);
            }
            """
        ),
        encoding="utf-8",
    )

    functions = discover_marked_functions_in_headers((header,))

    assert len(functions) == 1
    assert functions[0].name == "root_create_entity"
    assert (
        functions[0].doc
        == "Create an IFC entity.\n\nInitializes identity and ownership metadata."
    )


def test_cpp_spec_frontend_preserves_contract_header_module(tmp_path: Path) -> None:
    header = tmp_path / "shape_builder.h"
    header.write_text(
        dedent(
            """
            #define IFCAPI_BINDING

            namespace demo {
            IFCAPI_BINDING void shape_builder_get_polyline_coords();
            }
            """
        ),
        encoding="utf-8",
    )
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text('#include "shape_builder.h"\n', encoding="utf-8")

    functions = discover_cpp_spec_functions(
        _environment(tmp_path),
        spec_path,
        "demo",
        contract_headers=(header,),
    )
    calls = lower_cpp_spec_functions_to_calls(
        functions,
        {},
        c_prefix="ifcopenshell",
    )

    assert functions[0].public_module == "shape_builder"
    assert calls[0].public_module == "shape_builder"


def test_contract_discovery_uses_only_adjacent_function_docs(tmp_path: Path) -> None:
    header = tmp_path / "demo.h"
    header.write_text(
        dedent(
            """
            #define IFCAPI_BINDING

            namespace demo {
            /**
             * Options for entity creation.
             */
            struct CreateEntityOptions {
                /// IFC class name.
                const char* ifc_class;
            };

            /**
             * Create an IFC entity.
             */
            IFCAPI_BINDING int root_create_entity(const CreateEntityOptions& options);
            }
            """
        ),
        encoding="utf-8",
    )

    functions = discover_marked_functions_in_headers((header,))

    assert len(functions) == 1
    assert functions[0].name == "root_create_entity"
    assert functions[0].doc == "Create an IFC entity."


def test_cpp_spec_frontend_discovers_option_structs(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>
            #include <string>

            namespace ifcopenshell::capi_spec {
            struct CreateEntityOptions {
                /**
                 * IFC class name.
                 *
                 * This paragraph should survive field documentation lowering.
                 */
                std::string ifc_class;
                /// Optional predefined type.
                std::optional<std::string> predefined_type = std::string("NOTDEFINED");
                std::optional<std::string> name;
            };

            inline int root_create_entity(const CreateEntityOptions& options) {
                return options.ifc_class.empty() ? 0 : 1;
            }

            inline int root_create_entity_with_defaults(
                std::optional<CreateEntityOptions> options = std::nullopt) {
                return options ? 1 : 0;
            }
            }
            """
        ),
        encoding="utf-8",
    )

    functions = discover_cpp_spec_functions(
        _environment(tmp_path),
        spec_path,
        "ifcopenshell::capi_spec",
    )
    option_structs = discover_cpp_spec_option_structs(
        _environment(tmp_path),
        spec_path,
        functions,
        {},
        c_prefix="ifcopenshell_demo",
    )

    options = option_structs["CreateEntityOptions"]
    assert options.cpp_type == "ifcopenshell::capi_spec::CreateEntityOptions"
    assert options.c_type == "ifcopenshell_demo_create_entity_options_t"
    fields = {field.name: field for field in options.fields}
    assert fields["ifc_class"].type.kind == "string"
    assert fields["ifc_class"].type.nullable is False
    assert (
        fields["ifc_class"].doc
        == "IFC class name.\n\nThis paragraph should survive field documentation lowering."
    )
    assert fields["predefined_type"].type.kind == "string"
    assert fields["predefined_type"].type.nullable is True
    assert fields["predefined_type"].doc == "Optional predefined type."
    assert fields["predefined_type"].has_default is True
    assert fields["name"].type.kind == "string"
    assert fields["name"].type.nullable is True
    assert fields["name"].doc is None
    assert fields["name"].has_default is False

    calls = lower_cpp_spec_functions_to_calls(
        functions,
        {},
        option_structs=option_structs,
        c_prefix="ifcopenshell_demo",
    )
    call = next(
        item for item in calls if item.expose_as == "root_create_entity_with_defaults"
    )
    assert call.params[0].type.kind == "option"
    assert call.params[0].type.struct == "CreateEntityOptions"
    assert call.params[0].type.nullable is True
    assert call.params[0].has_default is True


def test_cpp_spec_frontend_preserves_fixed_aliases_and_enum_literals(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <array>
            #include <optional>

            namespace demo {
            using Vec3 = std::array<double, 3>;
            enum class Direction {
                Positive __attribute__((annotate("ifcapi.literal:FORWARD"))) = 1,
                Negative = -1
            };

            struct TransformOptions {
                Vec3 origin;
                Direction direction;
                std::optional<Direction> optional_direction = std::nullopt;
            };

            inline Vec3 transform(const TransformOptions& options) { (void)options; return {}; }
            }
            """
        ),
        encoding="utf-8",
    )
    environment = _environment(tmp_path)
    functions = discover_cpp_spec_functions(environment, spec_path, "demo")

    option_structs = discover_cpp_spec_option_structs(
        environment,
        spec_path,
        functions,
        {},
        c_prefix="ifcopenshell_demo",
    )
    options = option_structs["TransformOptions"]
    fields = {field.name: field.type for field in options.fields}

    assert fields["origin"].kind == "double"
    assert fields["origin"].sequence_depth == 1
    assert fields["origin"].fixed_lengths == (3,)
    assert fields["origin"].alias == "Vec3"
    assert fields["direction"].kind == "int32"
    assert fields["direction"].alias == "Direction"
    assert fields["direction"].enum_values == ("FORWARD", "Negative")
    assert fields["direction"].enum_numeric_values == (1, -1)
    assert fields["optional_direction"].kind == "int32"
    assert fields["optional_direction"].nullable is True
    assert fields["optional_direction"].enum_values == ("FORWARD", "Negative")

    transform = lower_cpp_spec_functions_to_calls(
        functions, {}, option_structs=option_structs
    )[0]
    assert transform.returns.kind == "double"
    assert transform.returns.fixed_lengths == (3,)
    assert transform.returns.alias == "Vec3"

    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"
    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "to_fixed_array<3>(to_cpp_double_list(options->origin))" in generated_cpp
    assert "static_cast<demo::Direction>(options->direction)" in generated_cpp
    assert "static_cast<demo::Direction>(options->optional_direction)" in generated_cpp


def test_cpp_spec_frontend_discovers_input_variant_records(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <array>
            #include <optional>
            #include <variant>
            #include <vector>

            namespace demo {
            using Vec3 = std::array<double, 3>;
            enum class Mode {
                Fast __attribute__((annotate("ifcapi.literal:FAST-MODE"))),
                Exact
            };
            struct PlaneClipping { Vec3 location; Vec3 normal; };
            struct EntityClipping { int entity_id; };
            using Clipping = std::variant<PlaneClipping, EntityClipping>;
            using Clippings = std::vector<Clipping>;
            struct ApplyOptions {
                std::optional<Clippings> clippings;
                Mode mode;
                std::optional<bool> enabled = false;
                double required_zero;
            };
            inline void apply(const ApplyOptions& options) { (void)options; }
            }
            """
        ),
        encoding="utf-8",
    )
    environment = _environment(tmp_path)
    functions = discover_cpp_spec_functions(environment, spec_path, "demo")

    records = discover_cpp_spec_option_structs(
        environment,
        spec_path,
        functions,
        {},
        c_prefix="ifcopenshell_demo",
    )

    assert set(records) == {"ApplyOptions", "PlaneClipping", "EntityClipping"}
    apply_fields = {field.name: field for field in records["ApplyOptions"].fields}
    clipping = apply_fields["clippings"].type
    assert clipping.kind == "variant"
    assert clipping.nullable is True
    assert clipping.sequence_depth == 1
    assert [(item.kind, item.struct) for item in clipping.variants] == [
        ("option", "PlaneClipping"),
        ("option", "EntityClipping"),
    ]
    plane_fields = {field.name: field.type for field in records["PlaneClipping"].fields}
    assert plane_fields["location"].alias == "Vec3"
    assert plane_fields["normal"].fixed_lengths == (3,)
    assert apply_fields["mode"].type.enum_values == ("FAST-MODE", "Exact")
    assert apply_fields["enabled"].has_default is True
    assert apply_fields["required_zero"].has_default is False

    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"
    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )
    generated_header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "variant_list_t" in generated_header
    assert (
        "std::vector<std::variant<demo::PlaneClipping, demo::EntityClipping>> "
        "nested_values_options_cpp_clippings" in generated_cpp
    )
    assert (
        "nested_values_options_cpp_clippings.reserve(options->clippings->size)"
        in generated_cpp
    )

    calls = lower_cpp_spec_functions_to_calls(
        functions,
        {},
        option_structs=records,
        c_prefix="ifcopenshell_demo",
    )
    contract = finalize_binding_ir(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={},
            result_structs={},
            option_structs=records,
            calls=tuple(
                CallIR(
                    expose_as=call.expose_as,
                    c_name=call.c_name,
                    receiver=call.receiver,
                    returns=call.returns,
                    params=call.params,
                    operation=DirectCallOp(cpp_name="demo::apply"),
                    doc=call.doc,
                    public_module="demo",
                )
                for call in calls
            ),
        )
    )
    metadata = finalize_abi(contract)
    declarations = render_typescript_declarations(metadata)

    assert "type Vec3 = [number, number, number];" in declarations
    assert "type Mode = 'FAST-MODE' | 'Exact';" in declarations
    assert "clippings?: (" in declarations
    assert "location: Vec3;" in declarations
    assert "mode: Mode;" in declarations
    assert "enabled?: boolean;" in declarations
    assert "entity_id: number;" in declarations
    assert "required_zero: number;" in declarations


def test_cpp_spec_frontend_discovers_nested_mesh_items(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <array>
            #include <cstdint>
            #include <optional>
            #include <vector>

            namespace demo {
            struct MeshFace {
                std::vector<std::uint32_t> outer;
                std::optional<std::vector<std::vector<std::uint32_t>>> inner_loops;
            };
            struct MeshItem {
                std::vector<std::array<double, 3>> vertices;
                std::vector<MeshFace> faces;
            };
            struct MeshOptions { std::vector<MeshItem> items; };
            inline void mesh(const MeshOptions& options) { (void)options; }
            }
            """
        ),
        encoding="utf-8",
    )
    environment = _environment(tmp_path)
    functions = discover_cpp_spec_functions(environment, spec_path, "demo")
    records = discover_cpp_spec_option_structs(
        environment,
        spec_path,
        functions,
        {},
        c_prefix="ifcopenshell_demo",
    )

    assert set(records) == {"MeshOptions", "MeshItem", "MeshFace"}
    options_fields = {field.name: field.type for field in records["MeshOptions"].fields}
    item_fields = {field.name: field.type for field in records["MeshItem"].fields}
    face_fields = {field.name: field.type for field in records["MeshFace"].fields}
    assert (options_fields["items"].kind, options_fields["items"].struct) == (
        "option",
        "MeshItem",
    )
    assert options_fields["items"].sequence_depth == 1
    assert item_fields["vertices"].fixed_lengths == (None, 3)
    assert (item_fields["faces"].kind, item_fields["faces"].struct) == (
        "option",
        "MeshFace",
    )
    assert item_fields["faces"].sequence_depth == 1
    assert face_fields["outer"].kind == "uint32"
    assert face_fields["outer"].sequence_depth == 1
    assert face_fields["inner_loops"].kind == "uint32"
    assert face_fields["inner_loops"].sequence_depth == 2
    assert face_fields["inner_loops"].nullable is True

    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"
    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "nested_values_options_cpp_items" in generated_cpp
    assert "nested_values_nested_value_options_cpp_items_faces" in generated_cpp
    assert "const auto* item_nested_value_options_cpp_items_faces" in generated_cpp


def test_cpp_spec_frontend_generates_fixed_sequence_variant_parameters(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <array>
            #include <variant>
            #include <vector>

            namespace demo {
            using Vec2 = std::array<double, 2>;
            using Vec3 = std::array<double, 3>;
            using Points = std::variant<std::vector<Vec2>, std::vector<Vec3>>;

            inline std::array<double, 16> transform(
                const Points& points,
                const Vec3& origin) {
                (void)points;
                (void)origin;
                return {};
            }
            }
            """
        ),
        encoding="utf-8",
    )
    environment = _environment(tmp_path)
    functions = discover_cpp_spec_functions(environment, spec_path, "demo")
    transform = lower_cpp_spec_functions_to_calls(functions, {})[0]

    points = transform.params[0].type
    assert points.kind == "variant"
    assert [(item.sequence_depth, item.fixed_lengths) for item in points.variants] == [
        (2, (None, 2)),
        (2, (None, 3)),
    ]
    assert transform.params[1].type.fixed_lengths == (3,)
    assert transform.returns.fixed_lengths == (16,)

    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"
    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )
    generated_header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "variant_t" in generated_header
    assert "std::variant<std::vector<std::array<double, 2>>" in generated_cpp
    assert "to_fixed_array<3>(to_cpp_double_list(origin))" in generated_cpp
    assert "make_double_list(transform_sequence(demo::transform" in generated_cpp


def test_cpp_spec_result_field_docs_come_from_semantic_type(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #define IFCAPI_RESULT_STRUCT(...)

            namespace demo {
            struct SemanticResult {
                /// Documentation for the first semantic field.
                double first;
                /// Documentation for the second semantic field.
                double second;
            };
            }

            IFCAPI_RESULT_STRUCT(demo::SemanticResult)
            struct ifcopenshell_demo_result_t {
                /// This mirror comment must not be used.
                double second;
                /// This mirror comment must not be used either.
                double first;
            };
            """
        ),
        encoding="utf-8",
    )

    environment = _environment(tmp_path)
    structs = discover_cpp_spec_result_structs(spec_path, "demo")
    result = lower_cpp_spec_result_structs_to_specs(
        structs,
        {},
        environment=environment,
        translation_unit=spec_path,
    )["ifcopenshell_demo_result_t"]

    assert [(field.name, field.doc) for field in result.fields] == [
        ("second", "Documentation for the second semantic field."),
        ("first", "Documentation for the first semantic field."),
    ]


def test_c_header_renders_option_structs() -> None:
    code = _render_header(
        finalize_binding_ir(
            BindingIR(
                module="demo",
                c_prefix="ifcopenshell_demo",
                public_headers=(),
                handles={},
                result_structs={},
                calls=(),
                option_structs={
                    "CreateEntityOptions": OptionStructSpec(
                        name="CreateEntityOptions",
                        cpp_type="demo::CreateEntityOptions",
                        c_type="ifcopenshell_demo_create_entity_options_t",
                        fields=(
                            OptionStructFieldSpec("ifc_class", TypeSpec(kind="string")),
                            OptionStructFieldSpec(
                                "name", TypeSpec(kind="string", nullable=True)
                            ),
                            OptionStructFieldSpec(
                                "properties",
                                TypeSpec(
                                    kind="option",
                                    struct="NestedProperties",
                                    nullable=True,
                                ),
                            ),
                        ),
                    ),
                    "NestedProperties": OptionStructSpec(
                        name="NestedProperties",
                        cpp_type="demo::NestedProperties",
                        c_type="ifcopenshell_demo_nested_properties_t",
                        fields=(
                            OptionStructFieldSpec("depth", TypeSpec(kind="double")),
                        ),
                    ),
                },
            )
        )
    )

    assert "typedef struct ifcopenshell_demo_create_entity_options_t {" in code
    assert (
        "typedef struct ifcopenshell_demo_nested_properties_t ifcopenshell_demo_nested_properties_t;"
        in code
    )
    assert "    const char* ifc_class;" in code
    assert "    const char* name;" in code
    assert "    bool has_name;" in code
    assert "    const ifcopenshell_demo_nested_properties_t* properties;" in code
    assert "} ifcopenshell_demo_create_entity_options_t;" in code


def test_c_error_contract_preserves_stable_low_level_codes() -> None:
    spec = finalize_binding_ir(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={},
            result_structs={},
            calls=(),
        )
    )

    header = _render_header(spec)
    cpp = _render_cpp(spec, "demo_api.h")
    internal_header = _render_internal_header(spec, "demo_api.h")

    for name, value in (
        ("NONE", 0),
        ("RUNTIME", 1),
        ("VALUE", 2),
        ("TYPE", 3),
    ):
        assert f"IFCOPENSHELL_ERROR_{name} = {value}" in header
    assert "IFCOPENSHELL_ERROR_CODE_INVALID_ARGUMENT = 2" in header
    assert "IFCOPENSHELL_ERROR_CODE_DOMAIN_ERROR = 3" in header
    assert "int ifcopenshell_demo_last_error_code(void);" in header
    assert "thread_local int g_last_error_code = IFCOPENSHELL_ERROR_CODE_NONE;" in cpp
    assert "g_last_error_code = IFCOPENSHELL_ERROR_CODE_NONE;" in cpp
    assert "ifcapi" not in internal_header

    custom_catalog = replace(
        spec.abi.error_catalog,
        codes=(ErrorCatalogEntryIR("NONE", 27),),
    )
    custom_spec = replace(spec, abi=replace(spec.abi, error_catalog=custom_catalog))
    assert "IFCOPENSHELL_ERROR_CODE_NONE = 27" in _render_header(custom_spec)


def test_c_abi_variants_destroy_owned_alternatives() -> None:
    variant = TypeSpec(
        kind="variant",
        cpp_type="std::variant<Demo::Instance*, std::string>",
        variants=(
            TypeSpec(
                kind="handle",
                handle="instance",
                cpp_type="Demo::Instance*",
                ownership="owned",
            ),
            TypeSpec(kind="string", cpp_type="std::string"),
        ),
    )
    spec = finalize_binding_ir(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={
                "instance": HandleSpec(
                    name="instance",
                    cpp_type="Demo::Instance",
                    c_type="ifcopenshell_demo_instance_t",
                    destructor="delete",
                )
            },
            result_structs={},
            calls=(
                CallIR(
                    expose_as="value",
                    c_name="ifcopenshell_demo_value",
                    receiver=None,
                    returns=variant,
                    params=(),
                    operation=DirectCallOp(cpp_name="Demo::value"),
                ),
            ),
        )
    )

    header = _render_header(spec)
    cpp = _render_cpp(spec, "demo_api.h")
    metadata = finalize_abi(spec)

    assert (
        "void ifcopenshell_demo_instance_string_variant_destroy(ifcopenshell_demo_instance_string_variant_t* value);"
        in header
    )
    assert "case 0:\n        ifcopenshell_demo_instance_destroy(value->value_0);" in cpp
    assert "case 1:\n        ifcopenshell_string_destroy(&value->value_1);" in cpp
    assert metadata.value_types["demo_instance_string_variant"].destroy_function == (
        "ifcopenshell_demo_instance_string_variant_destroy"
    )


def test_c_abi_result_structs_destroy_nested_values_and_handle_envelopes() -> None:
    inner = ResultStructSpec(
        name="DemoInner",
        cpp_type="Demo::Inner",
        c_type="ifcopenshell_demo_inner_t",
        fields=(ResultStructFieldSpec("value", TypeSpec(kind="double")),),
    )
    result = ResultStructSpec(
        name="DemoResult",
        cpp_type="Demo::Result",
        c_type="ifcopenshell_demo_result_t",
        fields=(
            ResultStructFieldSpec(
                "item",
                TypeSpec(
                    kind="handle",
                    handle="item",
                    cpp_type="Demo::Item*",
                    ownership="borrowed",
                ),
            ),
            ResultStructFieldSpec(
                "items",
                TypeSpec(
                    kind="handle",
                    handle="item",
                    cpp_type="std::vector<Demo::Item*>",
                    sequence_depth=1,
                ),
            ),
            ResultStructFieldSpec(
                "values",
                TypeSpec(
                    kind="double",
                    cpp_type="std::vector<double>",
                    sequence_depth=1,
                ),
            ),
            ResultStructFieldSpec("label", TypeSpec(kind="string")),
            ResultStructFieldSpec(
                "inner",
                TypeSpec(kind="struct", struct="DemoInner", cpp_type="Demo::Inner"),
            ),
        ),
    )
    spec = finalize_binding_ir(
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
                )
            },
            result_structs={"DemoResult": result, "DemoInner": inner},
            calls=(
                CallIR(
                    expose_as="result",
                    c_name="ifcopenshell_demo_result",
                    receiver=None,
                    returns=TypeSpec(
                        kind="struct",
                        struct="DemoResult",
                        cpp_type="Demo::Result",
                    ),
                    params=(),
                    operation=DirectCallOp(cpp_name="Demo::result"),
                ),
            ),
        )
    )

    header = _render_header(spec)
    cpp = _render_cpp(spec, "demo_api.h")

    assert (
        "void ifcopenshell_demo_result_destroy(ifcopenshell_demo_result_t* value);"
        in header
    )
    assert "ifcopenshell_demo_item_destroy(value->item);" in cpp
    assert "ifcopenshell_demo_item_list_destroy(&value->items);" in cpp
    assert "ifcopenshell_double_list_destroy(&value->values);" in cpp
    assert "ifcopenshell_string_destroy(&value->label);" in cpp
    assert "ifcopenshell_demo_inner_destroy(&value->inner);" in cpp
    assert "ifcopenshell_demo_result_t result_value_c{};" in cpp
    assert "*out_result = result_value_c;" in cpp
    assert "ifcopenshell_demo_result_destroy(&result_value_c);" in cpp
    assert header.index("ifcopenshell_demo_inner_t {") < header.index(
        "ifcopenshell_demo_result_t {"
    )
    metadata = spec.abi
    assert metadata is not None
    assert metadata.value_types["DemoResult"].destroy_function == (
        "ifcopenshell_demo_result_destroy"
    )


def test_c_abi_result_record_sequences_are_owned_and_dependency_ordered() -> None:
    support = ResultStructSpec(
        name="Support",
        cpp_type="Demo::Support",
        c_type="ifcopenshell_demo_support_t",
        fields=(
            ResultStructFieldSpec("points", TypeSpec(kind="double", sequence_depth=2)),
        ),
    )
    result = ResultStructSpec(
        name="Result",
        cpp_type="Demo::Result",
        c_type="ifcopenshell_demo_result_t",
        fields=(
            ResultStructFieldSpec(
                "supports",
                TypeSpec(kind="struct", struct="Support", sequence_depth=1),
            ),
        ),
    )
    spec = finalize_binding_ir(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={},
            result_structs={"Result": result, "Support": support},
            calls=(
                CallIR(
                    expose_as="supports",
                    c_name="ifcopenshell_demo_supports",
                    receiver=None,
                    returns=TypeSpec(kind="struct", struct="Support", sequence_depth=1),
                    params=(),
                    operation=DirectCallOp(cpp_name="Demo::supports"),
                ),
                CallIR(
                    expose_as="result",
                    c_name="ifcopenshell_demo_result",
                    receiver=None,
                    returns=TypeSpec(kind="struct", struct="Result"),
                    params=(),
                    operation=DirectCallOp(cpp_name="Demo::result"),
                ),
            ),
        )
    )

    header = _render_header(spec)
    cpp = _render_cpp(spec, "demo_api.h")
    support_pos = header.index("} ifcopenshell_demo_support_t;")
    list_pos = header.index("} ifcopenshell_demo_support_list_t;")
    result_pos = header.index("} ifcopenshell_demo_result_t;")

    assert support_pos < list_pos < result_pos
    assert "ifcopenshell_demo_support_t* items;" in header
    assert "ifcopenshell_demo_support_list_t supports;" in header
    assert "ifcopenshell_demo_support_list_destroy" in header
    assert "new ifcopenshell_demo_support_t[values.size()]{}" in cpp
    assert "ifcopenshell_demo_support_destroy(&items[i]);" in cpp
    assert "ifcopenshell_demo_support_list_destroy(&value->supports);" in cpp
    assert "catch (...)" in cpp


def test_generated_compound_cleanup_runtime_preserves_transferred_handles(
    tmp_path: Path,
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    variant = TypeSpec(
        kind="variant",
        cpp_type="std::variant<Demo::Item*, std::string>",
        variants=(
            TypeSpec(
                kind="handle",
                handle="item",
                cpp_type="Demo::Item*",
                ownership="borrowed",
            ),
            TypeSpec(kind="string", cpp_type="std::string"),
        ),
    )
    handle = HandleSpec(
        name="item",
        cpp_type="Demo::Item",
        c_type="ifcopenshell_demo_item_t",
        destructor="function:destroy_demo_item",
    )
    result = ResultStructSpec(
        name="DemoResult",
        cpp_type="Demo::Result",
        c_type="ifcopenshell_demo_result_t",
        fields=(
            ResultStructFieldSpec(
                "borrowed",
                TypeSpec(
                    kind="handle",
                    handle="item",
                    cpp_type="Demo::Item*",
                    ownership="borrowed",
                ),
            ),
            ResultStructFieldSpec(
                "owned",
                TypeSpec(
                    kind="handle",
                    handle="item",
                    cpp_type="Demo::Item*",
                    ownership="owned",
                ),
            ),
            ResultStructFieldSpec(
                "items",
                TypeSpec(
                    kind="handle",
                    handle="item",
                    cpp_type="std::vector<Demo::Item*>",
                    sequence_depth=1,
                ),
            ),
            ResultStructFieldSpec("alternative", variant),
        ),
    )
    ir = finalize_binding_ir(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={"item": handle},
            result_structs={"DemoResult": result},
            calls=(
                CallIR(
                    expose_as="value",
                    c_name="ifcopenshell_demo_value",
                    receiver=None,
                    returns=variant,
                    params=(),
                    operation=DirectCallOp(cpp_name="Demo::value"),
                ),
            ),
        )
    )
    metadata = ir.abi
    assert metadata is not None
    result_type = metadata.value_types["DemoResult"]
    list_type = next(
        value
        for value in metadata.value_types.values()
        if value.kind == "handle_sequence"
    )
    variant_type = next(
        value for value in metadata.value_types.values() if value.kind == "variant"
    )

    def struct_declaration(c_type: str) -> str:
        value = next(
            item for item in metadata.value_types.values() if item.c_type == c_type
        )
        fields = "\n".join(
            f"    {field.c_type} {field.name};" for field in value.fields
        )
        return f"struct {c_type} {{\n{fields}\n}};"

    handle_destroy = f"""void ifcopenshell_demo_item_destroy(ifcopenshell_demo_item_t* handle) {{
    if (handle == nullptr) {{
        return;
    }}
    {_destroy_body(handle)}
}}"""
    fixture = f"""
#include <cassert>
#include <cstddef>
#include <cstdint>

static int envelope_count = 0;
static int pointee_count = 0;

struct ifcopenshell_string_t {{
    char* data;
    size_t size;
    bool owned;
}};

struct ifcopenshell_demo_item_t {{
    int* ptr;
    bool owned;
    ~ifcopenshell_demo_item_t() {{ ++envelope_count; }}
}};
{struct_declaration(list_type.c_type)}
{struct_declaration(variant_type.c_type)}
{struct_declaration(result_type.c_type)}

void ifcopenshell_string_destroy(ifcopenshell_string_t* value) {{
    if (value == nullptr) return;
    if (value->owned) delete[] value->data;
    value->data = nullptr;
    value->size = 0;
    value->owned = false;
}}

void destroy_demo_item(int* value) {{
    ++pointee_count;
    delete value;
}}

{handle_destroy}
{_render_handle_list_destroy_impl(handle)}
{_render_variant_destroy_impls(ir)}
{_render_result_struct_destroy(result_type, metadata)}

int main() {{
    int* borrowed_pointee = new int(1);
    int* sequence_pointee = new int(2);
    int* alternative_pointee = new int(3);
    auto* borrowed = new ifcopenshell_demo_item_t{{borrowed_pointee, false}};
    auto* owned = new ifcopenshell_demo_item_t{{new int(4), true}};
    auto* sequence_item = new ifcopenshell_demo_item_t{{sequence_pointee, false}};
    auto* alternative = new ifcopenshell_demo_item_t{{alternative_pointee, false}};
    auto** items = new ifcopenshell_demo_item_t*[1]{{sequence_item}};
    ifcopenshell_demo_result_t value{{borrowed, owned, {{items, 1}}, {{0, alternative}}}};

    value.borrowed = nullptr;
    value.items.items[0] = nullptr;
    value.alternative.value_0 = nullptr;
    ifcopenshell_demo_result_destroy(&value);
    assert(envelope_count == 1);
    assert(pointee_count == 1);
    assert(*borrowed_pointee == 1);
    assert(*sequence_pointee == 2);
    assert(*alternative_pointee == 3);

    ifcopenshell_demo_result_destroy(&value);
    assert(envelope_count == 1);
    assert(pointee_count == 1);

    ifcopenshell_demo_item_destroy(borrowed);
    ifcopenshell_demo_item_destroy(sequence_item);
    ifcopenshell_demo_item_destroy(alternative);
    assert(envelope_count == 4);
    assert(pointee_count == 1);
    delete borrowed_pointee;
    delete sequence_pointee;
    delete alternative_pointee;
}}
"""
    source = tmp_path / "cleanup_fixture.cpp"
    executable = tmp_path / "cleanup_fixture"
    source.write_text(fixture, encoding="utf-8")
    subprocess.run(
        [compiler, "-std=c++17", "-O0", str(source), "-o", str(executable)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run([str(executable)], check=True, capture_output=True, text=True)


def test_owner_backed_numeric_sequences_move_storage_and_destroy_once(
    tmp_path: Path,
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    kinds = ("double_list", "double_list_list")
    fixture = f"""
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <utility>
#include <vector>

{_render_common_type_decls(kinds)}

static int owner_destructions = 0;

struct capi_buffer_owner {{
    virtual ~capi_buffer_owner() {{ ++owner_destructions; }}
}};

template <typename T>
struct capi_value_owner final : capi_buffer_owner {{
    explicit capi_value_owner(T value) : value(std::move(value)) {{}}
    T value;
}};

template <typename T>
struct capi_array_owner final : capi_buffer_owner {{
    explicit capi_array_owner(size_t size)
        : values(size == 0 ? nullptr : std::make_unique<T[]>(size)) {{}}
    std::unique_ptr<T[]> values;
}};

void validate_list_items(const char*, const void* items, size_t size) {{
    assert(size == 0 || items != nullptr);
}}

{_render_common_type_impls(kinds)}
{_render_sequence_helpers(kinds)}

int main() {{
    std::vector<double> values{{1.0, 2.0, 3.0}};
    auto* original_data = values.data();
    auto flat = make_double_list(std::move(values));
    assert(flat.owner != nullptr);
    assert(flat.items == original_data);
    flat.items[1] = 8.0;
    assert(flat.items[1] == 8.0);
    ifcopenshell_double_list_destroy(&flat);
    assert(owner_destructions == 1);
    ifcopenshell_double_list_destroy(&flat);
    assert(owner_destructions == 1);

    std::vector<std::vector<double>> nested_values{{{{4.0, 5.0}}, {{6.0}}}};
    auto* first_row_data = nested_values[0].data();
    auto* second_row_data = nested_values[1].data();
    auto nested = make_double_list_list(std::move(nested_values));
    assert(nested.owner != nullptr);
    assert(nested.items[0].items == first_row_data);
    assert(nested.items[1].items == second_row_data);
    ifcopenshell_double_list_list_destroy(&nested);
    assert(owner_destructions == 4);
    ifcopenshell_double_list_list_destroy(&nested);
    assert(owner_destructions == 4);

    double caller_items[] = {{10.0, 11.0}};
    ifcopenshell_double_list_t borrowed{{caller_items, 2, nullptr}};
    ifcopenshell_double_list_destroy(&borrowed);
    assert(owner_destructions == 4);
    assert(caller_items[0] == 10.0);
}}
"""
    source = tmp_path / "owner_backed_buffer_fixture.cpp"
    executable = tmp_path / "owner_backed_buffer_fixture"
    source.write_text(fixture, encoding="utf-8")
    subprocess.run(
        [compiler, "-std=c++17", "-O0", str(source), "-o", str(executable)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run([str(executable)], check=True, capture_output=True, text=True)


def test_c_backend_emits_sequence_helpers_used_only_by_option_structs() -> None:
    spec = finalize_binding_ir(
        BindingIR(
            module="demo",
            c_prefix="ifcopenshell_demo",
            public_headers=(),
            handles={},
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
                            "vertices", TypeSpec(kind="double", sequence_depth=3)
                        ),
                        OptionStructFieldSpec(
                            "faces", TypeSpec(kind="int32", sequence_depth=4)
                        ),
                    ),
                )
            },
        )
    )

    header = _render_header(spec)
    cpp = _render_cpp(spec, "demo_api.h")

    assert "typedef struct ifcopenshell_int32_list_list_list_list_t {" in header
    assert "void ifcopenshell_int32_list_list_list_list_destroy" in header
    assert (
        "static std::vector<std::vector<std::vector<std::vector<int>>>> to_cpp_int32_list_list_list_list"
        in cpp
    )
    assert (
        "options_cpp.faces = to_cpp_int32_list_list_list_list(options->faces);" in cpp
    )


def test_cpp_spec_generation_lowers_option_parameters(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>
            #include <string>

            namespace demo {
            struct CreateEntityOptions {
                std::string ifc_class;
                std::optional<std::string> name;
                std::optional<bool> force;
            };

            inline int root_create_entity(const CreateEntityOptions& options) {
                return options.ifc_class.empty() ? 0 : 1;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "typedef struct ifcopenshell_demo_create_entity_options_t {" in header
    assert "    const char* ifc_class;" in header
    assert "    const char* name;" in header
    assert "    bool has_name;" in header
    assert "    bool force;" in header
    assert "    bool has_force;" in header
    assert (
        "bool ifcopenshell_demo_root_create_entity("
        "const ifcopenshell_demo_create_entity_options_t* options, int32_t* out_result);"
    ) in header
    assert "demo::CreateEntityOptions options_cpp{};" in generated_cpp
    assert 'Options field \\"ifc_class\\" must not be null' in generated_cpp
    assert "options_cpp.ifc_class = std::string(options->ifc_class);" in generated_cpp
    assert "if (options->has_name) {" in generated_cpp
    assert "options_cpp.name = std::string(options->name);" in generated_cpp
    assert "if (options->has_force) {" in generated_cpp
    assert "options_cpp.force = options->force;" in generated_cpp
    assert "static_cast<std::optional<bool>>" not in generated_cpp
    assert "demo::root_create_entity(options_cpp)" in generated_cpp


def test_cpp_spec_generation_lowers_input_record_sequences(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>
            #include <string>
            #include <vector>

            #define IFCAPI_HANDLE(name, cpp_type, destructor, ptr_type)
            struct DemoValue {};
            IFCAPI_HANDLE(demo_value, DemoValue, none, value)

            namespace demo {
            struct ItemOptions {
                bool enabled;
                std::optional<std::string> label;
                std::optional<DemoValue> value;
                std::optional<std::vector<std::string>> tags;
            };

            struct BatchOptions {
                std::optional<std::vector<ItemOptions>> items = std::nullopt;
            };

            inline int consume(const std::vector<ItemOptions>& items) {
                return static_cast<int>(items.size());
            }

            inline int consume_batch(const BatchOptions& options) {
                return options.items ? static_cast<int>(options.items->size()) : 0;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "typedef struct ifcopenshell_demo_item_options_list_t" in header
    assert "ifcopenshell_demo_item_options_t* items;" in header
    assert "const ifcopenshell_demo_item_options_list_t* items" in header
    assert "std::vector<demo::ItemOptions> items_cpp;" in generated_cpp
    assert "items_cpp.reserve(items->size);" in generated_cpp
    assert "value.label = std::string(item->label);" in generated_cpp
    assert "value.value = item->value->value;" in generated_cpp
    assert "value.tags = to_cpp_string_list(item->tags);" in generated_cpp
    assert "const ifcopenshell_demo_item_options_list_t* items;" in header
    assert "bool has_items;" in header
    assert header.index(
        "typedef struct ifcopenshell_demo_item_options_list_t ifcopenshell_demo_item_options_list_t;"
    ) < header.index("typedef struct ifcopenshell_demo_batch_options_t {")
    assert (
        "std::vector<demo::ItemOptions> nested_values_options_cpp_items;"
        in generated_cpp
    )
    assert (
        "nested_values_options_cpp_items.reserve(options->items->size);"
        in generated_cpp
    )
    assert (
        "options_cpp.items = std::move(nested_values_options_cpp_items);"
        in generated_cpp
    )


def test_cpp_spec_generation_lowers_std_optional_option_fields(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>

            namespace demo {
            struct UpdateOptions {
                std::optional<bool> force;
            };

            inline bool update(const UpdateOptions& options) {
                return true;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "bool force;" in header
    assert "bool has_force;" in header
    assert "options_cpp.force = options->force;" in generated_cpp
    assert "static_cast<std::optional<bool>>" not in generated_cpp


def test_cpp_spec_generation_lowers_standalone_optional_handle_and_string_params(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>
            #include <string>

            struct DemoValue {};
            #define IFCAPI_HANDLE(name, cpp_type, destructor)
            IFCAPI_HANDLE(demo_value, DemoValue, none)

            namespace demo {
            inline int update(std::optional<DemoValue> value, std::optional<std::string> name) {
                return value.has_value() || name.has_value() ? 1 : 0;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert (
        "bool ifcopenshell_demo_update(ifcopenshell_demo_demo_value_t* value, const char* name, int32_t* out_result);"
        in header
    )
    assert "std::optional<DemoValue> value_cpp;" in generated_cpp
    assert (
        "if (value != nullptr && value->ptr != nullptr) { value_cpp = *value->ptr; }"
        in generated_cpp
    )
    assert "std::optional<std::string> name_cpp;" in generated_cpp
    assert "if (name != nullptr) { name_cpp = std::string(name); }" in generated_cpp
    assert "demo::update(value_cpp, name_cpp)" in generated_cpp


def test_cpp_spec_generation_tracks_default_parameters(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>
            #include <string>

            namespace demo {
            inline bool update(std::optional<std::string> value, std::optional<std::string> suffix = std::nullopt) {
                return value.has_value() || suffix.has_value();
            }
            }
            """
        ),
        encoding="utf-8",
    )

    functions = discover_cpp_spec_functions(
        _environment(tmp_path),
        spec_path,
        "demo",
    )
    calls = lower_cpp_spec_functions_to_calls(
        functions, {}, c_prefix="ifcopenshell_demo"
    )
    ir = BindingIR(
        module="demo",
        c_prefix="ifcopenshell_demo",
        public_headers=(),
        handles={},
        result_structs={},
        calls=tuple(
            CallIR(
                expose_as=call.expose_as,
                c_name=call.c_name,
                receiver=call.receiver,
                returns=call.returns,
                params=call.params,
                operation=DirectCallOp(cpp_name="demo::update"),
                doc=call.doc,
            )
            for call in calls
        ),
    )
    metadata = finalize_abi(ir)
    function = metadata.functions["ifcopenshell_demo_update"]
    params = {param.name: param for param in function.params}

    assert params["value"].nullable is True
    assert params["value"].has_default is False
    assert params["suffix"].nullable is True
    assert params["suffix"].has_default is True


def test_cpp_spec_generation_preserves_omittable_native_defaults(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>
            #include <string>
            #include <vector>

            namespace demo {
            enum class Mode { Fast, Exact };
            inline bool update(
                std::optional<double> tolerance = std::nullopt,
                std::optional<std::string> label = std::nullopt,
                std::optional<Mode> mode = std::nullopt,
                std::optional<std::vector<double>> offsets = std::nullopt) {
                return tolerance || label || mode || offsets;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert "const double* tolerance" in header
    assert "const char* label" in header
    assert "const int32_t* mode" in header
    assert "const ifcopenshell_double_list_t* offsets" in header
    assert "if (tolerance != nullptr)" in generated_cpp
    assert "if (label != nullptr)" in generated_cpp
    assert "if (mode != nullptr)" in generated_cpp
    assert "if (offsets != nullptr)" in generated_cpp


def test_cpp_spec_generation_lowers_optional_owned_handle_returns(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #include <optional>

            struct DemoValue {};
            #define IFCAPI_HANDLE(name, cpp_type, destructor)
            #define IFCAPI_OWNED
            IFCAPI_HANDLE(demo_value, DemoValue, delete)

            namespace demo {
            inline IFCAPI_OWNED std::optional<DemoValue*> find_value(bool found) {
                return found ? std::optional<DemoValue*>(new DemoValue()) : std::nullopt;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    header = header_out.read_text(encoding="utf-8")
    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert (
        "bool ifcopenshell_demo_find_value(bool found, ifcopenshell_demo_demo_value_t** out_result);"
        in header
    )
    assert "auto result_value = demo::find_value(found_cpp);" in generated_cpp
    assert "if (!result_value) {" in generated_cpp
    assert "*out_result = nullptr;" in generated_cpp
    assert "auto unwrapped_result = *result_value;" in generated_cpp
    assert (
        "*out_result = new ifcopenshell_demo_demo_value_t{unwrapped_result, true};"
        in generated_cpp
    )


def test_cpp_spec_generation_lowers_nullable_owned_raw_handle_returns(
    tmp_path: Path,
) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            struct DemoValue {};
            #define IFCAPI_HANDLE(name, cpp_type, destructor)
            #define IFCAPI_OWNED
            IFCAPI_HANDLE(demo_value, DemoValue, delete)

            namespace demo {
            inline IFCAPI_OWNED DemoValue* find_value(bool found) {
                return found ? new DemoValue() : nullptr;
            }
            }
            """
        ),
        encoding="utf-8",
    )
    header_out = tmp_path / "demo_api.h"
    cpp_out = tmp_path / "demo_api.cpp"

    _generate_cpp_specs(
        [spec_path],
        ["demo"],
        "demo",
        "ifcopenshell_demo",
        header_out,
        cpp_out,
        discovery_include_dirs=(tmp_path,),
    )

    generated_cpp = cpp_out.read_text(encoding="utf-8")
    assert (
        "auto result_value = std::unique_ptr<DemoValue>(demo::find_value(found_cpp));"
        in generated_cpp
    )
    assert "if (!result_value) {" in generated_cpp
    assert "*out_result = nullptr;" in generated_cpp
    assert (
        "*out_result = new ifcopenshell_demo_demo_value_t{result_value.release(), true};"
        in generated_cpp
    )


def test_cpp_spec_frontend_rejects_overloaded_exports(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            namespace ifcopenshell::capi_spec {
            inline int ifcopenshell_demo_value(int value) {
                return value;
            }
            inline int ifcopenshell_demo_value(double value) {
                return static_cast<int>(value);
            }
            }
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="declared more than once"):
        discover_cpp_spec_functions(
            _environment(tmp_path),
            spec_path,
            "ifcopenshell::capi_spec",
        )


def test_cpp_spec_frontend_excludes_private_helpers(tmp_path: Path) -> None:
    from unittest.mock import patch

    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            namespace ifcopenshell::capi_spec {
            inline int ifcopenshell_demo_exported() {
                return 42;
            }
            inline int ifcopenshell_demo_internal_helper() {
                return 0;
            }
            }
            """
        ),
        encoding="utf-8",
    )

    with patch(
        "src.ifcwrap.binding_generator.cpp_spec_frontend._PRIVATE_NAMES",
        frozenset({"to_base_vector", "ifcopenshell_demo_internal_helper"}),
    ):
        functions = discover_cpp_spec_functions(
            _environment(tmp_path),
            spec_path,
            "ifcopenshell::capi_spec",
        )

    exported_names = {f.name for f in functions}
    assert "ifcopenshell_demo_exported" in exported_names
    assert "ifcopenshell_demo_internal_helper" not in exported_names


def test_cpp_spec_frontend_rejects_duplicate_handles(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #define IFCAPI_HANDLE(cpp_type, destructor)

            namespace ifcopenshell::capi_spec {
            struct DemoFile {};
            IFCAPI_HANDLE(ifcopenshell::capi_spec::DemoFile, delete)
            struct ifcopenshell_demo_file_t;
            IFCAPI_HANDLE(ifcopenshell::capi_spec::DemoFile, delete)
            struct ifcopenshell_demo_file_t;
            }
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="declared more than once"):
        discover_cpp_spec_handles(spec_path)


def test_cpp_spec_frontend_discovers_receiver_operator_adapters(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.cpp"
    spec_path.write_text(
        dedent(
            """
            #define IFCAPI_HANDLE(name, cpp_type, destructor)
            #define IFCAPI_OWNED

            struct DemoValue {};
            IFCAPI_HANDLE(demo_value, DemoValue, delete)
            struct ifcopenshell_demo_value_t;

            namespace demo {
            inline IFCAPI_OWNED DemoValue* add(DemoValue* self, DemoValue* other) {
                return nullptr;
            }

            inline bool equals(DemoValue* self, DemoValue* other) {
                return self == other;
            }
            }
            """
        ),
        encoding="utf-8",
    )

    functions = discover_cpp_spec_functions(_environment(tmp_path), spec_path, "demo")
    handles = lower_cpp_spec_handles_to_specs(discover_cpp_spec_handles(spec_path))
    calls = {
        call.c_name: call
        for call in lower_cpp_spec_functions_to_calls(functions, handles)
    }

    add = calls["ifcopenshell_demo_value_add"]
    assert add.receiver == "demo_value"
    assert add.returns.ownership == "owned"
    assert add.returns.nullable is True
    assert [param.name for param in add.params] == ["other"]
    assert add.params[0].type.ownership == "borrowed"
    assert add.params[0].type.nullable is False

    equals = calls["ifcopenshell_demo_value_equals"]
    assert equals.receiver == "demo_value"
    assert equals.returns.kind == "bool"
    assert [param.name for param in equals.params] == ["other"]
