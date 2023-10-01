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
#define PI 3.1415926535897932384626433832795

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
> curve_seg_types;

enum segment_type_t {
	ST_HORIZONTAL, ST_VERTICAL, ST_CANT
};

class curve_segment_evaluator {
private:
	double length_unit_;
	double start_;
	double length_;
	segment_type_t segment_type_;
	IfcSchema::IfcCurve* curve_;

	std::optional<std::function<Eigen::VectorXd(double)>> eval_;

public:
	// First constructor, takes parameters from IfcCurveSegment
	curve_segment_evaluator(double length_unit, segment_type_t segment_type, IfcSchema::IfcCurve* curve, IfcSchema::IfcCurveMeasureSelect* st, IfcSchema::IfcCurveMeasureSelect* le)
		: length_unit_(length_unit)
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

// Clothoid using Taylor Series approximation
//#ifdef SCHEMA_HAS_IfcClothoid
//	// Then initialize Function(double) -> Vector3, by means of IfcCurve subtypes
//	void operator()(IfcSchema::IfcClothoid* c) {
//		// @todo verify
//		auto sign = [](double v)->int{return v < 0 ? -1 : (0 < v ? 1 : 0); };
//		auto sign_s = sign(start_);
//		auto sign_l = sign(length_);
//		double L = 0;
//		if (sign_s == 0) L = fabs(length_);
//		else if (sign_s == sign_l) L = fabs(start_ + length_);
//		else L = fabs(start_);
//
//		auto A = c->ClothoidConstant();
//		auto R = A * A / L;
//		auto RL = (A < 0 ? -1.0 : 1.0) * R * L;
//
//		auto position = c->Position();
//		auto placement = position->as<IfcSchema::IfcAxis2Placement2D>();
//		auto ref_direction = placement->RefDirection();
//		double theta = 0.0; // angle the circle's placement X-axis makes with respect to global X axis
//		if (ref_direction)
//		{
//			auto dr = ref_direction->DirectionRatios();
//			auto dx = dr[0];
//			auto dy = dr[1];
//			theta = atan2(dy, dx);
//		}
//
//		auto C = placement->Location();
//		if (!C->as<IfcSchema::IfcCartesianPoint>())
//		{
//			throw std::runtime_error("Only IfcCartesianPoint is supported for center of IfcCircle");
//			// @todo add support for other IfcPoint subtypes
//		}
//		auto Cx = C->as<IfcSchema::IfcCartesianPoint>()->Coordinates()[0];
//		auto Cy = C->as<IfcSchema::IfcCartesianPoint>()->Coordinates()[1];
//
//		eval_ = [RL,Cx,Cy,theta](double u) {
//			// coordinate along clothoid is local coordinates
//			auto xterm_1 = u;
//			auto xterm_2 = std::pow(u, 5) / (40 * std::pow(RL, 2));
//			auto xterm_3 = std::pow(u, 9) / (3456 * std::pow(RL, 4));
//			auto xterm_4 = std::pow(u, 13) / (599040 * std::pow(RL, 6));
//			auto xl = xterm_1 - xterm_2 + xterm_3 - xterm_4;
//
//			auto yterm_1 = std::pow(u, 3) / (6 * RL);
//			auto yterm_2 = std::pow(u, 7) / (336 * std::pow(RL, 3));
//			auto yterm_3 = std::pow(u, 11) / (42240 * std::pow(RL, 5));
//			auto yterm_4 = std::pow(u, 15) / (9676800 * std::pow(RL, 7));
//			auto yl = yterm_1 - yterm_2 + yterm_3 - yterm_4;
//
//			// transform point into clothoid's coodinate system
//			auto x = xl * cos(theta) - yl * sin(theta) + Cx;
//			auto y = xl * sin(theta) + yl * cos(theta) + Cy;
//			return Eigen::VectorXd(x, y, 0.0);
//		};
//	}
//#endif

