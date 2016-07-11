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

#ifndef IFCSHAPELIST_H
#define IFCSHAPELIST_H

#include <gp_GTrsf.hxx>
#include <TopoDS_Shape.hxx>

#include "../ifcgeom/IfcGeomRenderStyles.h"

namespace IfcGeom {	
	class IFC_GEOM_API IfcRepresentationShapeItem {
	private:
		gp_GTrsf placement;
		TopoDS_Shape shape;
		const SurfaceStyle* style;
	public:
		IfcRepresentationShapeItem(const gp_GTrsf& placement, const TopoDS_Shape& shape, const SurfaceStyle* style)
			: placement(placement), shape(shape), style(style) {}
		IfcRepresentationShapeItem(const gp_GTrsf& placement, const TopoDS_Shape& shape)
			: placement(placement), shape(shape), style(0) {}
		IfcRepresentationShapeItem(const TopoDS_Shape& shape, const SurfaceStyle* style)
			: shape(shape), style(style) {}
		IfcRepresentationShapeItem(const TopoDS_Shape& shape)
			: shape(shape), style(0) {}
		void append(const gp_GTrsf& trsf) { placement.Multiply(trsf); }
		void prepend(const gp_GTrsf& trsf) { placement.PreMultiply(trsf); }
		const TopoDS_Shape& Shape() const { return shape; }
		const gp_GTrsf& Placement() const { return placement; }
		bool hasStyle() const { return style != 0; }
		const SurfaceStyle& Style() const { return *style; }
		void setStyle(const SurfaceStyle* style) { this->style = style; }
	};
	typedef std::vector<IfcRepresentationShapeItem> IfcRepresentationShapeItems;
}
#endif
