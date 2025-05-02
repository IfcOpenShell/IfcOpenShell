#include "function_item_evaluator.h"
#include "profile_helper.h"

#include <boost/math/quadrature/trapezoidal.hpp>

using namespace ifcopenshell::geometry;

std::vector<double> ifcopenshell::geometry::helmert_curve_point(double A0, double A1, double A2, double s) {
    auto theta = [A0, A1, A2](double t) -> double {
       auto a0 = A0 ? t / A0 : 0.0;
       auto a1 = A1 ? A1 * std::pow(t, 2) / (2 * fabs(std::pow(A1, 3))) : 0.0;
       auto a2 = A2 ? std::pow(t, 3) / (3 * std::pow(A2, 3)) : 0.0;
       return a0 + a1 + a2;
    };

    auto fn_x = [theta](double t) -> double { return cos(theta(t)); };
    auto fn_y = [theta](double t) -> double { return sin(theta(t)); };
    auto x = boost::math::quadrature::trapezoidal(fn_x, 0.0, s);
    auto y = boost::math::quadrature::trapezoidal(fn_y, 0.0, s);
    auto angle = theta(x);
    return {x, y, angle};
}

struct functor_fn_evaluator : public fn_evaluator {
    functor_fn_evaluator(taxonomy::functor_item::const_ptr fn, const ifcopenshell::geometry::Settings& settings) : fn_evaluator(settings),
                                                                                                                          fn_(fn) {
    }

    fn_evaluator* clone() const override { return new functor_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end();  }

    Eigen::Matrix4d evaluate(double u) const override {
        return (*fn_)(u);
    }

    taxonomy::functor_item::const_ptr fn_;
};

struct piecewise_fn_evaluator : public fn_evaluator {
    piecewise_fn_evaluator(taxonomy::piecewise_function::const_ptr fn, const ifcopenshell::geometry::Settings& settings) : fn_evaluator(settings),
                                                                                                                          fn_(fn) {
    }

    fn_evaluator* clone() const override { return new piecewise_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end(); }

    Eigen::Matrix4d evaluate(double u) const override {
        // assume monotonic evaluation and store last evaluated segment
        if (current_span_fn_ == nullptr || (u < current_span_start_ || current_span_end_ < u)) {
            // there isn't a current span or u is outside the range of the current span
            // get a new "current span"
            std::tie(current_span_start_, current_span_end_, current_span_fn_) = get_span(u);
        }

        u -= current_span_start_; // make u relative to start of span
        function_item_evaluator evaluator(settings_, current_span_fn_);
        return evaluator.evaluate(u);
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
            auto tolerance = settings_.get<ifcopenshell::geometry::settings::Precision>().get();
            if (span_start <= u && u < span_end + tolerance) {
                return {span_start, span_end, fn};
            }
            span_start += fn->length();
        }

        Logger::Error("piecewise span not found.");
        return {0, 0, nullptr};
    }

    taxonomy::piecewise_function::const_ptr fn_;
    mutable double current_span_start_ = 0;
    mutable double current_span_end_ = 0;
    mutable taxonomy::function_item::const_ptr current_span_fn_ = nullptr;
};

struct gradient_fn_evaluator : public fn_evaluator {
    gradient_fn_evaluator(taxonomy::gradient_function::const_ptr fn, const ifcopenshell::geometry::Settings& settings) : 
       fn_evaluator(settings),
       fn_(fn), 
       horizontal_evaluator_(settings, fn->get_horizontal()),
       vertical_evaluator_(settings, fn->get_vertical())
    {
        start_ = fn_->get_vertical()->start();
    }

    fn_evaluator* clone() const override { return new gradient_fn_evaluator(*this); }
    double start() const override { return fn_->start(); }
    double end() const override { return fn_->end(); }

