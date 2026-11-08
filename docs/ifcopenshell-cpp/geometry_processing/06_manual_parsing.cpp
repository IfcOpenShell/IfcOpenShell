// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: manual parsing.

#include <ifcparse/file.h>
#include <ifcparse/schemas/Ifc4.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 06_manual_parsing <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // IfcOpenShell lets you traverse any IFC entity graph, so the attributes of
    // representation items can be read without a geometry kernel. The caveat is
    // that you then have to deal with the many ways in which IFC can express
    // geometry yourself, including the units of the project and the many nested
    // placements.
    double unit_scale = 1.;
    try {
        // The second member of the pair is the factor to apply to a value in the
        // units of the project, to get its value in SI units.
        unit_scale = model.get_unit("LENGTHUNIT").second;
    } catch (const ifcopenshell::exception&) {
        std::cerr << "No length unit found in the project unit assignment" << std::endl;
    }

    // In the case of an extrusion, the only thing that has to be known
    // beforehand is which profile is swept, and how far.
    std::size_t reported = 0;
    for (auto& solid : model.instances_by_type<Ifc4::IfcExtrudedAreaSolid>()) {
        if (reported++ < 5) {
            const double depth = solid.Depth();
            // In project length units, and in SI meters.
            std::cout << depth << " = " << depth * unit_scale << " m" << std::endl;
        }
    }
    // end::example

    std::cout << reported << " extruded area solids in total" << std::endl;

    // This approach can be very simple and extremely fast to extract specific
    // types of geometry, but it requires an in-depth understanding of the IFC
    // representation items involved, so it is generally only recommended for
    // specific tasks.
    return 0;
}
