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
auto sign = [](double v) -> double { return v ? v/fabs(v) : 1.0; };

// @todo change the calculation at end of this to std::lerp when upgrading to C++ 20
template <typename T>
auto compute_adjustment = [](double u, const T& a, const T& b, double l) -> double { return l == 0.0 ? 0.0 : u * (b - a) / l; };


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
    bool enable_adjustments() const { return adjustments_; }

    // This object doesn't have access to the eval_ property of the curve_segment_evaluator.
    // The end point of the segment being adjusted, without adjustments, is computed externally
    // and provided to the curve_segment_adjustor through this method
    void set_segment_end_point(const Eigen::Matrix4d& end_of_inst) {
       end_of_inst_ = end_of_inst;
       init_adjustments();
    }

    // Transforms the ParentCurve geometry with the IfcCurveSegment.Placement and
    // applies geometric adjustments to the geometry, if enabled
    virtual Eigen::Matrix4d transform_and_adjust(double u, const Eigen::Matrix4d& parent_curve_point) const {
       // transform the parent curve's value into the segment curve's coordinate system
       Eigen::Matrix4d segment_curve_point = transformation_matrix_ * parent_curve_point;
       if (adjustments_) {
          apply_adjustments(u, segment_curve_point);
       }
       return segment_curve_point;
    }

    const Eigen::Matrix4d& get_placement() const { return transformation_matrix_; }

    protected:
    // precompute any values that are constant when applying geometry adjustments
    // (subclasses to override as needed). 
    virtual void init_adjustments() { /*do nothing*/ }

    // Applies geometric adjustment to the segment curve point evaluated at u
    // This default implementation does nothing
    virtual void apply_adjustments(double /*u*/, Eigen::Matrix4d& /*p*/) const { /* do nothing - override in subclass if needed */ }

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
       void init_adjustments() override {
          // @todo: rb - implement to improve efficiency
          // cache delta = (start_next - end_this)/length 
          // adjustment is then adj = u*delta
    }

    void apply_adjustments(double u, Eigen::Matrix4d& p) const override {
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
class cant_adjuster : public GEOMETRY_ADJUSTER {
  public:
    using GEOMETRY_ADJUSTER::GEOMETRY_ADJUSTER;

    Eigen::Matrix4d transform_and_adjust(double u, const Eigen::Matrix4d& parent_curve_point) const override {
       // Consider a line connection two rails. The upwards vector normal to that line is used to define
       // the cant tilt. For no tilt, the vector is upwards so the tilt angle is PI/2.
       // If the left rail is higher than the right angle, the tilt is clockwise and the tilt angle is less than PI/2
        
       // The cant (D) and half the railhead distance is needed to compute the tilt angle.
       // tan(tilt_angle) = 2*D/rail_head_distance
       // 
       // However, the rail head distance is not known from the geometric definition. It is only known in the 
       // business logic definition.
       // 
       // From the geometric definition, the cant and tilt angle are known at both ends of the segment.
       // From this, the rail head distance can be computed as follows:
       // 
       // Get the placement at the start of this segment and the start of the next segment
       auto& start_this = get_start_of_segment();
       auto& start_next = get_start_of_next_segment();

       // Get the cant at the start of this and the next segment
       auto start_cant = start_this.col(3)(1);
       auto next_cant = start_next.col(3)(1);

       // Compute the tilt angle at start of this and start of next segment
       // This is the angle of the normal vector to the line connecting the rail heads
       auto tilt_start_this = atan2(start_this.col(2)(2), start_this.col(2)(1));
       auto tilt_start_next = atan2(start_next.col(2)(2), start_next.col(2)(1));

       // Compute half the rail head distance
       // Cant is measured half way between rails, so it is easier to work with half the rail head distance
       // Need to do this calculation with a non-zero cant value. The tilt angle is PI/2 for zero cant
       // and the tangent of PI/2 is infinity - not helpful
       double h;
       if (start_cant) {
           h = start_cant * tan(tilt_start_this);
       } else {
           h = next_cant * tan(tilt_start_next);
       }

       // Get the cant from the parent curve point
       // Using the cant and half the rail head distance, compute the tilt angle
       // For cant tilt toward the left (CCW rotation), the tilt angle used to
       // compute h is greater than PI/2 and the tangent of that angle is negative.
       // For this reason, use fabs(h) so tilt is between 0 and PI
       double cant = parent_curve_point.col(3)(1);
       auto tilt = -atan2(fabs(h), cant);

       // Create a transformation matrix
       Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
       m.col(2)(1) = cos(tilt);
       m.col(2)(2) = sin(tilt);

       // apply cant tilt to the parent curve point
       Eigen::Matrix4d p = m * parent_curve_point;

       return p;

       // apply the base class transformation, which is just applying the IfcCurveSegment placement
       //return GEOMETRY_ADJUSTER::transform_and_adjust(u, p);
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
    mapping* mapping_ = nullptr;
    const IfcSchema::IfcCurveSegment* inst_ = nullptr; // this curve segment instance
    const IfcSchema::IfcCurveSegment* next_inst_ = nullptr; // next curve segment instance, if it exists
    double length_unit_;
    double start_;
    double length_; // length along the curve, as provided from the IfcCurveSegment
    segment_type_t segment_type_;
    const IfcSchema::IfcCurve* parent_curve_ = nullptr;

    double projected_length_; // for vertical segments, this is the length of curve projected onto the "Distance Along" axis

    std::shared_ptr<segment_geometry_adjuster> geometry_adjuster_; // object that positions the segment using the IfcCurveSegment.Placement and makes geometry adjustments

    std::optional<std::function<Eigen::Matrix4d(double)>> eval_; // function for the curve. Function takes distances along, u, and returns the 4x4 position matrix

  public:
    curve_segment_evaluator(mapping* mapping, const IfcSchema::IfcCurveSegment* inst, const IfcSchema::IfcCurveSegment* next_inst, double length_unit, segment_type_t segment_type)
        : mapping_(mapping),
          inst_(inst),
          next_inst_(next_inst),
          length_unit_(length_unit),
          segment_type_(segment_type),
          parent_curve_(inst->ParentCurve()) {

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
        if (eval_ && geometry_adjuster_) {
            geometry_adjuster_->enable_adjustments(false); // disable adjustments
            auto end_point = (*eval_)(fabs(length_)); // compute the end point without correction
            geometry_adjuster_->set_segment_end_point(end_point); // save the unadjusted end point it can be used to compute adjustments
            geometry_adjuster_->enable_adjustments(true); // enable adjustments
        }
    }

    void set_spiral_function(mapping* mapping_, double s, std::function<double(double)> fnX, std::function<double(double)> fnY) {
        if (segment_type_ == ST_HORIZONTAL) {
            auto start = start_;
            projected_length_ = length_;
            auto spiral = inst_->ParentCurve()->as<IfcSchema::IfcSpiral>();
            auto position = spiral->Position()->as<IfcSchema::IfcAxis2Placement2D>();
            auto location = position->Location()->as<IfcSchema::IfcCartesianPoint>();

            // parent curve placement information
            auto pcX = location->Coordinates()[0];
            auto pcY = location->Coordinates()[1];

            // orientation of the coordinate system at the center point
            // normalize the direction ratios
            auto ref_direction = position->RefDirection();
            double pcDx = 1.0, pcDy = 0.0;
            if (ref_direction) {
                auto dr = ref_direction->DirectionRatios();
                double m_squared = std::inner_product(dr.begin(), dr.end(), dr.begin(), 0.0);
                double m = sqrt(m_squared);
                std::for_each(dr.begin(), dr.end(), [m](auto& d) { return d / m; });
                // dx,dy of the parent curve X-axis
                pcDx = dr[0];
                pcDy = dr[1];
            }

            // start of trimmed curve
            double pcStartX = 0.0, pcStartY = 0.0;
            double pcStartDx = 1.0, pcStartDy = 0.0;
            if (start)
            {
               // the spiral doesn't start at the inflection point
               // compute the point where it starts
                auto x = boost::math::quadrature::trapezoidal(fnX, 0.0, start / s);
                auto y = boost::math::quadrature::trapezoidal(fnY, 0.0, start / s);

                // compute the slope of the spiral at the start point
                auto dx = s ? fnX(start/s) / s : 1.0;
                auto dy = s ? fnY(start/s) / s : 0.0;

                pcStartX = x * pcDx - y * pcDy + pcX;
                pcStartY = x * pcDy + y * pcDx + pcY;
                pcStartDx = dx * pcDx - dy * pcDy;
                pcStartDy = dx * pcDy + dy * pcDx;
            }

            geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);
            eval_ = [start, s, pcX, pcY, pcDx, pcDy, pcStartX, pcStartY, pcStartDx, pcStartDy, fnX, fnY, geometry_adjuster = geometry_adjuster_](double u) {

                u += start;

                // integration limits, integrate from a to b
                auto b = s ? u / s : 0.0;

                // point on parent curve
                auto x = boost::math::quadrature::trapezoidal(fnX, 0.0, b);
                auto y = boost::math::quadrature::trapezoidal(fnY, 0.0, b);
                auto dx = s ? fnX(b) / s : 1.0;
                auto dy = s ? fnY(b) / s : 0.0;

                auto x1 = x * pcDx - y * pcDy + pcX;
                auto y1 = x * pcDy + y * pcDx + pcY;
                auto dx1 = dx * pcDx - dy * pcDy;
                auto dy1 = dx * pcDy + dy * pcDx;

                auto x2 = (x1 - pcStartX) * pcStartDx - (y1 - pcStartY) * (-pcStartDy);
                auto y2 = (x1 - pcStartX) * (-pcStartDy) + (y1 - pcStartY) * pcStartDx;
                auto dx2 = dx1 * pcStartDx + dy1 * (-pcStartDy);
                auto dy2 = dx1 * (-pcStartDy) + dy1 * pcStartDx;

                Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
                m.col(0) = Eigen::Vector4d(dx2, dy2, 0, 0);
                m.col(1) = Eigen::Vector4d(-dy2, dx2, 0, 0);
                m.col(3) = Eigen::Vector4d(x2, y2, 0.0, 1.0);
                return geometry_adjuster->transform_and_adjust(u, m);

                //auto pcX = boost::math::quadrature::trapezoidal(fnX, 0.0, b) + pcCenterX - pcStartX;
                //auto pcY = boost::math::quadrature::trapezoidal(fnY, 0.0, b) + pcCenterY - pcStartY;

                //auto angle1 = atan2(pcStartDy, pcStartDx);
                //auto angle2 = atan2(pcDy, pcDx);
                //auto angle = angle2 - angle1;
                //auto csX = pcX * cos(angle) - pcY * sin(angle);
                //auto csY = pcX * sin(angle) + pcY * cos(angle);

                //// From https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcSpiral.htm, x = Integral(fnX du), y = Integral(fnY du)
                //// The tangent slope of a curve is the derivate of the curve, so the derivitive of an integral, is just the function
                //auto dx = s ? fnX(b) / s : 1.0;
                //auto dy = s ? fnY(b) / s : 0.0;


                //Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
                //m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
                //m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
                //m.col(3) = Eigen::Vector4d(csX, csY, 0.0, 1.0);
                //return geometry_adjuster->transform_and_adjust(u, m);
            };
        } else if (segment_type_ == ST_VERTICAL) {

           // This functor is f'(x) = dy/dx
            auto df = [fnX,fnY](double t) -> double {
                return fnY(t) / fnX(t);
            };

            // This functor computes the curve length
            // Integral (sqrt (f'(x) ^ 2 + 1)dx
            auto fc = [df](double x) -> double {
                auto fs = [df](double x) -> double {
                    return sqrt(pow(df(x), 2) + 1);
                };
                auto s = boost::math::quadrature::trapezoidal(fs, 0.0, x);
                return s;
            };

            eval_ = [s,fnX,fnY,fc](double u) -> Eigen::Matrix4d {
                // find x when u - s = 0
                std::uintmax_t max_iter = 5000;
                //auto max_iter_ = max_iter;
                auto tol = [](double a, double b) { return fabs(b - a) < 1.0E-09; };
                auto ux = u;
                try {
                    auto f = [fc, u](double x) -> double { return fc(x) - u; };
                    auto result = boost::math::tools::bracket_and_solve_root(f, u, 2.0, true, tol, max_iter);
                    ux = result.first;
                } catch (...) {
                    Logger::Warning("root solver failed");
                }

                // integration limits, integrate from a to b
                auto a = 0.0;
                auto b = s ? u / s : 0.0;
                auto y = boost::math::quadrature::trapezoidal(fnY, a, b); // - start_y;

                auto dx = s ? fnX(b)/s : 1.0;
                auto dy = s ? fnY(b)/s : 0.0;

                Eigen::Matrix4d m;
                m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
                m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
                m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);
                m.col(3) = Eigen::Vector4d(0.0, y, 0.0, 1.0); 

                return m;
            };
        } else if (segment_type_ == ST_CANT) {
            Logger::Error(std::runtime_error("Unexpected segment type encountered - cant is handled in set_cant_spiral_function - should never get here"));
            eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
       else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
    }

    // defines the eval_ functor for cant segments.
    // Cant returns D at a distance along the curve, u.
    // CantSlope returns the slope of the Cant function at u. CantSlope(u) is the derivative of Cant(u)
    void set_cant_spiral_function(mapping* mapping_, std::function<double(double)> Cant, std::function<double(double)> CantSlope) {
        geometry_adjuster_ = std::make_shared<cant_adjuster>(mapping_, inst_, next_inst_);
        eval_ = [geometry_adjuster = geometry_adjuster_, Cant, CantSlope](double u) -> Eigen::Matrix4d {
            auto cant = Cant(u);
            auto slope = CantSlope(u);

            auto angle = atan(slope);
            auto dx = cos(angle);
            auto dy = sin(angle);

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
            m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);
            m.col(3) = Eigen::Vector4d(0.0, cant, 0.0, 1.0);

            return geometry_adjuster->transform_and_adjust(u, m);
        };
    }

    // defines the eval_ functor for constant cant segments.
    // the parent curve is IfcClothoid
    // For all the other cant types with spiral parent curves, just applying the cant_adjuster works
    // when compared to the results published at https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/
    // However, for IfcClothoid, the cant needs to be adjusted by the IfcCurveSegment.Placement.Y value to make the results
    // match those from the bSI Railway Room unit tests
    void set_clothoid_cant_spiral_function(mapping* mapping_, std::function<double(double)> Cant, std::function<double(double)> CantSlope) {
        geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);
        auto cant_adjuster_ = std::make_shared<cant_adjuster>(mapping_, inst_, next_inst_);
        eval_ = [geometry_adjuster = geometry_adjuster_,cant_adjuster=cant_adjuster_, Cant, CantSlope](double u) -> Eigen::Matrix4d {
            auto cant = Cant(u);
            auto slope = CantSlope(u);

            // this is the hack that makes this function different from set_cant_spiral_function
            cant += geometry_adjuster->get_placement().col(3)(1);

            auto angle = atan(slope);
            auto dx = cos(angle);
            auto dy = sin(angle);

            Eigen::Matrix4d m;
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
            m.col(2) = Eigen::Vector4d(0, 0, 1.0, 0);
            m.col(3) = Eigen::Vector4d(0.0, cant, 0.0, 1.0);

            return cant_adjuster->transform_and_adjust(u, m);
        };
    }

