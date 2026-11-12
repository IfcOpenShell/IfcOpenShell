#include "function_item_evaluator.h"
#include "profile_helper.h"

#include <boost/math/quadrature/gauss_kronrod.hpp>
#include <complex>

#include <algorithm>
#include <array>
#include <cmath>

using namespace ifcopenshell::geom;

std::vector<double> ifcopenshell::geom::helmert_curve_point(double A0, double A1, double A2, double s) {
    auto theta = [A0, A1, A2](double t) -> double {
       auto a0 = A0 ? t / A0 : 0.0;
       auto a1 = A1 ? A1 * std::pow(t, 2) / (2 * fabs(std::pow(A1, 3))) : 0.0;
       auto a2 = A2 ? std::pow(t, 3) / (3 * std::pow(A2, 3)) : 0.0;
       return a0 + a1 + a2;
    };

    // The components are integrated as one complex value so the tolerance is relative to the chord, not to y, which
    // can be zero. The integral is taken over 0 to 1, scaled by s, because Boost compares each interval's error
    // estimate, which isn't scaled by its width, with a tolerance that is.
    auto tangent = [theta, s](double t) { return std::polar(1.0, theta(s * t)); };
    auto z = s * boost::math::quadrature::gauss_kronrod<double, 15>::integrate(tangent, 0.0, 1.0, 15, 1.0e-12);
    auto x = z.real();
    auto y = z.imag();
    auto angle = theta(s);
    return {x, y, angle};
}

namespace {
double precision(const ifcopenshell::geom::settings& settings) {
    return settings.get<ifcopenshell::geom::settings::Precision>().get();
}

// The boundaries of two functions evaluated at the same distance along (such as the horizontal
// and vertical of a gradient curve) within start..end, with boundaries closer than tolerance merged
std::vector<double> merge_boundaries(const std::vector<double>& a, const std::vector<double>& b, double start, double end, double tolerance) {
    std::vector<double> inside;
    for (const auto* boundaries : {&a, &b}) {
        for (double u : *boundaries) {
            if (start < u && u < end) {
                inside.push_back(u);
            }
        }
    }
    std::sort(inside.begin(), inside.end());

    std::vector<double> merged{start};
    for (double u : inside) {
        if (u - merged.back() > tolerance && end - u > tolerance) {
            merged.push_back(u);
        }
    }
    merged.push_back(end);
    return merged;
}

double distance_to_segment(const Eigen::Vector3d& p, const Eigen::Vector3d& a, const Eigen::Vector3d& b) {
    const Eigen::Vector3d ab = b - a;
    const double length_squared = ab.squaredNorm();
    const double t = length_squared > 0.0 ? std::clamp((p - a).dot(ab) / length_squared, 0.0, 1.0) : 0.0;
    return (p - (a + t * ab)).norm();
}

double angle_between(const Eigen::Vector3d& a, const Eigen::Vector3d& b) {
    const double norms = a.norm() * b.norm();
    return norms > 0.0 ? std::acos(std::clamp(a.dot(b) / norms, -1.0, 1.0)) : 0.0;
}

// Bisects intervals between samples until the sections in them follow straight lines between the
// sections at their ends, see deflection_samples()
struct deflection_sampler {
    const section_function& section_at;
    double linear_deflection;
    double angular_deflection;
    double min_length;
    std::vector<double>& samples;

