// This file was generated with the assistance of an AI coding tool.
//
// Code examples and mechanisms: opening an IFC file.

#include <ifcparse/file.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 01_open_and_check <model.ifc>" << std::endl;
        return 1;
    }

    // tag::example
    // The basis of all parsing and getting information from the IFC starts with
    // an ifcopenshell::file, and validating that it is good for use. The path is
    // normally the path to your model, here it is taken from the command line so
    // that this example can actually be run.
    std::string input_file_path = argv[1];
    ifcopenshell::file model(input_file_path);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }
    // end::example

    // The schema of the file is detected while parsing.
    std::cout << "Parsed " << input_file_path << " as " << model.schema()->name() << std::endl;
    return 0;
}
