/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                          *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify        *
 * it under the terms of the Lesser GNU General Public License as published by *
 * the Free Software Foundation, either version 3.0 of the License, or         *
 * (at your option) any later version.                                        *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,             *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of              *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                *
 * Lesser GNU General Public License for more details.                         *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License    *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.        *
 *                                                                              *
 ********************************************************************************/

// This file was generated with the assistance of an AI coding tool.

#ifndef BOOLEAN_CGAL_FALLBACK_H
#define BOOLEAN_CGAL_FALLBACK_H

#include "boolean_utils.h"

namespace IfcGeom {
	namespace util {

		// Recomputes a boolean operation through the exact arithmetic CGAL kernel,
		// used as a fallback for cases where OCCT produces a non-manifold result
		// that cannot be trusted. Only planar-faced operands are supported, since
		// the conversion goes through a CGAL Nef polyhedron. Returns false when
		// the fallback is not available or not applicable, leaving result
		// untouched.
		bool boolean_operation_cgal_fallback(const TopoDS_Shape& a, const NCollection_List<TopoDS_Shape>& b, BOPAlgo_Operation op, TopoDS_Shape& result, double tol);

	}
}

#endif
