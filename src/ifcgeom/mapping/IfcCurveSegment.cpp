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

#include <numeric>

#include <boost/mpl/vector.hpp>
#include <boost/mpl/for_each.hpp>
#include <boost/math/quadrature/trapezoidal.hpp>
#include <boost/math/tools/roots.hpp>

namespace {
// @todo: rb is there a common math library these functions can be moved to?
auto sign = [](double v) -> int { return v < 0 ? -1 : 1; };                      // returns -1 or 1
auto binary_sign = [](double v) -> int { return v < 0 ? -1 : (0 < v ? 1 : 0); }; // returns -1, 0, or 1

// @todo change the calculation at end of this to std::lerp when upgrading to C++ 20
template <typename T>
auto compute_adjustment = [](double u, const T& a, const T& b, double l) -> double { return l == 0.0 ? 0.0 : u * (b - a) / l; };
} // namespace


enum segment_type_t {
    ST_HORIZONTAL,
    ST_VERTICAL,
    ST_CANT
};

// @todo use std::numbers::pi when upgrading to C++ 20
static const double PI = boost::math::constants::pi<double>();

// Current implementation uses the same segment_geometry_adjuster for all ParentCurve types.
// Comment/Uncomment to change the type of segment geometry adjuster
// Future implementations could use specialized adjusters based on ParentCurve type
#define GEOMETRY_ADJUSTER segment_geometry_adjuster
//#define GEOMETRY_ADJUSTER linear_segment_geometry_adjuster
 
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
    segment_geometry_adjuster(mapping* mapping, segment_type_t segment_type,const IfcSchema::IfcCurveSegment* inst, const IfcSchema::IfcCurveSegment* next_inst) : 
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
       } else {
          // there is not a next segment, however IfcGradientCurve and IfcSegmentedReferenceCurve
          // have an optional EndPoint attribute that serves the same purpose as the zero-length
          // "next segment" at the end of the curve. The Ifc specification is a little redundant
          // in that the "zero length" segment is required thereby negating the need for EndPoint
          // but some implementations use the EndPoint instead of the "zero length" segment
          //
          // Get the parent of this segment. If it is a IfcGradientCurve or IfcSegmentedReferenceCurve
          // look for the optional EndPoint attribute
          auto curves = inst->UsingCurves();
          if (curves && curves->size()) {
             auto curve = *curves->begin();
             const IfcSchema::IfcPlacement* placement = nullptr;
             if (curve->as<IfcSchema::IfcSegmentedReferenceCurve>()) {
                 auto s = curve->as<IfcSchema::IfcSegmentedReferenceCurve>();
                 placement = s->EndPoint();
             } else if (curve->as<IfcSchema::IfcGradientCurve>()) {
                 auto s = curve->as<IfcSchema::IfcGradientCurve>();
                 placement = s->EndPoint();
             }
             if (placement) {
                 start_of_next_inst_ = taxonomy::cast<taxonomy::matrix4>(mapping->map(placement))->ccomponents();
             }
          }
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
       init_adjustments();
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
       // precompute any values that are constant when applying geometry adjustments
       //( subclasses to override. 
    virtual void init_adjustments() { /*do nothing*/
    }
       // Applies geometric adjustment to the segment curve point evaluated at u
       // This default implementation does nothing
    virtual void apply_adjustments(double u, Eigen::Matrix4d& p) const { /* do nothing - override in subclass if needed */ }

    const Eigen::Matrix4d& get_end_of_segment() const { return end_of_inst_;  }
    const Eigen::Matrix4d& get_start_of_next_segment() const { return start_of_next_inst_; }
    IfcSchema::IfcTransitionCode::Value get_transition_code() const { return transition_code_; }
    double get_length() const { return length_; }

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

    protected:
       virtual void init_adjustments() override {
          // @todo: rb - implement to improve efficiency
          // cache delta = (start_next - end_this)/length 
          // adjustment is then adj = u*delta
    }

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
       auto x = compute_adjustment<decltype(xe)>(u, xe, xs, length);
       auto y = compute_adjustment<decltype(ye)>(u, ye, ys, length);

       p.col(3)(0) += x;
       p.col(3)(1) += y;

       if (transition_code == IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT or
           transition_code == IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENTSAMECURVATURE) {

          for (int i = 0; i < 2; i++) {
              auto dxe = end_this.col(i)(0);
              auto dye = end_this.col(i)(1);
              auto dxs = start_next.col(i)(0);
              auto dys = start_next.col(i)(1);
              auto dx = compute_adjustment<decltype(dxe)>(u,dxe,dxs,length);
              auto dy = compute_adjustment<decltype(dye)>(u,dye,dys,length);
              p.col(i)(0) += dx;
              p.col(i)(1) += dy;
              p.col(i).normalize();
          }
       }
    }
};

