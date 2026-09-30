import time

import ifcopenshell

from ...fixture_generate import normalize_header, pass_if, write_fixture

for i in range(3):
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    units = f.createIfcUnitAssignment(Units=[f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
    for j in range(i):
        f.createIfcProject(
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
    normalize_header(f)
    write_fixture(f, __file__, pass_if(i != 2), f"{i}-projects-ifc2x3")
