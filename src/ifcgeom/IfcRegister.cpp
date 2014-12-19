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

using namespace IfcSchema;
using namespace IfcUtil;

bool IfcGeom::Kernel::convert_shapes(const IfcBaseClass* l, IfcRepresentationShapeItems& r) {
#include "IfcRegisterConvertShapes.h"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
	return false;
}

bool IfcGeom::Kernel::is_shape_collection(const IfcBaseClass* l) {
#include "IfcRegisterIsShapeCollection.h"
	return false;
}

bool IfcGeom::Kernel::convert_shape(const IfcBaseClass* l, TopoDS_Shape& r) {
	const unsigned int id = l->entity->id();
	bool success = false;
	bool processed = false;
	std::map<int,TopoDS_Shape>::const_iterator it = cache.Shape.find(id);
	if ( it != cache.Shape.end() ) { r = it->second; return true; }
#include "IfcRegisterConvertShape.h"
	if ( processed ) { 
		const double precision = getValue(GV_PRECISION);
		apply_tolerance(r, precision);
		cache.Shape[id] = r;
	} else {
		Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l->entity);
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