// specializes segment_geometry_adjuster for cant segments.
// The specification for IfcSegmentedReferenceCurve provides the requirements for 
// how the cant deviates from the base curve and how the cant transitions over
// the length of an IfcCurveSegment. The exact requirements are unclear. For this
// reason, the following implementation may not conform with the IFC specification.
// 
// https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcSegmentedReferenceCurve.htm
// 
// The treatment of cant geometry is as follows in this class:
// 1) Superelevation (depression or elevation) from the axis of the base curve. 
// From 8.9.3.62
// "A deviating explicit position of a curve segment (IfcCurveSegment.Placement) from the axis of the base 
// curve produces a superelevation i.e. depression or elevation from the axis of the base curve."
// 
// Nothing in the specification indicates that the deviation from the axis of the base curve is to be interpolated.
// However, this would result in the cant elevation deviation being constant along each segment and there would
// potentially be abrupt changes in elevation at segment boundaries.
// 
// To address this, the cant at a point along a segment is interpolated between IfcCurveSegment.Placement.Location.Y for placement
// at the start of the current segment and the start of the next segment. If there is not a next segment, the optional
// IfcSegmentedReferenceCurve.EndPoint attribute is used if present.
// 
// For simplicity in matrix operations, the Location.Z values are also interpolated. Though, they can reasonably be
// expected to be 0.0 because cant is, in part, a vertical deviation from the IfcGradientCurve basis.
// 
// 2) Determination of Axis and RefDirection
// From 8.9.3.62
// "The superelevation rate of change is directly proportionate to the curve segment parent curve curvature gradient 
// equation (IfcCurveSegment.ParentCurve) in the linear parameter space of the base curve. If no deviation in the position 
// of the curve segment to the base curve axis is specified, the axes (Axis and RefDirection) directions of IfcAxis2Placement 
// are interpolated between the initial curve segment placement and the placement of the subsequent curve segment."
//
// This seems to say that the type of the IfcCurveSegment.ParentCurve is related to the rate of change of the Axis and RefDirection
// vectors along the length of the segment. The rate of change is understood to be equal to the derivative of the curvature of
// the IfcCurve subtype.
// 
// However, if the IfcCureSegment.Placement does not deviate from the basic curve (which occurs with a deviation of 0.0), ignore
// the IfcCurveSegment.ParentCurve type and linearly interpolate the Axis and RefDirection vectors from the stat of this and
// the next segment.
// 
// For now, the derivative of the curvature of the IfcCurve subtype is difficult to implement and example models from the IFC spec
// always use IfcAxis2Placement3D with Axis and RefDirection specified, the basic interpolation is used, ignoring the IfcCurve type. 
//
// This implementation will be revised as the understanding of IfcSegmentedReferenceCurve improves.
class cant_adjuster : public segment_geometry_adjuster {
  public:
    using segment_geometry_adjuster::segment_geometry_adjuster;

    virtual void transform_and_adjust(double u, Eigen::Matrix4d& p) const {
       // don't call parent class version 
       auto& start_this = get_start_of_segment();
       auto& start_next = get_start_of_next_segment();
       auto l = get_length();

       // tilt angle of vector normal to cant at start of this and start of next segment
       auto tilt_start_this = atan2(start_this.col(2)(2), start_this.col(2)(1));
       auto tilt_start_next = atan2(start_next.col(2)(2), start_next.col(2)(1));

       // tilt angle of vector normal to cant at u assuming linear interpolation
       // @todo: rb - rate of change of slope is related to curve type (such as clothoid or line)
       // need to somehow account for that - it is important when tilt at start of next isn't provided
       // because it defines how much tilt_start_this varies along the length
       auto tilt = tilt_start_this + (tilt_start_next - tilt_start_this) * u / l;

       // use linear interpolation to compute elevation change due to cant
       auto st = start_this.col(3)(1);
       auto sn = start_next.col(3)(1);
       auto slope = (sn - st) / l;

       // RefDirection.z is due to cant elevation change slope
       p.col(0)(2) = slope;
       p.col(0).normalize();

       // populate Axis vector
       p.col(2)(0) = -slope;
       p.col(2)(1) = cos(tilt);
       p.col(2)(2) = sin(tilt);
       p.col(2).normalize();

       // Axis X RefDirection = Y
       p.col(1).head<3>() = p.col(2).head<3>().cross(p.col(0).head<3>());

       auto result = st + u * slope;
       p.col(3)(1) = result;
    }

