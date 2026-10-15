# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape


@pytest.mark.parametrize("method", ["create_shape", "iterator"])
@pytest.mark.parametrize("with_library", [False, True], ids=["project_only", "unitless_library"])
def test_project_library_does_not_override_project_units_9926(method, with_library):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/9926
    model = ifcopenshell.file(schema="IFC4")
    if with_library:
        model.createIfcProjectLibrary(GlobalId=ifcopenshell.guid.new(), Name="Library without units")
    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, origin, None)
    units = model.createIfcUnitAssignment([model.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")])
    model.createIfcProject(GlobalId=ifcopenshell.guid.new(), RepresentationContexts=[context], UnitsInContext=units)
    profile = model.createIfcRectangleProfileDef("AREA", None, None, 1000.0, 200.0)
    solid = model.createIfcExtrudedAreaSolid(profile, origin, model.createIfcDirection((0.0, 0.0, 1.0)), 1000.0)
    body = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    placement = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((1000.0, 2000.0, 3000.0)))
    window = model.createIfcWindow(
        GlobalId=ifcopenshell.guid.new(),
        ObjectPlacement=model.createIfcLocalPlacement(None, placement),
        Representation=model.createIfcProductDefinitionShape(Representations=[body]),
    )

    settings = ifcopenshell.geom.settings()
    if method == "create_shape":
        shape = ifcopenshell.geom.create_shape(settings, window, geometry_library="opencascade")
    else:
        iterator = ifcopenshell.geom.iterator(
            settings, model, num_threads=1, include=[window], geometry_library="opencascade"
        )
        assert iterator.initialize()
        shape = iterator.get()

    translation = ifcopenshell.util.shape.get_shape_matrix(shape)[:3, 3]
    volume = ifcopenshell.util.shape.get_volume(shape.geometry)
    assert (*translation, volume) == pytest.approx((1.0, 2.0, 3.0, 0.2))
