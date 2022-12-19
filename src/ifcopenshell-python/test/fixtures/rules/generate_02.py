import time
import ifcopenshell

latitudes = [
    (False, (-361, 0, 0)),
    (False, (-361, 0, 0, 0)),
    (True, (-360, 0, 0, 0)),
    (True, (0, 0, 0, 0)),
    (True, (359, 0, 0, 0)),
    (False, (360, 0, 0, 0)),
    (True, (30, 30, 30)),
    (False, (1000, 1000, 1000)),
    (False, (0, 0, 1000)),
    (False, (0, 0, 1000, 0)),
    (True, (0, 0, 0, 100000)),
    (True, (1, 1, 1, 1)),
    (True, (-1, -1, -1, -1)),
    (False, (-1, -1, 1, 1)),
    (False, (1, -1, -1, -1)),
]

for i, (is_valid, lat) in enumerate(latitudes):
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
    f.createIfcSite(ifcopenshell.guid.new(), ownerhist, RefLatitude=lat)
    f.write(f"{'pass' if is_valid else 'fail'}-site-latitude-{i}-ifc2x3.ifc")