  protected:
    const Eigen::Matrix4d& get_start_of_segment() const { return transformation_matrix_; }
};

// vector of parent curve types that are supported for IfcCurveSegment.ParentCurve
typedef boost::mpl::vector<
   IfcSchema::IfcLine
#ifdef SCHEMA_HAS_IfcClothoid
   , IfcSchema::IfcClothoid
#endif
#if defined SCHEMA_HAS_IfcCosineSpiral
   , IfcSchema::IfcCosineSpiral
#endif
#if defined SCHEMA_HAS_IfcSineSpiral
    , IfcSchema::IfcSineSpiral
#endif
#if defined SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
   , IfcSchema::IfcSecondOrderPolynomialSpiral
#endif
#if defined SCHEMA_HAS_IfcThirdOrderPolynomialSpiral
    , IfcSchema::IfcThirdOrderPolynomialSpiral
#endif
#if defined SCHEMA_HAS_IfcSeventhOrderPolynomialSpiral
    , IfcSchema::IfcSeventhOrderPolynomialSpiral
#endif

   , IfcSchema::IfcPolyline
   , IfcSchema::IfcCircle
   , IfcSchema::IfcPolynomialCurve
> curve_seg_types;

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
        if (eval_ && geometry_adjuster) {
            geometry_adjuster->enable_adjustments(false); // disable adjustments
            auto end_point = (*eval_)(fabs(length_)); // compute the end point without correction
            geometry_adjuster->set_segment_end_point(end_point); // save the unadjusted end point it can be used to compute adjustments
            geometry_adjuster->enable_adjustments(true); // enable adjustments
        }
    }

    void set_spiral_function(mapping* mapping_, const IfcSchema::IfcSpiral* c, double s, std::function<double(double)> fnX, std::function<double(double)> fnY) {
        if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
            auto start = start_;
            auto segment_type = segment_type_;
            geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, segment_type_, inst_, next_inst_);
            using boost::math::quadrature::trapezoidal;
            auto start_x = s ? trapezoidal(fnX, 0.0, start / s) : 0.0;
            auto start_y = s ? trapezoidal(fnY, 0.0, start / s) : 0.0;
            auto start_dx = s ? fnX(start / s)/s : 0.0;
            auto start_dy = s ? fnY(start / s)/s : 0.0;
            eval_ = [start, s, start_x, start_y, start_dx,start_dy,fnX, fnY, segment_type, geometry_adjuster = this->geometry_adjuster](double u) {

                u += start;

                // integration limits, integrate from a to b
                auto a = 0.0;
                auto b = s ? u / s : 0.0;

                auto x = trapezoidal(fnX, a, b) - start_x;
                auto y = trapezoidal(fnY, a, b) - start_y;

                auto x1 = x * start_dx + y * start_dy;
                auto y1 = -x * start_dy + y * start_dx;
                x = x1;
                y = y1;

                // From https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcSpiral.htm, x = Integral(fnX du), y = Integral(fnY du)
                // The tangent slope of a curve is the derivate of the curve, so the derivitive of an integral, is just the function
                auto dx = s ? fnX(b)/s : 1.0;
                auto dy = s ? fnY(b)/s : 0.0;

                // rotate about the Z-axis
                Eigen::Matrix4d m;
                m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
                m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
                m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
                m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
                return geometry_adjuster->transform_and_adjust(u,m);
            };
        }
        else if (segment_type_ == ST_CANT) {
            auto cant_adjuster_ = std::make_shared<cant_adjuster>(mapping_, segment_type_, inst_, next_inst_);
            eval_ = [cant_adjuster_](double u) {
                Eigen::Matrix4d result = Eigen::Matrix4d::Identity();
                cant_adjuster_->transform_and_adjust(u, result);
                return result;
            };
    }
    else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
    }
}


   // Clothoid using numerical integration
