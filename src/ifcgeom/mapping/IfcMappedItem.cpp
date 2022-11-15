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

#include <gp_GTrsf.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcMappedItem* l, IfcRepresentationShapeItems& shapes) {
	gp_GTrsf gtrsf;
	IfcSchema::IfcCartesianTransformationOperator* transform = l->MappingTarget();
	if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator3DnonUniform::Class()) ) {
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3DnonUniform*)transform,gtrsf);
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator2DnonUniform::Class()) ) {
		Logger::Message(Logger::LOG_ERROR, "Unsupported MappingTarget:", transform);
		return false;
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator3D::Class()) ) {
		gp_Trsf trsf;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator3D*)transform,trsf);
		gtrsf = trsf;
	} else if ( transform->declaration().is(IfcSchema::IfcCartesianTransformationOperator2D::Class()) ) {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcCartesianTransformationOperator2D*)transform,trsf_2d);
		gtrsf = (gp_Trsf) trsf_2d;
	}
	IfcSchema::IfcRepresentationMap* map = l->MappingSource();
	IfcSchema::IfcAxis2Placement* placement = map->MappingOrigin();
	gp_Trsf trsf;
	if (placement->declaration().is(IfcSchema::IfcAxis2Placement3D::Class())) {
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement3D*)placement,trsf);
	} else {
		gp_Trsf2d trsf_2d;
		IfcGeom::Kernel::convert((IfcSchema::IfcAxis2Placement2D*)placement,trsf_2d);
		trsf = trsf_2d;
	}
	gtrsf.Multiply(trsf);

	auto mapped_item_style = get_style(l);
	
	const size_t previous_size = shapes.size();
	bool b = convert_shapes(map->MappedRepresentation(), shapes);
	
	for (size_t i = previous_size; i < shapes.size(); ++ i ) {
		shapes[i].prepend(gtrsf);

		// Apply styles assigned to the mapped item only if on
		// a more granular level no styles have been applied
		if (!shapes[i].hasStyle()) {
			shapes[i].setStyle(mapped_item_style);
		}
	}

	return b;
}
