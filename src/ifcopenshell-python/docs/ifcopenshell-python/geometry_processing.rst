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

.. warning::

   This section describes individual processing only. This is useful for
   learning how geometry processing works, but is not recommended for practical
   applications. See the `Geometry iterator`_ section below after reading this
   to see how to process geometry with multiple threads.


Here is a simple example of processing a single wall into a list of vertices and
faces. In this example, a ``shape`` variable is returned, which holds geometry
related information in ``shape.geometry``:

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.geom
    import ifcopenshell.util.shape

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
    print(shape.geometry.id)

    # A 4x4 matrix representing the location and rotation of the element, in the form:
    # [ [ x_x, y_x, z_x, x   ]
    #   [ x_y, y_y, z_y, y   ]
    #   [ x_z, y_z, z_z, z   ]
    #   [ 0.0, 0.0, 0.0, 1.0 ] ]
    # The position is given by the last column: (x, y, z)
    # The rotation is described by the first three columns, by explicitly specifying the local X, Y, Z axes.
    # The first column is a normalised vector of the local X axis: (x_x, x_y, x_z)
    # The second column is a normalised vector of the local Y axis: (y_x, y_y, y_z)
    # The third column is a normalised vector of the local Z axis: (z_x, z_y, z_z)
    # The axes follow a right-handed coordinate system.
    # Objects are never scaled, so the scale factor of the matrix is always 1.
    matrix = shape.transformation.matrix

    # For convenience, you might want the matrix as a nested numpy array, so you can do matrix math.
    matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

    # You can also extract the XYZ location of the matrix.
    location = matrix[:,3][0:3]

    # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
    # These vertices are local relative to the shape's transformation matrix.
    verts = shape.geometry.verts

    # Indices of vertices per edge e.g. [e1v1, e1v2, e2v1, e2v2, ...]
    # If the geometry is mesh-like, edges contain the original edges.
    # These may be quads or ngons and not necessarily triangles.
    edges = shape.geometry.edges

    # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
    # Note that faces are always triangles.
    faces = shape.geometry.faces

    # Since the lists are flattened, you may prefer to group them like so depending on your geometry kernel
    # A nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]
    grouped_verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
    # A nested numpy array e.g. [[e1v1, e1v2], [e2v1, e2v2], ...]
    grouped_edges = ifcopenshell.util.shape.get_edges(shape.geometry)
    # A nested numpy array e.g. [[f1v1, f1v2, f1v3], [f2v1, f2v2, f2v3], ...]
    grouped_faces = ifcopenshell.util.shape.get_faces(shape.geometry)

    # A list of styles that are relevant to this shape
    styles = shape.geometry.materials

    for style in styles:
        # Each style is named after the entity class if a default
        # material is applied. Otherwise, it is named "surface-style-{SurfaceStyle.name}"
        # All non-alphanumeric characters are replaced with a "-".
        print(style.original_name())

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

    # IDs representation item per triangle face e.g. [f1i, f2i, ...]
    item_ids = shape.geometry.item_ids

Alternatively, you may choose to retrieve an OpenCASCADE BRep:

.. code-block:: python

    import ifcopenshell
    import ifcopenshell.geom

    ifc_file = ifcopenshell.open('model.ifc')
    element = ifc_file.by_type('IfcWall')[0]

    settings = ifcopenshell.geom.settings()
    settings.set("use-python-opencascade", True)

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


When an element contains multiple shape representations with the same
identifier or when you want more explicit control over which representation is
processed (e.g ``Body`` or ``Tessellation``), you can use the third parameter of
``create_shape()`` to nominate a specific shape representation to be processed
in the context of a product.  The element in your ifc file might look like
this.

.. code-block:: ifc

    #1=IFCSHAPEREPRESENTATION(#4,'Body','BRep',(#1617476));
    #2=IFCSHAPEREPRESENTATION(#4,'Body','BRep',(#1617583));
    #3=IFCSHAPEREPRESENTATION(#4,'Body','BRep',(#1617630));
    #5=IFCPRODUCTDEFINITIONSHAPE($,$,(#1,#2,#3));
    #6=IFCWINDOW('0Rrp2csNr07QrVCrEBJezu',#9,'test','test',$,#7,#5,'test',$,$,$,$,$);

In order to get the geometry data (e.g. vertices) for this ``IfcWindow``, we can use the Python code below:

.. code-block:: python

    representations = window.Representation.Representations
    for representation in representations:
        # ... code that filters which representation you want ...
        shape = ifcopenshell.geom.create_shape(settings, window, representation)

.. seealso::

    You may find the ``ifcopenshell.util.representation`` module useful to
    filter out specific representations.


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
            element = ifc_file.by_id(shape.id)
            matrix = shape.transformation.matrix
            faces = shape.geometry.faces
            edges = shape.geometry.edges
            verts = shape.geometry.verts
            materials = shape.geometry.materials
            material_ids = shape.geometry.material_ids
            # ... write code to process geometry here ...
            if not iterator.next():
                break


There are a variety of configuration settings to get different output. For
example, you may filter elements from processing, extract 2D data, or return
non-triangulated OpenCASCADE BReps. For more information on the various
settings, see :doc:`Geometry Settings<../ifcopenshell/geometry_settings>`.

One of the more common settings used is the ``include`` setting, which
specifies only to process certain geometry. For example, this iterator will
only process wall elements.

.. code-block:: python

    walls = ifc.by_type('IfcWall')
    iterator = ifcopenshell.geom.iterator(settings, ifc, multiprocessing.cpu_count(), include=walls)

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

Geometry serialisation
----------------------

Geometry may be serialised into many different formats using
:doc:`IfcConvert<../ifcconvert>`. Alternatively, you may also access the
serialiser with Python to customise the conversion, such as by writing a script
that modifies the IFC on the fly before converting it, or writing complex
include and exclude filters.

Here is a typical example to serialising to glTF / glb. Example settings to
serialise to other formats are shown commented out. Different serialisations
may require different settings.

In addition to geometry settings, serialisation has its own set of
:doc:`../ifcopenshell/serialiser_settings`.

.. code-block:: python

   import multiprocessing
   
   import ifcopenshell
   import ifcopenshell.geom
   
   ifc_file = ifcopenshell.open("model.ifc")
   
   settings = ifcopenshell.geom.settings()
   
   # Settings for glTF / glb
   settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
   # Note that applying default materials is required in glTF serialisation.
   settings.set("apply-default-materials", True)
   
   # Settings for obj
   # settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
   # settings.set("apply-default-materials", True)
   # settings.set("use-world-coords", True)
   
   serialiser_settings = ifcopenshell.geom.serializer_settings()
   # Setting element GUIDs is optional, but useful to uniquely identify objects in non-semantic formats.
   serialiser_settings.set("use-element-guids", True)
   
   # Serialise to glTF / glb
   serialiser = ifcopenshell.geom.serializers.gltf("output.glb", settings, serialiser_settings)
   
   # Serialise to obj
   # serialiser = ifcopenshell.geom.serializers.obj('output.obj', 'output.mtl', settings, serialiser_settings)
   
   serialiser.setFile(ifc_file)
   serialiser.setUnitNameAndMagnitude("METER", 1.0)
   serialiser.writeHeader()
   
   iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
   if iterator.initialize():
       while True:
           serialiser.write(iterator.get())
           if not iterator.next():
               break
   serialiser.finalize()