#ifdef SCHEMA_HAS_IfcClothoid
// Then initialize Function(double) -> Vector3, by means of IfcCurve subtypes
   void operator()(const IfcSchema::IfcClothoid* c) {
      // see https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcClothoid.htm
      // also see, https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Clothoid_Transition_Segment/content.html,
      // which defines the clothoid constant as sqrt(L*R) and L is the length measured from the inflection point and R is the radius at L
      auto A = c->ClothoidConstant();
      auto s = fabs(A * sqrt(PI)); // curve length when u = 1.0

      auto fn_x = [A, s](double t) -> double { return A ? s * cos(PI * A * t * t / (2 * fabs(A))) : 0.0; };
      auto fn_y = [A, s](double t) -> double { return A ? s * sin(PI * A * t * t / (2 * fabs(A))) : 0.0; };

      set_spiral_function(mapping_, c, s, fn_x, fn_y);
   }
#endif

#if defined SCHEMA_HAS_IfcCosineSpiral
   void operator()(const IfcSchema::IfcCosineSpiral* c) {
      auto const_term = c->ConstantTerm();
      auto cosine_term = c->CosineTerm();
      auto L = length()*length_unit_;
      auto theta = [const_term, cosine_term,L,lu=length_unit_](double t) -> double {
          auto a0 = const_term.has_value() ? t / (const_term.value()*lu) : 0.0;
          auto a1 = (L/PI)*(1.0/(cosine_term*lu))*sin((PI/L)*t);
          return a0 + a1;
      };
      auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
      auto fn_y = [theta](double t) -> double { return sin(theta(t)); };
      double s = 1.0;
      set_spiral_function(mapping_, c, s, fn_x, fn_y);
   }
#endif

#if defined SCHEMA_HAS_IfcSineSpiral
   void operator()(const IfcSchema::IfcSineSpiral* c) {
      auto const_term = c->ConstantTerm();
      auto linear_term = c->LinearTerm();
      auto sine_term = c->SineTerm();
      auto L = length() * length_unit_;
      auto theta = [const_term, linear_term, sine_term,L,lu=length_unit_](double t) -> double {
          auto a0 = const_term.has_value() ? t / (const_term.value() * lu) : 0.0;
          auto a1 = linear_term.has_value() ? sign(linear_term.value())*pow(t / (linear_term.value()*lu), 2.0) / 2.0 : 0.0;
          auto a2 = -1.0*(L / (2 * PI * sine_term * lu)) * (cos(2 * PI * t / L) - 1.0);
          return a0 + a1 + a2;
      };
      auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
      auto fn_y = [theta](double t) -> double { return sin(theta(t)); };
      double s = 1.0;
      set_spiral_function(mapping_, c, s, fn_x, fn_y);
   }
#endif

    void polynomial_spiral(const IfcSchema::IfcSpiral* c, double lu, boost::optional<double> A0, boost::optional<double> A1, boost::optional<double> A2, boost::optional<double> A3, boost::optional<double> A4, boost::optional<double> A5, boost::optional<double> A6, boost::optional<double> A7) {
      auto theta = [A0, A1, A2, A3, A4, A5, A6, A7, lu](double t) {
          auto a0 = A0.has_value() ? t / (A0.value() * lu) : 0.0;
          auto a1 = A1.has_value() ? A1.value() * lu * std::pow(t, 2) / (2 * fabs(std::pow(A1.value() * lu, 3))) : 0.0;
          auto a2 = A2.has_value() ? std::pow(t, 3) / (3 * std::pow(A2.value() * lu, 3)) : 0.0;
          auto a3 = A3.has_value() ? A3.value() * lu * std::pow(t, 4) / (4 * fabs(std::pow(A3.value() * lu, 5))) : 0.0;
          auto a4 = A4.has_value() ? std::pow(t, 5) / (5 * std::pow(A4.value() * lu, 5)) : 0.0;
          auto a5 = A5.has_value() ? A5.value() * lu * std::pow(t, 6) / (6 * fabs(std::pow(A5.value() * lu, 7))) : 0.0;
          auto a6 = A6.has_value() ? std::pow(t, 7) / (7 * std::pow(A6.value() * lu, 7)) : 0.0;
          auto a7 = A7.has_value() ? A7.value() * lu * std::pow(t, 8) / (8 * fabs(std::pow(A7.value() * lu, 9))) : 0.0;
          return a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7;
      };

      auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
      auto fn_y = [theta](double t) -> double { return sin(theta(t)); };

      double s = 1.0;
      set_spiral_function(mapping_, c, s, fn_x, fn_y);
    }

