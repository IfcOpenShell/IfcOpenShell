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

#include <BRepAlgoAPI_Cut.hxx>
#include "../ifcgeom/IfcGeom.h"
#include <memory>

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcManifoldSolidBrep* l, IfcRepresentationShapeItems& shape) {
	TopoDS_Shape s;
	auto collective_style = get_style(l);
	if (convert_shape(l->Outer(),s) ) {
		auto indiv_style = get_style(l->Outer());

		IfcSchema::IfcClosedShell::list::ptr voids(new IfcSchema::IfcClosedShell::list);
		if (l->declaration().is(IfcSchema::IfcFacetedBrepWithVoids::Class())) {
			voids = l->as<IfcSchema::IfcFacetedBrepWithVoids>()->Voids();
		}
#ifdef SCHEMA_HAS_IfcAdvancedBrepWithVoids
		if (l->declaration().is(IfcSchema::IfcAdvancedBrepWithVoids::Class())) {
			voids = l->as<IfcSchema::IfcAdvancedBrepWithVoids>()->Voids();
		}
#endif

		for (IfcSchema::IfcClosedShell::list::it it = voids->begin(); it != voids->end(); ++it) {
			TopoDS_Shape s2;
			/// @todo No extensive shapefixing since shells should be disjoint.
			/// @todo Awaiting generalized boolean ops module with appropriate checking
			if (convert_shape(l->Outer(), s2)) {
				s = BRepAlgoAPI_Cut(s, s2).Shape();
			}
		}

		shape.push_back(IfcRepresentationShapeItem(l->data().id(), s, indiv_style ? indiv_style : collective_style));
		return true;
	}
	return false;
}
