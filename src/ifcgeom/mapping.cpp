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

/*
#include "IfcGeom.h"
#include "../ifcgeom_schema_agnostic/IfcGeomShapeType.h"
#include "../ifcgeom_schema_agnostic/wire_utils.h"

#include <BRepCheck.hxx>
#include <BRepCheck_Analyzer.hxx>

#define Kernel POSTFIX_SCHEMA(Kernel)

using namespace IfcUtil;

bool IfcGeom::Kernel::convert_shapes(const IfcBaseInterface* l, ConversionResults& r) {
	if (shape_type(l) != ST_SHAPELIST) {
		TopoDS_Shape shp;
		if (convert_shape(l, shp)) {
			std::shared_ptr<const IfcGeom::SurfaceStyle> style;
			if (l->as<IfcSchema::IfcRepresentationItem>()) {
				style = get_style(l->as<IfcSchema::IfcRepresentationItem>());
			}
			r.push_back(IfcGeom::ConversionResult(l->data().id(), shp, style));
			return true;
		}
		return false;
	}

#include "mapping_shapes.i"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}

IfcGeom::ShapeType IfcGeom::Kernel::shape_type(const IfcBaseInterface* l) {
#include "mapping_shape_type.i"
	return ST_OTHER;
}

bool IfcGeom::Kernel::convert_shape(const IfcBaseInterface* l, TopoDS_Shape& r) {
	const unsigned int id = l->data().id();
	bool success = false;
	bool processed = false;
	bool ignored = false;

#ifndef NO_CACHE
	std::map<int,TopoDS_Shape>::const_iterator it = cache.Shape.find(id);
	if ( it != cache.Shape.end() ) { r = it->second; return true; }
#endif
	const bool include_curves = getValue(GV_DIMENSIONALITY) != +1;
	const bool include_solids_and_surfaces = getValue(GV_DIMENSIONALITY) != -1;

	IfcGeom::ShapeType st = shape_type(l);
	ignored = (!include_solids_and_surfaces && (st == ST_SHAPE || st == ST_FACE)) || (!include_curves && (st == ST_WIRE || st == ST_CURVE));
	if (st == ST_SHAPELIST) {
		processed = true;
		ConversionResults items;
		success = convert_shapes(l, items) && util::flatten_shape_list(items, r, false, getValue(GV_PRECISION));
	} else if (st == ST_SHAPE && include_solids_and_surfaces) {
#include "mapping_shape.i"
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
		success = convert_curve(l, crv) && util::convert_curve_to_wire(crv, w);
		if (success) {
			r = w;
		}
	}

	if ( processed && success ) { 
#ifndef NO_CACHE
		cache.Shape[id] = r;
#endif

		if (Logger::LOG_DEBUG >= Logger::Verbosity()) {
			std::stringstream ss;

			BRepCheck_Analyzer ana(r);

			std::function<void(const TopoDS_Shape&)> traverse_subshapes;

			traverse_subshapes = [&traverse_subshapes, &ana, &ss](const TopoDS_Shape& shape) {
				if (shape.IsNull())
					return;

				TopoDS_Iterator it(shape);
				for (; it.More(); it.Next()) {
					const TopoDS_Shape& subs = it.Value();

					auto rs = ana.Result(subs);
					if (rs) {
						for (auto& msg : rs->Status()) {
							if (msg != BRepCheck_NoError) {
								ss << " ";
								std::stringstream sst;
								BRepCheck::Print(msg, sst);
								auto sss = sst.str();
								// remove trailing newline added by Print()
								ss << sss.substr(0, sss.size() - 1);
							}
						}
					}

					traverse_subshapes(subs);
				}
			};

			traverse_subshapes(r);

			Logger::Notice((ana.IsValid() ? "Valid shape" : "Invalid shape with:") + ss.str(), l);
		}
	} else if (!ignored) {
		const char* const msg = processed
			? "Failed to convert:"
			: "No operation defined for:";
		Logger::Message(Logger::LOG_ERROR, msg, l);
	}
	return success;
}

bool IfcGeom::Kernel::convert_wire(const IfcBaseInterface* l, TopoDS_Wire& r) {
#include "mapping_wire.i"
	Handle(Geom_Curve) curve;
	if (IfcGeom::Kernel::convert_curve(l, curve)) {
		return util::convert_curve_to_wire(curve, r);
	}
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}

bool IfcGeom::Kernel::convert_face(const IfcBaseInterface* l, TopoDS_Shape& r) {
#include "mapping_face.i"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}

bool IfcGeom::Kernel::convert_curve(const IfcBaseInterface* l, Handle(Geom_Curve)& r) {
#include "mapping_curve.i"
	Logger::Message(Logger::LOG_ERROR,"No operation defined for:",l);
	return false;
}
*/