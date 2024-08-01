#ifndef PIECEWISE_FUNCTION_IMPL
#define PIECEWISE_FUNCTION_IMPL

#include "taxonomy.h"

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

struct piecewise_function_impl {
    using spans_t = std::vector<std::pair<double, std::function<Eigen::Matrix4d(double u)>>>;

    piecewise_function_impl(double start, const spans_t& s, ifcopenshell::geometry::Settings* settings = nullptr) : start_(start),
                                                                                                                  settings_(settings),
                                                                                                                  spans_(s){};
    piecewise_function_impl(double start, const std::vector<piecewise_function::ptr>& pwfs, ifcopenshell::geometry::Settings* settings = nullptr) : start_(start),
                                                                                                                                                    settings_(settings) {
        for (auto& pwf : pwfs) {
            spans_.insert(spans_.end(), pwf->spans().begin(), pwf->spans().end());
        }
    };
    piecewise_function_impl(piecewise_function_impl&&) = default;
    piecewise_function_impl(const piecewise_function_impl&) = default;

    const ifcopenshell::geometry::Settings* settings_ = nullptr;

    const spans_t& spans() const { return spans_; }

    bool is_empty() const { return spans_.empty(); }

    double start() const {
        return start_;
    }

    double end() const {
        return start_ + length();
    }

    double length() const {
        if (!length_.has_value()) {
            length_ = std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s.first; });
        }
        return *length_;
    }

    piecewise_function_impl* clone_() const { return new piecewise_function_impl(*this); }

    /// @brief returns a vector of "distance along" points where the evaluate function computes loop points
    std::vector<double> evaluation_points() const;

    /// @brief returns a vector of "distance along" points between ustart and uend
    /// @param ustart starting location
    /// @param uend ending location
    /// @param nsteps number of steps to evaluate
    std::vector<double> evaluation_points(double ustart, double uend, unsigned nsteps) const;

    /// @brief evaluates the piecewise function between start and end
    /// evaluation point step size is taken from the settings object
    item::ptr evaluate() const;

    /// @brief evaluates the piecewise function between ustart and uend
    /// if ustart and uend are out of range, the range of values evaluated
    /// are constrained to start_ and start_+length_
    /// @param ustart starting location
    /// @param uend ending location
    /// @param nsteps number of steps to evaluate
    /// @return taxonomy::loop::ptr
    item::ptr evaluate(double ustart, double uend, unsigned nsteps) const;

    /// @brief evaluates the piecewise function at u
    /// @param u u is constrained to be between start_ and start_+length
    /// @return 4x4 placement matrix
    Eigen::Matrix4d evaluate(double u) const;

  private:
    item::ptr evaluate(const std::vector<double>& dist) const;
    std::tuple<double, double, const std::function<Eigen::Matrix4d(double u)>*> get_span(double u) const;
    double start_ = 0.0; // starting value of the pwf
    spans_t spans_;

    mutable double current_span_start_ = 0;
    mutable double current_span_end_ = 0;
    mutable const std::function<Eigen::Matrix4d(double u)>* current_span_fn_ = nullptr;
    mutable boost::optional<double> length_;
    mutable boost::optional<std::vector<double>> eval_points_;
};

} // namespace taxonomy
} // namespace geometry
} // namespace ifcopenshell
#endif PIECEWISE_FUNCTION_IMPL