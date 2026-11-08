#ifndef ITERATOR_PWF_EVALUATOR_H
#define ITERATOR_PWF_EVALUATOR_H

#include "../ifcgeom/taxonomy.h"

namespace ifcopenshell { namespace geom {

/// @brief Computes a point on a helmert curve at s.
/// Returns (x,y,theta) at L/2. The results are in a vector so they can be returned to python
IFC_GEOM_API std::vector<double> helmert_curve_point(double A0, double A1, double A2, double s);

/// @brief Converts a loop to a function item.
/// This is intended to be used from python side. Polylines are mapped to a loop, but when
/// representing an alignment they need to be a function_item so the can be evaluated by function_item_evaluator.
/// On the C++ side, the dcast operator take care of this, but dcast is not accessible on the python side.
/// @param loop
/// @return
inline taxonomy::function_item::ptr convert_loop_to_function_item(taxonomy::loop::ptr loop) {
    return ifcopenshell::geom::taxonomy::dcast<taxonomy::function_item>(loop);
}

#ifndef SWIG
/// @brief A cross section placed at some distance along a function, in world coordinates
struct sampled_section {
    /// where the function is
    Eigen::Vector3d origin;
    /// points of the section to keep within the deflection tolerances, as loops of consecutive
    /// points joined by faces between sections; a closed loop repeats its first point at the end
    std::vector<std::vector<Eigen::Vector3d>> loops;
};

using section_function = std::function<sampled_section(double)>;

/// @brief Distances along at which to place sections, refined until they follow the function
/// within the given deflections.
///
/// Every boundary is a sample. Each interval between samples is bisected until, at a quarter,
/// half and three quarters of it, every section point is within linear_deflection of the straight
/// line between its positions at the interval's ends, every face between two consecutive points of
/// a loop is within linear_deflection of flat, and the function turns by at most angular_deflection.
/// A straight with an unchanging section therefore needs only its ends.
IFC_GEOM_API std::vector<double> deflection_samples(std::vector<double> boundaries, const section_function& section_at, double linear_deflection, double angular_deflection, double tolerance);
#endif

/// @brief Abstract class for evaluating a function_item. This class is specialized for each of the function_item types.
struct IFC_GEOM_API fn_evaluator {
    fn_evaluator(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root()) : settings_(settings), logger_(logger) {
    }
    fn_evaluator(const fn_evaluator& other) = default;
    virtual ~fn_evaluator() = default;

    virtual fn_evaluator* clone() const = 0;

    virtual Eigen::Matrix4d evaluate(double u) const = 0;
    virtual double start() const = 0;
    virtual double end() const = 0;
    double length() const { return end() - start(); }
#ifndef SWIG
    /// @brief start(), end(), and every span boundary between them of every function this one is
    /// made of, in increasing order
    virtual std::vector<double> boundaries() const = 0;
#endif

    ifcopenshell::geom::settings settings_;

  protected:
    ifcopenshell::logger& logger_;
};

/// @brief utility class to evaluate function_item objects.
class IFC_GEOM_API function_item_evaluator {
  public:
    function_item_evaluator(const ifcopenshell::geom::settings& settings, taxonomy::function_item::const_ptr fn, ifcopenshell::logger& logger = ifcopenshell::logger::root());
    function_item_evaluator(const function_item_evaluator& other);
    ~function_item_evaluator();

    /// @brief returns a vector of "distance along" points where the evaluate function computes loop points
    /// Every span boundary is included, and the points between them are spaced so the polyline
    /// through them stays within mesher-linear-deflection of the curve and turns by at most
    /// mesher-angular-deflection between points. Straights need only their ends.
    std::vector<double> evaluation_points() const;

#ifndef SWIG
    /// @brief see fn_evaluator::boundaries()
    std::vector<double> boundaries() const;
#endif

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
    /// @return 4x4 placement matrix. Curvature values for horizontal, vertical, and vertical + cant are stored in the last row.
    Eigen::Matrix4d evaluate(double u) const;

  private:
    taxonomy::item::ptr evaluate(const std::vector<double>& dist) const;
    fn_evaluator* fn_evaluator_ = nullptr;

    mutable std::optional<std::vector<double>> eval_points_; // cache evaluation points
    ifcopenshell::logger& logger_;
};

}}

#endif
