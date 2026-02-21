from pathlib import Path

WHEEL_FILENAME = next(
    p.name for p in (Path.cwd() / "pyodide").iterdir() if p.name.startswith("ifcopenshell-") and p.suffix == ".whl"
)


def test_ifcopenshell_import(selenium):
    selenium.load_package("micropip")
    # Important to test it with `micropip.install`
    # without any dependencies loaded to ensure micropip will load them automatically.
    selenium.run_async(
        f"""
        import micropip
        await micropip.install(f"./{WHEEL_FILENAME}")
        import ifcopenshell
        ifc_file = ifcopenshell.file()
        wall = ifc_file.create_entity("IfcWall")
        wall1 = ifc_file.by_type("IfcWall")[0]
        print(wall, wall1)
        assert wall == wall1, "Wall entity doesn't match"
        wall.Name = "Test"
        assert wall.Name == "Test", f"Entity name wasn't changed: {{wall}}"
        print(wall)
        """
    )
