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

#include "../../ifcgeom/schema_agnostic/IfcGeomRenderStyles.h"
#include "../../ifcgeom/settings.h"
#include "../../ifcgeom/taxonomy.h"

namespace ifcopenshell { namespace geometry {

	namespace Representation {
		class IFC_GEOM_API Triangulation;
	}

	// @todo, this class is no longer necessary, we can directly use
	// taxonomy::matrix4, which does not need to be implemented specifically
	// in the respective kernels
	/*
	class IFC_GEOM_API ConversionResultPlacement {
	public:
		virtual void Multiply(const ifcopenshell::geometry::taxonomy::matrix4&) = 0;
		virtual void PreMultiply(const ifcopenshell::geometry::taxonomy::matrix4&) = 0;
		virtual void TranslationPart(double& X, double& Y, double& Z) const = 0;
		virtual ConversionResultPlacement* inverted() const = 0;
		virtual ConversionResultPlacement* multiplied(const ifcopenshell::geometry::taxonomy::matrix4&) const = 0;
		virtual double Value(int i, int j) const = 0;
		virtual ConversionResultPlacement* clone() const = 0;
		virtual ~ConversionResultPlacement() {}
	};
	*/

	class IFC_GEOM_API ConversionResultShape {
	public:
		virtual void Triangulate(const ifcopenshell::geometry::settings & settings, const ifcopenshell::geometry::taxonomy::matrix4& place, ifcopenshell::geometry::Representation::Triangulation* t, int surface_style_id) const = 0;

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
		ifcopenshell::geometry::taxonomy::style style;
	public:
		ConversionResult(int id, const ifcopenshell::geometry::taxonomy::matrix4& placement, const ConversionResultShape* shape, const ifcopenshell::geometry::taxonomy::style& style)
			: id(id), placement(placement), shape(shape->clone()), style(style) {}
		ConversionResult(int id, const ifcopenshell::geometry::taxonomy::matrix4& placement, const ConversionResultShape* shape)
			: id(id), placement(placement), shape(shape->clone()) {}
		ConversionResult(int id, const ConversionResultShape* shape, const ifcopenshell::geometry::taxonomy::style& style)
			: id(id), shape(shape->clone()), style(style) {}
		ConversionResult(int id, const ConversionResultShape* shape)
			: id(id), shape(shape->clone()) {}
		void append(const ifcopenshell::geometry::taxonomy::matrix4& trsf) {
			// @todo verify order
			*placement.components = *placement.components * *trsf.components;
		}
		void prepend(const ifcopenshell::geometry::taxonomy::matrix4& trsf) {
			// @todo verify order
			*placement.components = *trsf.components * *placement.components;
		}
		const ConversionResultShape* Shape() const { return shape; }
		ConversionResultShape* Shape() { return shape; }
		const ifcopenshell::geometry::taxonomy::matrix4& Placement() const { return placement; }
		// @todo
		bool hasStyle() const { return style.diffuse.is_initialized(); }
		const ifcopenshell::geometry::taxonomy::style& Style() const { return style; }
		void setStyle(const ifcopenshell::geometry::taxonomy::style& newStyle) { style = newStyle; }
		int ItemId() const { return id; }
	};
    
	typedef std::vector<ConversionResult> ConversionResults;
}}
#endif
