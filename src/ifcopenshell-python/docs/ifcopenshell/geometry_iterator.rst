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
settings, see :doc:`Geometry Settings<geometry_settings>`.

Basic usage in C++
-------------------

``IfcGeom::Iterator`` takes a geometry kernel (created with
``ifcopenshell::geometry::kernels::construct()``), a settings object, the
file to process, an optional list of filters, and the number of threads to
use for processing. After construction, call ``initialize()`` once, then
loop by alternating calls to ``get()`` (retrieve the current element) and
``next()`` (advance and process the next one, returning a null pointer once
the model is exhausted).

By default the iterator produces triangulated output, so ``get()`` can be
cast to ``IfcGeom::TriangulationElement``. Each element exposes its GUID,
IFC class, name, and an ``IfcGeom::Representation::Triangulation`` with flat
``verts()`` and ``faces()`` vectors.

.. code-block:: c++

    #include <ifcparse/IfcFile.h>
    #include <ifcgeom/Iterator.h>
    #include <iostream>

    int main(int argc, char** argv) {
        if (argc < 2) {
            std::cerr << "Usage: " << argv[0] << " <model.ifc>" << std::endl;
            return 1;
        }

        IfcParse::IfcFile file(argv[1]);
        if (!file.good()) {
            std::cerr << "Unable to parse .ifc file" << std::endl;
            return 1;
        }

        ifcopenshell::geometry::Settings settings;
        // Ask for coordinates already placed in world space, rather than
        // relative to each element's local placement.
        settings.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;

        int num_threads = 1;
        IfcGeom::Iterator iterator(
            ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings, Logger::Root()),
            settings, &file, {}, num_threads, Logger::Root());

        if (!iterator.initialize()) {
            std::cerr << "No geometrical elements found" << std::endl;
            return 1;
        }

        size_t num_elements = 0;
        do {
            const auto* triangulation = static_cast<const IfcGeom::TriangulationElement*>(iterator.get());
            const auto& geometry = triangulation->geometry();

            std::cout << triangulation->guid() << " (" << triangulation->type() << ") "
                      << geometry.verts().size() / 3 << " verts, "
                      << geometry.faces().size() / 3 << " triangles" << std::endl;

            ++num_elements;
        } while (iterator.next());

        std::cout << "Processed " << num_elements << " elements" << std::endl;

        return 0;
    }

.. note::

    ``next()`` performs the actual conversion of the following element and
    returns a null pointer once every element has been processed, so it
    doubles as the loop condition. This mirrors the pattern used throughout
    ``IfcConvert`` (see ``src/ifcconvert/IfcConvert.cpp``), which is built
    entirely on top of ``IfcGeom::Iterator``.

Filtering which elements are processed
---------------------------------------

The filter list accepts any ``boost::function<bool(IfcUtil::IfcBaseEntity*)>``,
so a lambda is enough to restrict processing to specific IFC classes, for
example only walls and slabs:

.. code-block:: c++

    std::vector<IfcGeom::filter_t> filters;
    filters.push_back([](IfcUtil::IfcBaseEntity* prod) {
        return prod->declaration().is("IfcWall") || prod->declaration().is("IfcSlab");
    });

    IfcGeom::Iterator iterator(
        ifcopenshell::geometry::kernels::construct(&file, "opencascade", settings, Logger::Root()),
        settings, &file, filters, num_threads, Logger::Root());

For more elaborate filtering (by layer, by attribute value, or by a list of
entity names), see the ready-made filters in ``src/ifcgeom/IfcGeomFilter.h``,
which is what ``IfcConvert``'s ``--include`` and ``--exclude`` options are
built on.

Multithreading
---------------

Passing a ``num_threads`` greater than ``1`` processes elements concurrently.
``get()`` and ``next()`` remain safe to call from a single consumer thread; the
iterator internally manages the worker pool.