#ifdef SCHEMA_HAS_IfcClothoid
   void operator()(const IfcSchema::IfcClothoid* c) {
      // see https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcClothoid.htm
      // also see, https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Partial_Templates/Geometry/Curve_Segment_Geometry/Clothoid_Transition_Segment/content.html,
      auto A = c->ClothoidConstant();

      if (segment_type_ == ST_CANT) {
          auto Cant = [A,L=length_*length_unit_](double t) -> double 
             { return A ? L*A * t / fabs(pow(A, 3)) : 0.0; };
          auto CantSlope = [A, L = length_ * length_unit_](double /*t*/) -> double 
             { return A ? L*A / fabs(pow(A, 3)) : 0.0; };
          set_clothoid_cant_spiral_function(mapping_, Cant, CantSlope);
      } else {
          auto s = fabs(A * sqrt(PI)); // curve length when u = 1.0
          auto fn_x = [A, s](double t) -> double { return A ? s * cos(PI * A * t * t / (2 * fabs(A))) : 0.0; };
          auto fn_y = [A, s](double t) -> double { return A ? s * sin(PI * A * t * t / (2 * fabs(A))) : 0.0; };
          set_spiral_function(mapping_, s, fn_x, fn_y);
      }
   }
#endif

#if defined SCHEMA_HAS_IfcCosineSpiral
   void operator()(const IfcSchema::IfcCosineSpiral* c) {
      auto constant_term = c->ConstantTerm();
      auto cosine_term = c->CosineTerm();
      auto L = length()*length_unit_;
      if (segment_type_ == ST_HORIZONTAL) {

          auto theta = [constant_term, cosine_term, L, lu = length_unit_](double t) -> double {
              auto a0 = constant_term.has_value() ? t / (constant_term.value() * lu) : 0.0;
              auto a1 = (L / PI) * (1.0 / (cosine_term * lu)) * sin((PI / L) * t);
              return a0 + a1;
          };
          auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
          auto fn_y = [theta](double t) -> double { return sin(theta(t)); };
          double s = 1.0;
          set_spiral_function(mapping_, s, fn_x, fn_y);
      } else if (segment_type_ == ST_CANT) {
          auto Cant = [constant_term, cosine_term, L, lu = length_unit_](double t) -> double 
             {
              auto a0 = constant_term.has_value() ? L / (constant_term.value() * lu) : 0.0;
              auto a1 = (L / (cosine_term * lu)) * cos(PI * t*lu/L);
              return a0 + a1;
             };
          auto CantSlope = [cosine_term, L, lu = length_unit_](double t) -> double {
              auto a1 = -(PI/L)*(L / (cosine_term * lu)) * sin(PI * t * lu / L);
              return a1;
          };
          set_cant_spiral_function(mapping_, Cant, CantSlope);
      } else if (segment_type_ == ST_VERTICAL) {
          Logger::Error(std::runtime_error("IfcCosineSpiral cannot be used for vertical alignment"));
          eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      } else {
          Logger::Error(std::runtime_error("Unexpected segment type encountered"));
          eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      }
   }
