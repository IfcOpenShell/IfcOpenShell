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

#include <boost/math/quadrature/trapezoidal.hpp>
#include <boost/math/tools/roots.hpp>
#include <boost/mpl/for_each.hpp>
#include <boost/mpl/vector.hpp>
#include <numeric>

namespace {
// @todo: rb is there a common math library these functions can be moved to?
auto sign = [](double v) -> double { return v ? v / fabs(v) : 1.0; };

enum segment_type_t {
    ST_HORIZONTAL,
    ST_VERTICAL,
    ST_CANT
};

// @todo use std::numbers::pi when upgrading to C++ 20
static const double PI = boost::math::constants::pi<double>();

double translate_to_length_measure(const IfcSchema::IfcCurve* crv, double param_value) {
    if (std::abs(param_value) < 1.e-7) {
        return param_value;
    } else if (auto line = crv->as<IfcSchema::IfcLine>()) {
        return line->Dir()->Magnitude() * param_value;
    } else if (auto clothoid = crv->as<IfcSchema::IfcClothoid>()) {
       // param_value = 1.0, corresponds to tangent direction = PI/2
       // param_value = (arc length)/fabs(A*PI)
        return fabs(clothoid->ClothoidConstant()*sqrt(PI))*param_value;
    } else if (auto circ = crv->as<IfcSchema::IfcCircle>()) {
        return circ->Radius() * param_value;
    } else if (auto circ = crv->as<IfcSchema::IfcPolynomialCurve>()) {
        return param_value;
    } else {
        throw std::runtime_error("Unsupported curve measure type");
    }
}

double translate_if_param_value(const IfcSchema::IfcCurve* crv, IfcSchema::IfcCurveMeasureSelect* val) {
    if (auto param = val->as<IfcSchema::IfcParameterValue>()) {
        // We don't care whether length- or positive length measure.
        return translate_to_length_measure(crv, *param);
    } else {
        return val->data().get_attribute_value(0);
    }
}

// vector of parent curve types that are supported for IfcCurveSegment.ParentCurve
typedef boost::mpl::vector<
      IfcSchema::IfcLine
    , IfcSchema::IfcCircle
    , IfcSchema::IfcPolynomialCurve
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
> curve_seg_types;

class curve_segment_evaluator {
  private:
    mapping* mapping_ = nullptr;
    const IfcSchema::IfcCurveSegment* inst_ = nullptr;      // this curve segment instance
    double length_unit_;
    double start_;
    double length_; // length along the curve, as provided from the IfcCurveSegment
    segment_type_t segment_type_;
    const IfcSchema::IfcCurve* parent_curve_ = nullptr;

    double projected_length_; // for vertical segments, this is the length of curve projected onto the "Distance Along" axis

    std::optional<std::function<Eigen::Matrix4d(double)>> parent_curve_fn_; // function for the parent curve. Function takes distances along, u, and returns the 4x4 position matrix
    std::optional<Eigen::Matrix4d> parent_curve_start_point_;                 // placement matrix for the parent curve

    std::optional<Eigen::Matrix4d> placement_; // placement of this segment
    std::optional<Eigen::Matrix4d> next_segment_placement_; // placement of the next segment

