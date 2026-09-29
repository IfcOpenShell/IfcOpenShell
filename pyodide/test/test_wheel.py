import zipfile
from pathlib import Path

from ..order_pyodide_wheel_shared_objects import shared_object_sort_key


def _first_so_name(wheel_path: Path) -> str:
    with zipfile.ZipFile(wheel_path) as zf:
        for name in zf.namelist():
            if name.endswith(".so"):
                return Path(name).name
    return wheel_path.name


def test_ifcopenshell_import(selenium, request):
    dist_dir = Path(request.config.getoption("--dist-dir"))
    wheel_paths = list(dist_dir.glob("ifcopenshell*.whl"))
    wheel_paths.sort(key=lambda path: shared_object_sort_key(_first_so_name(path), 0))
    WHEEL_NAMES = tuple(path.name for path in wheel_paths)

    selenium.load_package("micropip")
    selenium.run_async(f"""
        import micropip
        wheel_filenames = {WHEEL_NAMES!r}
        for wheel_filename in wheel_filenames:
            print(f"Loading {{wheel_filename}}...")
            await micropip.install(f"./{{wheel_filename}}")
        import ifcopenshell
        from pathlib import Path
        ifcopenshell.set_plugin_search_paths([str(Path(ifcopenshell.__file__).parent)])
        ifc_file = ifcopenshell.file()
        wall = ifc_file.create_entity("IfcWall")
        wall1 = ifc_file.by_type("IfcWall")[0]
        print(wall, wall1)
        assert wall == wall1, "Wall entity doesn't match"
        wall.Name = "Test"
        assert wall.Name == "Test", f"Entity name wasn't changed: {{wall}}"
        print(wall)
        """)
