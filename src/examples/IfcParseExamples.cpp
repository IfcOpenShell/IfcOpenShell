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

#include "../ifcparse/IfcParse.h"

using namespace Ifc2x3;

int main(int argc, char** argv) {

	if ( argc != 2 ) {
		std::cout << "usage: IfcParseExamples <filename.ifc>" << std::endl;
		return 1;
	}

	// Redirect the output (both progress and log) to stdout
	Ifc::SetOutput(&std::cout,&std::cout);

	// Parse the IFC file provided in argv[1]
	if ( ! Ifc::Init(argv[1]) ) {
		std::cout << "Unable to parse .ifc file" << std::endl;
		return 1;
	}

	// Lets get a list of IfcBuildingElements, this is the parent
	// type of things like walls, windows and doors.
	// EntitiesByType is a templated function and returns a
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
	//
	// Since we are accessing properties that represent a length
	// measure we can multiply the value by Ifc::LengthUnit, which
	// contains the ratio of the unit defined in the IfcUnitAssignment
	// to the standard SI Unit, the meter.
	IfcBuildingElement::list elements = Ifc::EntitiesByType<IfcBuildingElement>();

	std::cout << "Found " << elements->Size() << " elements in " << argv[1] << ":" << std::endl;
	
	for ( IfcBuildingElement::it it = elements->begin(); it != elements->end(); ++ it ) {
		
		const IfcBuildingElement::ptr element = *it;
		std::cout << element->entity->toString() << std::endl;
		
		if ( element->is(IfcWindow::Class()) ) {
			const IfcWindow::ptr window = reinterpret_pointer_cast<IfcBuildingElement,IfcWindow>(element);
			
			if ( window->hasOverallWidth() && window->hasOverallHeight() ) {
				const float area = window->OverallWidth()*window->OverallHeight() * (Ifc::LengthUnit*Ifc::LengthUnit);
				std::cout << "This window has an area of " << area << "m2" << std::endl;
			}
		}

	}

}