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

#include "CgalKernel.h"

#define CgalKernel MAKE_TYPE_NAME(CgalKernel)

using namespace IfcUtil;

bool IfcGeom::CgalKernel::convert_shapes(const IfcBaseClass* l, ConversionResults& r) {
	if (shape_type(l) != ST_SHAPELIST) {
		cgal_shape_t shp;
		if (convert_shape(l, shp)) {
			r.push_back(IfcGeom::ConversionResult(l->data().id(), new CgalShape(shp), get_style(l->as<IfcSchema::IfcRepresentationItem>())));
			return true;
		}
		return false;
	}

#include "CgalEntityMappingShapes.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}

IfcGeom::ShapeType IfcGeom::CgalKernel::shape_type(const IfcBaseClass* l) {
#include "CgalEntityMappingShapeType.h"
	return ST_OTHER;
}

bool IfcGeom::CgalKernel::convert_shape(const IfcBaseClass* l, cgal_shape_t& r) {
	const unsigned int id = l->data().id();
	bool success = false;
	bool processed = false;
	bool ignored = false;

#ifndef NO_CACHE
	std::map<int, cgal_shape_t>::const_iterator it = cache.Shape.find(id);
	if ( it != cache.Shape.end() ) { r = it->second; return true; }
#endif
	const bool include_curves = getValue(GV_DIMENSIONALITY) != +1;
	const bool include_solids_and_surfaces = getValue(GV_DIMENSIONALITY) != -1;

	IfcGeom::ShapeType st = shape_type(l);
	ignored = (!include_solids_and_surfaces && (st == ST_SHAPE || st == ST_FACE)) || (!include_curves && (st == ST_WIRE || st == ST_CURVE));
	if (st == ST_SHAPE && include_solids_and_surfaces) {
#include "CgalEntityMappingShape.h"
	}

	if ( processed && success ) { 
//		const double precision = getValue(GV_PRECISION);
		// apply_tolerance(r, precision);
#ifndef NO_CACHE
		cache.Shape[id] = r;
#endif
	} else if (!ignored) {
		const char* const msg = processed
			? "Failed to convert:"
			: "No operation defined for:";
		Logger::Message(Logger::LOG_ERROR, msg, l);
	}
	return success;
}

bool IfcGeom::CgalKernel::convert_wire(const IfcBaseClass* l, cgal_wire_t& r) {
#include "CgalEntityMappingWire.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}

bool IfcGeom::CgalKernel::convert_face(const IfcBaseClass* l, cgal_face_t& r) {
#include "CgalEntityMappingFace.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}

bool IfcGeom::CgalKernel::convert_curve(const IfcBaseClass* l, cgal_curve_t& r) {
#include "CgalEntityMappingCurve.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}