    // whether the sections q at a quarter, half and three quarters of an interval follow straight
    // lines between the sections a and b at its ends
    bool follows(const sampled_section& a, const std::array<sampled_section, 3>& q, const sampled_section& b) const {
        // turning, as the angle between the directions over the first and last quarter
        if (angle_between(q[0].origin - a.origin, b.origin - q[2].origin) > angular_deflection) {
            return false;
        }
        for (size_t l = 0; l < a.loops.size() && l < b.loops.size(); ++l) {
            const auto& loop_a = a.loops[l];
            const auto& loop_b = b.loops[l];
            const size_t n = std::min(loop_a.size(), loop_b.size());
            // every point within linear_deflection of the line between its ends
            for (const auto& section : q) {
                if (l >= section.loops.size()) {
                    continue;
                }
                const auto& loop_q = section.loops[l];
                for (size_t k = 0; k < n && k < loop_q.size(); ++k) {
                    if (distance_to_segment(loop_q[k], loop_a[k], loop_b[k]) > linear_deflection) {
                        return false;
                    }
                }
            }
            // every face between consecutive points within linear_deflection of flat: faceted as
            // two triangles, it deviates by a quarter of how far its corners are out of plane
            for (size_t k = 0; k + 1 < n; ++k) {
                const Eigen::Vector3d normal = (loop_a[k + 1] - loop_a[k]).cross(loop_b[k] - loop_a[k]);
                const double norm = normal.norm();
                if (norm < 1.e-12) {
                    continue;
                }
                const Eigen::Vector3d twist = loop_a[k] - loop_a[k + 1] - loop_b[k] + loop_b[k + 1];
                if (std::abs(twist.dot(normal)) / norm / 4.0 > linear_deflection) {
                    return false;
                }
            }
        }
        return true;
    }

    // adds the samples needed strictly between u0 and u1, in order
    void refine(double u0, const sampled_section& s0, double u1, const sampled_section& s1) {
        if (u1 - u0 <= min_length) {
            return;
        }
        const double h = (u1 - u0) / 4.0;
        const std::array<sampled_section, 3> q{section_at(u0 + h), section_at(u0 + 2.0 * h), section_at(u0 + 3.0 * h)};
        if (follows(s0, q, s1)) {
            return;
        }
        refine(u0, s0, u0 + 2.0 * h, q[1]);
        samples.push_back(u0 + 2.0 * h);
        refine(u0 + 2.0 * h, q[1], u1, s1);
    }
};
} // namespace

std::vector<double> ifcopenshell::geom::deflection_samples(std::vector<double> boundaries, const section_function& section_at, double linear_deflection, double angular_deflection, double tolerance) {
    std::sort(boundaries.begin(), boundaries.end());
    std::vector<double> distinct;
    for (double u : boundaries) {
        if (distinct.empty() || u - distinct.back() > tolerance) {
            distinct.push_back(u);
        }
    }
    if (distinct.size() < 2) {
        return distinct;
    }

    std::vector<double> samples{distinct.front()};
    // an interval shorter than linear_deflection can't deviate from its chord by more than that
    deflection_sampler sampler{section_at, linear_deflection, angular_deflection, std::max(linear_deflection, tolerance), samples};
    auto section = section_at(distinct.front());
    for (size_t i = 1; i < distinct.size(); ++i) {
        auto next = section_at(distinct[i]);
        sampler.refine(distinct[i - 1], section, distinct[i], next);
        samples.push_back(distinct[i]);
        section = std::move(next);
    }
    return samples;
}

struct functor_fn_evaluator : public fn_evaluator {
    functor_fn_evaluator(taxonomy::functor_item::const_ptr fn, const ifcopenshell::geom::settings& settings) : fn_evaluator(settings),
                                                                                                                          fn_(fn) {
    }

    fn_evaluator* clone() const override { return new functor_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end();  }

    Eigen::Matrix4d evaluate(double u) const override {
        return (*fn_)(u);
    }

    std::vector<double> boundaries() const override {
        return {start(), end()};
    }

    taxonomy::functor_item::const_ptr fn_;
};

struct piecewise_fn_evaluator : public fn_evaluator {
    piecewise_fn_evaluator(taxonomy::piecewise_function::const_ptr fn, const ifcopenshell::geom::settings& settings) : fn_evaluator(settings),
                                                                                                                          fn_(fn) {
    }

    // A copy starts without a current span, so copies never share a span evaluator
    piecewise_fn_evaluator(const piecewise_fn_evaluator& other) : fn_evaluator(other), fn_(other.fn_) {}

    fn_evaluator* clone() const override { return new piecewise_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end(); }

    Eigen::Matrix4d evaluate(double u) const override {
        // assume monotonic evaluation and store last evaluated segment
        if (current_span_fn_ == nullptr || (u < current_span_start_ || current_span_end_ < u)) {
            // there isn't a current span or u is outside the range of the current span
            // get a new "current span"
            std::tie(current_span_start_, current_span_end_, current_span_fn_) = get_span(u);
            current_span_evaluator_ = std::make_shared<function_item_evaluator>(settings_, current_span_fn_);
        }

        u -= current_span_start_; // make u relative to start of span
        return current_span_evaluator_->evaluate(u);
    }

