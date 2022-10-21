Geometry processing
===================

Geometry is specified in many ways in IFC. Some geometry is defined explicitly
with coordinates, vertices, and faces. Some geometry is defined implicitly with
equations, boolean operations, and parametric shapes.

Individual processing
---------------------

The simplest way to process any geometry in a standardised fashion is to use the
IfcOpenShell ``create_shape()`` function. This will provide a list of vertices,
edges, and faces, or alternatively an OpenCASCADE BRep.

Here is a simple example of processing a single wall into a list of vertices and
faces. In this example, a ``shape`` variable is returned, which holds geometry
related information in ``shape.geometry``:

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.geom

    ifc_file = ifcopenshell.open('model.ifc')
    element = ifc_file.by_type('IfcWall')[0]

    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, element)

    # The GUID of the element we processed
    print(shape.guid)

    # The ID of the element we processed
    print(shape.id)

    # The element we are processing
    print(ifc_file.by_guid(shape.guid))

    # A unique geometry ID, useful to check whether or not two geometries are
    # identical for caching and reuse. The naming scheme is:
    # IfcShapeRepresentation.id{-layerset-LayerSet.id}{-material-Material.id}{-openings-[Opening n.id ...]}{-world-coords}
    print(shape.geometry.id())

    # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
    faces = shape.geometry.faces

    # Indices of vertices per edge e.g. [e1v1, e1v2, e2v1, e2v2, ...]
    edges = shape.geometry.edges

    # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
    verts = shape.geometry.verts

    # Since the lists are flattened, you may prefer to group them like so depending on your geometry kernel
    grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
    grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]
    grouped_faces = [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]

    # A list of styles that are relevant to this shape
    styles = shape.geometry.materials

    for style in styles:
        # Each style is named after the entity class if a default
        # material is applied. Otherwise, it is named "surface-style-{SurfaceStyle.name}"
        # All non-alphanumeric characters are replaced with a "-".
        print(style.original_name)

        # A more human readable name
        print(style.name)

        # Each style may have diffuse colour RGB codes
        if style.has_diffuse:
            print(style.diffuse)

        # Each style may have transparency data
        if style.has_transparency:
            print(style.transparency)

    # Indices of material applied per triangle face e.g. [f1m, f2m, ...]
    material_ids = shape.geometry.material_ids

Alternatively, you may choose to retrieve an OpenCASCADE BRep:

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.geom

    ifc_file = ifcopenshell.open('model.ifc')
    element = ifc_file.by_type('IfcWall')[0]

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)

    try:
        shape = geom.create_shape(settings, element)
        geometry = shape.geometry # see #1124
        # These are methods of the TopoDS_Shape class from pythonOCC
        shape_gpXYZ = geometry.Location().Transformation().TranslationPart()
        # These are methods of the gpXYZ class from pythonOCC
        print(shape_gpXYZ.X(), shape_gpXYZ.Y(), shape_gpXYZ.Z())
    except:
        print("Shape creation failed")

When an entire element is passed into ``create_shape()``, the 3D representation
is processed by default with all openings applied. However, it is also possible
to only process a single shape representation with no openings, representation
item, or profile definition.

In these scenarios, a ``geometry`` is returned directly, equivalent to
``shape.geometry`` in the example above.

.. code-block:: python

    ifc_file = ifcopenshell.open('model.ifc')
    element = ifc_file.by_type('IfcWall')[0]

    # Process a shape representation
    body = ifcopenshell.util.representation.get_representation(element, "Model", "Body")

    # Note: geometry is returned directly, equivalent to shape.geometry when passing in an element
    geometry = geom.create_shape(settings, body)

    # Process a representation item
    geometry = geom.create_shape(settings, ifc_file.by_type("IfcExtrudedAreaSolid")[0])

    # Process a profile
    geometry = geom.create_shape(settings, ifc_file.by_type("IfcProfileDef")[0])

Geometry iterator
-----------------

IfcOpenShell provides a geometry iterator function to efficiently process
geometry in an IFC model. The iterator is always used in IfcConvert, and may
also be invoked in C++ or in Python. It offers the same features as the
``create_shape()`` function for `Individual processing`_.

The geometry iterator makes it easy to collect possible geometry in a model,
supports multicore processing, and implements caching and reuse to improve the
efficiency of geometry processing. For any bulk geometry processing, it is
always recommended to use the iterator.

By default, the geometry iterator processes all 3D geometry in a model from all
elements, and returns a list of X Y Z vertex ordinates in a flattened list, as
well as a flattened list of triangulated faces denoted by vertex indices.

There are a variety of configuration settings to get different output. For
example, you may filter elements from processing, extract 2D data, or return
non-triangulated OpenCASCADE BReps. For more information on the various
settings, see :doc:`Geometry Settings<../ifcopenshell/geometry_settings>`.

Here is a simple example in Python:

.. code-block:: python

    import multiprocessing
    import ifcopenshell
    import ifcopenshell.geom

    ifc_file = ifcopenshell.open('model.ifc')

    settings = ifcopenshell.geom.settings()
    iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
    if iterator.initialize():
        while True:
            shape = iterator.get()
            faces = shape.geometry.faces
            edges = shape.geometry.edges
            verts = shape.geometry.verts
            materials = shape.geometry.materials
            material_ids = shape.geometry.material_ids
            # ... write code to process geometry here ...
            if not iterator.next():
                break

.. note::

    The iterator can only be used to process whole elements, not individual
    shape representations, representation items, and profiles.

Manual parsing
--------------

IfcOpenShell lets you traverse any IFC entity graph. This means it is possible
for you to manually browse through the ``Representation`` attribute of IFC
elements, and parse the corresponding IFC shape representations yourself instead
of using generic geometric processing such as `Individual processing`_ and the
`Geometry iterator`_.

This approach requires an in-depth understanding of IFC geometry
representations, as well as its many caveats with units and transformations, but
can be very simple and extremely fast to extract specific types of geometry. For
example, if you know you are dealing with IfcCircle geometry, you can
specifically pinpoint the Radius parameter.

.. code-block:: python

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

    for circle in ifc_file.by_type("IfcCircle"):
        # In project length units
        print(circle.Radius)

        # In SI meters
        print(circle.Radius * unit_scale)

Given the advanced nature of manual processing, it is generally not recommended
except in specific tasks.
