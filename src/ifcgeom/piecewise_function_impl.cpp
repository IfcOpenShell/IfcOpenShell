#include "piecewise_function_impl.h"
#include "profile_helper.h"

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

std::vector<double> ifcopenshell::geometry::taxonomy::piecewise_function_impl::evaluation_points() const {
    if (!eval_points_.has_value()) {
        double curve_length = length();

        auto param_type = settings_ ? settings_->get<ifcopenshell::geometry::settings::PiecewiseStepType>().get() : ifcopenshell::geometry::settings::PiecewiseStepMethod::MAXSTEPSIZE;
        auto param = settings_ ? settings_->get<ifcopenshell::geometry::settings::PiecewiseStepParam>().get() : 0.5;
        unsigned num_steps = 0;
        if (param_type == ifcopenshell::geometry::settings::PiecewiseStepMethod::MAXSTEPSIZE) {
            // parameter is max step size
            num_steps = (unsigned)std::ceil(curve_length / param);
        } else {
            // parameter is minimum number of steps
            num_steps = (unsigned)std::ceil(param);
        }

        eval_points_ = evaluation_points(start_, start_ + curve_length, num_steps);
    }
    return *eval_points_;
}

std::vector<double> ifcopenshell::geometry::taxonomy::piecewise_function_impl::evaluation_points(double ustart, double uend, unsigned nsteps) const {
    double curve_length = length();
    ustart = std::max(start_, ustart);
    uend = std::min(uend, start_ + curve_length);

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

ifcopenshell::geometry::taxonomy::item::ptr ifcopenshell::geometry::taxonomy::piecewise_function_impl::evaluate() const {
    return evaluate(evaluation_points());
}

item::ptr ifcopenshell::geometry::taxonomy::piecewise_function_impl::evaluate(double ustart, double uend, unsigned nsteps) const {
    return evaluate(evaluation_points(ustart, uend, nsteps));
}

item::ptr ifcopenshell::geometry::taxonomy::piecewise_function_impl::evaluate(const std::vector<double>& dist) const {
    std::vector<taxonomy::point3::ptr> polygon;
    polygon.reserve(dist.size());
    for (auto& u : dist) {
        Eigen::Matrix4d m = evaluate(u);
        polygon.push_back(taxonomy::make<taxonomy::point3>(m.col(3)(0), m.col(3)(1), m.col(3)(2)));
    }

    return polygon_from_points(polygon);
}

Eigen::Matrix4d ifcopenshell::geometry::taxonomy::piecewise_function_impl::evaluate(double u) const {
    // assume monotonic evaluation and store last evaluated segment
    if (current_span_fn_ == nullptr || (u < current_span_start_ || current_span_end_ < u)) {
        // there isn't a current span or u is outside the range of the current span
        // get a new "current span"
        std::tie(current_span_start_, current_span_end_, current_span_fn_) = get_span(u);
    }

    u -= current_span_start_; // make u relative to start of span
    return (*current_span_fn_)(u);
}

std::tuple<double, double, const std::function<Eigen::Matrix4d(double u)>*> ifcopenshell::geometry::taxonomy::piecewise_function_impl::get_span(double u) const {
    // force u to be within bounds of the curve
    double s = start();
    double e = end();
    u = std::max(s, u);
    u = std::min(u, e);

    double span_start = s;
    for (auto& [length, fn] : spans_) {
        double span_end = span_start + length;
        auto tolerance = settings_ ? settings_->get<ifcopenshell::geometry::settings::Precision>().get() : 0.001;
        if (span_start <= u && u < span_end + tolerance) {
            return {span_start, span_end, &fn};
        }
        span_start += length;
    }

    Logger::Error("piecewise_function_impl::get_span span not found.");
    return {0, 0, nullptr};
}

} // namespace taxonomy

} // namespace geometry

} // namespace ifcopenshell
