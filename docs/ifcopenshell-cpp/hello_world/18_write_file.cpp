// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): writing the model back out to an IFC-SPF file.

#include <fstream>
#include <ifcparse/file.h>
#include <ifcparse/parse.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 18_write_file <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // After modifying some IFC data, the file can be saved to a new IFC-SPF
    // file. All of the serialisation happens in the stream operator.
    std::ofstream output("/path/to/a/new.ifc");
    output << model;
    // end::example

    return 0;
}
