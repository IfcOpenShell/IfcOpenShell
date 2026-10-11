// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: filtering the geometry iterator.

#include <ifcgeom/element.h>
#include <ifcgeom/filter.h>
#include <ifcgeom/iterator.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/representation.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <algorithm>
#include <iostream>
#include <set>
#include <thread>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 05_iterator_filter <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    ifcopenshell::geom::settings settings;
    const int num_threads = static_cast<int>((std::max)(1u, std::thread::hardware_concurrency()));

    // tag::example
    // One of the more common settings is to include only a subset of the model.
    // Filters are passed to the iterator as a list, and each of them either
    // includes only what it matches, or excludes what it matches.
    std::set<int> window_ids;
    for (auto& window : model.instances_by_type<Ifc4::IfcWindow>()) {
        window_ids.insert(static_cast<int>(window.id()));
    }
    std::vector<ifcopenshell::geom::filter_function> filters;
    filters.push_back(ifcopenshell::geom::instance_id_filter(true, false, window_ids));
    // A filter can also be based on the entity type, which, like elsewhere in the
    // API, includes subtypes, so this would process IfcWallStandardCase as well:
    //   filters.push_back(ifcopenshell::geom::entity_filter(true, false, {"IfcWall"}));

    ifcopenshell::geom::iterator it(
        ifcopenshell::geom::kernels::construct(&model, "hybrid-cgal-simple-opencascade", settings),
        settings, &model, filters, num_threads);

    std::size_t processed = 0;
    if (it.initialize()) {
        while (true) {
            auto element = it.get();
            std::cout << element->id() << " " << element->type() << std::endl;
            ++processed;
            if (!it.next()) {
                break;
            }
        }
    }
    // end::example

    std::cout << processed << " windows processed, out of "
              << model.instances_by_type<Ifc4::IfcWindow>().size() << std::endl;

    // Note that the iterator can only process whole elements, not individual
    // shape representations, representation items, or profiles.
    return 0;
}
