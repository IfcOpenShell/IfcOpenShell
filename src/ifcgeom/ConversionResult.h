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

#include <vector>

namespace IfcGeom {	

	namespace Representation {
		class IFC_GEOM_API Triangulation;
	}

	class IFC_GEOM_API ConversionResultShape {
	public:
		virtual void Triangulate(const IteratorSettings& settings, const ifcopenshell::geometry::taxonomy::matrix4& place, Representation::Triangulation* t, int surface_style_id) const = 0;

		virtual void Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string&) const = 0;
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
		ifcopenshell::geometry::taxonomy::matrix4::ptr placement_;
		ConversionResultShape* shape_;
		ifcopenshell::geometry::taxonomy::style::ptr style_;
	public:
		ConversionResult(int id, ifcopenshell::geometry::taxonomy::matrix4::ptr placement, ConversionResultShape* shape, ifcopenshell::geometry::taxonomy::style::ptr style)
			: id(id), placement_(placement ? placement : ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape), style_(style)
		{}
		ConversionResult(int id, ifcopenshell::geometry::taxonomy::matrix4::ptr placement, ConversionResultShape* shape)
			: id(id), placement_(placement ? placement : ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape)
		{}
		ConversionResult(int id, ConversionResultShape* shape, ifcopenshell::geometry::taxonomy::style::ptr style)
			: id(id), placement_(ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape), style_(style)
		{}
		ConversionResult(int id, ConversionResultShape* shape)
			: id(id), placement_(ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape)
		{}
		void append(ifcopenshell::geometry::taxonomy::matrix4::ptr trsf) {
			// @todo verify order
			placement_->components() = placement_->ccomponents() * trsf->ccomponents();
		}
		void prepend(ifcopenshell::geometry::taxonomy::matrix4::ptr trsf) {
			// @todo verify order
			placement_->components() = trsf->ccomponents() * placement_->ccomponents();
		}
		ConversionResultShape* Shape() const { return shape_; }
		ifcopenshell::geometry::taxonomy::matrix4::ptr Placement() const { return placement_; }
		bool hasStyle() const { return !!style_; }
		const ifcopenshell::geometry::taxonomy::style& Style() const { return *style_; }
		ifcopenshell::geometry::taxonomy::style::ptr StylePtr() const { return style_; }
		void setStyle(ifcopenshell::geometry::taxonomy::style::ptr newStyle) { style_ = newStyle; }
		int ItemId() const { return id; }
	};

	typedef std::vector<ConversionResult> ConversionResults;


	namespace util {
		// @todo this is now moved to occt kernel, do we need something similar in cgal?
		// bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse, double tol);
	}
}
#endif
