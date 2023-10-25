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

#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

#ifdef SCHEMA_HAS_IfcCurveSegment

#include "../profile_helper.h"

#include <boost/mpl/vector.hpp>
#include <boost/mpl/for_each.hpp>
#include <boost/math/quadrature/trapezoidal.hpp>

// @todo use std::numbers::pi when upgrading to C++ 20
static const double PI = boost::math::constants::pi<double>();

namespace {
// @todo: rb is there a common math library these functions can be moved to?
auto sign = [](double v) -> int { return v < 0 ? -1 : 1; };                      // returns -1 or 1
auto binary_sign = [](double v) -> int { return v < 0 ? -1 : (0 < v ? 1 : 0); }; // returns -1, 0, or 1
} // namespace

typedef boost::mpl::vector<
	IfcSchema::IfcLine
#ifdef SCHEMA_HAS_IfcClothoid
	, IfcSchema::IfcClothoid
#endif
#if defined SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
	, IfcSchema::IfcSecondOrderPolynomialSpiral
#endif
	, IfcSchema::IfcPolyline
	, IfcSchema::IfcCircle
	, IfcSchema::IfcPolynomialCurve
> curve_seg_types;

enum segment_type_t {
	ST_HORIZONTAL, ST_VERTICAL, ST_CANT
};

class curve_segment_evaluator {
private:
	mapping* mapping_;
	double length_unit_;
	double start_;
	double length_;
	segment_type_t segment_type_;
	IfcSchema::IfcCurve* curve_;

	std::optional<std::function<Eigen::Matrix4d(double)>> eval_;

public:
	// First constructor, takes parameters from IfcCurveSegment
	curve_segment_evaluator(mapping* mapping,double length_unit, segment_type_t segment_type, IfcSchema::IfcCurve* curve, IfcSchema::IfcCurveMeasureSelect* st, IfcSchema::IfcCurveMeasureSelect* le)
		: mapping_(mapping)
		, length_unit_(length_unit)
		, segment_type_(segment_type)
		, curve_(curve)
	{
		// @todo in IFC4X3_ADD2 this needs to be length measure

		if (!st->as<IfcSchema::IfcLengthMeasure>() || !le->as<IfcSchema::IfcLengthMeasure>()) {
			// @nb Parameter values are forbidden in the specification until parametrization is provided for all spirals
			throw std::runtime_error("Unsupported curve measure type");
		}

		start_ = *st->as<IfcSchema::IfcLengthMeasure>() * length_unit;
		length_ = *le->as<IfcSchema::IfcLengthMeasure>() * length_unit;
	}

	void set_spiral_functor(mapping* mapping_,IfcSchema::IfcSpiral* c, double s, std::function<double(double)> signX, std::function<double(double)> fnX, std::function<double(double)> signY, std::function<double(double)> fnY)
	{
		// determine the length of the spiral from the local origin to the end point
		auto sign_s = binary_sign(start_);
		auto sign_l = binary_sign(length_);
		double L = 0;
		if (sign_s == 0) L = fabs(length_); // start_ is at zero so length_ is the L
		else if (sign_s == sign_l) L = fabs(start_ + length_); // start_ and length_ are additive
		else L = fabs(start_); // start_ and length_ are in opposite directions so start_ is furthest from the origin

		auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();

		auto segment_type = segment_type_;
		auto start = start_;

        eval_ = [L, start, s, signX, fnX, signY, fnY, transformation_matrix, segment_type](double u) {
				using boost::math::quadrature::trapezoidal;

				u += start;

				// integration limits, integrate from a to b
				auto a = 0.0;
				auto b = fabs(u / s);

				auto x = signX(u) * trapezoidal(fnX, a, b);
				auto y = signY(u) * trapezoidal(fnY, a, b);

				// From https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcSpiral.htm, x = Integral(fnX du), y = Integral(fnY du)
				// The tangent slope of a curve is the derivate of the curve, so the derivitive of an integral, is just the function
				// Therefore, Dx/Du = fnX(u) and Dy/Du = fnY(u) which leads to du = Dx/fnX(u) and Dy = fnY(u)*Du = fnY(u)*Dx/fnX(u) so Dy/Dx = fnY(u)/fnX(u)
				// However, Dx and Dy are not normalized. Recall that slope = rise/run
				// If run = 1.0, then rise = Dy/Dx = fnY(u)/fnX(u) and l = sqrt((fnY(u)/fnX(u))^2 + 1.0^2)
				// The direction ratios are dx = 1.0/l and dy = (fnY/fnX)/l;
            auto rise = fnY(u) / fnX(u);
            auto run = 1.0;
            auto l = sqrt(run * run + rise * rise);
            auto dx = run / l;
            auto dy = rise / l;

            Eigen::Matrix4d m;
            if (segment_type == ST_HORIZONTAL) {
                // rotate about the Z-axis
                m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
                m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
                m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
                m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
            } else if (segment_type == ST_VERTICAL) {
                // rotate about the Y-axis (slope along u is dx, slope vertically is dy, vertical position is y)
                m.col(0) = Eigen::Vector4d(dx, 0, dy, 0);
                m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
                m.col(2) = Eigen::Vector4d(-dy, 0, dx, 0);
                m.col(3) = Eigen::Vector4d(0, 0, y, 1.0); // y is an elevation so store it as z
            } else if (segment_type == ST_CANT) {
                Logger::Warning(std::runtime_error("Use of IfcSpiral for cant is not supported"));
            } else {
                Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            }


				Eigen::Matrix4d result = transformation_matrix * m;
            return result;
			};
	}


