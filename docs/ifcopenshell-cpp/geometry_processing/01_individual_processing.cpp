// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: individual processing.

#include <ifcgeom/converter.h>
#include <ifcgeom/element.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/representation.h>
#include <ifcgeom/taxonomy.h>
#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <array>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 01_individual_processing <model.ifc>" << std::endl;
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

    // tag::example
    // The equivalent of ifcopenshell.geom.create_shape() is to ask a converter
    // for the BRep of the product, and to triangulate that. Choosing a geometry
    // kernel has a big impact on speed and capability, the hybrid of the CGAL
    // simple kernel with OpenCASCADE as a fallback is recommended.
    ifcopenshell::geom::settings settings;
    ifcopenshell::geom::converter converter(
        ifcopenshell::geom::kernels::construct(&model, "hybrid-cgal-simple-opencascade", settings),
        &model, settings);

    // When an entire element is processed, its 3D representation is used, with
    // all of its openings applied.
    auto representation = converter.mapping()->representation_of(element);
    ifcopenshell::geom::native_element* brep = converter.create_brep_for_representation_and_product(representation, element);
    if (brep == nullptr) {
        std::cerr << "Shape creation failed" << std::endl;
        return 1;
    }
    ifcopenshell::geom::triangulation_element shape(*brep);
    delete brep;

    // The GUID and the ID of the element we processed.
    std::cout << shape.guid() << std::endl;
    std::cout << shape.id() << std::endl;
    // The element itself is one lookup away.
    model.instance_by_guid(shape.guid()).to_string(std::cout);
    std::cout << std::endl;

    // A unique geometry id, useful to check whether two geometries are
    // identical for caching and reuse. The naming scheme is:
    // IfcShapeRepresentation.id{-layerset-LayerSet.id}{-material-Material.id}{-openings-[Opening n.id ...]}{-world-coords}
    std::cout << shape.geometry().id() << std::endl;

    // A 4x4 matrix with the location and rotation of the element, in the form:
    // [ [ x_x, y_x, z_x, x   ]
    //   [ x_y, y_y, z_y, y   ]
    //   [ x_z, y_z, z_z, z   ]
    //   [ 0.0, 0.0, 0.0, 1.0 ] ]
    // The position is the last column, the rotation is described by the first
    // three columns, by explicitly specifying the local X, Y and Z axes. The
    // axes follow a right-handed coordinate system, and objects are never
    // scaled, so the scale factor of the matrix is always 1.
    const auto matrix = shape.transformation().data();
    const auto origin = matrix->translation_part();
    std::cout << origin.x() << ", " << origin.y() << ", " << origin.z() << std::endl;

    const auto& geometry = shape.geometry();
    // X Y Z of the vertices in a flattened list, e.g. [v1x, v1y, v1z, v2x, ...]
    // The vertices are local, relative to the transformation matrix above.
    const auto& verts = geometry.verts();
    // Indices of the vertices per edge, e.g. [e1v1, e1v2, e2v1, e2v2, ...]. These
    // are the original edges of the geometry, which may be quads or ngons.
    const auto& edges = geometry.edges();
    // Indices of the vertices per triangle face, e.g. [f1v1, f1v2, f1v3, ...].
    // Faces are always triangles.
    const auto& faces = geometry.faces();
    std::cout << verts.size() / 3 << " vertices, " << edges.size() / 2 << " edges, "
              << faces.size() / 3 << " faces" << std::endl;

    // Since the lists are flattened, you may prefer to group them.
    std::vector<std::array<double, 3>> grouped_verts;
    for (std::size_t i = 0; i + 2 < verts.size(); i += 3) {
        grouped_verts.push_back({verts[i], verts[i + 1], verts[i + 2]});
    }
    std::vector<std::array<int, 3>> grouped_faces;
    for (std::size_t i = 0; i + 2 < faces.size(); i += 3) {
        grouped_faces.push_back({faces[i], faces[i + 1], faces[i + 2]});
    }
    std::cout << grouped_verts.size() << " grouped vertices, " << grouped_faces.size()
              << " grouped faces" << std::endl;

    // The styles which are relevant to this shape. A style is named after the
    // entity class when a default material is applied, otherwise it is named
    // after the surface style it comes from.
    for (auto& style : geometry.materials()) {
        std::cout << style->name << std::endl;
        const auto& colour = style->get_color();
        std::cout << "  diffuse " << colour.r() << ", " << colour.g() << ", " << colour.b() << std::endl;
        if (style->has_transparency()) {
            std::cout << "  transparency " << style->transparency << std::endl;
        }
    }

    // Indices of the material applied per triangle face, e.g. [f1m, f2m, ...],
    // and the representation item each face came from, e.g. [f1i, f2i, ...].
    std::cout << geometry.material_ids().size() << " material ids, "
              << geometry.item_ids().size() << " item ids" << std::endl;
    // end::example

    return 0;
}
