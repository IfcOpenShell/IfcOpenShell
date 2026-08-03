import ifcopenshell

cases = (
    ("pass", "label-values", ("test1", "test2")),
    ("pass", "nil-values", None),
    ("fail", "distinct-value-types", ("test1", 2)),
)

for result, name, values in cases:
    ifc_file = ifcopenshell.file(schema="IFC4X3")
    list_values = None
    if values is not None:
        list_values = [
            ifc_file.create_entity("IfcInteger", v) if isinstance(v, int) else ifc_file.create_entity("IfcLabel", v)
            for v in values
        ]
    ifc_file.create_entity("IfcPropertyListValue", Name="Test", ListValues=list_values)
    ifc_file.write(f"{result}-property-list-value-{name}.ifc")