    Eigen::Matrix4d evaluate(double u) const override {
        auto xy = horizontal_evaluator_.evaluate(u);
        auto uz = vertical_evaluator_.evaluate(u);

        // curvature is stored in row 3 - capture it and remove it from the xy and uz matrices
        // so the matrix operations (ie multiplication) works correct.y
        auto horizontal_curvature = xy.row(3);
        xy.row(3) = Eigen::Vector4d(0, 0, 0, 1);

        auto vertical_curvature = uz.row(3);
        uz.row(3) = Eigen::Vector4d(0, 0, 0, 1);

        uz(0, 3) = 0.0;      // x is distance along. zero it out so it doesn't add to the x from horizontal
        uz.col(1).swap(uz.col(2)); // uz is 2D in distance along - y plane, swap y and z so elevations become z
        uz.row(1).swap(uz.row(2));

        Eigen::Matrix4d m;
        m = xy * uz; // combine horizontal and vertical

        // Put curvature back into the solution matrix
        // curvature for vertical is in column 0, need it to be in column 1
        // so it doesn't add to curvature for horizontal
        std::swap(vertical_curvature(3, 0), vertical_curvature(3, 1));
        m.row(3) = horizontal_curvature + vertical_curvature;

        return m;
    }

    function_item_evaluator horizontal_evaluator_, vertical_evaluator_;
    double start_; // start of vertical
    taxonomy::gradient_function::const_ptr fn_;
};

struct cant_fn_evaluator : public fn_evaluator {
   cant_fn_evaluator(taxonomy::cant_function::const_ptr fn, const ifcopenshell::geometry::Settings& settings) : fn_evaluator(settings),
      fn_(fn),
      gradient_evaluator_(settings, fn->get_gradient()),
      cant_evaluator_(settings, fn->get_cant()) {
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

        // multiply g and c to get the axes in the correct orientation
        Eigen::Matrix4d m = g * c;

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

   function_item_evaluator gradient_evaluator_, cant_evaluator_;
   double start_; // start of cant
   taxonomy::cant_function::const_ptr fn_;
};

struct offset_fn_evaluator : public fn_evaluator {
    offset_fn_evaluator(taxonomy::offset_function::const_ptr fn, const ifcopenshell::geometry::Settings& settings) : fn_evaluator(settings),
                                                                                                                       fn_(fn),
                                                                                                                       basis_evaluator_(settings, fn->get_basis()),
                                                                                                                       offset_evaluator_(settings, fn->get_offset()) {
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

    function_item_evaluator basis_evaluator_, offset_evaluator_;
    taxonomy::offset_function::const_ptr fn_;
};




function_item_evaluator::function_item_evaluator(const ifcopenshell::geometry::Settings& settings,taxonomy::function_item::const_ptr fn) {
    auto kind = fn->kind();
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
        Logger::Error("Unexpected function type");
    }
}

function_item_evaluator::function_item_evaluator(const function_item_evaluator& other) {
    fn_evaluator_ = other.fn_evaluator_->clone();
    eval_points_ = other.eval_points_;
}

function_item_evaluator::~function_item_evaluator() {
    delete fn_evaluator_;
}

std::vector<double> function_item_evaluator::evaluation_points() const {
    if (!eval_points_.has_value()) {
        double curve_length = fn_evaluator_->length();

        auto param_type = fn_evaluator_->settings_.get<ifcopenshell::geometry::settings::FunctionStepType>().get();
        auto param = fn_evaluator_->settings_.get<ifcopenshell::geometry::settings::FunctionStepParam>().get();
        unsigned num_steps = 0;
        if (param_type == ifcopenshell::geometry::settings::FunctionStepMethod::MAXSTEPSIZE) {
            // parameter is max step size
            num_steps = (unsigned)std::ceil(curve_length / param);
        } else {
            // parameter is minimum number of steps
            num_steps = (unsigned)std::ceil(param);
        }

        eval_points_ = evaluation_points(fn_evaluator_->start(), fn_evaluator_->end(), num_steps);
    }
    return *eval_points_;
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
    Eigen::Matrix4d m = fn_evaluator_->evaluate(u);
    if (!fn_evaluator_->settings_.get<ifcopenshell::geometry::settings::ComputeCurvature>().get()) {
        m.row(3) = Eigen::Vector4d(0, 0, 0, 1);
    }
    return m;
}
