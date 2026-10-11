// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): getting an instance by its GlobalId.

#include <ifcparse/file.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 04_by_guid <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // Getting data from beginning to end is not meaningful to humans, but a
    // GlobalId is. The returned instance is falsy when there is no instance
    // with that GlobalId in the file.
    auto instance = model.instance_by_guid("0EI0MSHbX9gg8Fxwar7lL8");
    if (instance) {
        instance.to_string(std::cout);
        std::cout << std::endl;
    }
    // end::example

    return 0;
}