	// Clothoid using Taylor Series approximation
//#ifdef SCHEMA_HAS_IfcClothoid
//	// Then initialize Function(double) -> Vector3, by means of IfcCurve subtypes
//	void operator()(IfcSchema::IfcClothoid* c) {
//		auto sign_s = binary_sign(start_);
//		auto sign_l = binary_sign(length_);
//		double L = 0;
//		if (sign_s == 0) L = fabs(length_);
//		else if (sign_s == sign_l) L = fabs(start_ + length_);
//		else L = fabs(start_);
//
//		auto A = c->ClothoidConstant();
//		auto R = A * A / L;
//		auto RL = sign(A) * R * L;
//
//		//const auto& transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();
//		auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();
//
//		auto start = start_;
//		eval_ = [RL, transformation_matrix, start](double u) {
//			// coordinate along clothoid is local coordinates
//			u += start;
//
//			auto xterm_1 = u;
//			auto xterm_2 = std::pow(u, 5) / (40 * std::pow(RL, 2));
//			auto xterm_3 = std::pow(u, 9) / (3456 * std::pow(RL, 4));
//			auto xterm_4 = std::pow(u, 13) / (599040 * std::pow(RL, 6));
//			auto x = xterm_1 - xterm_2 + xterm_3 - xterm_4;
//
//			auto yterm_1 = std::pow(u, 3) / (6 * RL);
//			auto yterm_2 = std::pow(u, 7) / (336 * std::pow(RL, 3));
//			auto yterm_3 = std::pow(u, 11) / (42240 * std::pow(RL, 5));
//			auto yterm_4 = std::pow(u, 15) / (9676800 * std::pow(RL, 7));
//			auto y = yterm_1 - yterm_2 + yterm_3 - yterm_4;
//
//			// transform point into clothoid's coodinate system
//			auto result = transformation_matrix * Eigen::Vector4d(x, y, 0.0, 1.0);
//			Eigen::VectorXd vec(4);
//			vec << result(0), result(1), 0.0, 1.0;
//			return vec;			
//			};
//	}
//#endif

	// Clothoid using numerical integration
#ifdef SCHEMA_HAS_IfcClothoid
// Then initialize Function(double) -> Vector3, by means of IfcCurve subtypes
	void operator()(IfcSchema::IfcClothoid* c) {
		// see https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcClothoid.htm
		// also see, https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Clothoid_Transition_Segment/content.html,
		// which defines the clothoid constant as sqrt(L) and L is the length measured from the inflection point
		auto A = c->ClothoidConstant();
      auto s = fabs(A * sqrt(PI));

		// the integration is for the +X, +Y quadrant - need to adjust the signs of the resulting X and Y values
		// so that the results are in the correct quadrant.
		// A > 0 and u > 0 -> +X, +Y
		// A < 0 and u > 0 -> +X, -Y
		// A > 0 and u < 0 -> -X, -Y
		// A < 0 and u < 0 -> -X, +Y
		// X depends only on u, Y depends on u and A.
		auto sign_x = [](double t) {return sign(t); };
		auto sign_y = [A](double t) {return sign(t) == sign(A) ? 1.0 : -1.0; };
		auto fn_x = [A,s](double t)->double {return s * cos(PI * fabs(A) * t * t / (2 * fabs(A))); };
		auto fn_y = [A,s](double t)->double {return s * sin(PI * fabs(A) * t * t / (2 * fabs(A))); };

		set_spiral_functor(mapping_, c, s, sign_x, fn_x, sign_y, fn_y);
	}
#endif

#ifdef SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
	void operator()(IfcSchema::IfcSecondOrderPolynomialSpiral* c)
	{
		// @todo: rb verify - this is an example implementation of a different kind of spiral - lots of clean up needed
		auto A0 = c->ConstantTerm();
		auto A1 = c->LinearTerm();
		auto A2 = c->QuadraticTerm();

		auto theta = [A0, A1, A2](double t)
			{
				auto a0 = A0.has_value() ? t / A0.value() : 0.0;
				auto a1 = A1.has_value() ? A1.value() * std::pow(t, 2) / (2 * fabs(std::pow(A1.value(), 3))) : 0.0;
				auto a2 = std::pow(t, 3) / (3 * std::pow(A2, 3));
				return a0 + a1 + a2;
			};

		auto sign_x = [](double t) {return sign(t); };
		auto sign_y = [](double t) {return sign(t); }; // @todo: rb - fix - not sure about sign_y yet, need to find some plots of this spiral

		auto fn_x = [theta](double t)->double {return cos(theta(t)); };
		auto fn_y = [theta](double t)->double {return sin(theta(t)); };

		double s = 1.0; // @todo: rb - this is supposed to be the curve length when the parametric value u = 1.0
		set_spiral_functor(mapping_, c, s, sign_x, fn_x, sign_y, fn_y);
	}
#endif

