// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: the geometry iterator.

#include <ifcgeom/element.h>
#include <ifcgeom/iterator.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/representation.h>
#include <ifcparse/file.h>
#include <algorithm>
#include <iostream>
#include <thread>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 04_geometry_iterator <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // The iterator offers the same features as processing a single element, but
    // it collects all geometry in a model, supports multicore processing, and
    // implements caching and reuse to improve the efficiency of geometry
    // processing. For bulk geometry processing, it is always recommended to use
    // the iterator.
    //
    // By default it processes all 3D geometry in a model, from all elements, and
    // returns the vertices as a flattened list, and the triangulated faces as
    // indices into that list.
    ifcopenshell::geom::settings settings;
    const int num_threads = static_cast<int>((std::max)(1u, std::thread::hardware_concurrency()));
    ifcopenshell::geom::iterator it(
        ifcopenshell::geom::kernels::construct(&model, "hybrid-cgal-simple-opencascade", settings),
        settings, &model, num_threads);

    if (it.initialize()) {
        while (true) {
            auto element = it.get();
            // The output is triangulated, unless the IteratorOutput setting says
            // otherwise, so the element is a triangulation_element.
            auto* shape = static_cast<const ifcopenshell::geom::triangulation_element*>(element.get());
            const auto& geometry = shape->geometry();
            std::cout << shape->id() << " " << shape->type() << " " << shape->guid() << " "
                      << geometry.verts().size() / 3 << " vertices, "
                      << geometry.edges().size() / 2 << " edges, "
                      << geometry.faces().size() / 3 << " faces, "
                      << geometry.materials().size() << " styles" << std::endl;
            // ... write code to process the geometry here ...
            if (!it.next()) {
                break;
            }
        }
    }
    // end::example

    std::cout << "processed " << it.processed_ << " elements" << std::endl;
    return 0;
}
