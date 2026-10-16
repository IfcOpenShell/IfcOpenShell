# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): creating a simple model from scratch.

import ifcopenshell

# tag::example
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit

# Create a blank model
model = ifcopenshell.api.project.create_file()

# All projects must have one IFC Project element
project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="My Project")

# Geometry is optional in IFC, but because we want to use geometry in this
# example, let's define units. Assigning without arguments defaults to metric.
ifcopenshell.api.unit.assign_unit(model)

# Let's create a modeling geometry context, so we can store 3D geometry
# (note: IFC supports 2D too!)
context = ifcopenshell.api.context.add_context(model, context_type="Model")

# In particular, in this example we want to store the 3D "body" geometry of
# objects, i.e. the body shape
body = ifcopenshell.api.context.add_context(
    model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
)

# Create a site, building, and storey. Many hierarchies are possible.
site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="My Site")
building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name="Building A")
storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name="Ground Floor")

# Since the site is our top level location, assign it to the project.
# Then place our building on the site, and our storey in the building.
ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])
ifcopenshell.api.aggregate.assign_object(model, relating_object=site, products=[building])
ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])

# Let's create a new wall
wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

# Give our wall a local origin at (0, 0, 0)
ifcopenshell.api.geometry.edit_object_placement(model, product=wall)

# Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
representation = ifcopenshell.api.geometry.add_wall_representation(
    model, context=body, length=5, height=3, thickness=0.2
)
# Assign our new body geometry back to our wall
ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=representation)

# Place our wall in the ground floor
ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[wall])

# Write out to a file
model.write("model.ifc")
# end::example

written = ifcopenshell.open("model.ifc")
assert len(written.by_type("IfcWall")) == 1
assert written.by_type("IfcWall")[0].Representation
