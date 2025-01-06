import time
import ifcopenshell

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
    f.write(f"{'fail' if i == 2 else 'pass'}-{i}-projects-ifc2x3.ifc")