	void set_spiral_functor(IfcSchema::IfcSpiral* s, std::function<double(double)> signX,std::function<double(double)> fnX, std::function<double(double)> signY, std::function<double(double)> fnY)
	{
		// determine the length of the spiral from the local origin to the end point
		auto binary_sign = [](double v)->int {return v < 0 ? -1 : (0 < v ? 1 : 0); }; // returns -1, 0, or 1
		auto sign_s = binary_sign(start_);
		auto sign_l = binary_sign(length_);
		double L = 0;
		if (sign_s == 0) L = fabs(length_); // start_ is at zero so length_ is the L
		else if (sign_s == sign_l) L = fabs(start_ + length_); // start_ and length_ are additive
		else L = fabs(start_); // start_ and length_ are in opposite directions so start_ is furthest from the origin

		auto position = s->Position();
		auto placement = position->as<IfcSchema::IfcAxis2Placement2D>(); // @todo Update, this could be IfcAxis2Placement2D or IfcAxisPlacement3D
		if (!placement) { throw std::runtime_error("Only IfcAxis2Placement2D is supported right now"); }
		auto ref_direction = placement->RefDirection();
		double theta = 0.0; // angle the circle's placement X-axis makes with respect to global X axis
		if (ref_direction)
		{
			auto dr = ref_direction->DirectionRatios();
			auto dx = dr[0];
			auto dy = dr[1];
			theta = atan2(dy, dx);
		}

		auto C = placement->Location();
		if (!C->as<IfcSchema::IfcCartesianPoint>())
		{
			throw std::runtime_error("Only IfcCartesianPoint is supported right now");
			// @todo add support for other IfcPoint subtypes
		}
		auto Cx = C->as<IfcSchema::IfcCartesianPoint>()->Coordinates()[0];
		auto Cy = C->as<IfcSchema::IfcCartesianPoint>()->Coordinates()[1];

		eval_ = [L, Cx, Cy, theta, signX, fnX, signY, fnY](double u) {
			using boost::math::quadrature::trapezoidal;

			// integration limits, integrate from a to b
			// from 8.9.3.19.1, integration limits are 0.0 to u where u is a normalized parameter
			auto a = 0.0;
			auto b = fabs(u / L);

			// @todo where to plug this in?
			// auto n = 10; // use 10 steps in the numeric integration

			auto xl = signX(u)*trapezoidal(fnX, a, b);
			auto yl = signY(u)*trapezoidal(fnY, a, b);

			// transform point into clothoid's coodinate system
			auto x = xl * cos(theta) - yl * sin(theta) + Cx;
			auto y = xl * sin(theta) + yl * cos(theta) + Cy;
			Eigen::VectorXd vec(3);
			vec << x, y, 0.0;
			return vec;
		};
	}

// Clothoid using numerical integration
#ifdef SCHEMA_HAS_IfcClothoid
// Then initialize Function(double) -> Vector3, by means of IfcCurve subtypes
	void operator()(IfcSchema::IfcClothoid* c) {

		auto A = c->ClothoidConstant();

		// the integration is for the +X, +Y quadrant - need to adjust the signs of the resulting X and Y values
		// so that the results are in the correct quadrant.
		// A > 0 and u > 0 -> +X, +Y
		// A < 0 and u > 0 -> +X, -Y
		// A > 0 and u < 0 -> -X, -Y
		// A < 0 and u < 0 -> -X, +Y
		// X depends only on u, Y depends on u and A.
		auto sign = [](double v)->int {return v < 0 ? -1 : 1; }; // returns -1 or 1
		auto sign_x = [sign](double t) {return sign(t); };
		auto sign_y = [sign, A](double t) {return sign(t) == sign(A) ? 1.0 : -1.0; };
		auto fn_x = [A](double t)->double {return A * sqrt(PI) * cos(PI * A * t * t / (2 * fabs(A))); };
		auto fn_y = [A](double t)->double {return A * sqrt(PI) * sin(PI * A * t * t / (2 * fabs(A))); };
		
		set_spiral_functor(c->as<IfcSchema::IfcSpiral>(), sign_x, fn_x, sign_y, fn_y);
	}
#endif

#ifdef SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
	void operator()(IfcSchema::IfcSecondOrderPolynomialSpiral* s)
	{
		// @todo verify - this is an example implementation of a different kind of spiral - lots of clean up needed
		auto A0 = s->ConstantTerm();
		auto A1 = s->LinearTerm();
		auto A2 = s->QuadraticTerm();

		auto theta = [A0, A1, A2](double t)
			{
				auto a0 = A0.has_value() ? t / A0.value() : 0.0;
				auto a1 = A1.has_value() ? A1.value() * std::pow(t, 2) / (2 * fabs(std::pow(A1.value(), 3))) : 0.0;
				auto a2 = std::pow(t, 3) / (3 * std::pow(A2, 3));
				return a0 + a1 + a2;
			};

		auto sign = [](double v)->int {return v < 0 ? -1 : 1; }; // returns -1 or 1
		auto sign_x = [sign](double t) {return sign(t); };
		auto sign_y = [sign](double t) {return sign(t); }; // @todo fix - not sure about sign_y yet, need to find some plots of this spiral

		auto fn_x = [theta](double t)->double {return cos(theta(t)); };
		auto fn_y = [theta](double t)->double {return sin(theta(t)); };

		set_spiral_functor(s->as<IfcSchema::IfcSpiral>(), sign_x, fn_x, sign_y, fn_y);
	}
#endif

