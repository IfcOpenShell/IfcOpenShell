#include "piecewise_function_evaluator.h"
#include "profile_helper.h"

using namespace ifcopenshell::geometry;


piecewise_function_evaluator::piecewise_function_evaluator(taxonomy::piecewise_function::const_ptr pwf, const ifcopenshell::geometry::Settings* settings) : pwf_(pwf) {
    if (settings) {
        settings_ = *settings;
    }
}

std::vector<double> piecewise_function_evaluator::evaluation_points() const {
    if (!eval_points_.has_value()) {
        double curve_length = pwf_->length();

        auto param_type = settings_.get<ifcopenshell::geometry::settings::PiecewiseStepType>().get();
        auto param = settings_.get<ifcopenshell::geometry::settings::PiecewiseStepParam>().get();
        unsigned num_steps = 0;
        if (param_type == ifcopenshell::geometry::settings::PiecewiseStepMethod::MAXSTEPSIZE) {
            // parameter is max step size
            num_steps = (unsigned)std::ceil(curve_length / param);
        } else {
            // parameter is minimum number of steps
            num_steps = (unsigned)std::ceil(param);
        }

        eval_points_ = evaluation_points(pwf_->start(), pwf_->start() + curve_length, num_steps);
    }
    return *eval_points_;
}

std::vector<double> piecewise_function_evaluator::evaluation_points(double ustart, double uend, unsigned nsteps) const {
    double curve_length = pwf_->length();
    ustart = std::max(pwf_->start(), ustart);
    uend = std::min(uend, pwf_->start() + curve_length);

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

taxonomy::item::ptr piecewise_function_evaluator::evaluate() const {
    return evaluate(evaluation_points());
}

taxonomy::item::ptr piecewise_function_evaluator::evaluate(double ustart, double uend, unsigned nsteps) const {
    return evaluate(evaluation_points(ustart, uend, nsteps));
}

Eigen::Matrix4d piecewise_function_evaluator::evaluate(double u) const {
    // assume monotonic evaluation and store last evaluated segment
    if (current_span_fn_ == nullptr || (u < current_span_start_ || current_span_end_ < u)) {
        // there isn't a current span or u is outside the range of the current span
        // get a new "current span"
        std::tie(current_span_start_, current_span_end_, current_span_fn_) = get_span(u);
    }

    u -= current_span_start_; // make u relative to start of span
    return (*current_span_fn_)(u);
}

taxonomy::item::ptr piecewise_function_evaluator::evaluate(const std::vector<double>& dist) const {
    std::vector<taxonomy::point3::ptr> polygon;
    polygon.reserve(dist.size());
    for (auto& u : dist) {
        Eigen::Matrix4d m = evaluate(u);
        polygon.push_back(taxonomy::make<taxonomy::point3>(m(0, 3), m(1, 3), m(2, 3)));
    }

    return polygon_from_points(polygon);
}

std::tuple<double, double, const std::function<Eigen::Matrix4d(double u)>*> piecewise_function_evaluator::get_span(double u) const {
    // force u to be within bounds of the curve
    double s = pwf_->start();
    double e = pwf_->end();
    u = std::max(s, u);
    u = std::min(u, e);

    double span_start = s;
    for (auto& [length, fn] : pwf_->spans()) {
        double span_end = span_start + length;
        auto tolerance = settings_.get<ifcopenshell::geometry::settings::Precision>().get();
        if (span_start <= u && u < span_end + tolerance) {
            return {span_start, span_end, &fn};
        }
        span_start += length;
    }

    Logger::Error("piecewise_function_impl::get_span span not found.");
    return {0, 0, nullptr};
}
