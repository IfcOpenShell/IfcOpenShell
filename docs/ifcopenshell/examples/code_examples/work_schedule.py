# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): a work schedule constructing a building floor by
# floor.

import sys

ifc_path = sys.argv[1]

# tag::example
import datetime

import ifcopenshell
import ifcopenshell.api.sequence
from ifcopenshell.util.element import get_decomposition
from ifcopenshell.util.placement import get_storey_elevation


# Define a convenience function to add a task chained to a predecessor
def add_task(model, name, predecessor, work_schedule):
    # Add a construction task
    task = ifcopenshell.api.sequence.add_task(
        model, work_schedule=work_schedule, name=name, predefined_type="CONSTRUCTION"
    )

    # Give it a time
    task_time = ifcopenshell.api.sequence.add_task_time(model, task=task)

    # Arbitrarily set the task's scheduled time duration to be 1 week
    ifcopenshell.api.sequence.edit_task_time(
        model,
        task_time=task_time,
        attributes={"ScheduleStart": datetime.date(2000, 1, 1), "ScheduleDuration": "P1W"},
    )

    # If a predecessor exists, create a finish to start relationship
    if predecessor:
        ifcopenshell.api.sequence.assign_sequence(model, relating_process=predecessor, related_process=task)

    return task


# Open an existing IFC4 model you have of a building
model = ifcopenshell.open(ifc_path)

# Create a new construction schedule
schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction")

# Let's imagine a starting task for site establishment.
task = add_task(model, "Site establishment", None, schedule)
start_task = task

# Get all our storeys sorted by elevation ascending.
storeys = sorted(model.by_type("IfcBuildingStorey"), key=lambda s: get_storey_elevation(s))

# For each storey ...
for storey in storeys:
    # Add a construction task to construct that storey, using our convenience function
    task = add_task(model, f"Construct {storey.Name}", task, schedule)

    # Assign all the products in that storey to the task as construction outputs.
    for product in get_decomposition(storey):
        ifcopenshell.api.sequence.assign_product(model, relating_product=product, related_object=task)

# Ask the computer to calculate all the dates for us from the start task.
# For example, if the first task started on the 1st of January and took a
# week, the next task will start on the 8th of January. This saves us
# manually doing date calculations.
ifcopenshell.api.sequence.cascade_schedule(model, task=start_task)

# Calculate the critical path and floats.
ifcopenshell.api.sequence.recalculate_schedule(model, work_schedule=schedule)

# Write out to a file
model.write("model.ifc")
# end::example

assert len(ifcopenshell.open("model.ifc").by_type("IfcTask")) == len(storeys) + 1
