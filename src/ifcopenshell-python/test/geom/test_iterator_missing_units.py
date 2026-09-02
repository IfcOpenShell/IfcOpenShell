import ifcopenshell
import ifcopenshell.geom


def _minimal_ifc2x3_with_blank_units_in_context(path):
    """Write an IFC2X3 file whose IfcProject.UnitsInContext (attribute index 8) is blank.

    UnitsInContext is mandatory per the schema, but IfcOpenShell's lenient STEP parser
    accepts files where a non-conformant authoring tool omitted it anyway (see #7489).
    """
    f = ifcopenshell.file(schema="IFC2X3")
    person = f.create_entity("IfcPerson", GivenName="A")
    org = f.create_entity("IfcOrganization", Name="Org")
    person_org = f.create_entity("IfcPersonAndOrganization", ThePerson=person, TheOrganization=org)
    app = f.create_entity(
        "IfcApplication",
        ApplicationDeveloper=org,
        Version="1",
        ApplicationFullName="x",
        ApplicationIdentifier="x",
    )
    owner_hist = f.create_entity(
        "IfcOwnerHistory",
        OwningUser=person_org,
        OwningApplication=app,
        ChangeAction="NOCHANGE",
        CreationDate=0,
    )
    pt = f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
    ax = f.create_entity("IfcAxis2Placement3D", Location=pt)
    ctx = f.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=1e-05,
        WorldCoordinateSystem=ax,
    )
    si_unit = f.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    units = f.create_entity("IfcUnitAssignment", Units=[si_unit])
    project = f.create_entity(
        "IfcProject",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_hist,
        Name="Test",
        RepresentationContexts=[ctx],
        UnitsInContext=units,
    )
    f.write(str(path))

    # The Python API refuses to assign None to a non-optional attribute directly,
    # so simulate a non-conformant file by blanking it out in the raw SPF text.
    content = path.read_text()
    project_line = f"#{project.id()}=IFCPROJECT("
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith(project_line):
            lines[i] = line.rsplit(f"#{units.id()});", 1)[0] + "$);\n"
            break
    else:
        raise AssertionError("IfcProject line not found in written file")
    path.write_text("".join(lines))


def test_iterator_construction_survives_blank_units_in_context(tmp_path):
    ifc_path = tmp_path / "blank_units.ifc"
    _minimal_ifc2x3_with_blank_units_in_context(ifc_path)

    f = ifcopenshell.open(str(ifc_path))
    settings = ifcopenshell.geom.settings()

    # Regression test for #7489: this used to raise
    # "RuntimeError: Type held at index 8 is class Blank and not class IfcUtil::IfcBaseClass *"
    # because IfcProject.UnitsInContext is required by the schema and the generated
    # accessor was called unguarded while detecting model units.
    iterator = ifcopenshell.geom.iterator(settings, f)
    assert iterator is not None
