import itertools
import time
import ifcopenshell

for pty, ety in itertools.product(("GRILLE", "USERDEFINED"), (None, "Something")):
    f = ifcopenshell.file(schema="IFC2X3")
    p = f.createIfcPerson(Id="tfk", GivenName="Thomas")
    o = f.createIfcOrganization(Name="AECgeeks")
    pando = f.createIfcPersonAndOrganization(p, o)
    appl = f.createIfcApplication(o, ifcopenshell.version, "IfcOpenShell", f"IfcOpenShell {ifcopenshell.version}")
    ownerhist = f.createIfcOwnerHistory(pando, appl, ChangeAction="ADDED", CreationDate=int(time.time()))
    f.createIfcAirTerminalType(ifcopenshell.guid.new(), ownerhist, "My Type", ElementType=ety, PredefinedType=pty)
    valid = pty != "USERDEFINED" or ety is not None
    f.write(f"{'pass' if valid else 'fail'}-air-terminal-type-{pty}-{ety}-ifc2x3.ifc")
