import ifcopenshell

create_none = lambda f: None
create_polyline = lambda f: f.createIfcPolyline(
    (f.createIfcCartesianPoint((0.0, 0.0)), f.createIfcCartesianPoint((1.0, 0.0)))
)
create_point = lambda f: f.createIfcCartesianPoint((0.0, 0.0))

for i, make_item in enumerate((create_none, create_polyline, create_point)):
    f = ifcopenshell.file(schema="IFC2X3")
    inst = f.createIfcAnnotationCurveOccurrence(
        make_item(f), [f.createIfcPresentationStyleAssignment([f.createIfcCurveStyle()])]
    )
    f.write(
        f"{'fail' if i == 2 else 'pass'}-annotation-curve-occurence-{'None' if inst.Item is None else inst.Item.is_a()}-ifc2x3.ifc"
    )
