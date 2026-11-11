# This file was generated with the assistance of an AI coding tool.
import ifcopenshell.api.aggregate
import ifcopenshell.api.group
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.structural
import ifcopenshell.api.unit
import pytest


@pytest.fixture
def model():
    """Create an IFC4 model with a spatial hierarchy and a wall."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="TestSite")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="TestBuilding")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Ground Floor")

    ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
    ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
    ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)

    wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="Wall001")
    ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)

    slab = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSlab", name="Slab001")
    ifcopenshell.api.spatial.assign_container(f, products=[slab], relating_structure=storey)

    return f


@pytest.fixture
def structural_model():
    """An IFC4 cantilever: a member between two connections, one of them fixed,
    linked to a beam, with a point load in a load case, through a load group,
    and a load combination of that case."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]
    ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    analysis = ifcopenshell.api.structural.add_structural_analysis_model(f)
    analysis.Name = "Analysis"
    member = ifcopenshell.api.root.create_entity(
        f, ifc_class="IfcStructuralCurveMember", predefined_type="RIGID_JOINED_MEMBER", name="Cantilever"
    )
    root = ifcopenshell.api.root.create_entity(f, ifc_class="IfcStructuralPointConnection", name="Root")
    tip = ifcopenshell.api.root.create_entity(f, ifc_class="IfcStructuralPointConnection", name="Tip")
    for connection in (root, tip):
        ifcopenshell.api.structural.add_structural_member_connection(
            f, relating_structural_member=member, related_structural_connection=connection
        )
    condition = ifcopenshell.api.structural.add_structural_boundary_condition(f, connection=root)
    condition.Name = "Fixed"
    condition.TranslationalStiffnessZ = f.createIfcBoolean(True)
    condition.RotationalStiffnessY = f.createIfcRotationalStiffnessMeasure(1000.0)
    ifcopenshell.api.structural.assign_structural_analysis_model(
        f, products=[member, root, tip], structural_analysis_model=analysis
    )
    beam = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBeam", name="Beam")
    ifcopenshell.api.structural.assign_product(f, relating_product=member, related_object=beam)

    case = ifcopenshell.api.structural.add_structural_load_case(
        f, name="Live", action_type="VARIABLE_Q", action_source="LIVE_LOAD_Q"
    )
    case.SelfWeightCoefficients = (0.0, 0.0, 0.0)
    group = ifcopenshell.api.structural.add_structural_load_group(f, name="Point loads")
    ifcopenshell.api.group.assign_group(f, products=[group], group=case)
    force = ifcopenshell.api.structural.add_structural_load(f, name="P", ifc_class="IfcStructuralLoadSingleForce")
    force.ForceZ = -1000.0
    action = ifcopenshell.api.structural.add_structural_activity(
        f, applied_load=force, structural_member=tip, ifc_class="IfcStructuralPointAction", predefined_type=None
    )
    ifcopenshell.api.group.assign_group(f, products=[action], group=group)

    combination = ifcopenshell.api.structural.add_structural_load_combination(f, name="ULS")
    combination.Coefficient = 2.0
    ifcopenshell.api.structural.assign_structural_load_combination(
        f, load_case=case, load_combination=combination, factor=1.5
    )
    analysis.LoadedBy = [combination]

    # A load case no model is loaded by
    ifcopenshell.api.structural.add_structural_load_case(f, name="Unused")
    return f
