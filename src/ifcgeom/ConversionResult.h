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

#include "../ifcgeom/IfcGeomRenderStyles.h"
#include "../ifcgeom/IteratorSettings.h"
#include "../ifcgeom/taxonomy.h"

#include <gp_GTrsf.hxx>
#include <TopoDS_Shape.hxx>

#include <vector>

namespace IfcGeom {	

	namespace Representation {
		class IFC_GEOM_API Triangulation;
	}

	class IFC_GEOM_API ConversionResultShape {
	public:
		virtual void Triangulate(const IteratorSettings& settings, const ifcopenshell::geometry::taxonomy::matrix4& place, Representation::Triangulation* t, int surface_style_id) const = 0;

		virtual void Serialize(std::string&) const = 0;
		virtual ConversionResultShape* clone() const = 0;
		virtual int surface_genus() const = 0;
		virtual bool is_manifold() const = 0;
		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual double bounding_box(void*& b) const = 0;
		virtual int num_vertices() const = 0;
		virtual void set_box(void* b) = 0;
		virtual ~ConversionResultShape() {}
	};

	class IFC_GEOM_API ConversionResult {
	private:
		int id;
		ifcopenshell::geometry::taxonomy::matrix4 placement;
		ConversionResultShape* shape;
		ifcopenshell::geometry::taxonomy::style style_;
	public:
		ConversionResult(int id, const ifcopenshell::geometry::taxonomy::matrix4& placement, const ConversionResultShape* shape, const ifcopenshell::geometry::taxonomy::style* style)
			: id(id), placement(placement), shape(shape->clone())
		{
			if (style) {
				style_ = *style;
			}
		}
		ConversionResult(int id, const ifcopenshell::geometry::taxonomy::matrix4& placement, const ConversionResultShape* shape)
			: id(id), placement(placement), shape(shape->clone()) {}
		ConversionResult(int id, const ConversionResultShape* shape, const ifcopenshell::geometry::taxonomy::style* style)
			: id(id), shape(shape->clone())
		{
			if (style) {
				style_ = *style;
			}
		}
		ConversionResult(int id, const ConversionResultShape* shape)
			: id(id), shape(shape->clone()) {}
		void append(const ifcopenshell::geometry::taxonomy::matrix4& trsf) {
			// @todo verify order
			placement.components() = placement.ccomponents() * trsf.ccomponents();
		}
		void prepend(const ifcopenshell::geometry::taxonomy::matrix4& trsf) {
			// @todo verify order
			placement.components() = trsf.ccomponents() * placement.ccomponents();
		}
		const ConversionResultShape* Shape() const { return shape; }
		ConversionResultShape* Shape() { return shape; }
		const ifcopenshell::geometry::taxonomy::matrix4& Placement() const { return placement; }
		bool hasStyle() const { return !!style_.diffuse; }
		const ifcopenshell::geometry::taxonomy::style& Style() const { return style_; }
		void setStyle(const ifcopenshell::geometry::taxonomy::style& newStyle) { style_ = newStyle; }
		int ItemId() const { return id; }
	};

	typedef std::vector<ConversionResult> ConversionResults;


	namespace util {
		// @todo this is now moved to occt kernel, do we need something similar in cgal?
		// bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse, double tol);
	}
}
#endif
