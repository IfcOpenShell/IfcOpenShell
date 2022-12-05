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
    # Convert to SI unit:
    si_meters = ifc_project_length * unit_scale
    # Convert from SI unit:
    ifc_project_length = si_meters / unit_scale

Example
.. code-block:: python
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
    wall_height_in_project_units = wall.Representation.Representations[1].Items[0].Depth  #might be a different expression, for wall_height
    wall_height_in_si_units = wall_height_in_project_units * unit_scale
    wall.Representation.Representations[1].Items[0].Depth = wall_height_in_si_units


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

    wall_copy_class = ifcopenshell.api.run("root.copy_class", model, product = wall)

This is high level and makes sensible assumptions about copying things like properties and quantities. It does not copy the element's representation, however.

.. code-block:: python

    wall_shallow_copy = ifcopenshell.util.element.copy(model, wall)

This is for shallow copies.  That is, associated things like the element's type, materials, and properties are not copied.  The new element, however, has the same representation and placement as the original.

.. code-block:: python

    wall_deepgraph_copy = ifcopenshell.util.element.copy_deep(model, wall, exclude = None)

This is for deep graph copy.  Like shallow copy, it does not copy over things like associated type/properties/quantities, but it does copy the representation and placement.  

Also note that ifcopenshell.file.add() can be used to copy instances from one file to the other.

.. code-block:: python

    f = ifcopenshell.open(...)
    g = ifcopenshell.file(schema=f.schema)
    g.add(f.by_type(...)[0])

Note that, in this case, it does copy over recursively, however, it does not make any other attempts at resulting in a valid file. Factor in things like length unit conversion if both files (f and g) have project length unit defined. 

Create a simple model from scratch
----------------------------------

