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

#ifndef CGALCONVERSIONRESULT_H
#define CGALCONVERSIONRESULT_H

#include "../../../ifcgeom/schema_agnostic/ConversionResult.h"

namespace IfcGeom {

    class CgalPlacement : public ConversionResultPlacement {
    public:
        CgalPlacement(const cgal_placement_t& trsf)
            : trsf_(trsf)
        {}

        const cgal_placement_t& trsf() const { return trsf_; }
		operator const cgal_placement_t& () { return trsf_; }
		
		virtual double Value(int i, int j) const {
			// Get cell from placement as 4x3 matrix as implemented in OCCT. We'll have to check exact semantics.
			throw std::runtime_error("Not implemented");
		}

		virtual void Multiply(const ConversionResultPlacement* other) {
			// Multiply matrix as implemented in OCCT. We'll have to check exact semantics.
			throw std::runtime_error("Not implemented");
		}

		virtual void PreMultiply(const ConversionResultPlacement* other) {
			// PreMultiply matrix as implemented in OCCT. We'll have to check exact semantics.
			throw std::runtime_error("Not implemented");
		}

		virtual ConversionResultPlacement* clone() const {
			return new CgalPlacement(trsf_);
		}

		virtual ConversionResultPlacement* inverted() const {
			throw std::runtime_error("Not implemented");
		}

		virtual ConversionResultPlacement* multiplied(const ConversionResultPlacement*) const {
			throw std::runtime_error("Not implemented");
		}
    private:
        cgal_placement_t trsf_;
    };
    
    class CgalShape : public ConversionResultShape {
    public:
        CgalShape(const cgal_shape_t& shape)
            : shape_(shape)
        {}

		const cgal_shape_t& shape() const { return shape_; }
		operator const cgal_shape_t& () { return shape_; }

		virtual void Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<float> * t, int surface_style_id) const;
		
		virtual void Triangulate(const IfcGeom::IteratorSettings & settings, const IfcGeom::ConversionResultPlacement * place, IfcGeom::Representation::Triangulation<double>* t, int surface_style_id) const;
		
		virtual void Serialize(std::string&) const {
			throw std::runtime_error("Not implemented");
		}

		virtual ConversionResultShape* clone() const {
			return new CgalShape(shape_);
		}

		virtual int surface_genus() const {
			throw std::runtime_error("Not implemented");
		}
    private:
        cgal_shape_t shape_;
	};
    
}

#endif