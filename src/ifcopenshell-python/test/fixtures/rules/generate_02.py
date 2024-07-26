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
    f.write(f"{'pass' if is_valid else 'fail'}-site-latitude-{i}-ifc2x3.ifc")
