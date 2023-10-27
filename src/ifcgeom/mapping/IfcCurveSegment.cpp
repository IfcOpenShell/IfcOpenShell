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

namespace {
// @todo: rb is there a common math library these functions can be moved to?
auto sign = [](double v) -> int { return v < 0 ? -1 : 1; };                      // returns -1 or 1
auto binary_sign = [](double v) -> int { return v < 0 ? -1 : (0 < v ? 1 : 0); }; // returns -1, 0, or 1

// @todo change the calculation at end of this to std::lerp when upgrading to C++ 20
auto interpolate = [](double u, double a, double b, double l) -> double { return l == 0.0 ? 0.0 : u * (b - a) / l; };
} // namespace


// @todo use std::numbers::pi when upgrading to C++ 20
static const double PI = boost::math::constants::pi<double>();

// Current implementation uses the same segment_geometry_adjuster for all ParentCurve types.
// Comment/Uncomment to change the type of segment geometry adjuster
// Future implementations could use specialized adjusters based on ParentCurve type
//#define GEOMETRY_ADJUSTER segment_geometry_adjuster
#define GEOMETRY_ADJUSTER linear_segment_geometry_adjuster
 
// Curve segments are evaluated using a parametric function over the curve length, u
// IfcCurveSegment.TransitionCode defines how the end of a segment connects to the next segment.
// When segments are continuously joined, the placement at u = length should be equal to the placement at u = 0
// of the next segment. However, numerical errors can cause these two points to be slightly offset
// from one another (the tangents could be slightly different as well). 
// 
// The sources of these numerical errors include geometric approximations (series expansion versus integration 
// for spiral curves), the IfcCurveSegment.SegmentStart or .SegmentLength parameters contain roundoff or
// truncation error, minor errors in placement at the start of a segment can magnify error at the end
// of the segment. There are probably others as well.
// 
// The evaluation of the relative location of the end and start points of adjacent segments occurs
// after the IfcCurveSegment.Placement is applied to the ParentCurve. The ParentCurve can be defined in
// a convenient coordinate system, such as the center of a circle or the origin of a line at (0,0). The Placement
// them moves the computed geometry to its relative position. It is the geometry after applying the Placement
// that needs to be evaluated and any difference forms the bases for the adjustments made by segment_geometry_adjuster
// or one of its subclasses.
//
// This class applies the IfcCurveSegment.Placement to inst_. The placement at the start of next_inst_ can then be
// obtained from mapping->map and compared to the end placement of inst_ and the placement at u can be adjusted
// as needed. This default implementation doesn't make any adjustments. Subclass and override the transform_and_adjust
// function to specialize the refinement of the placement at u.
class segment_geometry_adjuster {
  public:
    segment_geometry_adjuster(mapping* mapping, const IfcSchema::IfcCurveSegment* inst, const IfcSchema::IfcCurveSegment* next_inst) : 
       end_of_inst_(Eigen::Matrix4d::Identity()),
       start_of_next_inst_(Eigen::Matrix4d::Identity()),
       transition_code_(inst->Transition())
    {

        transformation_matrix_ = taxonomy::cast<taxonomy::matrix4>(mapping->map(inst->Placement()))->ccomponents();
        length_ = fabs(*inst->SegmentLength()->as<IfcSchema::IfcLengthMeasure>() * mapping->get_length_unit());

       if (next_inst) {
          // if there is a next segment, get the coordinates at the start.
          // Note that mapping->map(next_inst) causes mapping to occur recursively 
          // through all of the curve segments until the end of curve is reached.
          // Mapping of IfcCompositeCurve, IfcGradientCurve, and IfcSegmentedReferenceCurve may
          // need to traverse the IfcCurveSegment objects in reverse order to avoid recursion.
			 auto next = taxonomy::cast<taxonomy::piecewise_function>(mapping->map(next_inst));
          start_of_next_inst_ = next->evaluate(0.0);
       }
    }

    // To determine the geometry adjustments the curve segment needs to be evaluated
    // without adjustments. This function toggles the application of geometry adjustments
    void enable_adjustments(bool adjustments) { adjustments_ = adjustments; }

    // This object doesn't have access to the eval_ property of the curve_segment_evaluator.
    // The end point of the segment being adjusted, without adjustments, is computed externally
    // and provided to the curve_segment_adjustor through this method
    void set_segment_end_point(const Eigen::Matrix4d& end_of_inst) {
       end_of_inst_ = end_of_inst;
    }

    // Transforms the ParentCurve geometry with the IfcCurveSegment.Placement and
    // applies geometric adjustments to the geometry, if enabled
	 Eigen::Matrix4d transform_and_adjust(double u, const Eigen::Matrix4d& parent_curve_point) const {
       // transform the parent curve's value into the segment curve's coordinate system
       Eigen::Matrix4d segment_curve_point = transformation_matrix_ * parent_curve_point;
       if (adjustments_) {
          apply_adjustments(u, segment_curve_point);
       }
       return segment_curve_point;
    }

