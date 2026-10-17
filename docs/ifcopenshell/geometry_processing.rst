Geometry processing
===================

Geometry is specified in many ways in IFC. Some geometry is defined explicitly
with coordinates, vertices, and faces. Some geometry is defined implicitly with
equations, boolean operations, and parametric shapes.

IfcOpenShell turns all of these into explicit geometry, in **Python**, **C++**,
and **JavaScript / TypeScript**. The geometry engine is the same C++ core in all
three languages, with the same :doc:`geometry settings <geometry_settings>`, so
the explanations below apply to every language.

The code blocks continue from :doc:`hello_world`, with a ``model`` that is
already open. They are cut from the programs in
``docs/ifcopenshell/examples/geometry_processing``, which the test suite runs
against ``AC20-FZK-Haus.ifc``.

Before you start
----------------

Geometry processing needs a geometry kernel, in addition to the parser.

.. snippet:: geometry_processing/individual_processing
    :tag: setup
    :caption-python: Geometry processing lives in the ``ifcopenshell.geom``
        module.
    :caption-cpp: The examples link against ``IfcOpenShell::IfcGeom``,
        ``IfcOpenShell::geometry_kernel_opencascade`` and, for serialisation,
        ``IfcOpenShell::geometry_serializer``.
    :caption-js: The native build also provides the ``opencascade``,
        ``cgal``, and ``cgalsimple`` kernels. Load the kernel you select, and
        pass its name as ``geometryLibrary``.

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

.. snippet:: geometry_processing/individual_processing
    :caption-cpp: In C++, a converter is asked for the BRep of the product,
        which is then triangulated.
    :caption-js: Destroy the geometry and the triangulation before the shape
        that owns them.

Untriangulated geometry
~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you may choose to retrieve an OpenCASCADE BRep:

.. snippet:: geometry_processing/native_geometry
    :na: js
    :caption-python: ``use-python-opencascade`` returns a pythonOCC shape, so
        pythonOCC has to be installed.
    :caption-js: The JavaScript bindings only return triangulated geometry.

The shape is opaque so that kernels other than OpenCASCADE can be used, but
when you know the shape was made by the OpenCASCADE kernel, it can be used with
OpenCASCADE directly:

.. snippet:: geometry_processing/native_geometry
    :tag: opencascade
    :na: python, js
    :title: Using the OpenCASCADE shape directly

A shape can also be taken apart, in which case each of the sub-shapes can be
asked for its own properties:

.. snippet:: geometry_processing/native_geometry
    :tag: sub-shapes
    :na: python, js
    :title: Taking a shape apart

Processing a particular representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When an entire element is passed into ``create_shape()``, the 3D representation
is processed by default with all openings applied. However, it is also possible
to only process a single shape representation with no openings, representation
item, or profile definition.

In these scenarios, a ``geometry`` is returned directly, equivalent to
``shape.geometry`` in the example above.

.. snippet:: geometry_processing/representation
    :tag: standalone
    :na: cpp, js
    :title: Processing a representation without a product

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

.. snippet:: geometry_processing/representation

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

.. snippet:: geometry_processing/iterator
    :caption-js: Call ``get()`` once at each position, then ``next()`` to
        advance, and keep the model and settings alive until iteration
        finishes. Processing is synchronous, so a browser application can run
        it in a worker.

There are a variety of configuration settings to get different output. For
example, you may filter elements from processing, extract 2D data, or return
non-triangulated OpenCASCADE BReps. For more information on the various
settings, see :doc:`Geometry Settings<geometry_settings>`.

One of the more common settings used is the ``include`` setting, which
specifies only to process certain geometry. For example, this iterator will
only process wall elements.

.. snippet:: geometry_processing/iterator_filter
    :js: geometry_processing/iterator#filter
    :caption-python: ``include`` takes the elements to process.
    :caption-cpp: This iterator only processes the windows of the model.
    :caption-js: ``include`` and ``exclude`` take STEP IDs or IFC type names,
        and are mutually exclusive.

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

.. snippet:: geometry_processing/manual_parsing
    :caption-js: The depth is in project length units.

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

The same settings object also exposes the
:doc:`serialisation options <serialiser_settings>`.

.. snippet:: geometry_processing/serialisation
    :caption-python: Settings for other formats are shown commented out.
    :caption-cpp: The serialisers are plugins which are discovered next to the
        IfcOpenShell libraries, so a serialiser is only available when it was
        built and installed.
    :caption-js: ``exportToBuffer()`` exports OBJ, SVG, or TTL text. Load the
        format's serialiser plugin first. OBJ returns both the geometry and the
        material text, and ``null`` means the iterator could not initialise.