	void operator()(IfcSchema::IfcCircle* c)
	{
		auto R = c->Radius();

      auto sign_l = sign(length_);
		auto start = start_;

		//const auto& transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();
		auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();

		auto segment_type = segment_type_;

		eval_ = [R, start, sign_l, transformation_matrix, segment_type](double u)
			{
				auto angle = start + sign_l * u / R;

				auto dx = cos(angle);
            auto dy = sin(angle);

				auto x = R * dx;
				auto y = R * dy;

            Eigen::Matrix4d m;
            if (segment_type == ST_HORIZONTAL) {
                // rotate about the Z-axis
                m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
                m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
                m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
                m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
            } else if (segment_type == ST_VERTICAL) {
                // rotate about the Y-axis (slope along u is dx, slope vertically is dy, vertical position is y)
                m.col(0) = Eigen::Vector4d(dx, 0, dy, 0);
                m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
                m.col(2) = Eigen::Vector4d(-dy, 0, dx, 0);
                m.col(3) = Eigen::Vector4d(0, 0, y, 1.0); // y is an elevation so store it as z
            } else if (segment_type == ST_CANT) {
                Logger::Warning(std::runtime_error("Use of IfcCircle for cant is not supported"));
            } else {
                Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            }


            Eigen::Matrix4d result = transformation_matrix * m;
            return result;
			};
	}

