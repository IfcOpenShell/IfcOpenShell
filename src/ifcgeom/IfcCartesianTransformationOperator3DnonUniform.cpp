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
#include <gp_GTrsf.hxx>
#include <gp_Trsf.hxx>
#include <gp_Ax3.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCartesianTransformationOperator3DnonUniform* l, gp_GTrsf& gtrsf) {
	IN_CACHE(IfcCartesianTransformationOperator3DnonUniform,l,gp_GTrsf,gtrsf)
	gp_Trsf trsf;
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
	trsf.SetTransformation(ax3);
	trsf.Invert();
	const double scale1 = l->Scale().get_value_or(1.);
	const double scale2 = l->Scale2().get_value_or(scale1);
	const double scale3 = l->Scale3().get_value_or(scale1);
	gtrsf = gp_GTrsf();
	gtrsf.SetValue(1,1,scale1);
	gtrsf.SetValue(2,2,scale2);
	gtrsf.SetValue(3,3,scale3);
	gtrsf.PreMultiply(trsf);

	if (is_identity(gtrsf, getValue(GV_PRECISION))) {
		gtrsf = gp_GTrsf();
	}

	CACHE(IfcCartesianTransformationOperator3DnonUniform,l,gtrsf)
	return true;
}
