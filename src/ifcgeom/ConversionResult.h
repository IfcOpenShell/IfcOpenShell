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
#include "../ifcgeom/IfcGeomIteratorSettings.h"

namespace IfcGeom {

	namespace Representation {
		template <typename P>
		class IFC_GEOM_API Triangulation;
	}

	class IFC_GEOM_API ConversionResultPlacement {
	public:
		virtual void Multiply(const ConversionResultPlacement*) = 0;
		virtual void PreMultiply(const ConversionResultPlacement*) = 0;
		virtual double Value(int i, int j) const = 0;
		virtual ConversionResultPlacement* clone() const = 0;
		virtual ~ConversionResultPlacement() {}
	};

	class IFC_GEOM_API ConversionResultShape {
	public:
		virtual void Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement* place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const = 0;
		virtual void Serialize(std::string&) const = 0;
		virtual ConversionResultShape* clone() const = 0;
		virtual ~ConversionResultShape() {}
	};

	class IFC_GEOM_API ConversionResult {
	private:
		ConversionResultPlacement* placement;
		ConversionResultShape* shape;
		const SurfaceStyle* style;
	public:
		ConversionResult(const ConversionResultPlacement* placement, const ConversionResultShape* shape, const SurfaceStyle* style)
			: placement(placement->clone()), shape(shape->clone()), style(style) {}
		ConversionResult(const ConversionResultPlacement* placement, const ConversionResultShape* shape)
			: placement(placement->clone()), shape(shape->clone()), style(0) {}
		ConversionResult(const ConversionResultShape* shape, const SurfaceStyle* style)
			: placement(0), shape(shape->clone()), style(style) {}
		ConversionResult(const ConversionResultShape* shape)
			: placement(0), shape(shape->clone()), style(0) {}
		void append(const ConversionResultPlacement* trsf) {
			if (placement == 0) {
				placement = trsf->clone();
			} else {
				placement->Multiply(trsf); 
			}
		}
		void prepend(const ConversionResultPlacement* trsf) {
			if (placement == 0) {
				placement = trsf->clone();
			} else {
				placement->PreMultiply(trsf);
			}
		}
		const ConversionResultShape* Shape() const { return shape; }
		const ConversionResultPlacement* Placement() const { return placement; }
		bool hasStyle() const { return style != 0; }
		const SurfaceStyle& Style() const { return *style; }
		void setStyle(const SurfaceStyle* style) { this->style = style; }
	};
    
	typedef std::vector<ConversionResult> ConversionResults;
}
#endif
