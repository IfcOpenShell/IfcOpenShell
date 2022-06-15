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

#include "../ifcgeom_schema_agnostic/IfcGeomRenderStyles.h"

namespace IfcGeom {	
	class IFC_GEOM_API IfcRepresentationShapeItem {
	private:
		int id;
		gp_GTrsf placement;
		TopoDS_Shape shape;
		std::shared_ptr<const SurfaceStyle> style;
	public:
		IfcRepresentationShapeItem(int id, const gp_GTrsf& placement, const TopoDS_Shape& shape, std::shared_ptr<const SurfaceStyle> style)
			: id(id), placement(placement), shape(shape), style(style) {}
		IfcRepresentationShapeItem(int id, const gp_GTrsf& placement, const TopoDS_Shape& shape)
			: id(id), placement(placement), shape(shape), style(0) {}
		IfcRepresentationShapeItem(int id, const TopoDS_Shape& shape, std::shared_ptr<const SurfaceStyle> style)
			: id(id), shape(shape), style(style) {}
		IfcRepresentationShapeItem(int id, const TopoDS_Shape& shape)
			: id(id), shape(shape), style(0) {}
		void append(const gp_GTrsf& trsf) { placement.Multiply(trsf); }
		void prepend(const gp_GTrsf& trsf) { placement.PreMultiply(trsf); }
		const TopoDS_Shape& Shape() const { return shape; }
		const gp_GTrsf& Placement() const { return placement; }
		bool hasStyle() const { return !!style; }
		const SurfaceStyle& Style() const { return *style; }
		const std::shared_ptr<const SurfaceStyle> StylePtr() const { return style; }
		void setStyle(std::shared_ptr<const SurfaceStyle> newStyle) { style = newStyle; }
		int ItemId() const { return id; }
	};
	typedef std::vector<IfcRepresentationShapeItem> IfcRepresentationShapeItems;
}
#endif
