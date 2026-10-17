// This file was generated with the assistance of an AI coding tool.
//
// Hello, world! (C++): releasing the model.

#include <ifcparse/file.h>
#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: release_model <model.ifc>" << std::endl;
        return 1;
    }

    // tag::example
    {
        ifcopenshell::file model(argv[1]);
        if (!model.good()) {
            std::cerr << "Unable to parse .ifc file" << std::endl;
            return 1;
        }
        // ... use the model and its instances here ...
    } // The model and all of its instances are released here.
    // end::example

    return 0;
}