	void operator()(IfcSchema::IfcPolyline* pl)
	{
		struct Range
		{
			double u_start;
			double u_end;
			std::function<bool(double, double, double)> compare;
			bool operator<(const Range& r) const { return u_start < r.u_start; }
		};

		using Function = std::function<Eigen::Matrix4d(double u)>;
		std::map<Range, Function> fns;

		auto p = pl->Points();
		if (p->size() < 2)
		{
			throw std::runtime_error("invalid polyline - must have at least 2 points"); // this should never happen, but just in case it does
		}

		auto std_compare = [](double u_start, double u, double u_end) {return u_start <= u && u < u_end; };
		auto end_compare = [](double u_start, double u, double u_end) {return u_start <= u && u <= (u_end + 0.001); };

		auto begin = p->begin();
		auto iter = begin;
		auto end = p->end();
		auto last = std::prev(end);
		auto p1 = *(iter++);
      
		if (p1->Coordinates().size() != 2)  Logger::Warning("Expected IfcPolyline.Points to be 2D",pl);
      
		auto u = 0.0;
		for (; iter != end; iter++)
		{
			auto p2 = *iter;

			auto p1x = p1->Coordinates()[0];
			auto p1y = p1->Coordinates()[1];

			auto p2x = p2->Coordinates()[0];
			auto p2y = p2->Coordinates()[1];

			auto dx = p2x - p1x;
			auto dy = p2y - p1y;
			auto l = sqrt(dx * dx + dy * dy);
					
			if (l < mapping_->conversion_settings().getValue(ConversionSettings::GV_PRECISION))
			{
            std::ostringstream os;
            os << "Coincident IfcPolyline.Points are not expected. Skipping point " << std::distance(iter, begin) << std::endl;
            Logger::Warning(os.str(), pl);
            continue; // go to next point
			}

			dx /= l;
			dy /= l;

   		auto segment_type = segment_type_;

         auto fn = [p1x, p1y, dx, dy, segment_type](double u) {
                auto x = segment_type == ST_HORIZONTAL ? p1x + u * dx : u;
                auto y = p1y + u * dy;

                Eigen::Matrix4d m;
                if (segment_type == ST_HORIZONTAL) {
                    // rotate about the Z-axis
                    m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
                    m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
                    m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
                    m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
                } else if (segment_type == ST_VERTICAL) {
                    // rotate about the Y-axis (slope along u is dx, slope vertically is dy, vertical position is y)
                    m.col(0) = Eigen::Vector4d(dx, 0, dy, 0);
                    m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
                    m.col(2) = Eigen::Vector4d(-dy, 0, dx, 0);
                    m.col(3) = Eigen::Vector4d(0, 0, y, 1.0); // y is an elevation so store it as z
                } else if (segment_type == ST_CANT) {
                  Logger::Warning(std::runtime_error("Use of IfcPolyline for cant is not supported"));
                } else {
                  Logger::Error(std::runtime_error("Unexpected segment type encountered"));
                }

					 return m;
				};

			fns.insert(std::make_pair(Range{ u, u + l,iter == last ? end_compare : std_compare }, fn));

			p1 = p2;
			u = u + l;
		}

		eval_ = [fns](double u) {
			auto iter = std::find_if(fns.cbegin(), fns.cend(), [=](const auto& fn)
				{
					auto [u_start, u_end, compare] = fn.first;
					return compare(u_start, u, u_end);
				});

			if (iter == fns.end()) throw std::runtime_error("invalid distance from start"); // this should never happen, but just in case it does, throw an exception so the problem gets automatically detected

			const auto& [u_start, u_end, compare] = iter->first;
         const auto& fn = iter->second;
			Eigen::Matrix4d m = fn(u - u_start); // (u - u_start) is distance from start of this segment of the polyline
         return m;
			};
	}

