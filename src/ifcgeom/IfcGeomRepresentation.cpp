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
	, id_(brep.id())
{
	TopoDS_Compound compound = brep.as_compound();
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = brep.begin(); it != brep.end(); ++ it) {
		if (it->hasStyle() && it->Style().Diffuse()) {
			const IfcGeom::SurfaceStyle::ColorComponent& clr = *it->Style().Diffuse();
			surface_styles_.push_back(clr.R());
			surface_styles_.push_back(clr.G());
			surface_styles_.push_back(clr.B());
		} else {
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
		}
		if (it->hasStyle() && it->Style().Transparency()) {
			surface_styles_.push_back(1. - *it->Style().Transparency());
		} else {
			surface_styles_.push_back(1.);
		}
	}
	std::stringstream sstream;
	BRepTools::Write(compound,sstream);
	brep_data_ = sstream.str();
}

TopoDS_Compound IfcGeom::Representation::BRep::as_compound() const {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);
	for (IfcGeom::IfcRepresentationShapeItems::const_iterator it = begin(); it != end(); ++it) {
		const TopoDS_Shape& s = it->Shape();
		gp_GTrsf trsf = it->Placement();

		if (settings().get(IteratorSettings::CONVERT_BACK_UNITS)) {
			gp_Trsf scale;
			scale.SetScaleFactor(1.0 / settings().unit_magnitude());
			trsf.PreMultiply(scale);
		}

		const TopoDS_Shape moved_shape = IfcGeom::Kernel::apply_transformation(s, trsf);
		builder.Add(compound, moved_shape);
	}
	return compound;
}