import time

import ifcopenshell
from generate import normalize_header, pass_if, write_fixture

latitudes = [
    (False, (-361, 0, 0), 1),
    (False, (-361, 0, 0, 0), 1),
    (True, (-360, 0, 0, 0), 1),
    (True, (0, 0, 0, 0), 1),
    (True, (359, 0, 0, 0), 1),
    (False, (360, 0, 0, 0), 1),
    (True, (30, 30, 30), 1),
    (False, (1000, 1000, 1000), 3),
    (False, (0, 0, 1000), 1),
    (False, (0, 0, 1000, 0), 1),
    (True, (0, 0, 0, 100000), 1),
    (True, (1, 1, 1, 1), 1),
    (True, (-1, -1, -1, -1), 1),
    (False, (-1, -1, 1, 1), 1),
    (False, (1, -1, -1, -1), 1),
]

for i, (is_valid, lat, errors_if_fail) in enumerate(latitudes):
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
    units = f.createIfcUnitAssignment(Units=[f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    site = f.createIfcSite(ifcopenshell.guid.new(), ownerhist, RefLatitude=lat)
    proj = f.createIfcProject(
        ifcopenshell.guid.new(),
        ownerhist,
        "My Project",
        UnitsInContext=units,
        RepresentationContexts=[
            f.createIfcGeometricRepresentationContext(
                None,
                None,
                3,
                None,
                f.create_entity(f"IfcAxis2Placement3D", f.createIfcCartesianPoint((0.0, 0.0, 0.0))),
            )
        ],
    )
    f.createIfcRelAggregates(ifcopenshell.guid.new(), ownerhist, None, None, proj, [site])
    normalize_header(f)
    write_fixture(f, __file__, pass_if(is_valid, errors_if_fail=errors_if_fail), f"site-latitude-{i}-ifc2x3")