	void operator()(IfcSchema::IfcCircle* c)
	{
		auto R = c->Radius();

		auto position = c->Position();
		auto placement = position->as<IfcSchema::IfcAxis2Placement2D>();
		auto ref_direction = placement->RefDirection();
		double theta = 0.0; // angle the circle's placement X-axis makes with respect to global X axis
		if (ref_direction)
			{
			auto dr = ref_direction->DirectionRatios();
			auto dx = dr[0];
			auto dy = dr[1];
			theta = atan2(dy, dx);
		}

		// center of circle location
		auto C = placement->Location();
		if (!C->as<IfcSchema::IfcCartesianPoint>())
		{
			throw std::runtime_error("Only IfcCartesianPoint is supported for center of IfcCircle");
			// @todo add support for other IfcPoint subtypes
		}
		auto Cx = C->as<IfcSchema::IfcCartesianPoint>()->Coordinates()[0];
		auto Cy = C->as<IfcSchema::IfcCartesianPoint>()->Coordinates()[1];

		eval_ = [R, Cx, Cy, theta](double u)
			{
				auto angle = u / R; // angle subtended by arc length u

				// compute point on circle centered at (0,0) with x-axis horizontal and y-axis vertical
				auto xl = R * cos(angle);
				auto yl = R * sin(angle);

				// transform point into circle's coodinate system
				auto x = xl * cos(theta) - yl * sin(theta) + Cx;
				auto y = xl * sin(theta) + yl * cos(theta) + Cy;
				Eigen::VectorXd vec;
				vec << x, y, 0.0;
				return vec;
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
		using Function = std::function<std::pair<double, double>(double u)>;
		std::map<Range, Function> fns;

		auto p = pl->Points();
		if (p->size() < 2)
		{
			throw std::runtime_error("invalid polyline - must have at least 2 points"); // this should never happen, but just in case it does
		}

		auto std_compare = [](double u_start, double u, double u_end) {return u_start <= u && u < u_end; };
		auto end_compare = [](double u_start, double u, double u_end) {return u_start <= u && u <= (u_end+0.001); };

		auto iter = p->begin();
		auto end = p->end();
		auto last = std::prev(end);
		auto p1 = *(iter++);
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
			if (l == 0.0)
			{
				// @todo use closeness tolerance instead of absolute 0.0
				throw std::runtime_error("invalid polyline - points must not be coincident");
			}

			dx /= l;
			dy /= l;

			auto fn = [p1x, p1y, dx, dy](double u) { return std::make_pair(p1x + u * dx, p1y + u * dy); };

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
			
			if (iter == fns.end()) throw std::runtime_error("invalid distance from start"); // this should never happen, but just in case it does
			
			auto [u_start, u_end, compare] = iter->first;
			auto [x,y] = (iter->second)(u - u_start); // (u - u_start) is distance from start of this segment of the polyline
			Eigen::VectorXd vec;
			vec << x, y, 0;
			return vec;
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
				Eigen::VectorXd vec;
				vec << x, y, 0;
				return vec;
			};

		} else if (segment_type_ == ST_VERTICAL) {
			
			eval_ = [px, py, dx, dy](double u) {
				auto z = py + u * dy;
				Eigen::VectorXd vec;
				vec << z;
				return vec;
			};

		}
	}

	// Take the boost::type value from mpl::for_each and test it against our curve instance
	template <typename T>
	void operator()(boost::type<T>) {
		if (curve_->as<T>()) {
			(*this)(curve_->as<T>());
		}
	}

	// Then, with function populated based on IfcCurve subtype, we can evaluate to points
	Eigen::VectorXd operator()(double u) {
		if (eval_) {
			return (*eval_)((u + start_) * length_unit_);
		} else {
			throw std::runtime_error(curve_->declaration().name() + " not implemented");
		}
	}

	double length() const {
		return length_;
	}

	const std::optional<std::function<Eigen::VectorXd(double)>>& evaluation_function() const {
		return eval_;
	}
};

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCurveSegment* inst) {
	// @todo figure out what to do with the zero length segments at the end of compound curves

	bool is_horizontal = false;
	bool is_vertical = false;
	bool is_cant = false;

	{
		aggregate_of_instance::ptr segment_owners = inst->data().getInverse(&IfcSchema::IfcCompositeCurve::Class(), 0);
		if (segment_owners) {
			for (auto& cc : *segment_owners) {
				if (cc->as<IfcSchema::IfcSegmentedReferenceCurve>()) {
					is_cant = true;
				} else if (cc->as<IfcSchema::IfcGradientCurve>()) {
					is_vertical = true;
				} else {
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

	curve_segment_evaluator cse(length_unit_, segment_type, inst->ParentCurve(), inst->SegmentStart(), inst->SegmentLength());
	boost::mpl::for_each<curve_seg_types, boost::type<boost::mpl::_>>(std::ref(cse));
	
	auto fn = *cse.evaluation_function();
	auto length = cse.length();
	
	// @todo - for some reason this isn't working, the matrix gets all messed up
	//const auto& transformation_matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Placement()))->ccomponents();
	auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(map(inst->Placement()))->ccomponents();

	auto fn_transformed = [fn, transformation_matrix](double u) {
		return transformation_matrix * fn(u);
	};

	// @todo it might be suboptimal that we no longer have the spans now
	auto pwf = taxonomy::make<taxonomy::piecewise_function>();
	pwf->spans.push_back({ length, fn_transformed });
	return pwf;

	/*
	static int NUM_SEGMENTS = 64;
	std::vector<taxonomy::point3::ptr> polygon;

	auto length = cse.length();
	if (0.001 < fabs(length))
	{
		for (int i = 0; i <= NUM_SEGMENTS; ++i) {
			auto u = length * i / NUM_SEGMENTS;
		
			auto p = cse(u);
			auto result =  transformation_matrix * Eigen::Vector4d(p(0),p(1),p(2), 1.);
			polygon.push_back(taxonomy::make<taxonomy::point3>(result(0),result(1),result(2)));
		}
	}

	return polygon_from_points(polygon);
	*/
}

#endif