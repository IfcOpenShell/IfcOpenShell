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

        wrapper = ifcopenshell.ifcopenshell_wrapper
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><g><path d="M 0 0 L 1 0 L 0 1 Z"/></g></svg>'
        segments = wrapper.svg_to_line_segments(svg, None)
        polygons = wrapper.line_segments_to_polygons(wrapper.EXACT_PREDICATES, 0.0, segments)
        assert len(polygons) == 1, f"Unexpected svgfill polygon groups: {{polygons}}"
        assert len(polygons[0]) == 1, f"Unexpected svgfill polygons: {{polygons}}"
        """
    )
