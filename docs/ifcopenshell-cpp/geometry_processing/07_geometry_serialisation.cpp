// This file was generated with the assistance of an AI coding tool.
//
// Geometry processing: geometry serialisation.

#include <ifcgeom/element.h>
#include <ifcgeom/geometry_serializer.h>
#include <ifcgeom/iterator.h>
#include <ifcgeom/kernel_registry.h>
#include <ifcgeom/representation.h>
#include <ifcparse/file.h>
#include <serializers/geometry_serializer_plugin.h>
#include <algorithm>
#include <filesystem>
#include <iostream>
#include <thread>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: 07_geometry_serialisation <model.ifc>" << std::endl;
        return 1;
    }
    ifcopenshell::file model(argv[1]);
    if (!model.good()) {
        std::cerr << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // tag::example
    // Geometry may be serialised into many different formats. The settings object
    // is the same one the iterator uses, extended with the settings the serialiser
    // itself supports.
    ifcopenshell::geom::settings settings;
    // Settings for glTF / glb.
    settings.get<ifcopenshell::geom::settings::OutputDimensionality>().value =
        ifcopenshell::geom::settings::CURVES_SURFACES_AND_SOLIDS;
    // Note that applying default materials is required in glTF serialisation.
    settings.get<ifcopenshell::geom::settings::ApplyDefaultMaterials>().value = true;
    // Settings for obj, which are serialised to world coordinates instead.
    //   settings.get<ifcopenshell::geom::settings::UseWorldCoords>().value = true;
    // Setting element GUIDs is optional, but useful to uniquely identify objects
    // in non semantic formats.
    settings.get<ifcopenshell::geom::settings::UseElementGuids>().value = true;

    // The serialisers are plugins, which are found next to the IfcOpenShell
    // libraries, and are addressed by the extension of the file to write. This
    // example writes output.glb in the current directory.
    ifcopenshell::serializers::geometry_serializer_context context{"output.glb", "output.glb", settings};
    auto& registry = ifcopenshell::serializers::geometry_serializer_registry_instance();
    registry.configure(".glb", context);
    auto serializer = registry.create(".glb", context);
    // To serialise to obj instead:
    //   auto serializer = registry.create(".obj", context);

    serializer->setFile(model);
    // Without the ConvertBackUnits setting, the geometry is in meters already.
    serializer->setUnitNameAndMagnitude("METER", 1.0f);
    serializer->writeHeader();

    ifcopenshell::geom::iterator it(
        ifcopenshell::geom::kernels::construct(&model, "hybrid-cgal-simple-opencascade", settings),
        settings, &model, static_cast<int>((std::max)(1u, std::thread::hardware_concurrency())));
    if (it.initialize()) {
        while (true) {
            auto element = it.get();
            serializer->write(
                static_cast<const ifcopenshell::geom::triangulation_element*>(element.get()));
            if (!it.next()) {
                break;
            }
        }
    }
    serializer->finalize();
    // end::example

    std::cout << std::filesystem::file_size("output.glb") << " bytes written to output.glb" << std::endl;
    return 0;
}