#endif

#if defined SCHEMA_HAS_IfcSineSpiral
   void operator()(const IfcSchema::IfcSineSpiral* c) {
       auto constant_term = c->ConstantTerm();
      auto linear_term = c->LinearTerm();
      auto sine_term = c->SineTerm();
      auto L = length() * length_unit_;
      if (segment_type_ == ST_HORIZONTAL) {
          auto theta = [constant_term, linear_term, sine_term, L, lu = length_unit_](double t) -> double {
              auto a0 = constant_term.has_value() ? t / (constant_term.value() * lu) : 0.0;
              auto a1 = linear_term.has_value() ? sign(linear_term.value()) * pow(t / (linear_term.value() * lu), 2.0) / 2.0 : 0.0;
              auto a2 = -1.0 * (L / (2 * PI * sine_term * lu)) * (cos(2 * PI * t / L) - 1.0);
              return a0 + a1 + a2;
          };
          auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
          auto fn_y = [theta](double t) -> double { return sin(theta(t)); };
          double s = 1.0;
          set_spiral_function(mapping_, s, fn_x, fn_y);
      } else if (segment_type_ == ST_CANT) {
          auto Cant = [constant_term,linear_term,sine_term, L, lu = length_unit_](double t) -> double {
              auto a0 = constant_term.has_value() ? L / (constant_term.value() * lu) : 0.0;
              auto a1 = linear_term.has_value() ? sign(linear_term.value()) * pow(L / (linear_term.value() * lu), 2.0) * (t/L) : 0.0;
              auto a2 = (L / (sine_term * lu)) * sin(2 * PI * t / L);
              return a0 + a1 + a2;
          };
          auto CantSlope = [linear_term, sine_term, L, lu = length_unit_](double t) -> double {
              auto a1 = linear_term.has_value() ? sign(linear_term.value()) * pow(L / (linear_term.value() * lu), 2.0) * (1.0 / L) : 0.0;
              auto a2 = (2*PI/L)*(L / (sine_term * lu)) * cos(2 * PI * t / L);
              return a1 + a2;
          };
          set_cant_spiral_function(mapping_, Cant, CantSlope);
      } else if (segment_type_ == ST_VERTICAL) {
          Logger::Error(std::runtime_error("IfcSineSpiral cannot be used for vertical alignment"));
          eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      } else {
          Logger::Error(std::runtime_error("Unexpected segment type encountered"));
          eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      }
   }