#ifdef SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
   void operator()(const IfcSchema::IfcSecondOrderPolynomialSpiral* c)
   {
      auto A0 = c->ConstantTerm();
      auto A1 = c->LinearTerm();
      auto A2 = c->QuadraticTerm();
      boost::optional<double> A3, A4, A5, A6, A7;
      polynomial_spiral(c, length_unit_, A0, A1, A2, A3, A4, A5, A6, A7);
    }
#endif

#ifdef SCHEMA_HAS_IfcThirdOrderPolynomialSpiral
    void operator()(const IfcSchema::IfcThirdOrderPolynomialSpiral* c) {
        auto A0 = c->ConstantTerm();
        auto A1 = c->LinearTerm();
        auto A2 = c->QuadraticTerm();
        auto A3 = c->CubicTerm();
        boost::optional<double> A4, A5, A6, A7;
        polynomial_spiral(c, length_unit_, A0, A1, A2, A3, A4, A5, A6, A7);
    }
#endif

#ifdef SCHEMA_HAS_IfcSeventhOrderPolynomialSpiral
    void operator()(const IfcSchema::IfcSeventhOrderPolynomialSpiral* c) {
        auto A0 = c->ConstantTerm();
        auto A1 = c->LinearTerm();
        auto A2 = c->QuadraticTerm();
        auto A3 = c->CubicTerm();
        auto A4 = c->QuarticTerm();
        auto A5 = c->QuinticTerm();
        auto A6 = c->SexticTerm();
        auto A7 = c->SepticTerm();

        polynomial_spiral(c, length_unit_, A0, A1, A2, A3, A4, A5, A6, A7);
    }
