// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: processing a specific shape representation.

#include <ifcgeom/converter.h>
#include <ifcgeom/element.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/representation.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 02_representation <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }
    auto windows = model.instances_by_type<Ifc4::IfcWindow>();
    if (windows.empty()) {
        std::cerr << "No IfcWindow instances found" << std::endl;
        return 1;
    }
    auto window = windows.front();
    if (!window.Representation()) {
        std::cerr << "The window has no representation" << std::endl;
        return 1;
    }

    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&model, "hybrid-cgal-simple-opencascade", settings),
        &model, settings);

    // An element typically has more than one representation, for example a
    // "Body" and a "Box" for bounding box data. Note that representations can be
    // shared through IfcRepresentationMap, and that the "Body" of a window is
    // usually mapped.
    for (auto& representation : window.Representation().Representations()) {
        std::cout << representation.RepresentationIdentifier().value_or("<none>") << " "
                  << representation.RepresentationType().value_or("<none>") << std::endl;
    }

    // tag::example
    // When an entire element is processed, its 3D representation is used, with
    // all of its openings applied. To process a single shape representation
    // instead - which is the equivalent of the third argument of create_shape()
    // - the representation is selected by its identifier, and processed in the
    // context of the element.
    ifcopenshell::geom::native_element* brep = nullptr;
    for (auto& representation : window.Representation().Representations()) {
        if (representation.RepresentationIdentifier() == "Body") {
            brep = converter.create_brep_for_representation_and_product(representation, window);
            break;
        }
    }
    if (brep == nullptr) {
        std::cerr << "Shape creation failed" << std::endl;
        return 1;
    }
    ifcopenshell::geom::triangulation_element shape(*brep);
    delete brep;

    // When a representation is processed on its own, the openings, materials and
    // the layer set of the product are not applied to it, and its geometry is in
    // the coordinate system of the representation.
    std::cout << shape.geometry().id() << std::endl;
    std::cout << shape.geometry().verts().size() / 3 << " vertices, "
              << shape.geometry().faces().size() / 3 << " faces" << std::endl;
    // end::example

    return 0;
}
