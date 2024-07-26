import time
import ifcopenshell

for ents in [
    ("IfcWall",),
    ("IfcSpace",),
    (
        "IfcZone",
        "IfcSpace",
    ),
    (
        "IfcWall",
        "IfcSpace",
    ),
]:
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    units = f.createIfcUnitAssignment(Units=[f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
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

    def elems():
        for ent in ents:
            el = f.create_entity(ent, ifcopenshell.guid.new(), ownerhist)
            if ent == "IfcZone":
                f.createIfcRelAssignsToGroup(
                    ifcopenshell.guid.new(),
                    ownerhist,
                    RelatedObjects=[f.createIfcSpace(ifcopenshell.guid.new(), ownerhist)],
                    RelatingGroup=el,
                )
            yield el

    zone = f.createIfcZone(ifcopenshell.guid.new(), ownerhist)
    f.createIfcRelAssignsToGroup(ifcopenshell.guid.new(), ownerhist, RelatedObjects=list(elems()), RelatingGroup=zone)
    f.createIfcRelAggregates(
        ifcopenshell.guid.new(), ownerhist, RelatingObject=proj, RelatedObjects=f.by_type("IfcSpace")
    )
    valid = not (set(ents) - {"IfcZone", "IfcSpace"})
    f.write(f"{'pass' if valid else 'fail'}-zone-with-{'-'.join(ents)}-{f.schema.lower()}.ifc")
