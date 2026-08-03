import ifcopenshell
from generate import normalize_header

for i, (r1, r2) in enumerate(
    [("SUPPLIER", None), ("SUPPLIER", "Valid"), ("USERDEFINED", "Valid"), ("USERDEFINED", None)]
):
    f = ifcopenshell.file(schema="IFC2X3")
    f.createIfcActorRole(r1, r2)
    normalize_header(f)
    f.write(f"{'fail' if i == 3 else 'pass'}-actor-role-{r1}-{r2}-ifc2x3.ifc")
