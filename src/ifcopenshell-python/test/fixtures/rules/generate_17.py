import time

import ifcopenshell
from generate import normalize_header, pass_if, write_fixture

for i, nm in enumerate(("no-mls", "mls", "mlsu")):
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    units = f.createIfcUnitAssignment(Units=[f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
    wall = f.createIfcWallStandardCase(ifcopenshell.guid.new(), ownerhist)
    if i in (1, 2):
        mls = f.createIfcMaterialLayerSet([f.createIfcMaterialLayer(None, 0.1)])
        if i == 2:
            mls = f.createIfcMaterialLayerSetUsage(mls, "AXIS2", "POSITIVE", 0.0)
        f.createIfcRelAssociatesMaterial(
            ifcopenshell.guid.new(), ownerhist, RelatedObjects=[wall], RelatingMaterial=mls
        )
    normalize_header(f)
    write_fixture(f, __file__, pass_if(i == 2), f"wall-{nm}-ifc2x3")
