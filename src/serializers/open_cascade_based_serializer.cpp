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

#ifdef IFOPSH_WITH_OPENCASCADE

#include "open_cascade_based_serializer.h"

#include "../ifcparse/utils.h"
#include "../ifcgeom/kernels/opencascade/opencascade_conversion_result.h"

#include <string>
#include <fstream>
#include <cstdio>

#include <Standard_Version.hxx>
#include <BRepBuilderAPI_Transform.hxx>

bool open_cascade_based_serializer::ready() {
	std::ofstream test_file(ifcopenshell::path::from_utf8(out_filename).c_str(), std::ios_base::binary);
	bool succeeded = test_file.is_open();
	test_file.close();
	ifcopenshell::path::delete_file(out_filename);
	return succeeded;
}

void open_cascade_based_serializer::write(const ifcopenshell::geom::native_element* o) {
	auto itm = o->geometry().as_compound();
	TopoDS_Shape compound = ((ifcopenshell::geom::open_cascade_shape*)itm)->shape();
	writeShape(object_id(o), compound);
	delete itm;
}

#define RATHER_SMALL (1e-3)
#define APPROXIMATELY_THE_SAME(a,b) (fabs(a-b) < RATHER_SMALL)

const char* open_cascade_based_serializer::getSymbolForUnitMagnitude(float mag) {
	if (APPROXIMATELY_THE_SAME(mag, 0.001f)) {
		return "MM";
	} else if (APPROXIMATELY_THE_SAME(mag, 0.01f)) {
		return "CM";
	} else if (APPROXIMATELY_THE_SAME(mag, 1.0f)) {
		return "M";
	} else if (APPROXIMATELY_THE_SAME(mag, 0.3048f)) {
		return "FT";
	} else if (APPROXIMATELY_THE_SAME(mag, 0.0254f)) {
		return "INCH";
	} else {
		return 0;
	}
}

#endif
