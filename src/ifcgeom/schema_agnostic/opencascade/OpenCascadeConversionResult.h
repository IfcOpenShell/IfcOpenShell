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

#ifndef IFCGEOMOPENCASCADEREPRESENTATION_H
#define IFCGEOMOPENCASCADEREPRESENTATION_H

#include <BRepMesh_IncrementalMesh.hxx>
#include <BRepGProp_Face.hxx>

#include <Poly_Triangulation.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColgp_Array1OfPnt2d.hxx>

#include <TopExp_Explorer.hxx>
#include <BRepTools.hxx>

#include <gp_GTrsf.hxx>
#include <BRepAdaptor_Curve.hxx>
#include <GCPnts_QuasiUniformDeflection.hxx>

#include "../../../ifcgeom/schema_agnostic/ConversionResult.h"

namespace ifcopenshell {
	namespace geometry {

		class OpenCascadePlacement : public ConversionResultPlacement {
		public:
			OpenCascadePlacement(const gp_GTrsf& trsf)
				: trsf_(trsf) {}

			const gp_GTrsf& trsf() const { return trsf_; }
			operator const gp_GTrsf& () { return trsf_; }

			virtual double Value(int i, int j) const {
				return trsf_.Value(i, j);
			}

			virtual void Multiply(const ConversionResultPlacement* other) {
				trsf_.Multiply(((OpenCascadePlacement*)other)->trsf_);
			}

			virtual void PreMultiply(const ConversionResultPlacement* other) {
				trsf_.PreMultiply(((OpenCascadePlacement*)other)->trsf_);
			}

			virtual ConversionResultPlacement* clone() const {
				return new OpenCascadePlacement(trsf_);
			}

			virtual ConversionResultPlacement* inverted() const {
				return new OpenCascadePlacement(trsf_.Inverted());
			}

			virtual ConversionResultPlacement* multiplied(const ConversionResultPlacement* other) const {
				return new OpenCascadePlacement(trsf_.Multiplied(((OpenCascadePlacement*)other)->trsf_));
			}

			virtual void TranslationPart(double& X, double& Y, double& Z) const {
				X = trsf_.TranslationPart().X();
				Y = trsf_.TranslationPart().Y();
				Z = trsf_.TranslationPart().Z();
			}
		private:
			gp_GTrsf trsf_;
		};

		class OpenCascadeShape : public ConversionResultShape {
		public:
			OpenCascadeShape(const TopoDS_Shape& shape)
				: shape_(shape) {}

			const TopoDS_Shape& shape() const { return shape_; }
			operator const TopoDS_Shape& () { return shape_; }

			virtual void Triangulate(const settings & settings, const ConversionResultPlacement * place, Representation::Triangulation* t, int surface_style_id) const;

			virtual void Serialize(std::string&) const {
				throw std::runtime_error("Not implemented");
			}

			virtual ConversionResultShape* clone() const {
				return new OpenCascadeShape(shape_);
			}

			virtual int surface_genus() const;
		private:
			TopoDS_Shape shape_;
		};

	}
}

#endif