Geometry processing
===================

Geometry is specified in many ways in IFC. Some geometry is defined explicitly
with coordinates, vertices, and faces. Some geometry is defined implicitly with
equations, boolean operations, and parametric shapes.

IfcOpenShell turns all of these into explicit geometry, in **Python**, **C++**,
and **JavaScript / TypeScript**. The geometry engine is the same C++ core in all
three languages, with the same :doc:`geometry settings <geometry_settings>`, so
the explanations below apply to every language. Pick a language on any snippet,
and all snippets switch with it.

The snippets continue from :doc:`hello_world`, with a ``model`` that is already
open.

Before you start
----------------

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        Geometry processing lives in the ``ifcopenshell.geom`` module.

        .. code-block:: python

            import ifcopenshell
            import ifcopenshell.geom

    .. tab-item:: C++
        :sync: cpp

        Geometry processing lives in the ``IfcGeom`` library, and needs a
        geometry kernel. The examples link against
        ``IfcOpenShell::IfcGeom``, ``IfcOpenShell::geometry_kernel_opencascade``
        and, for serialisation, ``IfcOpenShell::geometry_serializer``. Every C++
        snippet on this page is cut from a standalone program in
        ``docs/ifcopenshell-cpp/geometry_processing``, which is compiled and run
        against ``AC20-FZK-Haus.ifc``, see
        :ref:`building-and-running-the-examples`.

    .. tab-item:: JavaScript
        :sync: js

        Geometry processing needs the model's schema, the corresponding
        mapping, and a geometry kernel, each of which is a plugin. The mapping
        plugin interprets IFC representations, and the kernel performs the
        geometry operations.

        .. code-block:: javascript

            import * as geom from 'ifcopenshell/geom';

            await runtime.loadPlugin('mapping', 'ifc4');
            await runtime.loadPlugin('kernel', 'manifold');

        The native build also provides kernels including ``opencascade``,
        ``cgal``, and ``cgalsimple``; load the selected kernel and pass its
        identifier as ``geometryLibrary`` or the last ``createShape()``
        argument. Every JavaScript snippet on this page is cut from a program in
        ``docs/ifcopenshell-js/geometry_processing``, which the test suite runs.

Individual processing
---------------------

The simplest way to process any geometry in a standardised fashion is to ask
IfcOpenShell for the shape of a single product, with ``create_shape()``. It
provides a list of vertices, edges, and faces, or alternatively the
untriangulated BRep of the geometry kernel.

.. warning::

   This section describes individual processing only. This is useful for
   learning how geometry processing works, but is not recommended for practical
   applications. See the `Geometry iterator`_ section below after reading this
   to see how to process geometry with multiple threads.

Here is an example of processing a single wall into a list of vertices and
faces, along with its placement and styles. Vertices are flattened X Y Z
coordinates, and faces are flattened triangle vertex indices. The vertices are
local to the shape's transformation matrix, unless the ``use-world-coords``
setting is enabled. Geometry is in metres by default, see
:doc:`geometry_settings` for settings such as ``convert-back-units``.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        A ``shape`` variable is returned, which holds geometry related
        information in ``shape.geometry``:

        .. code-block:: python

            import ifcopenshell
            import ifcopenshell.geom
            import ifcopenshell.util.shape

            ifc_file = ifcopenshell.open('model.ifc')
            element = ifc_file.by_type('IfcWall')[0]

            # Create a shape using a hybrid of the cgal-simple geometry kernel and opencascade as a fallback
            # Choosing a geometry kernel has a big impact on speed and capability.
            # It is recommended to use the "hybrid-cgal-simple-opencascade" kernel.
            settings = ifcopenshell.geom.settings()
            shape = ifcopenshell.geom.create_shape(
                settings, element, geometry_library="hybrid-cgal-simple-opencascade")

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

    .. tab-item:: C++
        :sync: cpp

        In C++, a converter is asked for the BRep of the product, which is then
        triangulated. Here is a complete example of processing a single wall,
        and of everything that comes with it:

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/01_individual_processing.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        ``createShape()`` converts one product into a geometry element:

        .. literalinclude:: ../ifcopenshell-js/geometry_processing/01_individual.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

        Destroy the geometry and the triangulation before the shape that
        owns them.

