#ifndef PIECEWISE_FUNCTION_IMPL
#define PIECEWISE_FUNCTION_IMPL

#include "taxonomy.h"

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

struct piecewise_function_impl {
    using spans_t = std::vector<std::pair<double, std::function<Eigen::Matrix4d(double u)>>>;

    piecewise_function_impl(double start, const spans_t& s);
    piecewise_function_impl(double start, const std::vector<piecewise_function::ptr>& pwfs);
    piecewise_function_impl(piecewise_function_impl&&) = default;
    piecewise_function_impl(const piecewise_function_impl&) = default;

    const spans_t& spans() const;
    bool is_empty() const;
    double start() const;
    double end() const;
    double length() const;
    piecewise_function_impl* clone_() const;

  private:
    double start_ = 0.0; // starting value of the pwf
    spans_t spans_;

    //mutable boost::optional<double> length_; // used for length() method
};

} // namespace taxonomy
} // namespace geometry
} // namespace ifcopenshell
#endif PIECEWISE_FUNCTION_IMPL