	 protected:
       // Applies geometric adjustment to the segment curve point evaluated at u
       // This default implementation does nothing
    virtual void apply_adjustments(double u, Eigen::Matrix4d& p) const { /* do nothing - override in subclass if needed */ }

    const Eigen::Matrix4d& get_end_of_segment() const { return end_of_inst_;  }
    const Eigen::Matrix4d& get_start_of_next_segment() const { return start_of_next_inst_; }
    IfcSchema::IfcTransitionCode::Value get_transition_code() const { return transition_code_; }
    double get_length() const { return length_; }

    private:
    bool adjustments_ = true;
    Eigen::Matrix4d transformation_matrix_;
    Eigen::Matrix4d end_of_inst_;
    Eigen::Matrix4d start_of_next_inst_;
    double length_;
    IfcSchema::IfcTransitionCode::Value transition_code_;
};

// This class refines the geometric adjustment along the segment by dividing the
// difference between the segment end point and the start point of the next segment 
// into equal adjustments and applying the incremental adjustment to each position at u
class linear_segment_geometry_adjuster : public segment_geometry_adjuster {
  public:
    using segment_geometry_adjuster::segment_geometry_adjuster;

	 virtual void apply_adjustments(double u, Eigen::Matrix4d& p) const override {
       // make the adjustments based on the transition code
       // all segments must connect end to end except for last segment IfcTransitionCode_DISCONTINUOUS for open curve
       auto transition_code = get_transition_code();
       if (transition_code == IfcSchema::IfcTransitionCode::IfcTransitionCode_DISCONTINUOUS)
          return;

       const auto& end_this = get_end_of_segment();
       const auto& start_next = get_start_of_next_segment();
       auto xe = end_this.col(3)(0);
       auto ye = end_this.col(3)(1);
       auto xs = start_next.col(3)(0);
       auto ys = start_next.col(3)(1);
       auto length = get_length();
       auto x = interpolate(u,xe,xs,length);
       auto y = interpolate(u,ye,ys,length);

       p.col(3)(0) += x;
       p.col(3)(1) += y;

       if (transition_code == IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT or
           transition_code == IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENTSAMECURVATURE) {

          for (int i = 0; i < 2; i++) {
              auto dxe = end_this.col(i)(0);
              auto dye = end_this.col(i)(1);
              auto dxs = start_next.col(i)(0);
              auto dys = start_next.col(i)(1);
              auto dx = interpolate(u,dxe,dxs,length);
              auto dy = interpolate(u,dye,dys,length);
              p.col(i)(0) += dx;
              p.col(i)(1) += dy;
          }
       }
    }
};

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
    const IfcSchema::IfcCurveSegment* inst_;
    const IfcSchema::IfcCurveSegment* next_inst_;
    double length_unit_;
    double start_;
    double length_;
    segment_type_t segment_type_;
    const IfcSchema::IfcCurve* curve_;

    std::shared_ptr<segment_geometry_adjuster> geometry_adjuster;

    std::optional<std::function<Eigen::Matrix4d(double)>> eval_;

  public:
    // First constructor, takes parameters from IfcCurveSegment
    curve_segment_evaluator(mapping* mapping, const IfcSchema::IfcCurveSegment* inst, const IfcSchema::IfcCurveSegment* next_inst, double length_unit, segment_type_t segment_type)
        : mapping_(mapping),
          inst_(inst),
          next_inst_(next_inst),
          length_unit_(length_unit),
          segment_type_(segment_type),
          curve_(inst->ParentCurve()) {
        // @todo in IFC4X3_ADD2 this needs to be length measure


        if (!inst->SegmentStart()->as<IfcSchema::IfcLengthMeasure>() || !inst->SegmentLength()->as<IfcSchema::IfcLengthMeasure>()) {
            // @nb Parameter values are forbidden in the specification until parametrization is provided for all spirals
            throw std::runtime_error("Unsupported curve measure type");
        }

        start_ = *inst->SegmentStart()->as<IfcSchema::IfcLengthMeasure>() * length_unit;
        length_ = *inst->SegmentLength()->as<IfcSchema::IfcLengthMeasure>() * length_unit;
    }

    void compute_segment_end_point()
    {
       // The segment_geometry_adjuster needs to have both the end point of this segment
       // and the start point of the next segment. The start point of the next
       // segment is easy to get and is handled by the segment_geometry_adjuster.
       // The end point of this segment must be computed by calling the eval_ callback
       // at u = length_. But things are a little more complicated than that. eval_ will 
       // use segment_geometry_adjuster to correct deviations between this segment's end point and
       // the next segments start point. In order to compute those adjustments, the
       // end point of this segment, without correction, must be known. The end point not known
       // at this time because segment_geometry_adjuster doesn't have access to the eval_ callback.
       // Additionally, the eval_ callback needs to know if it is evaluating the segment geometry
       // with our without geometric adjustments.
       // 
       // Solving that conundrum is the purpose of this function. The geometric adjustments
       // of geometry_adjuster are disabled, eval_ is called to get the unadjusted end point
       // of this segment, the geometry_adjuster is updated with the end point so it can
       // compute and apply geometry adjustments.
        if (eval_) {
            geometry_adjuster->enable_adjustments(false); // disable adjustments
            auto end_point = (*eval_)(fabs(length_)); // compute the end point without correction
            geometry_adjuster->set_segment_end_point(end_point); // save the unadjusted end point it can be used to compute adjustments
            geometry_adjuster->enable_adjustments(true); // enable adjustments
        }
    }

    void set_spiral_function(mapping* mapping_, const IfcSchema::IfcSpiral* c, double s, std::function<double(double)> signX, std::function<double(double)> fnX, std::function<double(double)> signY, std::function<double(double)> fnY) {
        // determine the length of the spiral from the local origin to the end point
        auto sign_s = binary_sign(start_);
        auto sign_l = binary_sign(length_);
        double L = 0;
        if (sign_s == 0) {
            L = fabs(length_); // start_ is at zero so length_ is the L
        } else if (sign_s == sign_l) {
            L = fabs(start_ + length_); // start_ and length_ are additive
        } else {
            L = fabs(start_); // start_ and length_ are in opposite directions so start_ is furthest from the origin
        }

        auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();

        auto start = start_;

		  geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

        if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
            auto segment_type = segment_type_;
            eval_ = [L, start, s, signX, fnX, signY, fnY, transformation_matrix, segment_type, geometry_adjuster = this->geometry_adjuster](double u) {

                u += start;

                // integration limits, integrate from a to b
                auto a = 0.0;
                auto b = fabs(u / s);

                using boost::math::quadrature::trapezoidal;
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
                }
                Eigen::Matrix4d result = transformation_matrix * m;
                return geometry_adjuster->transform_and_adjust(u,result);
            };
	 }
    else if (segment_type_ == ST_CANT) {
            eval_ = [geometry_adjuster = this->geometry_adjuster](double u) {
                Eigen::Matrix4d result;
                return geometry_adjuster->transform_and_adjust(u, result);
            };
    }
    else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
    }
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
	void operator()(const IfcSchema::IfcClothoid* c) {
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

		set_spiral_function(mapping_, c, s, sign_x, fn_x, sign_y, fn_y);
	}
