.. This file was generated with the assistance of an AI coding tool.

Geometry processing
===================

Geometry is specified in many ways in IFC. Some geometry is defined explicitly
with coordinates, vertices, and faces. Some geometry is defined implicitly with
equations, boolean operations, and parametric shapes.

Individual processing
---------------------

The simplest way to process any geometry in a standardised fashion is to ask a
converter for the BRep of a product, and to triangulate that. It provides a list
of vertices, edges, and faces, or alternatively the untriangulated BRep of the
geometry kernel.

.. warning::

   This section describes individual processing only. This is useful for
   learning how geometry processing works, but is not recommended for practical
   applications. See the `Geometry iterator`_ section below after reading this
   to see how to process geometry with multiple threads.

Here is a complete example of processing a single wall, and of everything that
comes with it:

.. literalinclude:: geometry_processing/01_individual_processing.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

Untriangulated geometry
~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you may use the untriangulated geometry of the geometry kernel. Here the type of the data depends on the geometry kernel in use.

.. literalinclude:: geometry_processing/03_native_geometry.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

The shape is opaque so that kernels other than OpenCASCADE can be used, but when
you know the shape was made by the OpenCASCADE kernel it can be cast back to the
``TopoDS_Shape`` it wraps, and used with OpenCASCADE directly:

.. literalinclude:: geometry_processing/03_native_geometry.cpp
    :language: cpp
    :start-after: // tag::opencascade
    :end-before: // end::opencascade

A shape can also be taken apart, in which case each of the sub-shapes can be
asked for its own properties:

.. literalinclude:: geometry_processing/03_native_geometry.cpp
    :language: cpp
    :start-after: // tag::sub-shapes
    :end-before: // end::sub-shapes

Geometry iterator
-----------------

IfcOpenShell provides a geometry iterator to efficiently process geometry in an
IFC model. The iterator is always used in IfcConvert, and may also be invoked in
C++ or in Python. It offers the same features as individual processing, and
makes it easy to collect possible geometry in a model, supports multicore
processing, and implements caching and reuse to improve the efficiency of
geometry processing. For any bulk geometry processing, it is always recommended
to use the iterator.

By default, the geometry iterator processes all 3D geometry in a model from all
elements, and returns a list of X Y Z vertex ordinates in a flattened list, as
well as a flattened list of triangulated faces denoted by vertex indices:

.. literalinclude:: geometry_processing/04_geometry_iterator.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

There are a variety of configuration settings to get different output. For
example, you may filter elements from processing, extract 2D data, or return
non-triangulated OpenCASCADE BReps. For more information on the various
settings, see :doc:`Geometry Settings<../ifcopenshell/geometry_settings>`.

One of the more common settings used is a filter, which specifies only to
process certain geometry. For example, this iterator will only process the
windows of the model:

.. literalinclude:: geometry_processing/05_iterator_filter.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

.. note::

    The iterator can only be used to process whole elements, not individual
    shape representations, representation items, and profiles.

Manual parsing
--------------

IfcOpenShell lets you traverse any IFC entity graph. This means it is possible
for you to manually browse through the ``Representation`` attribute of IFC
elements, and parse the corresponding IFC representation items yourself instead
of using generic geometric processing such as individual processing and the
`Geometry iterator`_.

This approach requires an in-depth understanding of IFC geometry
representations, as well as its many caveats with units and transformations, but
can be very simple and extremely fast to extract specific types of geometry. For
example, if you know you are dealing with extrusions, you can specifically
pinpoint the depth of the extrusion.

.. literalinclude:: geometry_processing/06_manual_parsing.cpp
    :language: cpp
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
include and exclude filters.

Here is a typical example of serialising to glTF / glb, with the settings for
obj shown as a comment. Different serialisations may require different settings,
and the same settings object also exposes the
:doc:`serialisation options <../ifcopenshell/serialiser_settings>`.

.. literalinclude:: geometry_processing/07_geometry_serialisation.cpp
    :language: cpp
    :start-after: // tag::example
    :end-before: // end::example

.. note::

    The serialisers are plugins which are discovered next to the IfcOpenShell
    libraries, so a serialiser for a format is only available when it was built
    and installed.
