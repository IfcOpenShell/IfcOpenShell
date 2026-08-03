import ifcopenshell
from generate import fail_if, normalize_header, write_fixture

for i, (r1, r2) in enumerate(
    [("SUPPLIER", None), ("SUPPLIER", "Valid"), ("USERDEFINED", "Valid"), ("USERDEFINED", None)]
):
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcActorRole(r1, r2)
    normalize_header(f)
    write_fixture(f, __file__, fail_if(i == 3), f"actor-role-{r1}-{r2}-ifc2x3")
