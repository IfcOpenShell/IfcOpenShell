Geometry iterator
=================

IfcOpenShell provides a geometry iterator function to efficiently process
geometry in an IFC model. The iterator is always used in IfcConvert, and may
also be invoked in C++ or in Python.

The geometry iterator makes it easy to collect possible geometry in a model,
supports multicore processing, and implements caching and reuse to improve the
efficiency of geometry processing. It is also possible to process geometry one
by one using ``create_shape()``, but is significantly less efficient.

By default, the geometry iterator processes all 3D geometry in a model from all
elements, and returns a list of X Y Z vertex ordinates in a flattend list, as
well as a flattend list of triangulated faces denoted by vertex indices.

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
            # Get the current IFC element we are iterating over
            element = ifc_file.by_guid(shape.guid)
            # Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
            faces = shape.geometry.faces
            # X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
            verts = shape.geometry.verts
            # Material names and colour style information that are relevant to this shape
            materials = shape.geometry.materials
            # Indices of material applied per triangle face e.g. [f1m, f2m, ...]
            material_ids = shape.geometry.material_ids

            # Since the lists are flattened, you may prefer to group them per
            # face like so depending on your geometry kernel
            grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
            grouped_faces = [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]
            if not iterator.next():
                break
