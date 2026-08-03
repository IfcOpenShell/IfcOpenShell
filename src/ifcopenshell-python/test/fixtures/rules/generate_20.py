import ifcopenshell
from generate import normalize_header

task = lambda f: f.createIfcTask(ifcopenshell.guid.new(), None, "sleep", IsMilestone=True)
wall = lambda f: f.createIfcWall(ifcopenshell.guid.new())

for i, fn in enumerate((task, wall)):
    f = ifcopenshell.file(schema="IFC4")
    elem = fn(f)
    f.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(), None, None, None, [elem], f.createIfcMaterial("brick"))
    normalize_header(f)
    f.write(f"{'pass' if i else 'fail'}-assoc-material-{elem.is_a()}-{f.schema}.ifc")