  public:
    curve_segment_evaluator(mapping* mapping, const IfcSchema::IfcCurveSegment* inst, const IfcSchema::IfcCurveSegment* next_inst, double length_unit, segment_type_t segment_type)
        : mapping_(mapping),
          inst_(inst),
          length_unit_(length_unit),
          segment_type_(segment_type),
          parent_curve_(inst->ParentCurve()) {
        start_ = translate_if_param_value(inst->ParentCurve(), inst->SegmentStart()) * length_unit;
        length_ = translate_if_param_value(inst->ParentCurve(), inst->SegmentLength()) * length_unit;

        if (inst) {
            placement_ = taxonomy::cast<taxonomy::matrix4>(mapping_->map(inst->Placement()))->ccomponents();
        }

        if (next_inst) {
            next_segment_placement_ = taxonomy::cast<taxonomy::matrix4>(mapping_->map(next_inst->Placement()))->ccomponents();
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

    const std::optional<std::function<Eigen::Matrix4d(double)>>& parent_curve_function() const {
        return parent_curve_fn_;
    }

    const std::optional<Eigen::Matrix4d>& parent_curve_start_point() const {
        return parent_curve_start_point_;
    }

    const std::optional<Eigen::Matrix4d>& segment_placement() const {
        return placement_;
    }

    void set_spiral_function(double s, std::function<double(double)> fnX, std::function<double(double)> fnY) {
        if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
            projected_length_ = length_;

            // start of trimmed curve
            double pcStartX = 0.0, pcStartY = 0.0;
            double pcStartDx = 1.0, pcStartDy = 0.0;
            if (start_) {
                // the spiral doesn't start at the inflection point
                // compute the point where it starts
                pcStartX = boost::math::quadrature::trapezoidal(fnX, 0.0, start_ / s);
                pcStartY = boost::math::quadrature::trapezoidal(fnY, 0.0, start_ / s);

                // compute the slope of the spiral at the start point
                pcStartDx = s ? fnX(start_ / s) / s : 1.0;
                pcStartDy = s ? fnY(start_ / s) / s : 0.0;
            }

            Eigen::Matrix4d p = Eigen::Matrix4d::Identity();
            p.col(0) = Eigen::Vector4d(pcStartDx, pcStartDy, 0, 0);
            p.col(1) = Eigen::Vector4d(-pcStartDy, pcStartDx, 0, 0);
            p.col(3) = Eigen::Vector4d(pcStartX, pcStartY, 0, 1);
            parent_curve_start_point_ = p;

            std::function<double(double)> convert_u;
            if (segment_type_ == ST_HORIZONTAL)
            {
                convert_u = [](double u) -> double { return u; };
            } else {
                // This functor is f'(x) = dy/dx
                 auto df = [fnX,fnY](double t) -> double {
                    auto dy = fnY(t);
                    auto dx = fnX(t);
                    return dx ? dy / dx : 0.0;
                 };

                 // This functor computes the curve length
                 // Integral (sqrt (f'(x) ^ 2 + 1)dx
                 convert_u = [df](double x) -> double {
                     auto fs = [df](double x) -> double {
                         return sqrt(pow(df(x), 2) + 1);
                     };
                     auto s = boost::math::quadrature::trapezoidal(fs, 0.0, x);
                     return s;
                 };
            }

            parent_curve_fn_ = [start=start_, s, convert_u, fnX, fnY](double u) {
                u = convert_u(u+start);

                // integration limits, integrate from a to b
                auto b = s ? u / s : 0.0;

                // point on parent curve
                auto x = boost::math::quadrature::trapezoidal(fnX, 0.0, b);
                auto y = boost::math::quadrature::trapezoidal(fnY, 0.0, b);
                auto dx = s ? fnX(b) / s : 1.0;
                auto dy = s ? fnY(b) / s : 0.0;

                Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
                m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
                m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
                m.col(3) = Eigen::Vector4d(x, y, 0, 1);
                return m;
            };
        } else if (segment_type_ == ST_CANT) {
            Logger::Error(std::runtime_error("Unexpected segment type encountered - cant is handled in set_cant_spiral_function - should never get here"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        } else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
    }

    // defines the parent_curve_fn_ functor for cant segments.
    // Cant returns D at a distance along the curve, u.
    // CantSlope returns the slope of the Cant function at u. CantSlope(u) is the derivative of Cant(u)
    void set_cant_spiral_function(std::function<double(double)> Cant, std::function<double(double)> CantSlope) {
        parent_curve_fn_ = [Cant, CantSlope](double u) -> Eigen::Matrix4d {
            auto cant = Cant(u);
            auto slope = CantSlope(u);

            auto angle = atan(slope);
            auto dx = cos(angle);
            auto dy = sin(angle); 

            Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
            m.col(0) = Eigen::Vector4d(dx, dy, 0, 0);
            m.col(1) = Eigen::Vector4d(-dy, dx, 0, 0);
            m.col(3) = Eigen::Vector4d(0.0, cant, 0.0, 1.0);
            return m;
        };

        parent_curve_start_point_ = (*parent_curve_fn_)(0.0);
    }

    boost::optional<std::function<double(double)>> get_cant_superelevation_function() {
        boost::optional<std::function<double(double)>> fn;

        if (next_segment_placement_.has_value() && placement_.has_value()) {
            // cant superelevation should be y value (row 1)
            double y1 = (*placement_)(1, 3);
            double y2 = (*next_segment_placement_)(1, 3);

            // if y2-y1 = 0, there is no superelevation
            // so we need a Cant function that always returns zero
            if (!(y2 - y1)) {
                fn = [](double)->double { return 0.0; };
            }
        }

        return fn;
    }

#ifdef SCHEMA_HAS_IfcClothoid
    void operator()(const IfcSchema::IfcClothoid* c) {
        auto A = c->ClothoidConstant();

        if (segment_type_ == ST_CANT) {

           auto Cant = get_cant_superelevation_function(); // fn that always returns zero if there is no superelevation
            if (!Cant.has_value()) {
               // function not provided so there must be a superelevation - this function provides the superelevation transition
               Cant = [A, L = length_ * length_unit_](double t) -> double { return A ? L * A * t / fabs(pow(A, 3)) : 0.0; };
            }

            auto CantSlope = [A, L = length_ * length_unit_](double /*t*/) -> double { return A ? L * A / fabs(pow(A, 3)) : 0.0; };
            set_cant_spiral_function(*Cant, CantSlope);
        } else {
            auto s = fabs(A * sqrt(PI)); // curve length when u = 1.0
            auto fn_x = [A, s](double t) -> double { return A ? s * cos(PI * A * t * t / (2 * fabs(A))) : 0.0; };
            auto fn_y = [A, s](double t) -> double { return A ? s * sin(PI * A * t * t / (2 * fabs(A))) : 0.0; };
            set_spiral_function(s, fn_x, fn_y);
        }
    }
#endif

#if defined SCHEMA_HAS_IfcCosineSpiral
    void operator()(const IfcSchema::IfcCosineSpiral* c) {
        auto constant_term = c->ConstantTerm();
        auto cosine_term = c->CosineTerm();
        auto L = length() * length_unit_;
        if (segment_type_ == ST_HORIZONTAL) {

            auto theta = [constant_term, cosine_term, L, lu = length_unit_](double t) -> double {
                auto a0 = constant_term.has_value() ? t / (constant_term.value() * lu) : 0.0;
                auto a1 = (L / PI) * (1.0 / (cosine_term * lu)) * sin((PI / L) * t);
                return a0 + a1;
            };
            auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
            auto fn_y = [theta](double t) -> double { return sin(theta(t)); };
            double s = 1.0;
            set_spiral_function(s, fn_x, fn_y);
        } else if (segment_type_ == ST_CANT) {
            auto Cant = get_cant_superelevation_function(); // fn that always returns zero if there is no superelevation
            if (!Cant.has_value()) {
                // function not provided so there must be a superelevation - this function provides the superelevation transition
                Cant = [constant_term, cosine_term, L, lu = length_unit_](double t) -> double {
                    auto a0 = constant_term.has_value() ? L / (constant_term.value() * lu) : 0.0;
                    auto a1 = (L / (cosine_term * lu)) * cos(PI * t * lu / L);
                    return a0 + a1;
                };
            }

            auto CantSlope = [cosine_term, L, lu = length_unit_](double t) -> double {
                auto a1 = -(PI / L) * (L / (cosine_term * lu)) * sin(PI * t * lu / L);
                return a1;
            };
            set_cant_spiral_function(*Cant, CantSlope);
        } else if (segment_type_ == ST_VERTICAL) {
            Logger::Error(std::runtime_error("IfcCosineSpiral cannot be used for vertical alignment"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        } else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
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
            set_spiral_function(s, fn_x, fn_y);
        } else if (segment_type_ == ST_CANT) {
            auto Cant = get_cant_superelevation_function(); // fn that always returns zero if there is no superelevation
            if (!Cant.has_value()) {
                // function not provided so there must be a superelevation - this function provides the superelevation transition
                Cant = [constant_term, linear_term, sine_term, L, lu = length_unit_](double t) -> double {
                    auto a0 = constant_term.has_value() ? L / (constant_term.value() * lu) : 0.0;
                    auto a1 = linear_term.has_value() ? sign(linear_term.value()) * pow(L / (linear_term.value() * lu), 2.0) * (t / L) : 0.0;
                    auto a2 = (L / (sine_term * lu)) * sin(2 * PI * t / L);
                    return a0 + a1 + a2;
                };
            }

            auto CantSlope = [linear_term, sine_term, L, lu = length_unit_](double t) -> double {
                auto a1 = linear_term.has_value() ? sign(linear_term.value()) * pow(L / (linear_term.value() * lu), 2.0) * (1.0 / L) : 0.0;
                auto a2 = (2 * PI / L) * (L / (sine_term * lu)) * cos(2 * PI * t / L);
                return a1 + a2;
            };
            set_cant_spiral_function(*Cant, CantSlope);
        } else if (segment_type_ == ST_VERTICAL) {
            Logger::Error(std::runtime_error("IfcSineSpiral cannot be used for vertical alignment"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        } else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
    }
#endif

    void polynomial_spiral(boost::optional<double> A0, boost::optional<double> A1, boost::optional<double> A2, boost::optional<double> A3, boost::optional<double> A4, boost::optional<double> A5, boost::optional<double> A6, boost::optional<double> A7) {
        auto theta = [A0, A1, A2, A3, A4, A5, A6, A7, start = start_ * length_unit_, lu = length_unit_](double t) {
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
        set_spiral_function(s, fn_x, fn_y);
    }

    void polynomial_cant_spiral(boost::optional<double> A0, boost::optional<double> A1, boost::optional<double> A2, boost::optional<double> A3, boost::optional<double> A4, boost::optional<double> A5, boost::optional<double> A6, boost::optional<double> A7) {
        auto Cant = get_cant_superelevation_function(); // fn that always returns zero if there is no superelevation
        if (!Cant.has_value()) {
            // function not provided so there must be a superelevation - this function provides the superelevation transition
            Cant = [A0, A1, A2, A3, A4, A5, A6, A7, start = start_ * length_unit_, L = length_ * length_unit_, lu = length_unit_, length = length_](double t) {
                t += start;
                auto a0 = A0.has_value() ? 1 / (A0.value() * lu) : 0.0;
                auto a1 = A1.has_value() ? A1.value() * lu * t / fabs(std::pow(A1.value() * lu, 3)) : 0.0;
                auto a2 = A2.has_value() ? std::pow(t, 2) / std::pow(A2.value() * lu, 3) : 0.0;
                auto a3 = A3.has_value() ? A3.value() * lu * std::pow(t, 3) / fabs(std::pow(A3.value() * lu, 5)) : 0.0;
                auto a4 = A4.has_value() ? std::pow(t, 4) / std::pow(A4.value() * lu, 5) : 0.0;
                auto a5 = A5.has_value() ? A5.value() * lu * std::pow(t, 5) / fabs(std::pow(A5.value() * lu, 7)) : 0.0;
                auto a6 = A6.has_value() ? std::pow(t, 6) / std::pow(A6.value() * lu, 7) : 0.0;
                auto a7 = A7.has_value() ? A7.value() * lu * std::pow(t, 7) / fabs(std::pow(A7.value() * lu, 9)) : 0.0;
                return L * (a0 + a1 + a2 + a3 + a4 + a5 + a6 + a7);
            };
        }

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

        set_cant_spiral_function(*Cant, CantSlope);
    }

#ifdef SCHEMA_HAS_IfcSecondOrderPolynomialSpiral
    void operator()(const IfcSchema::IfcSecondOrderPolynomialSpiral* c) {
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

    void operator()(const IfcSchema::IfcCircle* c) {
        if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
            auto R = c->Radius() * length_unit_;
            auto parent_curve_position = taxonomy::cast<taxonomy::matrix4>(mapping_->map(c->Position()))->ccomponents();

            // center point of the parent curve
            auto pcCenterX = parent_curve_position(0, 3);
            auto pcCenterY = parent_curve_position(1, 3);
            auto pcDx = parent_curve_position(0, 0);
            auto pcDy = parent_curve_position(1, 0);

            // angle from X = 0 to the parent curve X-axis
            auto pc_axis_angle = atan2(pcDy, pcDx);
            // sweep angle from the parent curve X-axis to the first point on the trimmed curve
            auto sweep_start_angle = R ? start_ / R : 0.0;
            // angle from X = 0 to the first point on the trimmed curve
            auto start_angle = pc_axis_angle + sweep_start_angle;

            auto sign_l = sign(length_);

            projected_length_ = length_;

            std::function<double(double)> convert_u;
            if (segment_type_ == ST_HORIZONTAL) {
                convert_u = [](double u) { return u; };
            } else {
                auto curve_segment_placement = taxonomy::cast<taxonomy::matrix4>(mapping_->map(inst_->Placement()))->ccomponents();
                auto csStartX = curve_segment_placement(0, 3);
                auto csStartY = curve_segment_placement(1, 3);
                auto csStartDx = curve_segment_placement(0, 0);
                auto csStartDy = curve_segment_placement(1, 0);
                auto csCenterX = csStartX - sign_l * csStartDy * R;
                auto csCenterY = csStartY + sign_l * csStartDx * R;

                convert_u = [csStartX, csStartY, csCenterX, csCenterY, R, sign_l](double u) {
                    // for vertical, u is measured along the horizonal but we need it to be an arc length

                    // x and y are coordinates on the curve segment for horizontal distance u from the start point
                    // u is a horizontal distance so x = csStartX + u
                    // Recognizing the triangle
                    // R^2 = (u + csStartX - csCenterX)^2 + (y - csCenterY)^2
                    // solve for y
                    // (y - csCenterY) = sqrt( R^2 - (u + csStartX - csCenterX)^2 )
                    // y = csCenterY + sqrt( R^2 - (u + csStartX - csCenterX)^2 )
                    auto x = csStartX + u;
                    auto y = csCenterY - sign_l * sqrt(pow(R, 2) - pow(u + csStartX - csCenterX, 2));

                    // compute the chord distance between the start point and (x,y)
                    auto c = sqrt(pow(x - csStartX, 2.0) + pow(y - csStartY, 2.0));

                    // compute the subtended angle
                    // c = 2R*sin(delta/2)
                    auto delta = R ? 2.0 * asin(c / (2 * R)) : 0.0;

                    // compute the arc length (this will always be a positive value)
                    u = R * fabs(delta);
                    return u;
                };
            }

            parent_curve_fn_ = [segment_type = segment_type_, R, pcCenterX, pcCenterY, start_angle, sign_l, convert_u](double u) {
                u = convert_u(u);

                // u is measured along the circle
                // angle from the X=0 axis to the current point
                auto delta = R ? sign_l * u / R : 0.0;
                auto sweep_angle = start_angle + delta;
                auto cos_sweep_angle = cos(sweep_angle);
                auto sin_sweep_angle = sin(sweep_angle);

                // point on the parent curve
                auto pcX = R * cos_sweep_angle + pcCenterX;
                auto pcY = R * sin_sweep_angle + pcCenterY;

                auto pcDx = -sign_l * sin_sweep_angle;
                auto pcDy =  sign_l * cos_sweep_angle;

                Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
                m.col(0) = Eigen::Vector4d(pcDx, pcDy, 0, 0);
                m.col(1) = Eigen::Vector4d(-pcDy, pcDx, 0, 0);
                m.col(3) = Eigen::Vector4d(pcX, pcY, 0.0, 1.0);
                return m;
            };

            if (segment_type_ == ST_HORIZONTAL) {
                parent_curve_start_point_ = (*parent_curve_fn_)(start_);
            } else {
               // @todo - find a way to simplify this
               // For vertical circle "u" is a horizontal measurement and it needs to be converted
               // to a distance along the circle. However, when evaluating the start point,
               // start_ is distance along. parent_curve_fn_ will call it's convert_u method
               // which would be wrong in this case. For this reason, the start point of the parent curve
               // is explicitly computed here. This code is a little redundant with parent_curve_fn_.
                auto cos_start_angle = cos(start_angle);
                auto sin_start_angle = sin(start_angle);

                // point on the parent curve
                auto pcStartX = R * cos_start_angle + pcCenterX;
                auto pcStartY = R * sin_start_angle + pcCenterY;

                auto pcStartDx = -sign_l * sin_start_angle;
                auto pcStartDy =  sign_l * cos_start_angle;

                Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
                m.col(0) = Eigen::Vector4d(pcStartDx, pcStartDy, 0, 0);
                m.col(1) = Eigen::Vector4d(-pcStartDy, pcStartDx, 0, 0);
                m.col(3) = Eigen::Vector4d(pcStartX, pcStartY, 0.0, 1.0);
                parent_curve_start_point_ = m;
            }

        } else if (segment_type_ == ST_CANT) {
            Logger::Warning(std::runtime_error("Use of IfcCircle for cant is not supported"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        } else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
    }
    
    void operator()(const IfcSchema::IfcLine* l) {
       projected_length_ = length_;

       auto c = l->Pnt()->Coordinates();
       auto pcX = c[0] * length_unit_;
       auto pcY = c[1] * length_unit_;

       // 8.9.3.75 IfcVector https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcVector.htm
       // 8.9.3.30 IfcDirection https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcDirection.htm
       // "The IfcDirection does not imply a vector length, and the direction ratios does not have to be normalized."
       //
       // Therefore, the direction ratios need to be normalized to compute points on the line. 
       // 
       // Magnitude is not used because it relates to the parameterization of the line, which isn't currently done for IfcCurveSegment
       // @todo - parameterization was recently added so Magnitude needs to be taking into consideration
       auto dr = l->Dir()->Orientation()->DirectionRatios();

       // normalize the direction ratios
       double m_squared = std::inner_product(dr.begin(), dr.end(), dr.begin(), 0.0);
       double m = sqrt(m_squared);
       std::for_each(dr.begin(), dr.end(), [m](auto& d) { return d / m; });
       auto pcDx = dr[0];
       auto pcDy = dr[1];

       if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL || segment_type_ == ST_CANT) {
          std::function<double(double)> convert_u;
          if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_CANT) {
              convert_u = [](double u) { return u; }; // u is along curve
          } else {
             // u is along horizontal, convert to along curve
              convert_u = [pcDx](double u) { return u/pcDx; };
          }

          parent_curve_fn_ = [pcX, pcY, pcDx, pcDy, convert_u](double u) {
              u = convert_u(u);

              auto x = pcX + pcDx * u;
              auto y = pcY + pcDy * u;

              Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
              m.col(0) = Eigen::Vector4d(pcDx, pcDy, 0, 0);
              m.col(1) = Eigen::Vector4d(-pcDy, pcDx, 0, 0);
              m.col(3) = Eigen::Vector4d(x, y, 0.0, 1.0);
              return m;
          };

          parent_curve_start_point_ = (*parent_curve_fn_)(start_);
       } else {
            Logger::Warning(std::runtime_error("Unexpected segment type encountered"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
    }

    void operator()(const IfcSchema::IfcPolynomialCurve* pc) {
        // see https://forums.buildingsmart.org/t/ifcpolynomialcurve-clarification/4716 for discussion on IfcPolynomialCurve
        auto coeffX = pc->CoefficientsX().get_value_or(std::vector<double>());
        auto coeffY = pc->CoefficientsY().get_value_or(std::vector<double>());
        auto coeffZ = pc->CoefficientsZ().get_value_or(std::vector<double>());
        if (!coeffZ.empty()) {
            Logger::Warning("Expected IfcPolynomialCurve.CoefficientsZ to be undefined for alignment geometry. Coefficients ignored.", pc);
        }

        auto length_unit = length_unit_;

        if (segment_type_ == ST_HORIZONTAL || segment_type_ == ST_VERTICAL) {
            projected_length_ = length_;

            // There is one significant difference between IfcPolynomalCurve used for horizontal and vertical alignments.
            // For horizontal alignment, u is the distance along the curve. For vertical alignment, u is the horizontal distance.
            // From 4.2.2.2.8 the polynomial curve equation is in the form of y = Ax^3 for horizontal parabolic transition segments.
            // To evaluate the horizontal function, the value of x that corresponds to the distance along the curve u is needed.
            // This is what the convert_u functor does. For vertical curves, the convert_u functor simply returns x = u.
            std::function<double(double)> convert_u;

            if (segment_type_ == ST_HORIZONTAL) {
                // Distance along the curve is  Integral[0,x] (sqrt(f'(x)^2 + 1) dx

                // This functor is the derivative of y(x) => dy/dx = f'(x)
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
                // Integral[0,x] (sqrt(f'(x)^2 + 1) dx
                auto curve_length_fn = [df](double x) -> double {
                    auto fs = [df](double x) -> double {
                        return sqrt(pow(df(x), 2) + 1);
                    };
                    auto s = boost::math::quadrature::trapezoidal(fs, 0.0, x);
                    return s;
                };

                // There isn't a closed form solution to get x that corresponds to a distance along the curve, u
                // A numerical solution is required.
                // This functor finds the value of x such that s(x) - u = 0, where u is the input value and s is the
                // computed curve length.
                convert_u = [curve_length_fn](double u) -> double {
                    std::uintmax_t max_iter = 5000;
                    auto tol = [](double a, double b) { return fabs(b - a) < 1.0E-09; };
                    auto x = u; // start by assuming u = x (it's not, but it will be close)
                    try {
                        // set up the root finding function that evaluates s(x) - u
                        auto f = [curve_length_fn, u](double x) -> double { return curve_length_fn(x) - u; };
                        // use a root finder to get x
                        auto result = boost::math::tools::bracket_and_solve_root(f, x, 2.0, true, tol, max_iter);
                        x = result.first;
                    } catch (...) {
                        Logger::Warning("root solver failed");
                    }
                    return x;
                };
            } else {
                // for vertical, u = x
                convert_u = [](double u) -> double { return u; };
            }

            // This functor evaluates the polynomial at a distance u along the curve
            parent_curve_fn_ = [start = start_, coeffX, coeffY, length_unit, convert_u](double u) -> Eigen::Matrix4d {
                auto x = convert_u(u + start); // find x for u
                // evaluate the polynomial at x
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
                        position[i] += coeff * pow(x, exp);

                        if (iter != begin) {
                            slope[i] += coeff * exp * pow(x, exp - 1);
                        }

                        length_conversion /= length_unit;
                    }
                }

                auto X = position[0];
                auto Y = position[1];

                auto Dx = slope[0];
                auto Dy = slope[1];

                auto angle = atan2(Dy, Dx);
                Dx = cos(angle);
                Dy = sin(angle);

                Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
                m.col(0) = Eigen::Vector4d(Dx, Dy, 0, 0);
                m.col(1) = Eigen::Vector4d(-Dy, Dx, 0, 0);
                m.col(3) = Eigen::Vector4d(X, Y, 0.0, 1.0);
                return m;
            };

            parent_curve_start_point_ = (*parent_curve_fn_)(0.0); // start is added to u in parent_curve_fn_, so use 0.0 here
        } else if (segment_type_ == ST_CANT) {
            Logger::Warning(std::runtime_error("Use of IfcPolynomialCurve for cant is not supported"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        } else {
            Logger::Error(std::runtime_error("Unexpected segment type encountered"));
            parent_curve_fn_ = [](double /*u*/) -> Eigen::Matrix4d { return Eigen::Matrix4d::Identity(); };
        }
    }
};
} // namespace

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcCurveSegment* inst) {
    auto composite_curves = inst->UsingCurves();

    // Find the next segment after inst
    const IfcSchema::IfcCurveSegment* next_inst = nullptr;
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
        } else {
            Logger::Warning("IfcCurveSegment belongs to multiple IfcCompositeCurve instances. Cannot determine the next segment.");
        }
    }

    bool is_horizontal = false;
    bool is_vertical = false;
    bool is_cant = false;

    if (composite_curves) {
        for (auto& cc : *composite_curves) {
            if (cc->as<IfcSchema::IfcSegmentedReferenceCurve>()) {
                is_cant = true;
            } else if (cc->as<IfcSchema::IfcGradientCurve>()) {
                is_vertical = true;
            } else {
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
    const auto& parent_curve_fn = cse.parent_curve_function();
    const auto& parent_curve_start_point = cse.parent_curve_start_point();

    if (!parent_curve_fn || !parent_curve_start_point) {
        Logger::Error(std::runtime_error(inst->ParentCurve()->declaration().name() + " not implemented"), inst);
    }

    // Do a negative translation of the parent curve point relative to the start of the parent curve.
    // This moves parent_curve_fn(u=0.0) to coordinate (0,0).
    // This is done so the curve_segment_placement is applied relative to (0,0)
    Eigen::Matrix4d remove_parent_curve_translation = Eigen::Matrix4d::Identity();
    remove_parent_curve_translation.col(3) = -1.0 * (*parent_curve_start_point).col(3);
    remove_parent_curve_translation(3, 3) = 1.0;

    // Do a rotation so that the tangent of the parent curve is in the direction (1,0)
    // Example: if the parent curve IfcLine is at a 30 degree clockwise angle, this does
    // a 30 degree counter-clockwise rotation
    // Clockwise rotation matrix = [cos(angle) -sin(angle)]
    //                             [sin(angle)  cos(angle)]
    //
    // Counter-clockwise rotation = [ cos(angle) sin(angle)]
    //                              [-sin(angle) cos(angle)]
    //
    // That's just a sign flip in positions (0,1) and (1,0)
    Eigen::Matrix4d remove_parent_curve_rotation = *parent_curve_start_point;
    remove_parent_curve_rotation(0, 1) *= -1.0;
    remove_parent_curve_rotation(1, 0) *= -1.0;
    remove_parent_curve_rotation.col(3) = Eigen::Vector4d(0, 0, 0, 1); // remove the parent curve placement point

    const auto& curve_segment_placement = cse.segment_placement();

    std::function<Eigen::Matrix4d(double u)> fn;
    if (segment_type == ST_CANT)
    {
       // not sure if this is correct, but when applying my general formula to compute the 4x4 matrix of a point on curve segment,
       // p = curve_segment_placement * remove_parent_curve_rotation * remove_parent_curve_translation * parent_curve_point,
       // the directional vectors of curve_segment_placement are multiplied with the cant value (eg parent_curve_point(3,3)) and
       // cause the resulting z value to be slightly off. My solution is to change the upper 3x3 of the curve_segment_placement
       // matrix to identity. This results in correct cant values, but I think it messes up the resulting direction vectors
        Eigen::Matrix4d c = Eigen::Matrix4d::Identity();
        c.col(3) = (*curve_segment_placement).col(3);

        fn = [c, remove_parent_curve_rotation, remove_parent_curve_translation, parent_curve_fn](double u) -> Eigen::Matrix4d {
            Eigen::Matrix4d parent_curve_point = (*parent_curve_fn)(u);
            Eigen::Matrix4d p = c * remove_parent_curve_rotation * remove_parent_curve_translation * parent_curve_point;
            return p;
        };
    } else {
        fn = [curve_segment_placement, remove_parent_curve_rotation, remove_parent_curve_translation, parent_curve_fn](double u) -> Eigen::Matrix4d {
            auto parent_curve_point = (*parent_curve_fn)(u);
            return (*curve_segment_placement) * remove_parent_curve_rotation * remove_parent_curve_translation * parent_curve_point;
        };
    }

    auto length = cse.length();

    taxonomy::piecewise_function::spans_t spans;
    spans.emplace_back(fabs(length), fn);
    auto pwf = taxonomy::make<taxonomy::piecewise_function>(0.0, spans,&settings_,inst);
    return pwf;
}

#endif
