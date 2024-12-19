#ifndef ITERATOR_PWF_EVALUATOR_H
#define ITERATOR_PWF_EVALUATOR_H

#include "../ifcgeom/taxonomy.h"

#include <boost/function.hpp>

namespace ifcopenshell { namespace geometry {

/// @brief Abstract class for evaluating a function_item. This class is specialized for each of the function_item types.
struct fn_evaluator {
    fn_evaluator(const ifcopenshell::geometry::Settings& settings) : settings_(settings) {
    }
    fn_evaluator(const fn_evaluator& other) = default;
    virtual ~fn_evaluator() = default;

    virtual fn_evaluator* clone() const = 0;

    virtual Eigen::Matrix4d evaluate(double u) const = 0;
    virtual double start() const = 0;
    virtual double end() const = 0;
    double length() const { return end() - start(); }

    ifcopenshell::geometry::Settings settings_;
};

/// @brief utility class to evaluate function_item objects.
class function_item_evaluator {
  public:
    function_item_evaluator(const ifcopenshell::geometry::Settings& settings, taxonomy::function_item::const_ptr fn);
    function_item_evaluator(const function_item_evaluator& other);
    ~function_item_evaluator();

    /// @brief returns a vector of "distance along" points where the evaluate function computes loop points
    std::vector<double> evaluation_points() const;

    /// @brief returns a vector of "distance along" points between ustart and uend
    /// @param ustart starting location
    /// @param uend ending location
    /// @param nsteps number of steps to evaluate
    std::vector<double> evaluation_points(double ustart, double uend, unsigned nsteps) const;

    /// @brief evaluates the function between start and end
    /// evaluation point step size is taken from the settings object
    taxonomy::item::ptr evaluate() const;

    /// @brief evaluates the function between ustart and uend
    /// if ustart and uend are out of range, the range of values evaluated
    /// are constrained to start_ and start_+length_
    /// @param ustart starting location
    /// @param uend ending location
    /// @param nsteps number of steps to evaluate
    /// @return taxonomy::loop::ptr
    taxonomy::item::ptr evaluate(double ustart, double uend, unsigned nsteps) const;

    /// @brief evaluates the function at u
    /// @param u u is constrained to be between start_ and start_+length
    /// @return 4x4 placement matrix
    Eigen::Matrix4d evaluate(double u) const;

  private:
    taxonomy::item::ptr evaluate(const std::vector<double>& dist) const;
    fn_evaluator* fn_evaluator_ = nullptr;

    mutable boost::optional<std::vector<double>> eval_points_; // cache evaluation points
};

}}

#endif