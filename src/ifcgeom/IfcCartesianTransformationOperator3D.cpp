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
#include <gp_Ax3.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator3D* l, gp_Trsf& trsf) {
	IN_CACHE(IfcCartesianTransformationOperator3D,l,gp_Trsf,trsf)
	gp_Pnt origin;
	IfcGeom::Kernel::convert(l->LocalOrigin(),origin);
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	gp_Dir axis3 (0.,0.,1.);
	if ( l->Axis1() ) IfcGeom::Kernel::convert(l->Axis1(),axis1);
	if ( l->Axis2() ) IfcGeom::Kernel::convert(l->Axis2(),axis2);
	if ( l->Axis3() ) IfcGeom::Kernel::convert(l->Axis3(),axis3);
	gp_Ax3 ax3 (origin,axis3,axis1);
	if ( axis2.Dot(ax3.YDirection()) < 0 ) ax3.YReverse();
	
	if (!axis_equal(ax3, (gp_Ax3) gp::XOY(), getValue(GV_PRECISION))) {
		trsf.SetTransformation(ax3);
		trsf.Invert();
	}
	
	if (l->Scale() && !ALMOST_THE_SAME(*l->Scale(), 1.)) {
		trsf.SetScaleFactor(*l->Scale());
	}

	CACHE(IfcCartesianTransformationOperator3D,l,trsf)
	return true;
}
