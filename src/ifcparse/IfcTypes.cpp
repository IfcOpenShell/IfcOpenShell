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

#include <StdFail_NotDone.hxx>

#include "../ifcparse/IfcTypes.h"
#include "../ifcparse/IfcEnum.h"

using namespace IfcSchema;

#define IFC_PARSE_SOURCE
#include "../ifcparse/IfcSchema.h"
#undef IFC_PARSE_SOURCE

namespace IfcGeom {
	namespace Cache {
		std::map<int,TopoDS_Shape> Shape;
		std::map<int,TopoDS_Face> Face;
		std::map<int,TopoDS_Wire> Wire;
		std::map<int,Handle(Geom_Curve)> Curve;
		void PurgeShapeCache() {
			Shape.clear();
			Face.clear();
			Wire.clear();
			Curve.clear();
		}
	}
}

bool IfcGeom::convert_shape(const IfcEntity L, TopoDS_Shape &result) {
	if ( ! L ) return false;
	bool r = false;
	std::map<int,TopoDS_Shape>::const_iterator it = Cache::Shape.find(L->id);
	if ( it != Cache::Shape.end() ) { result = it->second; r = true; /*std::cout << "Read #" << L->id << " from cache" << std::endl;*/}
	if ( false ) {}
#define IFC_SHAPE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_SHAPE_SRC
	else std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	if ( r ) Cache::Shape[L->id] = result;
	return r;
}

bool IfcGeom::convert_wire(const IfcEntity L, TopoDS_Wire &result) {
	if ( ! L ) return false;
	bool r = false;
	std::map<int,TopoDS_Wire>::const_iterator it = Cache::Wire.find(L->id);
	if ( it != Cache::Wire.end() ) { result = it->second; r = true; /*std::cout << "Read #" << L->id << " from cache" << std::endl;*/}
	if ( false ) {}
#define IFC_WIRE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_WIRE_SRC
	else std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	if ( r ) Cache::Wire[L->id] = result;
	return r;
}

bool IfcGeom::convert_curve(const IfcEntity L, Handle(Geom_Curve) &result) {
	if ( ! L ) return false;
#define IFC_CURVE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_CURVE_SRC
	std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	return false;
}

bool IfcGeom::convert_face(const IfcEntity L, TopoDS_Face &result) {
	if ( ! L ) return false;
	bool r = false;
	std::map<int,TopoDS_Face>::const_iterator it = Cache::Face.find(L->id);
	if ( it != Cache::Face.end() ) { result = it->second; r = true; /*std::cout << "Read #" << L->id << " from cache" << std::endl;*/}
	if ( false ) {}
#define IFC_FACE_SRC
#include "../ifcparse/IfcSchema.h"
#undef IFC_FACE_SRC
	else std::cout << "[Error] Failed to interpret:" << std::endl << L->toString() << std::endl;
	if ( r ) Cache::Face[L->id] = result;
	return r;
}