.. code-block:: python

    import ifcopenshell
    from ifcopenshell.api import run

    # Create a blank model
    model = ifcopenshell.file()

    # All projects must have one IFC Project element
    # Example: project = #1=IfcProject('1y93FYOhjCEOq6QMsyib1g',$,'My Project',$,$,$,$,$,$)
    project = run(
        "root.create_entity", 
        model, 
        ifc_class="IfcProject", 
        name="My Project"
        )

    # Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
    # Assigning without arguments defaults to metric units
    # Example: units = #5=IfcUnitAssignment((#3,#4,#2))
                            #3=IfcSIUnit(*,.AREAUNIT.,$,.SQUARE_METRE.)
                            #4=IfcSIUnit(*,.VOLUMEUNIT.,$,.CUBIC_METRE.)
                            #2=IfcSIUnit(*,.LENGTHUNIT.,.MILLI.,.METRE.)

    units = run(
        "unit.assign_unit", 
        model
        )

    # Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
    # Example: context = #10=IfcGeometricRepresentationContext($,'Model',3,1.E-05,#9,$)
                    # context.WorldCoordinateSystem = #9=IfcAxis2Placement3D(#6,#7,#8)
                        # context.WorldCoordinateSystem.Location = #6=IfcCartesianPoint((0.,0.,0.))
                        # context.WorldCoordinateSystem.Axis = #7=IfcDirection((0.,0.,1.))
                        # context.WorldCoordinateSystem.RefDirection = #8=IfcDirection((1.,0.,0.))
    context = run(
        "context.add_context", 
        model, 
        context_type="Model"
        )
    # In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
    # Example: body = #11=IfcGeometricRepresentationSubContext('Body','Model',*,*,*,*,#10,$,.MODEL_VIEW.,$)
                    # body.ParentContext = #10=IfcGeometricRepresentationContext($,'Model',3,1.E-05,#9,$)
                        # body.ParentContext.WorldCoordinateSystem = #9=IfcAxis2Placement3D(#6,#7,#8)
    body = run(
        "context.add_context", 
        model,
        context_type="Model", 
        context_identifier="Body", 
        target_view="MODEL_VIEW", 
        parent=context
    )

    # Create a site, building, and storey. Many hierarchies are possible.
    # Example: site = #12=IfcSite('0D3VqQNi52LxthFbX0gAxV',$,'My Site',$,$,$,$,$,$,$,$,$,$,$)
    site = run(
        "root.create_entity", 
        model, 
        ifc_class="IfcSite", 
        name="My Site"
        )
    # Example: building = #13=IfcBuilding('09TEuRxrH1KhoE0ddAezhW',$,'Building A',$,$,$,$,$,$,$,$,$)
    building = run(
        "root.create_entity", 
        model, 
        ifc_class="IfcBuilding", 
        name="Building A"
        )
    # Example: storey = #14=IfcBuildingStorey('0JnPw2QG12IvngAC55M4WI',$,'Ground Floor',$,$,$,$,$,$,$)
    storey = run(
        "root.create_entity", 
        model, 
        ifc_class="IfcBuildingStorey", 
        name="Ground Floor")

    # Since the site is our top level location, assign it to the project
    # Then place our building on the site, and our storey in the building
    # Example: 
    # #15=IfcRelAggregates('11NpDvnL15wvAG1UPJml2p',$,$,$,#1,(#12))
        # project.IsDecomposedBy[0].RelatingObject: #1=IfcProject('1rUCNNpIfD4AC9sehqLZbm',$,'My Project',$,$,$,$,(#10),#5)
        # project.IsDecomposedBy[0].RelatedObjects[0]: #12=IfcSite('0D3VqQNi52LxthFbX0gAxV',$,'My Site',$,$,$,$,$,$,$,$,$,$,$)
        
        # or #

        # site.Decomposes[0].RelatingObject = #1=IfcProject('1rUCNNpIfD4AC9sehqLZbm',$,'My Project',$,$,$,$,(#10),#5)
        # site.Decomposes[0].RelatedObjects[0] = #12=IfcSite('0D3VqQNi52LxthFbX0gAxV',$,'My Site',$,$,$,$,$,$,$,$,$,$,$)

    run(
        "aggregate.assign_object", 
        model, 
        relating_object=project, 
        product=site)
    # Example: 
    # #16=IfcRelAggregates('04_iLngFP89AC0bSHTNAvr',$,$,$,#12,(#13))
        # site.IsDecomposedBy[0].RelatingObject = #12=IfcSite('0D3VqQNi52LxthFbX0gAxV',$,'My Site',$,$,$,$,$,$,$,$,$,$,$)
        # site.IsDecomposedBy[0].RelatedObjects[0] = #13=IfcBuilding('09TEuRxrH1KhoE0ddAezhW',$,'Building A',$,$,$,$,$,$,$,$,$)

        # or #

        # building.Decomposes[0].RelatingObject = #12=IfcSite('0D3VqQNi52LxthFbX0gAxV',$,'My Site',$,$,$,$,$,$,$,$,$,$,$)
        # building.Decomposes[0].RelatedObjects[0] = #13=IfcBuilding('09TEuRxrH1KhoE0ddAezhW',$,'Building A',$,$,$,$,$,$,$,$,$)

    run(
        "aggregate.assign_object", 
        model, 
        relating_object=site, 
        product=building)
    # Example: 
    # #17=IfcRelAggregates('1hetrTtrP029HJJC9NUh0j',$,$,$,#13,(#14))
        # building.IsDecomposedBy[0].RelatingObject = #13=IfcBuilding('09TEuRxrH1KhoE0ddAezhW',$,'Building A',$,$,$,$,$,$,$,$,$)
        # building.IsDecomposedBy[0].RelatedObjects = (#14=IfcBuildingStore...$,$,$,$,$),)

        # or #

        # storey.Decomposes[0].RelatingObject = #13=IfcBuilding('09TEuRxrH1KhoE0ddAezhW',$,'Building A',$,$,$,$,$,$,$,$,$)
        # storey.Decomposes[0].RelatedObjects[0] = #14=IfcBuildingStorey('0JnPw2QG12IvngAC55M4WI',$,'Ground Floor',$,$,$,$,$,$,$)

    run(
        "aggregate.assign_object", 
        model, 
        relating_object=building, 
        product=storey
        )

    # Let's create a new wall
    # #18=IfcWall('2zBASxKWH7QAE$TyvnS1LF',$,$,$,$,$,$,$,.NOTDEFINED.)
    wall = run(
        "root.create_entity", 
        model, 
        ifc_class="IfcWall"
        )
    # Add a new wall-like body geometry, 5 meters long, 3 meters high, and 200mm thick
    # Example: 
    # #28=IfcShapeRepresentation(#11,'Body','SweptSolid',(#27))
        # representation.ContextOfItems = #11=IfcGeometricRepresentationSubContext('Body','Model',*,*,*,*,#10,$,.MODEL_VIEW.,$)
            # representation.ContextOfItems.ParentContext = #10=IfcGeometricRepresentationContext($,'Model',3,1.E-05,#9,$)
        # representation.Items[0] = #27=IfcExtrudedAreaSolid(#22,#26,#21,3000.)
            # representation.Items[0].SweptArea = #22=IfcArbitraryClosedProfileDef(.AREA.,$,#20)
            # representation.Items[0].Position = #26=IfcAxis2Placement3D(#23,#24,#25)
            # representation.Items[0].ExtrudedDirection = #21=IfcDirection((0.,0.,1.))
            # representation.Items[0].Depth = 3000.0
    representation = run(
        "geometry.add_wall_representation", 
        model, 
        context=body, 
        length=5, 
        height=3, 
        thickness=0.2
        )
    # Assign our new body geometry back to our wall
    # Example: 
    # #18=IfcWall('2zBASxKWH7QAE$TyvnS1LF',$,$,$,$,$,#29,$,.NOTDEFINED.)
        # wall.Representation = #29=IfcProductDefinitionShape($,$,(#28))
            # wall.Representation.Representations[0] = #28=IfcShapeRepresentation(#11,'Body','SweptSolid',(#27))
                # wall.Representation.Representations[0].ContextOfItems = #11=IfcGeometricRepresentationSubContext('Body','Model',*,*,*,*,#10,$,.MODEL_VIEW.,$)
                    # wall.Representation.Representations[0].ContextOfItems.ParentContext = #10=IfcGeometricRepresentationContext($,'Model',3,1.E-05,#9,$)
                # wall.Representation.Representations[0].Items[0] = #27=IfcExtrudedAreaSolid(#22,#26,#21,3000.)
                    # representation.Items[0] = #27=IfcExtrudedAreaSolid(#22,#26,#21,3000.)
                        # wall.Representation.Representations[0].Items[0].SweptArea = #22=IfcArbitraryClosedProfileDef(.AREA.,$,#20)
                        # wall.Representation.Representations[0].Items[0].Position = #26=IfcAxis2Placement3D(#23,#24,#25)
                        # wall.Representation.Representations[0].Items[0].ExtrudedDirection = #21=IfcDirection((0.,0.,1.))
    run(
        "geometry.assign_representation", 
        model, 
        product=wall, 
        representation=representation
        )



    # Place our wall in the ground floor
    # Example: 
    # #30=IfcRelContainedInSpatialStructure('0gKybMl8r7h8cYSUXARx0q',$,$,$,(#18),#14)
        # wall.ContainedInStructure[0].RelatedElements[0] = #18=IfcWall('2zBASxKWH7QAE$TyvnS1LF',$,$,$,$,$,#29,$,.NOTDEFINED.)
        # wall.ContainedInStructure[0].RelatingStructure = #14=IfcBuildingStorey('0JnPw2QG12IvngAC55M4WI',$,'Ground Floor',$,$,$,$,$,$,$)

    run(
        "spatial.assign_container", 
        model, 
        relating_structure=storey, 
        product=wall
        )

    # Write out to a file
    model.write("/home/dion/model.ifc")

Here is the result:

.. image:: images/simple-model.png
