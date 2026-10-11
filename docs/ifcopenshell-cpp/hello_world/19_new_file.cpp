// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): creating a new, empty, file.

#include <ifcparse/file.h>
#include <ifcparse/schema.h>
#include <iostream>

int main(int argc, char** argv) {
    (void)argv;

    // tag::example
    // A new file can be created from scratch instead of reading an existing
    // one. Without arguments this is an IFC4 file.
    ifcopenshell::file model;
    // Or if you want a particular schema:
    ifcopenshell::file model_2x3(ifcopenshell::schema_by_name("IFC2X3"));
    // end::example

    std::cout << model.schema()->name() << std::endl;
    std::cout << model_2x3.schema()->name() << std::endl;
    return 0;
}