	void operator()(IfcSchema::IfcLine* l) {
		auto s = l->Pnt();
		auto c = s->Coordinates();
		auto v = l->Dir();
		auto dr = v->Orientation()->DirectionRatios();
		auto m = v->Magnitude();
		auto px = c[0];
		auto py = c[1];
		auto dx = dr[0] / m;
		auto dy = dr[1] / m;

		if (segment_type_ == ST_HORIZONTAL) {

			eval_ = [px, py, dx, dy](double u) {
				auto x = px + u * dx;
				auto y = py + u * dy;

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0); // vector tangent to the curve, in the direction of the curve
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
            m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
            m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
            return m;
				};

		}
		else if (segment_type_ == ST_VERTICAL) {

			eval_ = [px, py, dx, dy](double u) {
				// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcGradientCurve.htm
				// the parameter, u, is the parameter of the BaseCurve (u = plan view distance along base curve)
            
				// dx and dy are normalized so u needs to be scaled by dy/dx
				// Consider a 5% uphill grade defined by dr[0] = 1 and dr[1] = 0.05.
				// We would normally compute y = py + 0.05*u. 
				// However, m = sqrt(1*1 + 0.05*.0.05) = 1.0124922 we need to normalize the direction ratios as
				// dx = dr[0]/m and dy = dr[1]/m which makes dy = 0.05/1.0124922 = 0.0499376
				// y = py + u * dy/dx =  py + u * (dr[1]/m)*(m/dr[0]) = py + u * 0.05
				auto y = py + u * dy/dx; 

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, 0, dy, 0);
            m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
            m.col(2) = Eigen::Vector4d(-dy, 0, dx, 0);
            m.col(3) = Eigen::Vector4d(0, 0, y, 1.0); // y is an elevation so store it as z
            return m;
            };
		} 
		else if(segment_type_ == ST_CANT) {
         Logger::Warning(std::runtime_error("Use of IfcLine for cant is not supported"), l);
		}
		else {
         Logger::Error(std::runtime_error("Unexpected segment type encountered"), l);
		}
	}

	void operator()(IfcSchema::IfcPolynomialCurve* p) {
		// see https://forums.buildingsmart.org/t/ifcpolynomialcurve-clarification/4716 for discussion on IfcPolynomialCurve
		auto coeffX = p->CoefficientsX().get_value_or(std::vector<double>());
      auto coeffY = p->CoefficientsY().get_value_or(std::vector<double>());
      auto coeffZ = p->CoefficientsZ().get_value_or(std::vector<double>());
      if (!coeffZ.empty())
      Logger::Warning("Expected IfcPolynomialCurve.CoefficientsZ to be undefined for alignment geometry", p);

		auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(p->Position()))->ccomponents();

		auto segment_type = segment_type_;

      eval_ = [coeffX, coeffY, coeffZ,transformation_matrix,segment_type](double u) {
         std::array<const std::vector<double>*, 3> coefficients{&coeffX, &coeffY, &coeffZ};
         std::array<double, 3> position{0.0, 0.0, 0.0}; // @todo: rb, use Eigen::VectorXd - I'm sure there is a way to do this with Eigen, but this is what I know
         std::array<double, 3> slope{0.0, 0.0, 0.0}; // slope is derivative of the curve = SUM( coeff*pos*u^(pos-1) )
         for (int i = 0; i < 3; i++) {
             auto begin = coefficients[i]->cbegin();
             auto end = coefficients[i]->cend();
               for (auto iter = begin; iter != end; iter++) {
                  auto exp = std::distance(begin, iter);
                  position[i] += (*iter) * pow(u, exp);

						if (iter != begin) {
                      slope[i] += (*iter) * exp * pow(u, exp - 1);
                  }
               }
         }

			auto x = position[0];
         auto y = position[1];
         //auto z = position[2];

			auto dx = slope[0];
         auto dy = slope[1];
         //auto dz = slope[2];

         Eigen::Matrix4d m;
         if (segment_type == ST_HORIZONTAL) {
				// rotate about the Z-axis
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
            m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
            m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
         } else if (segment_type == ST_VERTICAL) {
				// rotate about the Y-axis (slope along u is dx, slope vertically is dy, vertical position is y)
            m.col(0) = Eigen::Vector4d(dx, 0, -dy, 0);
            m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
            m.col(2) = Eigen::Vector4d(dy, 0, dx, 0);
            m.col(3) = Eigen::Vector4d(0, 0, y, 1.0); // y is an elevation so store it as z
         } else if (segment_type == ST_CANT) {
                Logger::Warning(std::runtime_error("Use of IfcPolynomialCurve for cant is not supported"));
         } else {
                Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            }

			return m;
      };
	}

	// Take the boost::type value from mpl::for_each and test it against our curve instance
	template <typename T>
	void operator()(boost::type<T>) {
		if (curve_->as<T>()) {
			(*this)(curve_->as<T>());
		}
	}

	double length() const {
		return length_;
	}

	const std::optional<std::function<Eigen::Matrix4d(double)>>& evaluation_function() const {
		return eval_;
	}
};

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCurveSegment* inst) {
	// @todo: rb figure out what to do with the zero length segments at the end of compound curves

	bool is_horizontal = false;
	bool is_vertical = false;
	bool is_cant = false;

	{
		aggregate_of_instance::ptr segment_owners = inst->data().getInverse(&IfcSchema::IfcCompositeCurve::Class(), 0);
		if (segment_owners) {
			for (auto& cc : *segment_owners) {
				if (cc->as<IfcSchema::IfcSegmentedReferenceCurve>()) {
					is_cant = true;
				}
				else if (cc->as<IfcSchema::IfcGradientCurve>()) {
					is_vertical = true;
				}
				else {
					is_horizontal = true;
				}
			}
		}
	}

	if ((is_horizontal + is_vertical + is_cant) != 1) {
		// We have to choose the correct functor based on usage. We can't 
		// support multiple, because we don't know the caller at this point.
		return nullptr;
	}

	auto segment_type = is_horizontal ? ST_HORIZONTAL : is_vertical ? ST_VERTICAL : ST_CANT;

	curve_segment_evaluator cse(this,length_unit_, segment_type, inst->ParentCurve(), inst->SegmentStart(), inst->SegmentLength());
	boost::mpl::for_each<curve_seg_types, boost::type<boost::mpl::_>>(std::ref(cse));
	
	auto& eval_fn = cse.evaluation_function();
	if(!eval_fn) throw std::runtime_error(inst->ParentCurve()->declaration().name() + " not implemented");
	auto fn = *eval_fn;
	auto length = fabs(cse.length());

	auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Placement()))->ccomponents();

	auto fn_transformed = [fn, transformation_matrix](double u)->Eigen::Matrix4d {
        Eigen::Matrix4d f = fn(u);
        Eigen::Matrix4d result = transformation_matrix * f;
        return result;
		};

	// @todo it might be suboptimal that we no longer have the spans now
	auto pwf = taxonomy::make<taxonomy::piecewise_function>();
	pwf->spans.push_back({ length, fn_transformed });
	pwf->instance = inst;
	return pwf;
}

#endif