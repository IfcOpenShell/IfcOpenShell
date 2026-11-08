// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): loading the model.

#include <ifcparse/file.h>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 01_load_model <model.ifc>" << std::endl;
        return 1;
    }

    // tag::example
    // The path is normally the path to your model, here it is taken from the
    // command line so that this example can actually be run.
    std::string input_file_path = argv[1];
    ifcopenshell::file model(input_file_path);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }
    // end::example

    std::cout << "Loaded " << input_file_path << std::endl;
    return 0;
}
