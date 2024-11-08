#ifndef ITERATOR_PWF_EVALUATOR_H
#define ITERATOR_PWF_EVALUATOR_H

#include "../ifcgeom/taxonomy.h"

#include <boost/function.hpp>

namespace ifcopenshell { namespace geometry {

/// @brief utility class to evaluate piecewise_function objects
class piecewise_function_evaluator {
  public:
    piecewise_function_evaluator(taxonomy::piecewise_function::const_ptr pwf, const ifcopenshell::geometry::Settings* settings=nullptr);

    /// @brief returns a vector of "distance along" points where the evaluate function computes loop points
    std::vector<double> evaluation_points() const;

    /// @brief returns a vector of "distance along" points between ustart and uend
    /// @param ustart starting location
    /// @param uend ending location
    /// @param nsteps number of steps to evaluate
    std::vector<double> evaluation_points(double ustart, double uend, unsigned nsteps) const;

    /// @brief evaluates the piecewise function between start and end
    /// evaluation point step size is taken from the settings object
    taxonomy::item::ptr evaluate() const;

    /// @brief evaluates the piecewise function between ustart and uend
    /// if ustart and uend are out of range, the range of values evaluated
    /// are constrained to start_ and start_+length_
    /// @param ustart starting location
    /// @param uend ending location
    /// @param nsteps number of steps to evaluate
    /// @return taxonomy::loop::ptr
    taxonomy::item::ptr evaluate(double ustart, double uend, unsigned nsteps) const;

    /// @brief evaluates the piecewise function at u
    /// @param u u is constrained to be between start_ and start_+length
    /// @return 4x4 placement matrix
    Eigen::Matrix4d evaluate(double u) const;

  private:
    taxonomy::item::ptr evaluate(const std::vector<double>& dist) const;
    std::tuple<double, double, const std::function<Eigen::Matrix4d(double u)>*> get_span(double u) const;

    taxonomy::piecewise_function::const_ptr pwf_;

    ifcopenshell::geometry::Settings settings_;

    mutable double current_span_start_ = 0;
    mutable double current_span_end_ = 0;
    mutable const std::function<Eigen::Matrix4d(double u)>* current_span_fn_ = nullptr;
    mutable boost::optional<std::vector<double>> eval_points_;
};

}}

#endif