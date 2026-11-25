// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): inspecting the schema of a model.

#include <ifcparse/file.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 02_schema <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // May return IFC2X3, IFC4, or IFC4X3_ADD2.
    std::cout << model.schema()->name() << std::endl;
    // end::example

    return 0;
}
