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

#include <gp_Pnt.hxx>
#include <gp_Dir.hxx>
#include <gp_Trsf.hxx>
#include <gp_Ax1.hxx>
#include <TopoDS.hxx>
#include <TopExp_Explorer.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcRevolvedAreaSolid* l, TopoDS_Shape& shape) {
	const double ang = l->Angle() * getValue(GV_PLANEANGLE_UNIT);

	TopoDS_Shape face;
	if ( ! convert_face(l->SweptArea(),face) ) return false;

	gp_Ax1 ax1;
	IfcGeom::Kernel::convert(l->Axis(), ax1);

	gp_Trsf trsf;
	bool has_position = true;
#ifdef SCHEMA_IfcSweptAreaSolid_Position_IS_OPTIONAL
	has_position = l->Position() != nullptr;
#endif
	if (has_position) {
		IfcGeom::Kernel::convert(l->Position(), trsf);
	}


	{
		// https://github.com/IfcOpenShell/IfcOpenShell/issues/1030
		// Check whether Axis does not intersect SweptArea

		double min_dot = +std::numeric_limits<double>::infinity();
		double max_dot = -std::numeric_limits<double>::infinity();

		gp_Ax2 ax(ax1.Location(), gp::DZ(), ax1.Direction());

		TopExp_Explorer exp(face, TopAbs_EDGE);
		for (; exp.More(); exp.Next()) {
			BRepAdaptor_Curve crv(TopoDS::Edge(exp.Current()));
			GCPnts_QuasiUniformDeflection tessellater(crv, getValue(GV_PRECISION));

			int n = tessellater.NbPoints();
			for (int i = 1; i <= n; ++i) {
				double d = ax.YDirection().XYZ().Dot(tessellater.Value(i).XYZ());
				if (d < min_dot) {
					min_dot = d;
				}
				if (d > max_dot) {
					max_dot = d;
				}
			}
		}

		bool intersecting;
		if (std::abs(min_dot) > std::abs(max_dot)) {
			intersecting = max_dot > + getValue(GV_PRECISION);
		} else {
			intersecting = min_dot < - getValue(GV_PRECISION);
		}

		if (intersecting) {
			Logger::Warning("Warning Axis and SweptArea intersecting", l);
		}
	}

	if (ang >= M_PI * 2. - ALMOST_ZERO) {
		shape = BRepPrimAPI_MakeRevol(face, ax1);
	} else {
		shape = BRepPrimAPI_MakeRevol(face, ax1, ang);
	}

	if (has_position) {
		// IfcSweptAreaSolid.Position (trsf) is an IfcAxis2Placement3D
		// and therefore has a unit scale factor
		shape.Move(trsf);
	}

	return !shape.IsNull();
}