    std::tuple<double, double, taxonomy::function_item::const_ptr> get_span(double u) const {
        // force u to be within bounds of the curve
        double s = fn_->start();
        double e = fn_->end();
        u = std::max(s, u);
        u = std::min(u, e);

        double span_start = s;
        for (auto& fn : fn_->spans()) {
            double span_end = span_start + fn->length();
            auto tolerance = settings_.get<ifcopenshell::geom::settings::Precision>().get();
            if (span_start <= u && u < span_end + tolerance) {
                return {span_start, span_end, fn};
            }
            span_start += fn->length();
        }

        logger_.error("GEO", 37, "piecewise span not found.");
        return {0, 0, nullptr};
    }

    std::vector<double> boundaries() const override {
        // a span is evaluated relative to where it starts in the piecewise function (see evaluate)
        std::vector<double> result{fn_->start()};
        double span_start = fn_->start();
        for (auto& span : fn_->spans()) {
            function_item_evaluator evaluator(settings_, span);
            const double shift = span_start - span->start();
            for (double u : evaluator.boundaries()) {
                if (u + shift > result.back()) {
                    result.push_back(u + shift);
                }
            }
            span_start += span->length();
        }
        return result;
    }

    taxonomy::piecewise_function::const_ptr fn_;
    mutable double current_span_start_ = 0;
    mutable double current_span_end_ = 0;
    mutable taxonomy::function_item::const_ptr current_span_fn_ = nullptr;
    mutable std::shared_ptr<function_item_evaluator> current_span_evaluator_; // evaluates current_span_fn_
};

struct gradient_fn_evaluator : public fn_evaluator {
    gradient_fn_evaluator(taxonomy::gradient_function::const_ptr fn, const ifcopenshell::geom::settings& settings) :
       fn_evaluator(settings),
       horizontal_evaluator_(settings, fn->get_horizontal()),
       vertical_evaluator_(settings, fn->get_vertical()),
       fn_(fn)
    {
        start_ = fn_->get_vertical()->start();
    }

    fn_evaluator* clone() const override { return new gradient_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end(); }

    Eigen::Matrix4d evaluate(double u) const override {
        auto xy = horizontal_evaluator_.evaluate(u);
        auto uz = vertical_evaluator_.evaluate(u);

        uz(0, 3) = 0.0;      // x is distance along. zero it out so it doesn't add to the x from horizontal
        uz.col(1).swap(uz.col(2)); // uz is 2D in distance along - y plane, swap y and z so elevations become z
        uz.row(1).swap(uz.row(2));

        Eigen::Matrix4d m;
        m = xy * uz; // combine horizontal and vertical

        return m;
    }

    std::vector<double> boundaries() const override {
        return merge_boundaries(horizontal_evaluator_.boundaries(), vertical_evaluator_.boundaries(), start(), end(), precision(settings_));
    }

    function_item_evaluator horizontal_evaluator_, vertical_evaluator_;
    double start_; // start of vertical
    taxonomy::gradient_function::const_ptr fn_;
};

struct cant_fn_evaluator : public fn_evaluator {
   cant_fn_evaluator(taxonomy::cant_function::const_ptr fn, const ifcopenshell::geom::settings& settings) : fn_evaluator(settings),
      gradient_evaluator_(settings, fn->get_gradient()),
      cant_evaluator_(settings, fn->get_cant()),
      fn_(fn) {
        start_ = fn_->get_cant()->start();
    }

    fn_evaluator* clone() const override { return new cant_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end(); }

