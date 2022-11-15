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

#include <TopoDS_Face.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcCompositeProfileDef* l, TopoDS_Shape& face) {
	// BRepBuilderAPI_MakeFace mf;

	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	IfcSchema::IfcProfileDef::list::ptr profiles = l->Profiles();
	//bool first = true;
	for (IfcSchema::IfcProfileDef::list::it it = profiles->begin(); it != profiles->end(); ++it) {
		TopoDS_Face f;
		if (convert_face(*it, f)) {
			builder.Add(compound, f);
			/* TopExp_Explorer exp(f, TopAbs_WIRE);
			for (; exp.More(); exp.Next()) {
				const TopoDS_Wire& wire = TopoDS::Wire(exp.Current());
				if (first) {
					mf.Init(BRepBuilderAPI_MakeFace(wire));
				} else {
					mf.Add(wire);
				}
				first = false;
			} */
		}
	}

	face = compound;
	return !face.IsNull();
}