Untriangulated geometry
~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you may use the untriangulated BRep of the geometry kernel, such
as an OpenCASCADE ``TopoDS_Shape``.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        Enable ``use-python-opencascade`` to receive a pythonOCC shape:

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

    .. tab-item:: C++
        :sync: cpp

        Here the type of the data depends on the geometry kernel in use.

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/03_native_geometry.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        The shape is opaque so that kernels other than OpenCASCADE can be used,
        but when you know the shape was made by the OpenCASCADE kernel it can be
        cast back to the ``TopoDS_Shape`` it wraps, and used with OpenCASCADE
        directly:

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/03_native_geometry.cpp
            :language: cpp
            :start-after: // tag::opencascade
            :end-before: // end::opencascade
            :dedent: 4

        A shape can also be taken apart, in which case each of the sub-shapes
        can be asked for its own properties:

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/03_native_geometry.cpp
            :language: cpp
            :start-after: // tag::sub-shapes
            :end-before: // end::sub-shapes
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The JavaScript guides only cover triangulated output so far.

Processing a particular representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an entire element is processed, the 3D representation is processed by
default, with all openings applied. However, it is also possible to process a
single shape representation, in the context of its product. Openings, materials,
and the layer set of the product are then not applied.

This is useful when an element contains multiple shape representations with
the same identifier, or when you want more explicit control over which
representation is processed (e.g ``Body`` or ``Tessellation``). The element in
your IFC file might look like this:

.. code-block:: text

    #1=IFCSHAPEREPRESENTATION(#4,'Body','BRep',(#1617476));
    #2=IFCSHAPEREPRESENTATION(#4,'Body','BRep',(#1617583));
    #3=IFCSHAPEREPRESENTATION(#4,'Body','BRep',(#1617630));
    #5=IFCPRODUCTDEFINITIONSHAPE($,$,(#1,#2,#3));
    #6=IFCWINDOW('0Rrp2csNr07QrVCrEBJezu',#9,'test','test',$,#7,#5,'test',$,$,$,$,$);

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        The third parameter of ``create_shape()`` nominates the shape
        representation to process:

        .. code-block:: python

            representations = window.Representation.Representations
            for representation in representations:
                # ... code that filters which representation you want ...
                shape = ifcopenshell.geom.create_shape(settings, window, representation)

        In Python, a shape representation, a representation item, or a profile
        can also be processed on its own, without a product. In these
        scenarios, a ``geometry`` is returned directly, equivalent to
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

        .. seealso::

            You may find the ``ifcopenshell.util.representation`` module useful
            to filter out specific representations.

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/02_representation.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The optional third argument to ``createShape()`` selects the
        representation:

        .. literalinclude:: ../ifcopenshell-js/geometry_processing/03_representation.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

Geometry iterator
-----------------

IfcOpenShell provides a geometry iterator to efficiently process geometry in an
IFC model. The iterator is always used in IfcConvert, and may also be invoked
from Python, C++, or JavaScript. It offers the same features as
`Individual processing`_.

The geometry iterator makes it easy to collect possible geometry in a model,
supports multicore processing, and implements caching and reuse to improve the
efficiency of geometry processing. For any bulk geometry processing, it is
always recommended to use the iterator.

By default, the geometry iterator processes all 3D geometry in a model from all
elements, and returns a list of X Y Z vertex ordinates in a flattened list, as
well as a flattened list of triangulated faces denoted by vertex indices.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            import multiprocessing
            import ifcopenshell
            import ifcopenshell.geom

            ifc_file = ifcopenshell.open('model.ifc')

            settings = ifcopenshell.geom.settings()
            iterator = ifcopenshell.geom.iterator(
                settings, ifc_file, multiprocessing.cpu_count(), geometry_library="hybrid-cgal-simple-opencascade")
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

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/04_geometry_iterator.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        .. literalinclude:: ../ifcopenshell-js/geometry_processing/02_iterator.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

        ``initialize()`` positions the iterator at its first element. Call
        ``get()`` once at each position, then ``next()`` to advance. Keep the
        model and settings alive until iteration finishes. Processing runs
        synchronously; a browser application can run it in a worker to keep its
        interface responsive. Thread counts depend on the WASM build's
        threading support.

There are a variety of configuration settings to get different output. For
example, you may filter elements from processing, extract 2D data, or return
non-triangulated OpenCASCADE BReps. For more information on the various
settings, see :doc:`Geometry Settings<geometry_settings>`.

