from __future__ import annotations

import shutil
import subprocess
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
from src.ifcwrap.binding_generator.cpp_spec_frontend import (
    discover_cpp_spec_functions,
    discover_cpp_spec_handles,
    discover_cpp_spec_methods,
    discover_cpp_spec_result_structs,
    lower_cpp_spec_functions_to_calls,
    lower_cpp_spec_handles_to_specs,
    lower_cpp_spec_methods_to_calls,
    lower_cpp_spec_result_structs_to_specs,
)
from src.ifcwrap.binding_generator.pipeline import build_binding_ir
from src.ifcwrap.binding_generator.policy_ir import BoolOutParamPolicyOp


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


def test_cpp_spec_frontend_discovers_selected_native_method(tmp_path: Path) -> None:
    spec_path = tmp_path / "demo_spec.hpp"
    spec_path.write_text(
        dedent(
            """
            #define IFCAPI_HANDLE(...)
            #define IFCAPI_DISCOVER_METHOD(...)

            namespace library {
            struct item {
                int value(const char*) const;
                int value(int) const;
                double measure() const;
                bool measure(double&) const;
            };
            }

            IFCAPI_HANDLE(item, library::item, none)
            IFCAPI_DISCOVER_METHOD(item, value, value_by_name, const char*)
            IFCAPI_DISCOVER_METHOD(item, measure, measure, double&)
            """
        ),
        encoding="utf-8",
    )
    handles = lower_cpp_spec_handles_to_specs(
        discover_cpp_spec_handles(spec_path, c_prefix="ifcopenshell")
    )

    calls = lower_cpp_spec_methods_to_calls(
        _environment(tmp_path),
        spec_path,
        discover_cpp_spec_methods(spec_path),
        handles,
    )

    assert len(calls) == 2
    assert calls[0].c_name == "ifcopenshell_item_value_by_name"
    assert calls[0].params[0].type.kind == "string"
    assert calls[1].returns.kind == "double"
    assert calls[1].params == ()
    assert isinstance(calls[1].policy_operation, BoolOutParamPolicyOp)


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
