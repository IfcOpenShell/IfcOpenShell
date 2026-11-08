// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: the native geometry of a kernel.

#include <ifcgeom/converter.h>
#include <ifcgeom/element.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/kernels/opencascade/opencascade_conversion_result.h>
#include <ifcgeom/representation.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <TopoDS_Shape.hxx>
#include <algorithm>
#include <iostream>
#include <memory>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 03_native_geometry <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }
    auto walls = model.instances_by_type<Ifc4::IfcWall>();
    if (walls.empty()) {
        std::cerr << "No IfcWall instances found" << std::endl;
        return 1;
    }
    auto element = walls.front();

    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&model, "hybrid-cgal-simple-opencascade", settings),
        &model, settings);

    // tag::example
    // Instead of triangulating the shape, the untriangulated geometry of the
    // kernel can be used. It is a list of shapes, one per representation item.
    std::unique_ptr<ifcopenshell::geom::native_element> brep(
        converter.create_brep_for_representation_and_product(
            converter.mapping()->representation_of(element), element));
    if (!brep) {
        std::cerr << "Shape creation failed" << std::endl;
        return 1;
    }
    std::cout << brep->geometry().shapes().size() << " representation items" << std::endl;

    // The shapes themselves are opaque, so that kernels other than OpenCASCADE
    // can be used, and are combined into a single compound to be able to ask
    // kernel agnostic questions. The compound is allocated, so it should be deleted again.
    ifcopenshell::geom::conversion_result_shape* compound = brep->geometry().as_compound();
    std::cout << "volume " << compound->volume().to_double() << std::endl;
    std::cout << "area " << compound->area().to_double() << std::endl;
    std::cout << compound->num_vertices() << " vertices, " << compound->num_edges()
              << " edges, " << compound->num_faces() << " faces" << std::endl;
    // end::example

    // tag::opencascade
    // If you know the shape was made by the OpenCASCADE kernel, it can be cast
    // back to the TopoDS_Shape it wraps, and used with OpenCASCADE directly.
    // Use compound->backend_id() to test.
    if (auto* occt = dynamic_cast<ifcopenshell::geom::open_cascade_shape*>(compound)) {
        const TopoDS_Shape& topods = occt->shape();
        GProp_GProps properties;
        BRepGProp::VolumeProperties(topods, properties);
        std::cout << "volume " << properties.Mass() << std::endl;
    }
    // end::opencascade

    // tag::sub-shapes
    // A shape can also be taken apart: facets() gives its faces and vertices()
    // its vertices, and each of those can be asked for its own properties, such
    // as the area() of a face. These shapes are allocated, so the caller deletes
    // them again.
    std::size_t planar_faces = 0;
    for (auto* facet : compound->facets()) {
        // position() is only defined for planar faces, and throws when the face
        // is, for example, part of a cylinder.
        try {
            const auto centre = facet->position().to_double();
            if (planar_faces++ == 0) {
                std::cout << "first face at " << centre[0] << ", " << centre[1] << ", " << centre[2] << std::endl;
            }
        } catch (const std::runtime_error&) {
        }
        delete facet;
    }
    std::cout << planar_faces << " planar faces" << std::endl;
    // end::sub-shapes

    delete compound;

    return 0;
}