#endif

#ifdef SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
	void operator()(const IfcSchema::IfcSecondOrderPolynomialSpiral* c)
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
		set_spiral_function(mapping_, c, s, sign_x, fn_x, sign_y, fn_y);
	}
#endif

	void operator()(const IfcSchema::IfcCircle* c)
	{
		auto R = c->Radius();

      auto sign_l = sign(length_);
		auto start = start_;

		auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();

		auto segment_type = segment_type_;

      geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

		eval_ = [R, start, sign_l, transformation_matrix, segment_type, geometry_adjuster = this->geometry_adjuster](double u)
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
          return geometry_adjuster->transform_and_adjust(u, result);
			};
	}

	void operator()(const IfcSchema::IfcPolyline* pl)
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
      auto end_compare = [](double u_start, double u, double u_end) { return u_start <= u && u <= (u_end + 0.001); };

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

		
		geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

		eval_ = [fns, geometry_adjuster = this->geometry_adjuster](double u) {
			auto iter = std::find_if(fns.cbegin(), fns.cend(), [=](const auto& fn)
				{
					auto [u_start, u_end, compare] = fn.first;
					return compare(u_start, u, u_end);
				});

			if (iter == fns.end()) throw std::runtime_error("invalid distance from start"); // this should never happen, but just in case it does, throw an exception so the problem gets automatically detected

			const auto& [u_start, u_end, compare] = iter->first;
         const auto& fn = iter->second;
			Eigen::Matrix4d m = fn(u - u_start); // (u - u_start) is distance from start of this segment of the polyline
            return geometry_adjuster->transform_and_adjust(u, m);
			};
	}

	void operator()(const IfcSchema::IfcLine* l) {
		auto s = l->Pnt();
		auto c = s->Coordinates();
		auto v = l->Dir();
		auto dr = v->Orientation()->DirectionRatios();
		auto m = v->Magnitude();
		auto px = c[0];
		auto py = c[1];
		auto dx = dr[0] / m;
		auto dy = dr[1] / m;

      geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);
      if (segment_type_ == ST_HORIZONTAL) {

			eval_ = [px, py, dx, dy, geometry_adjuster=this->geometry_adjuster](double u) {
				auto x = px + u * dx;
				auto y = py + u * dy;

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0); // vector tangent to the curve, in the direction of the curve
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
            m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
            m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
            return geometry_adjuster->transform_and_adjust(u, m);
			};
		}
		else if (segment_type_ == ST_VERTICAL || segment_type_ == ST_CANT) {
			eval_ = [py, dx, dy, geometry_adjuster = this->geometry_adjuster](double u) {
				// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcGradientCurve.htm
				// the parameter, u, is the parameter of the BaseCurve (u = plan view distance along base curve)
            
				// dx and dy are normalized so u needs to be scaled by dy/dx
				// Consider a 5% uphill grade defined by dr[0] = 1 and dr[1] = 0.05.
				// We would normally compute y = py + 0.05*u. 
				// However, m = sqrt(1*1 + 0.05*0.05) = 1.0124922 we need to normalize the direction ratios as
				// dx = dr[0]/m and dy = dr[1]/m which makes dy = 0.05/1.0124922 = 0.0499376
				// y = py + u * dy/dx =  py + u * (dr[1]/m)*(m/dr[0]) = py + u * 0.05
				auto y = py + u * dy/dx; 

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, 0, dy, 0);
            m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
            m.col(2) = Eigen::Vector4d(-dy, 0, dx, 0);
            m.col(3) = Eigen::Vector4d(0, 0, y, 1.0); // y is an elevation so store it as z
            return geometry_adjuster->transform_and_adjust(u, m);
         };
		} 
		else {
         Logger::Error(std::runtime_error("Unexpected segment type encountered"), l);
		}
    }

	void operator()(const IfcSchema::IfcPolynomialCurve* p) {
		// see https://forums.buildingsmart.org/t/ifcpolynomialcurve-clarification/4716 for discussion on IfcPolynomialCurve
		auto coeffX = p->CoefficientsX().get_value_or(std::vector<double>());
      auto coeffY = p->CoefficientsY().get_value_or(std::vector<double>());
      auto coeffZ = p->CoefficientsZ().get_value_or(std::vector<double>());
      if (!coeffZ.empty())
			Logger::Warning("Expected IfcPolynomialCurve.CoefficientsZ to be undefined for alignment geometry. Coefficients ignored.", p);

		auto transformation_matrix = taxonomy::cast<taxonomy::matrix4>(mapping_->map(p->Position()))->ccomponents();

		auto segment_type = segment_type_;

		geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);


      eval_ = [coeffX, coeffY, transformation_matrix, segment_type, geometry_adjuster = this->geometry_adjuster](double u) {
         std::array<const std::vector<double>*, 2> coefficients{&coeffX, &coeffY};
         std::array<double, 2> position{0.0, 0.0};
         std::array<double, 2> slope{0.0, 0.0}; // slope is derivative of the curve = SUM( coeff*pos*u^(pos-1) )
         for (int i = 0; i < 2; i++) {
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

			return geometry_adjuster->transform_and_adjust(u, m);
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
	// Find the next segment after inst
	const IfcSchema::IfcCurveSegment* next_inst = nullptr;
   auto composite_curves = inst->data().getInverse(&IfcSchema::IfcCompositeCurve::Class(), 0);
    if (composite_curves) {
		 if (composite_curves->size() == 1) {
            auto segments = (*composite_curves->begin())->as<IfcSchema::IfcCompositeCurve>()->Segments();
            bool emit_next = false;
            for (auto& s : *segments) {
					if (emit_next) {
                next_inst = s->as<IfcSchema::IfcCurveSegment>();
						 break;
					}
					if (s == inst) {
						 emit_next = true;
					}
            }
       }
		 else {
            Logger::Warning("IfcCurveSegment belongs to multiple IfcCompositeCurve instances. Cannot determine the next segment. Geometry adjustments will not be made.");
		 }
    }

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

	curve_segment_evaluator cse(this, inst, next_inst, length_unit_, segment_type);
	boost::mpl::for_each<curve_seg_types, boost::type<boost::mpl::_>>(std::ref(cse));
   cse.compute_segment_end_point();
	
	auto& eval_fn = cse.evaluation_function();
	if(!eval_fn) throw std::runtime_error(inst->ParentCurve()->declaration().name() + " not implemented");
	auto fn = *eval_fn;
	auto length = fabs(cse.length());

	// @todo it might be suboptimal that we no longer have the spans now
	auto pwf = taxonomy::make<taxonomy::piecewise_function>();
	pwf->spans.push_back({ length, fn });
	pwf->instance = inst;
	return pwf;
}

#endif