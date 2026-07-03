/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

// TODO: Multiple schemas
#define IfcSchema Ifc2x3

#include "../helpers/pset.h"
#include "../ifcparse/file.h"
#include "../ifcparse/logger.h"
#include "../ifcparse/schemas/Ifc2x3.h"

#if USE_VLD
#include <vld.h>
#endif

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cout << "usage: IfcParseExamples <filename.ifc>" << std::endl;
        return 1;
    }

    // Redirect the output (both progress and log) to stdout
    logger::set_output(&std::cout, &std::cout);

    // Parse the IFC file provided in argv[1]
    ifcopenshell::file file(argv[1]);
    if (!file.good()) {
        std::cout << "Unable to parse .ifc file" << std::endl;
        return 1;
    }

    // Lets get a list of IfcBuildingElements, this is the parent
    // type of things like walls, windows and doors.
    // entitiesByType is a templated function and returns a
    // templated class that behaves like a std::vector.
    // Note that the return types are all typedef'ed as members of
    // the generated classes, ::list for the templated vector class,
    // ::ptr for a shared pointer and ::it for an iterator.
    // We will simply iterate over the vector and print a string
    // representation of the entity to stdout.
    //
    // Secondly, lets find out which of them are IfcWindows.
    // In order to access the additional properties that windows
    // have on top af the properties of building elements,
    // we need to cast them to IfcWindows. Since these properties
    // are optional we need to make sure the properties are
    // defined for the window in question before accessing them.
    auto elements = file.instances_by_type<IfcSchema::IfcBuildingElement>();

    std::cout << "Found " << elements.size() << " elements in " << argv[1] << ":" << std::endl;

    for (auto& element : elements) {
        element.to_string(std::cout);
        std::cout << std::endl;

        if (auto window = element.as<IfcSchema::IfcWindow>()) {
            if (window.OverallWidth() && window.OverallHeight()) {
                const double area = *window.OverallWidth() * *window.OverallHeight();
                std::cout << "The area of this window is " << area << std::endl;
            }
        }

        element_properties props = get_psets(element);

        for (auto& ps : props) {
            std::cout << ps.first << std::endl;
            std::cout << std::string(ps.first.size(), '=') << std::endl;
            size_t max_key_len = 0;
            for (auto& p : ps.second) {
                if (p.first.size() > max_key_len) {
                    max_key_len = p.first.size();
                }
            }
            for (auto& p : ps.second) {
                std::cout << p.first << std::string(max_key_len - p.first.size(), ' ') << ":" << p.second << std::endl;
            }
            std::cout << std::endl;
        }
    }
}
