from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src.ifcwrap.binding_generator import libclang_index
from src.ifcwrap.binding_generator.clang_discovery import (
    CompilationConfig,
    DiscoveryEnvironment,
    _parse_discovered_cpp_type,
    discover_namespace_functions,
    discover_namespace_functions_with_synthetic_source,
    discover_public_fields,
    discover_public_methods,
)


def test_matching_libclang_uses_numeric_version_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    resource_dir = tmp_path / "llvm" / "lib" / "clang" / "18"
    resource_dir.mkdir(parents=True)
    older = resource_dir.parents[1] / "libclang.so.9"
    newer = resource_dir.parents[1] / "libclang.so.18"
    older.touch()
    newer.touch()
    monkeypatch.setattr(
        libclang_index, "_compiler_output", lambda compiler, *args: str(resource_dir)
    )

    assert libclang_index._matching_libclang("clang++") == newer.resolve()


def test_template_base_is_not_resolved_as_enum() -> None:
    cpp_type = _parse_discovered_cpp_type("vector<int>")

    assert cpp_type.template_name == "vector"
    assert cpp_type.is_enum is False


def test_discover_public_methods_with_discovery_environment(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "sample.h"
    source = tmp_path / "sample.cpp"

    header.write_text(
        """
#include <string>

namespace Demo {
class Foo {
public:
    int bar(int id);
    const std::string& baz(const std::string& guid) const;
    void qux(int id);
    void qux(const std::string& guid);
private:
    void hidden();
};

int walk(int steps);
void hop(int count);
void hop(const std::string& guid);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "sample.h"\n', encoding="utf-8")

    methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Foo",
    )

    assert set(methods) == {"bar", "baz", "qux"}
    assert len(methods["bar"]) == 1
    assert methods["bar"][0].return_cpp_type == "int"
    assert methods["bar"][0].params[0].name == "id"
    assert methods["bar"][0].params[0].cpp_type == "int"
    assert len(methods["baz"]) == 1
    assert methods["baz"][0].return_cpp_type == "const std::string &"
    assert methods["baz"][0].return_type_ref.is_const
    assert methods["baz"][0].return_type_ref.is_lvalue_reference
    assert methods["baz"][0].return_type_ref.base_name == "std::string"
    assert methods["baz"][0].params[0].name == "guid"
    assert methods["baz"][0].params[0].cpp_type == "const std::string &"
    assert methods["baz"][0].params[0].cpp_type_ref.base_name == "std::string"
    assert len(methods["qux"]) == 2
    assert [param.cpp_type for param in methods["qux"][0].params] == ["int"]
    assert [param.cpp_type for param in methods["qux"][1].params] == [
        "const std::string &"
    ]

    qualified_methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::Foo",
    )
    assert set(qualified_methods) == {"bar", "baz", "qux"}

    functions = discover_namespace_functions(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo",
    )
    assert set(functions) == {"walk", "hop"}
    assert len(functions["walk"]) == 1
    assert functions["walk"][0].return_cpp_type == "int"
    assert functions["walk"][0].params[0].cpp_type == "int"
    assert len(functions["hop"]) == 2


def test_translation_unit_is_parsed_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    source = tmp_path / "bindings.cpp"
    source.write_text(
        "namespace Demo { struct Item { int value() const; }; int count(); }\n",
        encoding="utf-8",
    )
    parse_count = 0
    original_parse = libclang_index.parse_translation_unit

    def counting_parse(command):
        nonlocal parse_count
        parse_count += 1
        return original_parse(command)

    monkeypatch.setattr(libclang_index, "parse_translation_unit", counting_parse)
    environment = DiscoveryEnvironment(
        compilation=CompilationConfig(
            compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
        )
    )

    discover_public_methods(environment, source, "Demo::Item")
    discover_public_methods(environment, source, "Demo::Item")
    discover_namespace_functions(environment, source, "Demo")

    assert parse_count == 1


def test_discover_namespace_functions_with_nested_qualified_namespace(
    tmp_path: Path,
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "bindings.h"
    source = tmp_path / "bindings.cpp"

    header.write_text(
        """
#include <string>

namespace ifcapi {
namespace bindings {
int nested_count(const std::string& name);
}
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text(
        """
#include "bindings.h"

namespace ifcapi::bindings {
double qualified_scale(double value) { return value; }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    functions = discover_namespace_functions(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "ifcapi::bindings",
    )

    assert set(functions) == {"nested_count", "qualified_scale"}
    assert functions["nested_count"][0].return_cpp_type == "int"
    assert functions["nested_count"][0].params[0].cpp_type == "const std::string &"
    assert functions["qualified_scale"][0].return_cpp_type == "double"


def test_discover_namespace_functions_with_synthetic_contract_source(
    tmp_path: Path,
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header_a = tmp_path / "contract_a.h"
    header_b = tmp_path / "contract_b.h"
    source = tmp_path / "reference.cpp"

    header_a.write_text(
        """
#include <string>

namespace ifcapi::bindings {
int contract_count(const std::string& name);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    header_b.write_text(
        """
namespace ifcapi::bindings {
double contract_scale(double value);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text("int reference() { return 0; }\n", encoding="utf-8")

    functions = discover_namespace_functions_with_synthetic_source(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        f'#include "{header_a.as_posix()}"\n#include "{header_b.as_posix()}"\n',
        "ifcapi::bindings",
        selected_names={"contract_count", "contract_scale"},
        reference_source_root=tmp_path,
    )

    assert set(functions) == {"contract_count", "contract_scale"}
    assert functions["contract_count"][0].params[0].cpp_type == "const std::string &"
    assert functions["contract_scale"][0].return_cpp_type == "double"


def test_discovery_uses_explicit_compilation(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "sample.h"
    source = tmp_path / "sample.cpp"

    header.write_text(
        """
#include <string>

namespace Demo {
class Foo {
public:
    int bar(int id);
    const std::string& baz(const std::string& guid) const;
};

int walk(int steps);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "sample.h"\n', encoding="utf-8")
    environment = DiscoveryEnvironment(
        compilation=CompilationConfig(
            compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
        )
    )

    methods = discover_public_methods(environment, source, "Demo::Foo")
    functions = discover_namespace_functions(environment, source, "Demo")

    assert set(methods) == {"bar", "baz"}
    assert methods["baz"][0].params[0].cpp_type == "const std::string &"
    assert set(functions) == {"walk"}
    assert functions["walk"][0].params[0].cpp_type == "int"


def test_synthetic_contract_discovery_uses_explicit_compilation(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "contract.h"
    header.write_text(
        """
#include <string>

namespace ifcapi::bindings {
int contract_count(const std::string& name);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    environment = DiscoveryEnvironment(
        compilation=CompilationConfig(
            compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
        )
    )

    functions = discover_namespace_functions_with_synthetic_source(
        environment,
        f'#include "{header.as_posix()}"\n',
        "ifcapi::bindings",
        selected_names={"contract_count"},
        reference_source_root=tmp_path,
    )

    assert set(functions) == {"contract_count"}
    assert functions["contract_count"][0].params[0].cpp_type == "const std::string &"


def test_discover_public_fields_with_inheritance(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "fields.h"
    source = tmp_path / "fields.cpp"

    header.write_text(
        """
#include <memory>

namespace Demo {
struct Node {
    using ptr = std::shared_ptr<Node>;
};

struct Base {
public:
    int inherited;
};

struct Derived : Base {
public:
    Node::ptr axis;
private:
    int hidden;
};
}

namespace Other {
struct Base {
public:
    int wrong;
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "fields.h"\n', encoding="utf-8")

    own_fields = discover_public_fields(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Derived",
    )
    assert set(own_fields) == {"axis"}
    assert own_fields["axis"].cpp_type == "Node::ptr"
    assert (
        own_fields["axis"].cpp_type_ref.desugared_spelling
        == "std::shared_ptr<Demo::Node>"
    )
    assert own_fields["axis"].cpp_type_ref.base_name == "std::shared_ptr"
    assert own_fields["axis"].cpp_type_ref.template_args[0].base_name == "Demo::Node"

    inherited_fields = discover_public_fields(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Derived",
        include_inherited=True,
    )
    assert set(inherited_fields) == {"axis", "inherited"}
    assert inherited_fields["inherited"].cpp_type == "int"
    assert inherited_fields["inherited"].cpp_type_ref.canonical_spelling == "int"

    qualified_inherited_fields = discover_public_fields(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::Derived",
        include_inherited=True,
    )
    assert set(qualified_inherited_fields) == {"axis", "inherited"}


def test_discover_cpp_types_marks_enums(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "enums.h"
    source = tmp_path / "enums.cpp"

    header.write_text(
        """
namespace Demo {
enum class Mode { A __attribute__((annotate("ifcapi.literal:ALPHA"))), B };

struct Widget {
    Mode mode() const;
    void set_mode(Mode value);
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "enums.h"\n', encoding="utf-8")

    methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::Widget",
    )

    assert methods["mode"][0].return_type_ref.is_enum
    assert methods["mode"][0].return_type_ref.base_name == "Mode"
    assert methods["mode"][0].return_type_ref.enum_values == (("ALPHA", 0), ("B", 1))
    assert methods["set_mode"][0].params[0].cpp_type_ref.is_enum


def test_discover_cpp_types_marks_typedef_enums(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "typedef_enums.h"
    source = tmp_path / "typedef_enums.cpp"

    header.write_text(
        """
namespace Demo {
struct SimpleType {
    typedef enum {
        integer_type,
        string_type
    } data_type;

    data_type declared_type() const;
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "typedef_enums.h"\n', encoding="utf-8")

    methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::SimpleType",
    )

    assert methods["declared_type"][0].return_type_ref.is_enum
    assert (
        methods["declared_type"][0].return_type_ref.enum_qualified_name
        == "Demo::SimpleType::data_type"
    )


def test_discover_cpp_types_marks_enum_fields_under_skipped_root(
    tmp_path: Path,
) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "enum_fields.h"
    source = tmp_path / "enum_fields.cpp"

    header.write_text(
        """
namespace ifcopenshell {
namespace demo {
struct Widget {
    enum Mode { A, B };
    Mode mode;
};
}
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "enum_fields.h"\n', encoding="utf-8")

    fields = discover_public_fields(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "ifcopenshell::demo::Widget",
    )

    assert fields["mode"].cpp_type_ref.is_enum
    assert (
        fields["mode"].cpp_type_ref.enum_qualified_name
        == "ifcopenshell::demo::Widget::Mode"
    )


def test_discovery_resolves_scoped_and_standard_types(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "scoped.h"
    source = tmp_path / "scoped.cpp"

    header.write_text(
        """
#include <string>

namespace Demo {
struct Outer {
    struct Inner {};
};

struct Container {
    Outer::Inner inner() const;
    const std::string& name() const;
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "scoped.h"\n', encoding="utf-8")

    methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::Container",
    )

    assert methods["inner"][0].return_type_ref.storage_spelling == "Outer::Inner"
    assert methods["name"][0].return_type_ref.storage_spelling == "const std::string&"


def test_discovery_resolves_lowercase_bare_type(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "lowercase.h"
    source = tmp_path / "lowercase.cpp"

    header.write_text(
        """
namespace Demo {
struct declaration {};

struct schema_definition {
    declaration declared() const;
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "lowercase.h"\n', encoding="utf-8")

    methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::schema_definition",
    )

    assert (
        methods["declared"][0].return_type_ref.storage_spelling == "Demo::declaration"
    )


def test_discovery_resolves_bare_ptr_and_iterator_aliases(tmp_path: Path) -> None:
    compiler = shutil.which("clang++")
    if compiler is None:
        pytest.skip("clang++ is not available")

    header = tmp_path / "aliases.h"
    source = tmp_path / "aliases.cpp"

    header.write_text(
        """
#include <memory>

namespace Demo {
struct Derived {
public:
    using ptr = std::shared_ptr<Derived>;
    using it = int;

    ptr axis;
    it index() const;
};
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    source.write_text('#include "aliases.h"\n', encoding="utf-8")

    fields = discover_public_fields(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::Derived",
    )
    methods = discover_public_methods(
        DiscoveryEnvironment(
            compilation=CompilationConfig(
                compiler=compiler, include_dirs=(tmp_path,), working_directory=tmp_path
            )
        ),
        source,
        "Demo::Derived",
    )

    assert (
        fields["axis"].cpp_type_ref.desugared_spelling
        == "std::shared_ptr<Demo::Derived>"
    )
    assert methods["index"][0].return_cpp_type == "it"
