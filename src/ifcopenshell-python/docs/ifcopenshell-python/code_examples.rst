Code examples
=============

Examples for common basic tasks are shown here. In all examples, it is assumed
that you have a IFC model loaded into model variable like so:


.. code-block:: python

    import ifcopenshell

    model = ifcopenshell.open('model.ifc')

This is only a small sample of common tasks. To view the full list of available
functions, check out the API Reference.

Get all wall types
------------------

.. code-block:: python

    for wall_type in model.by_type("IfcWallType"):
        print("The wall type element is", wall_type)
        print("The name of the wall type is", wall_type.Name)

Get all door occurrences of a type
----------------------------------

.. code-block:: python

    import ifcopenshell.util.element

    for door_type in model.by_type("IfcDoorType"):
        print("The door type is", door_type.Name)
        doors = ifcopenshell.util.element.get_types(door_type)
        print(f"There are {len(doors)} of this type")
        for door in doors:
            print("The door name is", door.Name)


Get the type of a wall
----------------------

.. code-block:: python

    import ifcopenshell.util.element

    wall = model.by_type("IfcWall")[0]
    wall_type = ifcopenshell.util.element.get_type(wall)
    print(f"The wall type of {wall.Name} is {wall_type.Name}")

Get the properties of a wall type
---------------------------------

.. code-block:: python

    import ifcopenshell.util.element

    wall = model.by_type("IfcWall")[0]
    wall_type = ifcopenshell.util.element.get_type(wall)

    # Get all properties and quantities as a dictionary
    # returns {"Pset_WallCommon": {"id": 123, "FireRating": "2HR", ...}}
    psets = ifcopenshell.util.element.get_psets(wall_type)
    print(psets)

    # Get all properties and quantities of the wall, including inherited type properties
    psets = ifcopenshell.util.element.get_psets(wall)
    print(psets)

    # Get only properties and not quantities
    print(ifcopenshell.util.element.get_psets(wall, psets_only=True))

    # Get only quantities and not properties
    print(ifcopenshell.util.element.get_psets(wall, qtos_only=True))


Find the spatial container of an element
----------------------------------------

.. code-block:: python

    import ifcopenshell.util.element

    wall = model.by_type("IfcWall")[0]
    # Walls are typically located on a storey, equipment might be located in spaces, etc
    container = ifcopenshell.util.element.get_container(wall)
    # The wall is located on Level 01
    print(f"The wall is located on {container.Name}")

Get all elements in a container
-------------------------------

.. code-block:: python

    import ifcopenshell.util.element

    for storey in model.by_type("IfcBuildingStorey"):
        elements = ifcopenshell.util.element.get_decomposition(storey)
        print(f"There are {len(elements)} located on storey {storey.Name}, they are:")
        for element in elements:
            print(element.Name)

Get the XYZ coordinates of a element
------------------------------------

.. code-block:: python

    import ifcopenshell.util.placement

    wall = model.by_type("IfcWall")[0]
    # This returns a 4x4 matrix, including the location and rotation. For example:
    # array([[ 1.00000000e+00,  0.00000000e+00,  0.00000000e+00, 2.00000000e+00],
    #        [ 0.00000000e+00,  1.00000000e+00,  0.00000000e+00, 3.00000000e+00],
    #        [ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00, 5.00000000e+00],
    #        [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00, 1.00000000e+00]])
    matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
    # The last column holds the XYZ values, such as:
    # array([ 2.00000000e+00,  3.00000000e+00,  5.00000000e+00])
    print(matrix[:,3][:3])

Get the geometry of an element
------------------------------

See :doc:`Geometry processing<geometry_processing>` for details.

Get the classification of an element
------------------------------------

.. code-block:: python

    import ifcopenshell.util.classification

    wall = model.by_type("IfcWall")[0]
    # Elements may have multiple classification references assigned
    references = ifcopenshell.util.classification.get_references(wall)
    for reference in references:
        # A reference code might be Pr_30_59_99_02
        print("The wall has a classification reference of", reference[1])
        # A system might be Uniclass 2015
        system = ifcopenshell.util.classification.get_classification(reference)
        print("This reference is part of the system", system.Name)

Convert to and from SI units and project units
----------------------------------------------

.. code-block:: python

    import ifcopenshell.util.unit

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
    si_meters = ifc_project_length * unit_scale
    ifc_project_length = si_meters / unit_scale

Get the distribution system of an element
-----------------------------------------

.. code-block:: python

    import ifcopenshell.util.classification

    pipe = model.by_type("IfcPipeSegment")[0]
    # Elements may be assigned to multiple systems simultaneously, such as electrical, hydraulic, etc
    systems = ifcopenshell.util.system.get_element_systems(pipe)
    for system in systems:
        # For example, it might be part of a Chilled Water system
        print("This pipe is part of the system", system.Name)

Copy an entity instance
-----------------------------------------

Copy an entity instance is possible in different ways, depending on the task. 

.. code-block:: python

    ifcopenshell.api.run("root.copy_class", ifc_file, product = entity_instance_to_copy)

This is high level and makes sensible assumptions about copying things like properties, quantities, openings, and other relationships.

.. code-block:: python

    ifcopenshell.util.element.copy(ifc_file, element)

This is for shallow copies.

.. code-block:: python

    ifcopenshell.util.element.copy_deep(ifc_file, element, exclude = None)

This is for deep graph copy.

Also note that ifcopenshell.file.add() can be used to copy instances from one file to the other.

.. code-block:: python

    f = ifcopenshell.open(...)
    g = ifcopenshell.file(schema=f.schema)
    g.add(f.by_type(...)[0])

Note that, in this case, it does copy over recursively, factor in length unit conversion if both files f and g have project length unit defined, but it does not make any other attempts at resulting in a valid file.

Create a simple model from scratch
----------------------------------

.. code-block:: python

    import ifcopenshell
    from ifcopenshell.api import run

    # Create a blank model
    model = ifcopenshell.file()

    # All projects must have one IFC Project element
    project = run("root.create_entity", model, ifc_class="IfcProject", name="My Project")

    # Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
    # Assigning without arguments defaults to metric units
    run("unit.assign_unit", model)

    # Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
    context = run("context.add_context", model, context_type="Model")
    # In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
    body = run(
        "context.add_context", model,
        context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
    )

    # Create a site, building, and storey. Many hierarchies are possible.
    site = run("root.create_entity", model, ifc_class="IfcSite", name="My Site")
    building = run("root.create_entity", model, ifc_class="IfcBuilding", name="Building A")
    storey = run("root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor")

    # Since the site is our top level location, assign it to the project
    # Then place our building on the site, and our storey in the building
    run("aggregate.assign_object", model, relating_object=project, product=site)
    run("aggregate.assign_object", model, relating_object=site, product=building)
    run("aggregate.assign_object", model, relating_object=building, product=storey)

    # Let's create a new wall
    wall = run("root.create_entity", model, ifc_class="IfcWall")
    # Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
    representation = run("geometry.add_wall_representation", model, context=body, length=5, height=3, thickness=0.2)
    # Assign our new body geometry back to our wall
    run("geometry.assign_representation", model, product=wall, representation=representation)

    # Place our wall in the ground floor
    run("spatial.assign_container", model, relating_structure=storey, product=wall)

    # Write out to a file
    model.write("/home/dion/model.ifc")

Here is the result:

.. image:: images/simple-model.png