#endif

   void operator()(const IfcSchema::IfcCircle* c)
   {
      if (segment_type_ == ST_HORIZONTAL) {
         auto R = c->Radius() * length_unit_;

         auto sign_l = sign(length_);
         auto start_angle = start_/R;

         auto start_x = R * cos(start_angle);
         auto start_y = R * sin(start_angle);

         auto segment_type = segment_type_;

         geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, segment_type_, inst_, next_inst_);

         eval_ = [R, start_x, start_y, start_angle, sign_l, segment_type, geometry_adjuster = this->geometry_adjuster](double u)
         {
            auto angle = start_angle + sign_l * u / R;

            auto dx = cos(angle);
            auto dy = sin(angle);

            auto x = R * dx - start_x;
            auto y = R * dy - start_y;

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
            m.col(2) = Eigen::Vector4d(0, 0, 1, 0);
            m.col(3) = Eigen::Vector4d(y * sign_l, -x * sign_l, 0.0, 1.0);
            return geometry_adjuster->transform_and_adjust(u, m);
         };
      }
      else if (segment_type_ == ST_VERTICAL) {
         auto R = c->Radius() * length_unit_;
         auto sign_l = sign(length_);

         geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, segment_type_, inst_, next_inst_);

         eval_ = [R, sign_l, geometry_adjuster = this->geometry_adjuster](double u) -> Eigen::Matrix4d {
             auto y = sign_l * (R - sqrt(R*R - u*u));
             Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
             m.col(3) = Eigen::Vector4d(u, y, 0.0, 1.0);
             return geometry_adjuster->transform_and_adjust(u, m);
         };
      } else if (segment_type_ == ST_CANT) {
         Logger::Warning(std::runtime_error("Use of IfcCircle for cant is not supported"));
         eval_ = [](double u) -> Eigen::Matrix4d {
               return Eigen::Matrix4d::Identity();
         };
      } else {
         Logger::Error(std::runtime_error("Unexpected segment type encountered"));
         eval_ = [](double u) -> Eigen::Matrix4d {
            return Eigen::Matrix4d::Identity();
         };
      }
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
               
         if (l < mapping_->settings().get<ifcopenshell::geometry::settings::Precision>().get())
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
                    m = Eigen::Matrix4d::Identity();
                } else {
                    Logger::Error(std::runtime_error("Unexpected segment type encountered"));
                    m = Eigen::Matrix4d::Identity();
                }

                return m;
            };

         fns.insert(std::make_pair(Range{ u, u + l,iter == last ? end_compare : std_compare }, fn));

         p1 = p2;
         u = u + l;
      }
     
         geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, segment_type_, inst_, next_inst_);

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

      // 8.9.3.75 IfcVector https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcVector.htm
      // 8.9.3.30 IfcDirection https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcDirection.htm
      // "The IfcDirection does not imply a vector length, and the direction ratios does not have to be normalized."
      //
      // Therefore, the direction ratios need to be normalized to compute points on the line. Magnitude is not used
      // because it relates to the parameterization of the line, which isn't currently done for IfcCurveSegment 
      auto dr = v->Orientation()->DirectionRatios();

      // normalize the direction ratios
      double m_squared = std::inner_product(dr.begin(), dr.end(), dr.begin(), 0.0);
      double m = sqrt(m_squared);
      std::for_each(dr.begin(), dr.end(), [m](auto& d) { return d / m; });
      auto dx = dr[0];
      auto dy = dr[1];

      auto px = c[0] * length_unit_;
      auto py = c[1] * length_unit_;

      geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, segment_type_, inst_, next_inst_);
      if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {

         eval_ = [px, py, dx, dy, geometry_adjuster=this->geometry_adjuster](double u) {
            auto x = px + u/dx;
            auto y = py;// + u * dy/dx;

            Eigen::Matrix4d m = Eigen::Matrix4d::Identity();;
            //m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
            //m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
            //m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
            m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
            return geometry_adjuster->transform_and_adjust(u, m);
         };
      }
      else if (segment_type_ == ST_CANT) {
            auto cant_adjuster_ = std::make_shared<cant_adjuster>(mapping_, segment_type_, inst_, next_inst_);
            eval_ = [cant_adjuster_](double u) {
                Eigen::Matrix4d result = Eigen::Matrix4d::Identity();
                cant_adjuster_->transform_and_adjust(u, result);
                return result;
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

      auto length_unit = length_unit_;

      geometry_adjuster = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, segment_type_, inst_, next_inst_);

      if (segment_type_ == ST_HORIZONTAL) {
         // @rb need to work on this - u is distance along curve, this differs from vertical where u = x
         eval_ = [start=start_,coeffX,coeffY,length_unit,geometry_adjuster = this->geometry_adjuster](double u) -> Eigen::Matrix4d {
             std::array<const std::vector<double>*, 2> coefficients{&coeffX, &coeffY};
             std::array<double, 2> position{0.0, 0.0}; // = SUM(coeff*u^pos)
             std::array<double, 2> slope{0.0, 0.0};    // slope is derivative of the curve = SUM( coeff*pos*u^(pos-1) )
             for (int i = 0; i < 2; i++) {             // loop over X and Y
                 auto length_conversion = length_unit;
                 auto begin = coefficients[i]->cbegin();
                 auto end = coefficients[i]->cend();
                 for (auto iter = begin; iter != end; iter++) {
                     auto exp = std::distance(begin, iter);
                     auto coeff = (*iter) * length_conversion;
                     position[i] += coeff * (pow(u + start, exp) - pow(start,exp));

                     if (iter != begin) {
                         slope[i] += coeff * exp * pow(u + start, exp - 1);
                     }

                     length_conversion /= length_unit;
                 }
             }

             auto x = position[0];
             auto y = position[1];

             auto dx = slope[0];
             auto dy = slope[1];

             Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
              m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
              m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
              m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
              m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
             return geometry_adjuster->transform_and_adjust(u + start, m);
         };
      }
      else if (segment_type_ == ST_VERTICAL) {
         auto p = inst_->Placement()->Location()->as<IfcSchema::IfcCartesianPoint>();
         double sx = p->Coordinates()[0] * length_unit_;
         double sy = p->Coordinates()[1] * length_unit_;
         eval_ = [start = start_, sx, sy, coeffX, coeffY, length_unit](double u) -> Eigen::Matrix4d {
             std::array<const std::vector<double>*, 2> coefficients{&coeffX, &coeffY};
             std::array<double, 2> position{0.0, 0.0}; // = SUM(coeff*u^pos)
             std::array<double, 2> slope{0.0, 0.0};    // slope is derivative of the curve = SUM( coeff*pos*u^(pos-1) )
             for (int i = 0; i < 2; i++) {             // loop over X and Y
                 auto length_conversion = length_unit;
                 auto begin = coefficients[i]->cbegin();
                 auto end = coefficients[i]->cend();
                 for (auto iter = begin; iter != end; iter++) {
                     auto exp = std::distance(begin, iter);
                     auto coeff = (*iter) * length_conversion;
                     position[i] += coeff * pow(u + start, exp);

                     if (iter != begin) {
                         slope[i] += coeff * exp * pow(u, exp - 1);
                     }
                     length_conversion /= length_unit;
                 }
             }

             auto x = position[0] - coeffX[0] + sx;
             auto y = position[1] - coeffY[0] + sy;
             auto dx = slope[0];
             auto dy = slope[1];

             Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
             m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
             m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
             m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
             m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
             return m;
         };
      } else if (segment_type_ == ST_CANT) {
         Logger::Warning(std::runtime_error("Use of IfcPolynomialCurve for cant is not supported"));
         eval_ = [](double u) -> Eigen::Matrix4d {
             return Eigen::Matrix4d::Identity();
         };
      } else {
         Logger::Error(std::runtime_error("Unexpected segment type encountered"));
         eval_ = [](double u) -> Eigen::Matrix4d {
             return Eigen::Matrix4d::Identity();
         };
      }

      //eval_ = [start = start_, coeffX, coeffY, segment_type, length_unit, geometry_adjuster = this->geometry_adjuster](double u) {
      //   std::array<const std::vector<double>*, 2> coefficients{&coeffX, &coeffY};
      //   std::array<double, 2> position{0.0, 0.0}; // = SUM(coeff*u^pos)
      //   std::array<double, 2> slope{0.0, 0.0}; // slope is derivative of the curve = SUM( coeff*pos*u^(pos-1) )
      //   for (int i = 0; i < 2; i++) { // loop over X and Y
      //       auto length_conversion = length_unit;
      //       auto begin = coefficients[i]->cbegin();
      //       auto end = coefficients[i]->cend();
      //       for (auto iter = begin; iter != end; iter++) {
      //            auto exp = std::distance(begin, iter);
      //            auto coeff = (*iter)*length_conversion;
      //            position[i] += coeff * pow(u+start, exp);

      //            if (iter != begin) {
      //                slope[i] += coeff * exp * pow(u+start, exp - 1);
      //            }

      //            length_conversion /= length_unit;
      //       }
      //   }

      //   auto x = position[0];
      //   auto y = position[1];

      //   auto dx = slope[0];
      //   auto dy = slope[1];

      //   Eigen::Matrix4d m;
      //   if (segment_type == ST_HORIZONTAL || segment_type == ST_VERTICAL) {
      //       rotate about the Z-axis
      //      m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);  // vector tangent to the curve, in the direction of the curve
      //      m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0); // vector perpendicular to the curve, towards the left when looking from start to end along the curve (this is used for IfcAxis2PlacementLinear.RefDirection when it is not provided)
      //      m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);  // cross product of x and y and will always be up (this is used for IfcAxis2PlacementLinear.Axis when it is not provided)
      //      m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
      //   }
      //   else if (segment_type == ST_CANT) {
      //      Logger::Warning(std::runtime_error("Use of IfcPolynomialCurve for cant is not supported"));
      //      m = Eigen::Matrix4d::Identity();
      //   } else {
      //      Logger::Error(std::runtime_error("Unexpected segment type encountered"));
      //      m = Eigen::Matrix4d::Identity();
      //   }

      //      return geometry_adjuster->transform_and_adjust(u+start, m);
      //  };
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
   auto composite_curves = inst->UsingCurves();
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

   if (composite_curves) {
      for (auto& cc : *composite_curves) {
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
   auto pwf = taxonomy::make<taxonomy::piecewise_function>(&settings_);
   pwf->spans.push_back({ length, fn });
   pwf->instance = inst;
   return pwf;
}

#endif