One of the more common settings used is a filter, which specifies only to
process certain geometry.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        The ``include`` argument takes the elements to process, for example only
        the walls:

        .. code-block:: python

            walls = ifc.by_type('IfcWall')
            iterator = ifcopenshell.geom.iterator(
                settings, ifc, multiprocessing.cpu_count(),
                include=walls, geometry_library="hybrid-cgal-simple-opencascade")

    .. tab-item:: C++
        :sync: cpp

        This iterator will only process the windows of the model:

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/05_iterator_filter.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The ``include`` and ``exclude`` options take STEP IDs or IFC type names,
        and are mutually exclusive. The iterator above already only processes
        walls and slabs:

        .. code-block:: javascript

            const iterator = new geom.Iterator(settings, model, {
              geometryLibrary: 'manifold',
              include: ['IfcWall', 'IfcSlab'],
            });

.. note::

    The iterator can only be used to process whole elements, not individual
    shape representations, representation items, and profiles.

Manual parsing
--------------

IfcOpenShell lets you traverse any IFC entity graph. This means it is possible
for you to manually browse through the ``Representation`` attribute of IFC
elements, and parse the corresponding IFC representation items yourself instead
of using generic geometric processing such as `Individual processing`_ and the
`Geometry iterator`_.

This approach requires an in-depth understanding of IFC geometry
representations, as well as its many caveats with units and transformations, but
can be very simple and extremely fast to extract specific types of geometry. For
example, if you know you are dealing with extrusions, you can specifically
pinpoint the depth of the extrusion, or the radius of a circle.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        .. code-block:: python

            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

            for circle in ifc_file.by_type("IfcCircle"):
                # In project length units
                print(circle.Radius)

                # In SI meters
                print(circle.Radius * unit_scale)

    .. tab-item:: C++
        :sync: cpp

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/06_manual_parsing.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

    .. tab-item:: JavaScript
        :sync: js

        The depth is in project length units.

        .. literalinclude:: ../ifcopenshell-js/geometry_processing/05_manual.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

Given the advanced nature of manual processing, it is generally not recommended
except in specific tasks.

Geometry serialisation
----------------------

Geometry may be serialised into many different formats using
:doc:`IfcConvert<../ifcconvert>`. Alternatively, you may also access the
serialiser directly to customise the conversion, such as by writing a program
that modifies the IFC on the fly before converting it, or implementing complex
include and exclude filters. Different serialisations may require different
settings, and the same settings object also exposes the
:doc:`serialisation options <serialiser_settings>`.

.. tab-set::
    :sync-group: lang

    .. tab-item:: Python
        :sync: python

        Here is a typical example of serialising to glTF / glb. Example
        settings to serialise to other formats are shown commented out.

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

           # Setting element GUIDs is optional, but useful to uniquely identify objects in non-semantic formats.
           settings.set("use-element-guids", True)

           # Serialise to glTF / glb
           serialiser = ifcopenshell.geom.serializers.gltf("output.glb", settings)

           # Serialise to obj
           # serialiser = ifcopenshell.geom.serializers.obj('output.obj', 'output.mtl', settings)

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

    .. tab-item:: C++
        :sync: cpp

        Here is a typical example of serialising to glTF / glb, with the
        settings for obj shown as a comment.

        .. literalinclude:: ../ifcopenshell-cpp/geometry_processing/07_geometry_serialisation.cpp
            :language: cpp
            :start-after: // tag::example
            :end-before: // end::example
            :dedent: 4

        The serialisers are plugins which are discovered next to the
        IfcOpenShell libraries, so a serialiser for a format is only available
        when it was built and installed.

    .. tab-item:: JavaScript
        :sync: js

        The ``exportToBuffer()`` convenience function exports OBJ, SVG, or TTL
        text. Load the format's serializer plugin, such as
        ``runtime.loadPlugin('geometry_serializer', 'obj')``, and import
        ``exportToBuffer`` from ``ifcopenshell/serializers`` before exporting.
        OBJ returns both the geometry text and the material text:

        .. literalinclude:: ../ifcopenshell-js/geometry_processing/04_serialise.mjs
            :language: javascript
            :start-after: // tag::example
            :end-before: // end::example

        In the browser, create downloadable blobs from the returned strings. A
        ``null`` result means the geometry iterator could not initialize. The
        generated native API also exposes serializer factories for other
        formats present in the plugin manifest.
