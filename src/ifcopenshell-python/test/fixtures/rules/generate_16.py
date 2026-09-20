import time

import ifcopenshell

from ...fixture_generate import normalize_header, pass_if, write_fixture

names = [("Same", "Same"), ("Different", "SomethingElse")]

make_prop = lambda f: lambda nm: f.createIfcPropertySingleValue(Name=nm)

old_map = map
map = lambda fn, *args: list(old_map(fn, *args))

for nms in names:
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    units = f.createIfcUnitAssignment(Units=[f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
    f.createIfcPropertySet(ifcopenshell.guid.new(), ownerhist, "MyPset", HasProperties=map(make_prop(f), nms))
    normalize_header(f)
    write_fixture(f, __file__, pass_if(len(set(nms)) == len(nms)), f"property-{'-'.join(map(str.lower, nms))}-ifc2x3")
