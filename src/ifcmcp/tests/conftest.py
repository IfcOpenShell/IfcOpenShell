# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import pytest

from ifcmcp.core import IfcSession


@pytest.fixture
def session():
    return IfcSession()


@pytest.fixture
def model():
    """IFC4 model with a spatial hierarchy, a wall, and a slab."""
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
def model_file(model, tmp_path):
    """Write the model fixture to a temp file and return the path."""
    path = tmp_path / "test.ifc"
    model.write(str(path))
    return str(path)


@pytest.fixture
def loaded_session(model):
    """An IfcSession with an in-memory model already loaded (no file path)."""
    s = IfcSession()
    s.model = model
    return s
