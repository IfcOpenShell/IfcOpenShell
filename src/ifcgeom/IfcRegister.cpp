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

namespace IfcGeom {
	namespace Cache {
		std::map<int,TopoDS_Shape> Shape;
		void PurgeShapeCache() {
			Shape.clear();
		}
	}
}

using namespace Ifc2x3;
using namespace IfcUtil;

bool IfcGeom::convert_shapes(const IfcBaseClass* l, ShapeList& r) {
#include "IfcRegisterConvertShapes.h"
	Ifc::LogMessage("Error","No operation defined for:",l->entity);
	return false;
}
bool IfcGeom::is_shape_collection(const IfcBaseClass* l) {
#include "IfcRegisterIsShapeCollection.h"
	return false;
}
const TopoDS_Shape* IfcGeom::convert_shape(const IfcBaseClass* l, TopoDS_Shape& r) {
	const unsigned int id = l->entity->id();
	std::map<int,TopoDS_Shape>::const_iterator it = Cache::Shape.find(id);
	if ( it != Cache::Shape.end() ) { r = it->second; return &(it->second); }
#include "IfcRegisterConvertShape.h"
	Ifc::LogMessage("Error","No operation defined for:",l->entity);
	return 0;
}
bool IfcGeom::convert_wire(const IfcBaseClass* l, TopoDS_Wire& r) {
#include "IfcRegisterConvertWire.h"
	Ifc::LogMessage("Error","No operation defined for:",l->entity);
	return false;
}
bool IfcGeom::convert_face(const IfcBaseClass* l, TopoDS_Face& r) {
#include "IfcRegisterConvertFace.h"
	Ifc::LogMessage("Error","No operation defined for:",l->entity);
	return false;
}
bool IfcGeom::convert_curve(const IfcBaseClass* l, Handle(Geom_Curve)& r) {
#include "IfcRegisterConvertCurve.h"
	Ifc::LogMessage("Error","No operation defined for:",l->entity);
	return false;
}