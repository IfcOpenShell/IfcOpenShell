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

#include "../ifcgeom/IfcGeom.h"
#include <memory>

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcShellBasedSurfaceModel* l, IfcRepresentationShapeItems& shapes) {
	aggregate_of_instance::ptr shells = l->SbsmBoundary();
	auto collective_style = get_style(l);
	for( aggregate_of_instance::it it = shells->begin(); it != shells->end(); ++ it ) {
		TopoDS_Shape s;
		decltype(collective_style) shell_style;
		if ((*it)->declaration().is(IfcSchema::IfcRepresentationItem::Class())) {
			shell_style = get_style((IfcSchema::IfcRepresentationItem*)*it);
		}
		if (convert_shape(*it,s)) {
			shapes.push_back(IfcRepresentationShapeItem(l->data().id(), s, shell_style ? shell_style : collective_style));
		}
	}
	return true;
}
