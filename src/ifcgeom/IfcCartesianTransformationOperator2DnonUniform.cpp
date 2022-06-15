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
#include <gp_Pnt2d.hxx>
#include <gp_Dir2d.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_Ax2d.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator2DnonUniform* l, gp_GTrsf2d& gtrsf) {
	IN_CACHE(IfcCartesianTransformationOperator2DnonUniform,l,gp_GTrsf2d,gtrsf)

	gp_Trsf2d trsf;
	gp_Pnt origin;
	gp_Dir axis1 (1.,0.,0.);
	gp_Dir axis2 (0.,1.,0.);
	
	IfcGeom::Kernel::convert(l->LocalOrigin(),origin);
	if ( l->Axis1() ) IfcGeom::Kernel::convert(l->Axis1(),axis1);
	if ( l->Axis2() ) IfcGeom::Kernel::convert(l->Axis2(),axis2);

	const gp_Pnt2d origin2d(origin.X(), origin.Y());
	const gp_Dir2d axis12d(axis1.X(), axis1.Y());
	const gp_Dir2d axis22d(axis2.X(), axis2.Y());
	
	const gp_Ax2d ax2d (origin2d, axis12d);
	trsf.SetTransformation(ax2d);
	
	if ( ax2d.Direction().Rotated(M_PI / 2.).Dot(axis22d) < 0. ) {
		gp_Trsf2d mirror; mirror.SetMirror(ax2d);
		trsf.Multiply(mirror);
	}

	trsf.Invert();
	
	const double scale1 = l->Scale().get_value_or(1.);
	const double scale2 = l->Scale2().get_value_or(scale1);
	gtrsf = gp_GTrsf2d();
	gtrsf.SetValue(1,1,scale1);
	gtrsf.SetValue(2,2,scale2);
	gtrsf.Multiply(trsf);

	if (is_identity(gtrsf, getValue(GV_PRECISION))) {
		gtrsf = gp_GTrsf2d();
	}

	CACHE(IfcCartesianTransformationOperator2DnonUniform,l,gtrsf)
	return true;
}
