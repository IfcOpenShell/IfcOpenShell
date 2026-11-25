// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): getting an instance by its STEP ID.

#include <ifcparse/file.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 03_by_id <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // In IFC-SPF every instance has a STEP ID, such as #1. The returned
    // instance is falsy when there is no such instance in the file.
    auto instance = model.instance_by_id(1);
    if (instance) {
        instance.to_string(std::cout);
        std::cout << std::endl;
    }
    // end::example

    return 0;
}
