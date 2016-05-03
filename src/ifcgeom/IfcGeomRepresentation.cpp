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

#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>

#include <TopoDS_Compound.hxx>

#include "../ifcgeom/IfcGeom.h"

#include "IfcGeomRepresentation.h"

IfcGeom::Representation::Serialization::Serialization(const BRep& brep)
	: Representation(brep.settings())
	, _id(brep.getId())
{
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = brep.begin(); it != brep.end(); ++ it) {
		const TopoDS_Shape& s = it->Shape();
		gp_GTrsf trsf = it->Placement();
		
		if (it->hasStyle() && it->Style().Diffuse()) {
			const IfcGeom::SurfaceStyle::ColorComponent& clr = *it->Style().Diffuse();
			_surface_styles.push_back(clr.R());
			_surface_styles.push_back(clr.G());
			_surface_styles.push_back(clr.B());
		} else {
			_surface_styles.push_back(-1.);
			_surface_styles.push_back(-1.);
			_surface_styles.push_back(-1.);
		}
		if (it->hasStyle() && it->Style().Transparency()) {
			_surface_styles.push_back(1. - *it->Style().Transparency());
		} else {
			_surface_styles.push_back(1.);
		}
		
		if (settings().get(IteratorSettings::CONVERT_BACK_UNITS)) {
			gp_Trsf scale;
			scale.SetScaleFactor(1.0 / settings().unit_magnitude());
			trsf.PreMultiply(scale);
		}
		
		const TopoDS_Shape moved_shape = IfcGeom::Kernel::apply_transformation(s, trsf);

		builder.Add(compound, moved_shape);
	}
	std::stringstream sstream;
	BRepTools::Write(compound,sstream);
	_brep_data = sstream.str();
}