import check_runtime_plugins as guard
import pytest

SCHEMAS = ("2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2")
WRAPPER = "_ifcopenshell_wrapper.cp313-win_amd64.pyd"
CORE = ["ifcopenshell.parse.dll", "ifcopenshell.geometry.dll", "ifcopenshell_document_rdb.dll"]


def package(schemas=SCHEMAS, families=guard.PER_SCHEMA_FAMILIES, suffix="dll"):
    names = [WRAPPER, *CORE, "ifcopenshell.py"]
    for prefix in families.values():
        names += [f"{prefix}{schema}.{suffix}" for schema in schemas]
    return names


def test_complete_package_passes():
    assert guard.problems(package()) == []


def test_reduced_schema_build_passes():
    """WASM and custom SCHEMA_VERSIONS builds ship a subset, that is not a regression."""
    assert guard.problems(package(schemas=("2x3", "4", "4x3_add2"))) == []


def test_executable_package_without_geometry_writers_passes():
    families = {k: v for k, v in guard.PER_SCHEMA_FAMILIES.items() if k != "geometry_writer"}
    assert guard.problems(package(families=families)) == []


def test_package_without_the_wrapper_is_not_checked():
    assert guard.problems(["svgfill.exe", "ifcopenshell_geometry_svgfill.dll"]) == []


def test_pre_9305_windows_package_fails():
    """The shipped 0.9.0 win64 package: link-visible libraries only, no load-by-name plugins."""
    issues = guard.problems([WRAPPER, *CORE])
    assert any("ifcopenshell_parse_schema_ifc*" in issue for issue in issues)


def test_single_missing_schema_plugin_is_named():
    names = [n for n in package() if n != "ifcopenshell_parse_schema_ifc4x2.dll"]
    with pytest.raises(RuntimeError, match=r"ifcopenshell_parse_schema_ifc4x2\.dll"):
        guard.check(names, "artifact")


def test_missing_geometry_mapping_for_a_built_schema_is_named():
    names = [n for n in package() if n != "ifcopenshell_geometry_mapping_ifc4.dll"]
    with pytest.raises(RuntimeError, match=r"ifcopenshell_geometry_mapping_ifc4\.dll"):
        guard.check(names, "artifact")


@pytest.mark.parametrize("suffix", ["so", "so.0.9.0", "dylib", "dll"])
def test_platform_suffixes(suffix):
    assert guard.problems(package(suffix=suffix)) == []
