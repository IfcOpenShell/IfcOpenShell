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

#include "IfcGeom.h"
#include "IfcGeomShapeType.h"

using namespace IfcSchema;
using namespace IfcUtil;

bool IfcGeom::Kernel::convert_shapes(const IfcBaseClass* l, IfcRepresentationShapeItems& r) {
#include "IfcRegisterConvertShapes.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

IfcGeom::ShapeType IfcGeom::Kernel::shape_type(const IfcBaseClass* l) {
#include "IfcRegisterShapeType.h"
	return ST_OTHER;
}

bool IfcGeom::Kernel::convert_shape(const IfcBaseClass* l, TopoDS_Shape& r) {
	const unsigned int id = l->entity->id();
	bool success = false;
	bool processed = false;
	bool ignored = false;

	std::map<int,TopoDS_Shape>::const_iterator it = cache.Shape.find(id);
	if ( it != cache.Shape.end() ) { r = it->second; return true; }
	const bool include_curves = getValue(GV_DIMENSIONALITY) != +1;
	const bool include_solids_and_surfaces = getValue(GV_DIMENSIONALITY) != -1;

	IfcGeom::ShapeType st = shape_type(l);
	ignored = (!include_solids_and_surfaces && (st == ST_SHAPE || st == ST_FACE)) || (!include_curves && (st == ST_WIRE || st == ST_CURVE));
	if (st == ST_SHAPELIST) {
		processed = true;
		IfcRepresentationShapeItems items;
		success = convert_shapes(l, items) && flatten_shape_list(items, r, false);
	} else if (st == ST_SHAPE && include_solids_and_surfaces) {
#include "IfcRegisterConvertShape.h"
	} else if (st == ST_FACE && include_solids_and_surfaces) {
		processed = true;
		success = convert_face(l, r);
	} else if (st == ST_WIRE && include_curves) {
		processed = true;
		TopoDS_Wire w;
		success = convert_wire(l, w);
		if (success) {
			r = w;
		}
	} else if (st == ST_CURVE && include_curves) {
		processed = true;
		Handle(Geom_Curve) crv;
		TopoDS_Wire w;
		success = convert_curve(l, crv) && convert_curve_to_wire(crv, w);
		if (success) {
			r = w;
		}
	}

	if ( processed && success ) { 
		const double precision = getValue(GV_PRECISION);
		apply_tolerance(r, precision);
		cache.Shape[id] = r;
	} else if (!ignored) {
		const char* const msg = processed
			? "Failed to convert:"
			: "No operation defined for:";
		Logger::Message(Logger::LOG_ERROR, msg, l->entity);
	}
	return success;
}

bool IfcGeom::Kernel::convert_wire(const IfcBaseClass* l, TopoDS_Wire& r) {
#include "IfcRegisterConvertWire.h"
	Handle(Geom_Curve) curve;
	if (IfcGeom::Kernel::convert_curve(l, curve)) {
		return IfcGeom::Kernel::convert_curve_to_wire(curve, r);
	}
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

bool IfcGeom::Kernel::convert_face(const IfcBaseClass* l, TopoDS_Shape& r) {
#include "IfcRegisterConvertFace.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

bool IfcGeom::Kernel::convert_curve(const IfcBaseClass* l, Handle(Geom_Curve)& r) {
#include "IfcRegisterConvertCurve.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}