#endif

    void polynomial_spiral(boost::optional<double> A0, boost::optional<double> A1, boost::optional<double> A2, boost::optional<double> A3, boost::optional<double> A4, boost::optional<double> A5, boost::optional<double> A6, boost::optional<double> A7) {
         auto theta = [A0, A1, A2, A3, A4, A5, A6, A7, start=start_*length_unit_,lu=length_unit_](double t) {
            //t += start;
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
      set_spiral_function(mapping_, s, fn_x, fn_y);
    }

    void polynomial_cant_spiral(boost::optional<double> A0, boost::optional<double> A1, boost::optional<double> A2, boost::optional<double> A3, boost::optional<double> A4, boost::optional<double> A5, boost::optional<double> A6, boost::optional<double> A7) {
        auto Cant = [A0, A1, A2, A3, A4, A5, A6, A7, start=start_*length_unit_,L=length_*length_unit_, lu=length_unit_,length=length_](double t) {
            t += start;
            auto a0 = A0.has_value() ? 1 / (A0.value() * lu) : 0.0;
            auto a1 = A1.has_value() ? A1.value() * lu * t / fabs(std::pow(A1.value() * lu, 3)) : 0.0;
            auto a2 = A2.has_value() ? std::pow(t, 2) / std::pow(A2.value() * lu, 3) : 0.0;
            auto a3 = A3.has_value() ? A3.value() * lu * std::pow(t, 3) / fabs(std::pow(A3.value() * lu, 5)) : 0.0;
            auto a4 = A4.has_value() ? std::pow(t, 4) / std::pow(A4.value() * lu, 5) : 0.0;
            auto a5 = A5.has_value() ? A5.value() * lu * std::pow(t, 5) / fabs(std::pow(A5.value() * lu, 7)) : 0.0;
            auto a6 = A6.has_value() ? std::pow(t, 6) / std::pow(A6.value() * lu, 7) : 0.0;
            auto a7 = A7.has_value() ? A7.value() * lu * std::pow(t, 7) / fabs(std::pow(A7.value() * lu, 9)) : 0.0;
            return L*(a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7);
        };

        auto CantSlope = [A1, A2, A3, A4, A5, A6, A7, start = start_ * length_unit_, L = length_ * length_unit_, lu = length_unit_, length = length_](double t) {
            t += start;
            auto a1 = A1.has_value() ? A1.value() * lu / fabs(std::pow(A1.value() * lu, 3)) : 0.0;
            auto a2 = A2.has_value() ? 2 * t / std::pow(A2.value() * lu, 3) : 0.0;
            auto a3 = A3.has_value() ? 3 * A3.value() * lu * std::pow(t, 2) / fabs(std::pow(A3.value() * lu, 5)) : 0.0;
            auto a4 = A4.has_value() ? 4 * std::pow(t, 3) / std::pow(A4.value() * lu, 5) : 0.0;
            auto a5 = A5.has_value() ? 5 * A5.value() * lu * std::pow(t, 4) / fabs(std::pow(A5.value() * lu, 7)) : 0.0;
            auto a6 = A6.has_value() ? 6 * std::pow(t, 5) / std::pow(A6.value() * lu, 7) : 0.0;
            auto a7 = A7.has_value() ? 7 * A7.value() * lu * std::pow(t, 6) / fabs(std::pow(A7.value() * lu, 9)) : 0.0;
            return L * (a1 + a2 + a3 + a4 + a5 + a6 + a7);
        };

        set_cant_spiral_function(mapping_, Cant, CantSlope);
    }

#ifdef SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
   void operator()(const IfcSchema::IfcSecondOrderPolynomialSpiral* c)
   {
      auto A0 = c->ConstantTerm();
      auto A1 = c->LinearTerm();
      auto A2 = c->QuadraticTerm();
      boost::optional<double> A3, A4, A5, A6, A7;

      if (segment_type_ == ST_CANT) {
          polynomial_cant_spiral(A0, A1, A2, A3, A4, A5, A6, A7);
      } else {
          polynomial_spiral(A0, A1, A2, A3, A4, A5, A6, A7);
      }
   }
#endif

#ifdef SCHEMA_HAS_IfcThirdOrderPolynomialSpiral
    void operator()(const IfcSchema::IfcThirdOrderPolynomialSpiral* c) {
        auto A0 = c->ConstantTerm();
        auto A1 = c->LinearTerm();
        auto A2 = c->QuadraticTerm();
        auto A3 = c->CubicTerm();
        boost::optional<double> A4, A5, A6, A7;


        if (segment_type_ == ST_CANT) {
            polynomial_cant_spiral(A0, A1, A2, A3, A4, A5, A6, A7);
        } else {
            polynomial_spiral(A0, A1, A2, A3, A4, A5, A6, A7);
        }
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

        if (segment_type_ == ST_CANT) {
            polynomial_cant_spiral(A0, A1, A2, A3, A4, A5, A6, A7);
        } else {
            polynomial_spiral(A0, A1, A2, A3, A4, A5, A6, A7);
        }
    }
#endif

   void operator()(const IfcSchema::IfcCircle* c)
   {
      if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
         auto R = c->Radius() * length_unit_;
         auto position = c->Position()->as<IfcSchema::IfcAxis2Placement2D>();
         auto location = position->Location()->as<IfcSchema::IfcCartesianPoint>();

         // center point of the parent curve
         auto pcCenterX = location->Coordinates()[0];
         auto pcCenterY = location->Coordinates()[1];
          
         // normalize the direction ratios
         auto ref_direction = position->RefDirection();
         auto pcDx = 1.0, pcDy = 0.0;
         if (ref_direction) {
             auto dr = ref_direction->DirectionRatios();
             double m_squared = std::inner_product(dr.begin(), dr.end(), dr.begin(), 0.0);
             double m = sqrt(m_squared);
             std::for_each(dr.begin(), dr.end(), [m](auto& d) { return d / m; });
             // dx,dy of the parent curve X-axis
             pcDx = dr[0];
             pcDy = dr[1];
         }

         // angle from X = 0 to the parent curve X-axis
         auto pc_axis_angle = atan2(pcDy, pcDx);
         // sweep angle from the parent curve X-axis to the first point on the trimmed curve
         auto sweep_start_angle = start_ / R;
         // angle from X = 0 to the first point on the trimmed curve
         auto start_angle = pc_axis_angle + sweep_start_angle;

         // first point on the trimmed curve
         auto pcStartX = pcCenterX + R * cos(start_angle);
         auto pcStartY = pcCenterY + R * sin(start_angle);

         auto sign_l = sign(length_);

         geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

         projected_length_ = length_;
         eval_ = [R, pcCenterX, pcCenterY, pcStartX, pcStartY, pc_axis_angle, start_angle, sign_l, segment_type=segment_type_, geometry_adjuster = geometry_adjuster_](double u)
         {
             // If segment_type == ST_VERTICAL and adjustments are enabled the input u is measured along the horizontal.
             // u needs to be the arc length along the circle. If adjustments are disabled u is one of the end points so its arc length
             if (segment_type == ST_VERTICAL && geometry_adjuster->enable_adjustments()) {
                 // x and y are distance from center of circle as if circle was centered at (0,0)
                 auto x = pcStartX + u - pcCenterX;
                 auto y = -sign_l*sqrt(R * R - x * x);
                 // move x and y so they are relative to the center of the circle
                 x += pcCenterX;
                 y += pcCenterY;
                 // compute the distance between the start point and (x,y)
                 auto c = sqrt(pow(x - pcStartX,2.0) + pow(y - pcStartY,2.0));
                 // compute the subtended angle
                 // c = 2R*sin(delta/2)
                 auto delta = 2 * asin(c / (2 * R));
                 // compute the arc length (this will always be a positive value)
                 u = R * fabs(delta);
             }

            // u is measured along the circle
            // angle from the X=0 axis to the current point
            auto delta = sign_l * u / R;
            auto angle = start_angle + delta;

            // point on the parent curve
            auto pcX = R * cos(angle) + pcCenterX;
            auto pcY = R * sin(angle) + pcCenterY;

            // translate parent curve point so it is relative to the parent curve start point
            pcX -= pcStartX;
            pcY -= pcStartY;

            // rotate the parent curve point about its start point
            // to eliminate the orientation of the parent curve axes
            auto rotate = -(sign_l*PI / 2 + start_angle);
            auto csX = pcX * cos(rotate) - pcY * sin(rotate);
            auto csY = pcX * sin(rotate) + pcY * cos(rotate);

            // direction of vector tangent to the curve segment
            // at this point the curve has been rotated so the start is
            // tangent to [1,0] so dx, dy in that coordinate system
            // is dependent only on delta
            auto dx = cos(delta);
            auto dy = sin(delta);

            // transform the point into the curve segment coordinate system
            Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
            m.col(3) = Eigen::Vector4d(csX, csY, 0.0, 1.0);
            return geometry_adjuster->transform_and_adjust(u, m);
         };
      }
      else if (segment_type_ == ST_CANT) {
         Logger::Warning(std::runtime_error("Use of IfcCircle for cant is not supported"));
         eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      } else {
         Logger::Error(std::runtime_error("Unexpected segment type encountered"));
         eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      }
   }

   void operator()(const IfcSchema::IfcPolyline* pl)
   {
       if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
           struct Range {
               double u_start;
               double u_end;
               std::function<bool(double, double, double)> compare;
               bool operator<(const Range& r) const { return u_start < r.u_start; }
           };

           using Function = std::function<Eigen::Matrix4d(double u)>;
           std::map<Range, Function> fns;

           auto p = pl->Points();
           if (p->size() < 2) {
               Logger::Error(std::runtime_error("invalid polyline - must have at least 2 points")); // this should never happen, but just in case it does
           }

           auto std_compare = [](double u_start, double u, double u_end) { return u_start <= u && u < u_end; };
           auto end_compare = [](double u_start, double u, double u_end) { return u_start <= u && u <= (u_end + 0.001); };

           auto begin = p->begin();
           auto iter = begin;
           auto end = p->end();
           auto last = std::prev(end);
           auto p1 = *(iter++);

           if (p1->Coordinates().size() != 2) {
               Logger::Warning("Expected IfcPolyline.Points to be 2D", pl);
           }

           auto u = 0.0;
           for (; iter != end; iter++) {
               auto p2 = *iter;

               auto p1x = p1->Coordinates()[0];
               auto p1y = p1->Coordinates()[1];

               auto p2x = p2->Coordinates()[0];
               auto p2y = p2->Coordinates()[1];

               auto dx = p2x - p1x;
               auto dy = p2y - p1y;
               auto l = sqrt(dx * dx + dy * dy);

               if (l < mapping_->settings().get<ifcopenshell::geometry::settings::Precision>().get()) {
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

               fns.insert(std::make_pair(Range{u, u + l, iter == last ? end_compare : std_compare}, fn));

               p1 = p2;
               u = u + l;
           }

           geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

           projected_length_ = length_;

           eval_ = [fns, geometry_adjuster = geometry_adjuster_](double u) {
               auto iter = std::find_if(fns.cbegin(), fns.cend(), [=](const auto& fn) {
                   auto [u_start, u_end, compare] = fn.first;
                   return compare(u_start, u, u_end);
               });

               if (iter == fns.end()) {
                   throw std::runtime_error("invalid distance from start"); // this should never happen, but just in case it does, throw an exception so the problem gets automatically detected
               }

               const auto& [u_start, u_end, compare] = iter->first;
               const auto& fn = iter->second;
               Eigen::Matrix4d m = fn(u - u_start); // (u - u_start) is distance from start of this segment of the polyline
               return geometry_adjuster->transform_and_adjust(u, m);
           };
       } else if (segment_type_ == ST_CANT) {
           Logger::Warning(std::runtime_error("Use of IfcPolyline for cant is not supported"));
           eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
       } else {
           Logger::Warning(std::runtime_error("Unexpected segment type encountered"));
           eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
       }
   }

   void operator()(const IfcSchema::IfcLine* l) {
      projected_length_ = length_;

      if (segment_type_ == ST_HORIZONTAL) {
          geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

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
          auto pcDx = dr[0];
          auto pcDy = dr[1];

          auto pcStartX = c[0] * length_unit_;
          auto pcStartY = c[1] * length_unit_;

          eval_ = [pcStartX, pcStartY, pcDx, pcDy, geometry_adjuster = geometry_adjuster_](double u) {
              auto pcX = pcStartX + pcDx*u;
              auto pcY = pcStartY + pcDy*u;

              // translate parent curve point to the origin
              pcX -= pcStartX;
              pcY -= pcStartY;

              auto rotate = -atan2(pcDy, pcDx);
              auto csX = pcX * cos(rotate) - pcY * sin(rotate);
              auto csY = pcX * sin(rotate) + pcY * cos(rotate);

              Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
              m.col(0) = Eigen::Vector4d(1, 0, 0, 0);
              m.col(1) = Eigen::Vector4d(0, 1, 0, 0);
              m.col(3) = Eigen::Vector4d(csX, csY, 0.0, 1.0);
              return geometry_adjuster->transform_and_adjust(u, m);
          };
      }
      else if (segment_type_ == ST_VERTICAL) {
         geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

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

         eval_ = [px, py, dx, dy, geometry_adjuster=geometry_adjuster_](double u) {
            auto x = px + u/dx;
            auto y = py;

            Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
            m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
            return geometry_adjuster->transform_and_adjust(u, m);
         };
      }
      else if (segment_type_ == ST_CANT) {
          geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);
          auto cant_adjuster_ = std::make_shared<cant_adjuster>(mapping_, inst_, next_inst_);
          eval_ = [geometry_adjuster = geometry_adjuster_,cant_adjuster=cant_adjuster_](double u) {
              Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
              return geometry_adjuster->transform_and_adjust(u, cant_adjuster->transform_and_adjust(u,m));
          };
      }
      else {
          Logger::Warning(std::runtime_error("Unexpected segment type encountered"));
          eval_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
      }
    }

   void operator()(const IfcSchema::IfcPolynomialCurve* pc) {
      // see https://forums.buildingsmart.org/t/ifcpolynomialcurve-clarification/4716 for discussion on IfcPolynomialCurve
      auto coeffX = pc->CoefficientsX().get_value_or(std::vector<double>());
      auto coeffY = pc->CoefficientsY().get_value_or(std::vector<double>());
      auto coeffZ = pc->CoefficientsZ().get_value_or(std::vector<double>());
      if (!coeffZ.empty())
         Logger::Warning("Expected IfcPolynomialCurve.CoefficientsZ to be undefined for alignment geometry. Coefficients ignored.", pc);

      auto length_unit = length_unit_;

      geometry_adjuster_ = std::make_shared<GEOMETRY_ADJUSTER>(mapping_, inst_, next_inst_);

      if (segment_type_ == ST_HORIZONTAL) {
         // @rb need to work on this - u is distance along curve, this differs from vertical where u = x
         projected_length_ = length_;

         // This functor evaluates the derivative of the Y polynomial
         auto df = [coeffY, length_unit](double x) -> double {
             auto begin = std::next(coeffY.begin());
             auto iter = begin;
             auto end = coeffY.end();
             auto length_conversion = length_unit;
             double value = 0;
             for (; iter != end; iter++) {
                 auto exp = std::distance(begin, iter);
                 auto coeff = (*iter) * length_conversion;
                 value += (double)exp * coeff * pow(x, exp);
                 length_conversion /= length_unit;
             }
             return value;
            };

         // This functor computes the curve length
         // Integral (sqrt (f'(x) ^ 2 + 1)dx
         auto fc = [df](double x) -> double {
             auto fs = [df](double x) -> double {
                return sqrt(pow(df(x), 2) + 1);
             };
             auto s = boost::math::quadrature::trapezoidal(fs, 0.0, x);
             return s;
         };

         eval_ = [start=start_,coeffX,coeffY,length_unit,geometry_adjuster = geometry_adjuster_, fc](double u) -> Eigen::Matrix4d {
            // find x when u - s = 0
             std::uintmax_t max_iter = 5000;
             //auto max_iter_ = max_iter;
             auto tol = [](double a, double b) { return fabs(b - a) < 1.0E-09; };
             auto ux = u;
             try {
                 auto f = [fc, u](double x) -> double { return fc(x) - u; };
                 auto result = boost::math::tools::bracket_and_solve_root(f, u, 2.0, true, tol, max_iter);
                 ux = result.first;
             } catch (...) {
                 Logger::Warning("root solver failed");
             }

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
                     position[i] += coeff * (pow(ux /*+ start*/, exp)/* - pow(start, exp)*/);

                     if (iter != begin) {
                         slope[i] += coeff * exp * pow(ux/* + start*/, exp - 1);
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
         projected_length_ = length_;

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
         eval_ = [](double /*u*/) -> Eigen::Matrix4d {
             return Eigen::Matrix4d::Identity();
         };
      } else {
         Logger::Error(std::runtime_error("Unexpected segment type encountered"));
         eval_ = [](double /*u*/) -> Eigen::Matrix4d {
             return Eigen::Matrix4d::Identity();
         };
      }
   }

   // Take the boost::type value from mpl::for_each and test it against our curve instance
   template <typename T>
   void operator()(boost::type<T>) {
      if (parent_curve_->as<T>()) {
           (*this)(parent_curve_->as<T>());
      }
   }

   double length() const {
      return (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_CANT) ? length_ : projected_length_;
   }

   const std::optional<std::function<Eigen::Matrix4d(double)>>& evaluation_function() const {
      return eval_;
   }
};
} // namespace

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