    Eigen::Matrix4d evaluate(double u) const override {
        auto g = gradient_evaluator_.evaluate(u);
        auto c = cant_evaluator_.evaluate(u);


        // curvature is stored in row 3 - capture it and remove it from the xy and uz matrices
        // so the matrix operations (ie multiplication) works correctly
        auto gradient_curvature = g.row(3);
        g.row(3) = Eigen::Vector4d(0, 0, 0, 1);

        auto cant_curvature = c.row(3);
        c.row(3) = Eigen::Vector4d(0, 0, 0, 1);

        // Need to multiply g and c so the axis vectors
        // from cant have the correct rotation applied so
        // they are relative to the gradient curve coordinate system
        //
        // However, the coordinate points don't need to have the rotations
        // of g applied. Save off the x,y,z and cant values
        auto x = g(0, 3);
        auto y = g(1, 3);
        auto z = g(2, 3);
        auto s = c(1, 3); // superelevation

        // change column 3 to (0,0,0,1)
        Eigen::Vector4d p(0, 0, 0, 1);
        g.col(3) = p;
        c.col(3) = p;

        // multiply g and c to get the axes in the correct orientation. g's frame is the gradient curve's tangent
        // T at grade angle alpha, the horizontal to the left L and the normal N, and c's is pitched by theta, the
        // slope of the deviating elevation, then rolled about T by the cross slope. The 3D curve's slope is
        // the grade plus the slope of the deviating elevation, tan(alpha) + tan(theta), so the pitches add up to
        // atan(tan(alpha) + tan(theta)), not alpha + theta: epsilon makes up the difference about L.
        const double tan_alpha = g(2, 0) / std::hypot(g(0, 0), g(1, 0));
        const double tan_theta = c(2, 0) / c(0, 0);
        const double epsilon = std::atan(tan_alpha + tan_theta) - std::atan(tan_alpha) - std::atan(tan_theta);
        Eigen::Matrix4d pitch = Eigen::Matrix4d::Identity();
        pitch(0, 0) = std::cos(epsilon);
        pitch(0, 2) = -std::sin(epsilon);
        pitch(2, 0) = std::sin(epsilon);
        pitch(2, 2) = std::cos(epsilon);
        Eigen::Matrix4d m = g * pitch * c;

        // reinstate the values for x and y.
        // z is the gradient curve z value plus the superelevation
        // that comes from the cant.
        m(0, 3) = x;
        m(1, 3) = y;
        m(2, 3) = z + s;

        // reinstate values for curvature.
        // cant_curvature is cant alone. this needs to be combined with gradient in column 3
        gradient_curvature[3] = gradient_curvature[2] + cant_curvature[3];
        m.row(3) = gradient_curvature;

        return m;
   }

   std::vector<double> boundaries() const override {
       return merge_boundaries(gradient_evaluator_.boundaries(), cant_evaluator_.boundaries(), start(), end(), precision(settings_));
   }

   function_item_evaluator gradient_evaluator_, cant_evaluator_;
   double start_; // start of cant
   taxonomy::cant_function::const_ptr fn_;
};

struct offset_fn_evaluator : public fn_evaluator {
    offset_fn_evaluator(taxonomy::offset_function::const_ptr fn, const ifcopenshell::geom::settings& settings) : fn_evaluator(settings),
                                                                                                                       basis_evaluator_(settings, fn->get_basis()),
                                                                                                                       offset_evaluator_(settings, fn->get_offset()),
                                                                                                                       fn_(fn) {
    }

    fn_evaluator* clone() const override { return new offset_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end(); }

    Eigen::Matrix4d evaluate(double u) const override {
        auto p = basis_evaluator_.evaluate(u);
        auto offset = offset_evaluator_.evaluate(u);
        Eigen::Matrix4d m = p * offset;
        return m;
    }

    std::vector<double> boundaries() const override {
        return merge_boundaries(basis_evaluator_.boundaries(), offset_evaluator_.boundaries(), start(), end(), precision(settings_));
    }

    function_item_evaluator basis_evaluator_, offset_evaluator_;
    taxonomy::offset_function::const_ptr fn_;
};




