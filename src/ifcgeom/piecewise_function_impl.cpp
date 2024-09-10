#include "piecewise_function_impl.h"
#include "profile_helper.h"

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

piecewise_function_impl::piecewise_function_impl(double start, const spans_t& s) : start_(start), spans_(s) {
}

piecewise_function_impl::piecewise_function_impl(double start, const std::vector<piecewise_function::ptr>& pwfs) : start_(start) {
    for (auto& pwf : pwfs) {
        spans_.insert(spans_.end(), pwf->spans().begin(), pwf->spans().end());
    }
}

const piecewise_function_impl::spans_t& piecewise_function_impl::spans() const { return spans_; }

bool piecewise_function_impl::is_empty() const { return spans_.empty(); }

double piecewise_function_impl::start() const {
    return start_;
}

double piecewise_function_impl::end() const {
    return start_ + length();
}

double piecewise_function_impl::length() const {
    return std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s.first; });

    // this is a secondary option where we only compute length once and cache it.
    // mutex is needed to prevent interruption of the accumulation if there is multi-threading
    // skipping this detail for now and just adding up the span lengths every time
    //if (!length_.has_value()) {
    //    length_ = std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s.first; });
    //}
    //return *length_;
}

piecewise_function_impl* piecewise_function_impl::clone_() const { return new piecewise_function_impl(*this); }

} // namespace taxonomy

} // namespace geometry

} // namespace ifcopenshell
