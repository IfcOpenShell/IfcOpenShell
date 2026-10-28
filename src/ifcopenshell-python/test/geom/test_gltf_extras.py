# This file was generated with the assistance of an AI coding tool.
import json
import struct

import pytest

import ifcopenshell.geom
import ifcopenshell.guid


def test_gltf_extras(tmp_path):
    path = tmp_path / "extras.glb"
    serializer = ifcopenshell.geom.serializers.gltf(str(path), ifcopenshell.geom.settings())
    serializer.setExtras("ifcopenshell-filters", ["exclude entities IfcOpeningElement IfcSpace"])
    serializer.setExtras("label", "before header")
    serializer.writeHeader()
    serializer.setExtras("label", "after header")
    serializer.setExtras("count", 42)
    serializer.setExtras("scale", 1.25)
    serializer.setExtras("empty", [])
    serializer.finalize()
    del serializer

    data = path.read_bytes()
    length, chunk_type = struct.unpack_from("<II", data, 12)
    assert chunk_type == 0x4E4F534A
    asset = json.loads(data[20 : 20 + length])["asset"]
    assert asset["version"] == "2.0"
    extras = asset["extras"]
    assert extras["ifcopenshell-filters"] == ["exclude entities IfcOpeningElement IfcSpace"]
    assert extras["label"] == "after header"
    assert extras["count"] == 42
    assert isinstance(extras["count"], int)
    assert extras["scale"] == 1.25
    assert extras["empty"] == []
    assert extras["ifcopenshell-settings"]["iterator-output"] == "TRIANGULATED"


def test_glb_iterator_offset_applied(tmp_path):
    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, origin, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")])
    model.createIfcProject(GlobalId=ifcopenshell.guid.new(), RepresentationContexts=[context], UnitsInContext=units)
    profile = model.createIfcRectangleProfileDef("AREA", None, None, 2000.0, 2000.0)
    # Center the two metre cube on its product placement, including along the extrusion axis.
    solid_origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, -1000.0)))
    solid = model.createIfcExtrudedAreaSolid(profile, solid_origin, model.createIfcDirection((0.0, 0.0, 1.0)), 2000.0)
    body = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((1e9, 2e9, 3e9)))
    model.createIfcBuildingElementProxy(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=model.createIfcLocalPlacement(None, placement),
        Representation=model.createIfcProductDefinitionShape(Representations=[body]),
    )

    settings = ifcopenshell.geom.settings()
    settings.set("max-offset", 1000.0)
    settings.set("no-parallel-mapping", True)
    settings.set("use-world-coords", True)
    iterator = ifcopenshell.geom.iterator(settings, model)
    assert iterator.initialize()
    # The Python iterator's settings attribute holds the original input settings.
    effective_settings = ifcopenshell.ifcopenshell_wrapper.iterator.settings(iterator)
    path = tmp_path / "offset.glb"
    serializer = ifcopenshell.geom.serializers.glb(str(path), effective_settings)
    serializer.setFile(model)
    serializer.writeHeader()
    shape = iterator.get()
    serializer.write(shape)
    assert not iterator.next()
    serializer.finalize()
    del serializer

    with path.open("rb") as stream:
        stream.seek(12)  # Skip the GLB header to read the first chunk (JSON).
        length, chunk_type = struct.unpack("<II", stream.read(8))
        assert chunk_type == 0x4E4F534A
        gltf = json.loads(stream.read(length))

    exported_settings = gltf["asset"]["extras"]["ifcopenshell-settings"]
    assert exported_settings["length-unit"] == pytest.approx(0.001)
    assert exported_settings["offset-applied"] == pytest.approx([-1e6, -2e6, -3e6])
    vertices = shape.geometry.verts
    for axis in range(3):
        assert min(vertices[axis::3]) == pytest.approx(-1.0)
        assert max(vertices[axis::3]) == pytest.approx(1.0)
    assert len(gltf["meshes"]) == 1