function_item_evaluator::function_item_evaluator(const ifcopenshell::geom::settings& settings,taxonomy::function_item::const_ptr fn, logger& logger) : logger_(logger) {
    auto kind = fn ? fn->kind() : taxonomy::kinds::NODE;
    if (kind == taxonomy::FUNCTOR_ITEM) {
        fn_evaluator_ = new functor_fn_evaluator(std::dynamic_pointer_cast<const taxonomy::functor_item>(fn),settings);
    } else if (kind == taxonomy::PIECEWISE_FUNCTION) {
        fn_evaluator_ = new piecewise_fn_evaluator(std::dynamic_pointer_cast<const taxonomy::piecewise_function>(fn), settings);
    } else if (kind == taxonomy::GRADIENT_FUNCTION) {
        fn_evaluator_ = new gradient_fn_evaluator(std::dynamic_pointer_cast<const taxonomy::gradient_function>(fn), settings);
    } else if (kind == taxonomy::CANT_FUNCTION) {
        fn_evaluator_ = new cant_fn_evaluator(std::dynamic_pointer_cast<const taxonomy::cant_function>(fn), settings);
    } else if (kind == taxonomy::OFFSET_FUNCTION) {
        fn_evaluator_ = new offset_fn_evaluator(std::dynamic_pointer_cast<const taxonomy::offset_function>(fn), settings);
    } else {
        logger_.error("GEO", 38, "Unexpected function type");
    }
}

function_item_evaluator::function_item_evaluator(const function_item_evaluator& other) : logger_(other.logger_) {
    fn_evaluator_ = other.fn_evaluator_->clone();
    eval_points_ = other.eval_points_;
}

function_item_evaluator::~function_item_evaluator() {
    delete fn_evaluator_;
}

std::vector<double> function_item_evaluator::evaluation_points() const {
    if (!eval_points_.has_value()) {
        const auto& settings = fn_evaluator_->settings_;
        // the curve itself is the only point of its section
        eval_points_ = deflection_samples(
            boundaries(),
            [this](double u) {
                const Eigen::Vector3d origin = evaluate(u).col(3).head<3>();
                return sampled_section{origin, {{origin}}};
            },
            settings.get<ifcopenshell::geom::settings::MesherLinearDeflection>().get(),
            settings.get<ifcopenshell::geom::settings::MesherAngularDeflection>().get(),
            precision(settings));
    }
    return *eval_points_;
}

std::vector<double> function_item_evaluator::boundaries() const {
    if (fn_evaluator_ == nullptr) {
        throw std::runtime_error("Function item not initialized");
    }
    return fn_evaluator_->boundaries();
}

std::vector<double> function_item_evaluator::evaluation_points(double ustart, double uend, unsigned nsteps) const {
    double curve_length = fn_evaluator_->length();
    ustart = std::max(fn_evaluator_->start(), ustart);
    uend = std::min(uend, fn_evaluator_->start() + curve_length);

    nsteps = std::max(1u, nsteps); // never have fewer than 1 step

    auto resolution = (uend - ustart) / nsteps;

    std::vector<double> u_values;
    u_values.reserve(nsteps);

    for (unsigned i = 0; i <= nsteps; ++i) {
        auto u = resolution * i + ustart;
        u_values.push_back(u);
    }

    return u_values;
}

taxonomy::item::ptr function_item_evaluator::evaluate() const {
    return evaluate(evaluation_points());
}

taxonomy::item::ptr function_item_evaluator::evaluate(double ustart, double uend, unsigned nsteps) const {
    return evaluate(evaluation_points(ustart, uend, nsteps));
}

taxonomy::item::ptr function_item_evaluator::evaluate(const std::vector<double>& dist) const {
    std::vector<taxonomy::point3::ptr> polygon;
    polygon.reserve(dist.size());
    for (auto& u : dist) {
        Eigen::Matrix4d m = evaluate(u);
        polygon.push_back(taxonomy::make<taxonomy::point3>(m(0, 3), m(1, 3), m(2, 3)));
    }

    return polygon_from_points(polygon);
}

Eigen::Matrix4d function_item_evaluator::evaluate(double u) const {
    if (fn_evaluator_ == nullptr) {
        throw std::runtime_error("Function item not initialized");
    }
    Eigen::Matrix4d m = fn_evaluator_->evaluate(u);
    if (!fn_evaluator_->settings_.get<ifcopenshell::geom::settings::ComputeCurvature>().get()) {
        m.row(3) = Eigen::Vector4d(0, 0, 0, 1);
    }
    return m;
}
