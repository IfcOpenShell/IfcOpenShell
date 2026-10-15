#include "taxonomy.h"

#include "../ifcparse/logger.h"
#include "function_item_evaluator.h"
#include "profile_helper.h"

using namespace ifcopenshell::geom::taxonomy;
namespace taxonomy = ifcopenshell::geom::taxonomy;

namespace {
constexpr double polygon_pi = boost::math::constants::pi<double>();

Eigen::Vector3d transform_point(const matrix4::ptr& m, const Eigen::Vector3d& p) {
    return m ? (m->ccomponents() * p.homogeneous()).head<3>().eval() : p;
}

double curve_parameter(const item::ptr& basis, const std::variant<boost::blank, point3::ptr, double>& trim) {
    if (auto u = std::get_if<double>(&trim)) {
        return *u;
    }
    if (auto p = std::get_if<point3::ptr>(&trim)) {
        auto c = std::dynamic_pointer_cast<curve>(basis);
        if (!c) {
            throw std::runtime_error("Point projection not implemented on this geometry type");
        }
        Eigen::Vector3d xyz = (*p)->ccomponents();
        if (c->matrix) {
            xyz = (c->matrix->ccomponents().inverse() * xyz.homogeneous()).head<3>().eval();
        }
        if (c->kind() == LINE) {
            return xyz.z();
        }
        if (c->kind() == CIRCLE) {
            return std::atan2(xyz.y(), xyz.x());
        }
        if (auto e = std::dynamic_pointer_cast<ellipse>(c)) {
            return std::atan2(xyz.y() / e->radius2, xyz.x() / e->radius);
        }
    }
    throw std::runtime_error("Unbounded or unsupported curve trim");
}

void append_polygon(std::vector<point3>& a, const std::vector<point3>& b, double tolerance) {
    if (!b.empty()) {
        size_t offset = !a.empty() && (a.back().ccomponents() - b.front().ccomponents()).norm() < tolerance ? 1 : 0;
        a.insert(a.end(), b.begin() + offset, b.end());
    }
}

Eigen::Vector3d endpoint_tangent(const item::ptr& i, bool at_end) {
    Eigen::Vector3d tangent;
    auto geometry = std::dynamic_pointer_cast<geom_item>(i);
    if (auto l = std::dynamic_pointer_cast<loop>(i)) {
        const bool reversed = !l->orientation.value_or(true);
        const bool end = at_end != reversed;
        tangent = endpoint_tangent(end ? l->children.back() : l->children.front(), end);
        if (reversed) {
            tangent = -tangent;
        }
    } else if (auto e = std::dynamic_pointer_cast<trimmed_curve>(i)) {
        if ((!e->basis || e->basis->kind() == LINE) && e->start.index() == 1 && e->end.index() == 1) {
            tangent = std::get<point3::ptr>(e->end)->ccomponents() - std::get<point3::ptr>(e->start)->ccomponents();
        } else {
            auto underlying = e->basis;
            while (auto nested = std::dynamic_pointer_cast<trimmed_curve>(underlying)) {
                underlying = nested->basis;
            }
            auto c = std::dynamic_pointer_cast<taxonomy::curve>(underlying);
            const bool end = at_end == e->orientation.value_or(true);
            const double u = curve_parameter(underlying, end ? e->end : e->start);
            if (auto circle = std::dynamic_pointer_cast<taxonomy::circle>(c)) {
                tangent = Eigen::Vector3d(-circle->radius * std::sin(u), circle->radius * std::cos(u), 0.);
            } else if (auto ellipse = std::dynamic_pointer_cast<taxonomy::ellipse>(c)) {
                tangent = Eigen::Vector3d(-ellipse->radius * std::sin(u), ellipse->radius2 * std::cos(u), 0.);
            } else if (c && c->kind() == LINE) {
                tangent = Eigen::Vector3d::UnitZ();
            } else {
                throw std::runtime_error("Unsupported swept disk tangent");
            }
            if (c->matrix) {
                tangent = c->matrix->ccomponents().topLeftCorner<3, 3>() * tangent;
            }
            if (!e->curve_sense.value_or(true)) {
                tangent = -tangent;
            }
        }
        if (!e->orientation.value_or(true)) {
            tangent = -tangent;
        }
    } else {
        throw std::runtime_error("Unsupported swept disk tangent");
    }
    if (geometry && geometry->matrix) {
        tangent = geometry->matrix->ccomponents().topLeftCorner<3, 3>() * tangent;
    }
    return tangent.normalized();
}
} // namespace

std::vector<point3> curve::to_polygon(const ifcopenshell::geom::settings& settings, double a, double b, int segments) const {
    if (kind() != LINE && a == -std::numeric_limits<double>::infinity() && b == std::numeric_limits<double>::infinity()) {
        a = 0.;
        b = 2. * polygon_pi;
    }
    if (!std::isfinite(a) || !std::isfinite(b)) {
        throw std::runtime_error("Cannot represent infinite curve segment");
    }
    if (kind() == LINE) {
        std::vector<point3> points;
        const int count = std::max(1, segments);
        for (int i = 0; i <= count; ++i) {
            points.emplace_back(transform_point(matrix, {0., 0., a + (b - a) * i / count}));
        }
        return points;
    }
    double rx, ry;
    if (auto c = dynamic_cast<const circle*>(this)) {
        rx = ry = c->radius;
    } else if (auto e = dynamic_cast<const ellipse*>(this)) {
        rx = e->radius;
        ry = e->radius2;
    } else {
        throw std::runtime_error("Polygonal approximation not implemented on this curve type");
    }
    a = std::fmod(a, 2. * polygon_pi);
    b = std::fmod(b, 2. * polygon_pi);
    if (b <= a) {
        b += 2. * polygon_pi;
    }
    const double span = b - a;
    const int circle_segments = settings.get<ifcopenshell::geom::settings::CircleSegments>().get();
    int count;
    if (segments > 0) {
        count = segments;
    } else if (circle_segments > 0) {
        count = static_cast<int>(std::ceil(span / (2. * polygon_pi) * std::max(3, circle_segments)));
    } else {
        const double radius = std::max(rx, ry);
        const double deflection = settings.get<ifcopenshell::geom::settings::MesherLinearDeflection>().get();
        const double angular = settings.get<ifcopenshell::geom::settings::MesherAngularDeflection>().get();
        double angle = polygon_pi / 2.;
        if (deflection > 0. && radius > deflection) {
            const double bound = 2. * std::acos(1. - deflection / radius);
            if (bound > 0.) {
                angle = std::min(angle, bound);
            }
        }
        if (angular > 0.) {
            angle = std::min(angle, angular);
        }
        count = static_cast<int>(std::ceil(span / angle));
    }
    count = std::max(1, count);
    std::vector<point3> points;
    points.reserve(count + 1);
    for (int i = 0; i <= count; ++i) {
        const double u = a + span * i / count;
        points.emplace_back(transform_point(matrix, {rx * std::cos(u), ry * std::sin(u), 0.}));
    }
    return points;
}

std::vector<point3> trimmed_curve::to_polygon(const ifcopenshell::geom::settings& settings) const {
    std::vector<point3> points;
    if ((!basis || basis->kind() == LINE) && start.index() == 1 && end.index() == 1) {
        const Eigen::Vector3d a = std::get<point3::ptr>(start)->ccomponents();
        const Eigen::Vector3d b = std::get<point3::ptr>(end)->ccomponents();
        const int count = std::max(1, polygon_segments);
        for (int i = 0; i <= count; ++i) {
            points.emplace_back(a + (b - a) * i / count);
        }
    } else {
        auto underlying = basis;
        while (auto nested = std::dynamic_pointer_cast<trimmed_curve>(underlying)) {
            underlying = nested->basis;
        }
        auto c = std::dynamic_pointer_cast<curve>(underlying);
        if (!c) {
            throw std::runtime_error("Unsupported curve basis");
        }
        const bool full_conic = start.index() == 0 && end.index() == 0 &&
                                (c->kind() == CIRCLE || c->kind() == ELLIPSE);
        double a = full_conic ? 0. : curve_parameter(underlying, start);
        double b = full_conic ? 2. * polygon_pi : curve_parameter(underlying, end);
        if (!curve_sense.value_or(true)) {
            std::swap(a, b);
        }
        points = c->to_polygon(settings, a, b, polygon_segments);
        if (!curve_sense.value_or(true)) {
            std::reverse(points.begin(), points.end());
        }
    }
    if (!orientation.value_or(true)) {
        std::reverse(points.begin(), points.end());
    }
    for (auto& p : points) {
        p.components() = transform_point(matrix, p.ccomponents());
    }
    return points;
}

std::vector<point3> loop::to_polygon(const ifcopenshell::geom::settings& settings) const {
    std::vector<point3> points;
    const double tolerance = settings.get<ifcopenshell::geom::settings::Precision>().get();
    for (const auto& e : children) {
        append_polygon(points, e->to_polygon(settings), tolerance);
    }
    if (closed.value_or(false) && points.size() > 1 &&
        (points.front().ccomponents() - points.back().ccomponents()).norm() > tolerance) {
        points.push_back(points.front());
    }
    if (!orientation.value_or(true)) {
        std::reverse(points.begin(), points.end());
    }
    for (auto& p : points) {
        p.components() = transform_point(matrix, p.ccomponents());
    }
    return points;
}

namespace {
bool polygonal(const item::ptr& i) {
    if (!i) {
        return true; // An interpolated loft has no remaining analytic directrix.
    }
    if (i->kind() == LINE) {
        return true;
    }
    if (auto e = std::dynamic_pointer_cast<edge>(i)) {
        return (!e->basis || e->basis->kind() == LINE) &&
               (e->basis || (e->start.index() == 1 && e->end.index() == 1));
    }
    if (auto l = std::dynamic_pointer_cast<loop>(i)) {
        return !l->children.empty() && std::all_of(l->children.begin(), l->children.end(), [](const edge::ptr& e) { return polygonal(e); });
    }
    if (auto f = std::dynamic_pointer_cast<face>(i)) {
        return (!f->basis || f->basis->kind() == PLANE) && !f->children.empty() &&
               std::all_of(f->children.begin(), f->children.end(), [](const loop::ptr& l) { return polygonal(l); });
    }
    return false;
}

loop::ptr polygon_loop(std::vector<point3::ptr> points, bool closed, bool external = true) {
    if (closed && points.front() != points.back()) {
        points.push_back(points.front());
    }
    auto l = ifcopenshell::geom::polygon_from_points(points, external);
    l->closed = closed;
    return l;
}

void triangle(const shell::ptr& s, const point3::ptr& a, const point3::ptr& b, const point3::ptr& c) {
    if ((b->ccomponents() - a->ccomponents()).cross(c->ccomponents() - a->ccomponents()).squaredNorm() == 0.) {
        return;
    }
    auto f = make<face>();
    f->children = {polygon_loop({a, b, c}, true)};
    s->children.push_back(f);
}

bool intersect_tags(const std::set<std::string>& a, const std::set<std::string>& b) {
    for (const auto& tag : a) {
        if (b.count(tag)) {
            return true;
        }
    }
    return false;
}

struct polygon_section {
    std::vector<point3::ptr> points;
    std::vector<std::set<std::string>> tags;
    bool closed, external;
};

polygon_section section_polygon(const loop::ptr& l, const matrix4::ptr& parent) {
    ifcopenshell::geom::settings settings;
    auto points = l->to_polygon(settings);
    auto tags = l->tags;
    if (tags && !l->orientation.value_or(true)) {
        std::reverse(tags->begin(), tags->end());
    }
    polygon_section section;
    section.closed = l->closed.value_or(points.size() > 1 &&
                                        (points.front().ccomponents() - points.back().ccomponents()).norm() < 1.e-9);
    section.external = l->external.value_or(true);
    // Tags name vertices, including coincident vertices carrying different names.
    if (tags && tags->size() != points.size()) {
        // to_polygon removes coincident vertices; retain them until their tags are merged.
        points.clear();
        if (!l->children.empty()) {
            points.push_back(*std::get<point3::ptr>(l->children.front()->start));
            for (const auto& e : l->children) {
                points.push_back(*std::get<point3::ptr>(e->end));
            }
            for (auto& p : points) {
                p.components() = transform_point(l->matrix, p.ccomponents());
            }
            if (!l->orientation.value_or(true)) {
                std::reverse(points.begin(), points.end());
            }
        }
    }
    if (tags && tags->size() != points.size()) {
        throw std::runtime_error("Profile vertex and tag counts differ");
    }
    const bool fixed_sampling = std::any_of(l->children.begin(), l->children.end(), [](const edge::ptr& e) { return e->polygon_segments > 0; });
    for (size_t i = 0; i < points.size(); ++i) {
        auto p = make<point3>(transform_point(parent, points[i].ccomponents()));
        if (!fixed_sampling && !section.points.empty() && p->ccomponents() == section.points.back()->ccomponents()) {
            if (tags) {
                section.tags.back().insert((*tags)[i]);
            }
        } else {
            section.points.push_back(p);
            if (tags) {
                section.tags.push_back({(*tags)[i]});
            }
        }
    }
    if (section.closed && section.points.size() > 1 &&
        (section.points.front()->ccomponents() - section.points.back()->ccomponents()).norm() < 1.e-9) {
        if (!section.tags.empty()) {
            section.tags.front().insert(section.tags.back().begin(), section.tags.back().end());
            section.tags.pop_back();
        }
        section.points.pop_back();
    }
    if (section.points.size() < (section.closed ? 3u : 2u)) {
        throw std::runtime_error("Not enough profile vertices");
    }
    return section;
}

void connect_sections(const shell::ptr& s, const polygon_section& a, const polygon_section& b) {
    if (a.closed != b.closed || a.external != b.external) {
        throw std::runtime_error("Incompatible loft profile boundaries");
    }
    if (!a.tags.empty() || !b.tags.empty()) {
        if (a.closed || a.tags.empty() || b.tags.empty() || !intersect_tags(a.tags.front(), b.tags.front())) {
            throw std::runtime_error("Starting vertices do not have corresponding tags");
        }
        size_t i = 0, j = 0;
        while (i + 1 < a.points.size() || j + 1 < b.points.size()) {
            if (i + 1 < a.points.size() && intersect_tags(a.tags[i + 1], b.tags[j])) {
                triangle(s, a.points[i], a.points[i + 1], b.points[j]);
                ++i;
            } else if (j + 1 < b.points.size() && intersect_tags(a.tags[i], b.tags[j + 1])) {
                triangle(s, a.points[i], b.points[j + 1], b.points[j]);
                ++j;
            } else if (i + 1 < a.points.size() && j + 1 < b.points.size() && intersect_tags(a.tags[i + 1], b.tags[j + 1])) {
                triangle(s, a.points[i], a.points[i + 1], b.points[j]);
                triangle(s, a.points[i + 1], b.points[j + 1], b.points[j]);
                ++i;
                ++j;
            } else {
                throw std::runtime_error("Unable to construct surface from profile tags");
            }
        }
        return;
    }
    if (a.points.size() != b.points.size()) {
        throw std::runtime_error("Loft profile vertex counts differ without corresponding tags");
    }
    const size_t count = a.points.size() - (a.closed ? 0 : 1);
    for (size_t i = 0; i < count; ++i) {
        const size_t j = (i + 1) % a.points.size();
        if (a.external) {
            triangle(s, a.points[i], a.points[j], b.points[j]);
            triangle(s, b.points[j], b.points[i], a.points[i]);
        } else {
            triangle(s, a.points[i], b.points[j], a.points[j]);
            triangle(s, b.points[j], a.points[i], b.points[i]);
        }
    }
}
} // namespace

bool loft::is_polygonal() const {
    return polygonal(axis) && !children.empty() &&
           std::all_of(children.begin(), children.end(), [](const geom_item::ptr& i) { return polygonal(i); });
}

loft::ptr loft::make_compatible_sections(const ifcopenshell::geom::settings& settings) const {
    if (children.empty()) throw std::runtime_error("Loft has no sections");
    std::vector<std::vector<loop::ptr>> boundaries;
    const bool solid = children.front()->kind() == FACE;
    for (const auto& child : children) {
        std::vector<loop::ptr> loops;
        if (auto f = std::dynamic_pointer_cast<face>(child); solid && f) {
            if (f->basis && f->basis->kind() != PLANE) throw std::runtime_error("Loft sections must be planar");
            for (bool outer : {true, false}) {
                for (const auto& l : f->children) {
                    if (l->external.value_or(f->children.size() == 1) == outer) loops.push_back(l);
                }
            }
        } else if (auto l = std::dynamic_pointer_cast<loop>(child); !solid && l) {
            loops = {l};
        } else {
            throw std::runtime_error("Incompatible loft section types: expected corresponding faces or loops");
        }
        if (loops.empty() || (!boundaries.empty() && loops.size() != boundaries.front().size())) {
            throw std::runtime_error("Loft profile boundary counts differ");
        }
        boundaries.push_back(std::move(loops));
    }
    std::vector<std::vector<int>> counts(boundaries.front().size());
    std::vector<std::vector<bool>> sample(boundaries.front().size());
    for (size_t i = 0; i < boundaries.front().size(); ++i) {
        const auto& first = boundaries.front()[i];
        const bool tagged = first->tags.has_value();
        for (const auto& section : boundaries) {
            const auto& l = section[i];
            if (l->tags.has_value() != tagged || l->closed != first->closed ||
                l->external.value_or(solid) != first->external.value_or(solid) ||
                l->orientation.value_or(true) != first->orientation.value_or(true)) {
                throw std::runtime_error("Incompatible loft boundary " + std::to_string(i + 1) + ": tags, closure, exterior or orientation differ");
            }
            if (tagged) {
                if (!polygonal(l)) throw std::runtime_error("Curved loft boundaries with vertex tags are not supported");
            } else if (l->children.size() != first->children.size()) {
                throw std::runtime_error("Loft boundary " + std::to_string(i + 1) + " edge counts differ without corresponding tags");
            }
        }
        if (tagged) continue; // Keep the existing correspondence of tagged linear profiles.
        for (size_t j = 0; j < first->children.size(); ++j) {
            const auto& edge = first->children[j];
            bool curved = !polygonal(edge), equal = true;
            for (const auto& section : boundaries) {
                const auto& other = section[i]->children[j];
                if (edge->orientation.value_or(true) != other->orientation.value_or(true)) {
                    throw std::runtime_error("Loft boundary " + std::to_string(i + 1) + " edge " + std::to_string(j + 1) + " orientations differ");
                }
                auto full_turn = [](const taxonomy::edge::ptr& e) {
                    return e->basis && (e->basis->kind() == CIRCLE || e->basis->kind() == ELLIPSE) &&
                        e->start.index() == 2 && e->end.index() == 2 &&
                        std::abs(std::abs(std::get<double>(e->end) - std::get<double>(e->start)) - 2. * polygon_pi) < 1.e-9;
                };
                if (full_turn(edge) && full_turn(other)) {
                    if (edge->curve_sense.value_or(true) != other->curve_sense.value_or(true) ||
                        std::abs(std::remainder(std::get<double>(edge->start) - std::get<double>(other->start), 2. * polygon_pi)) > 1.e-9) {
                        throw std::runtime_error("Loft closed-edge seams or sweep directions do not correspond");
                    }
                }
                curved = curved || !polygonal(other);
                equal = equal && equal_functor{}(edge, other);
            }
            // Changing edges use the same representation at every station,
            // including authored stations and intervals where that edge is equal.
            // This also keeps the raw edge layout compatible with ruled surfaces.
            sample[i].push_back(curved && !equal);
            int count = static_cast<int>(edge->to_polygon(settings).size()) - 1;
            if (curved && polygonal(edge)) count = std::max(3, count);
            if (count < 1) throw std::runtime_error("Loft edge has no usable sampling interval");
            counts[i].push_back(count);
        }
    }
    auto copy_metadata = [](const geom_item& source, geom_item& target) {
        target.instance = source.instance;
        target.matrix = source.matrix;
        target.surface_style = source.surface_style;
        target.orientation = source.orientation;
    };
    auto result = make<loft>(*this);
    copy_metadata(*this, *result);
    result->children.clear();
    for (size_t k = 0; k < children.size(); ++k) {
        std::vector<loop::ptr> loops;
        for (size_t i = 0; i < boundaries[k].size(); ++i) {
            const auto& source = boundaries[k][i];
            auto l = make<loop>(*source);
            copy_metadata(*source, *l);
            l->children.clear();
            for (size_t j = 0; j < source->children.size(); ++j) {
                auto e = make<edge>(*source->children[j]);
                if (source->tags) {
                    l->children.push_back(e);
                    continue;
                }
                e->polygon_segments = counts[i][j];
                if (!sample[i][j]) {
                    l->children.push_back(e);
                } else {
                    const auto points = e->to_polygon(settings);
                    for (size_t p = 1; p < points.size(); ++p) {
                        auto segment = make<edge>(make<point3>(points[p - 1]), make<point3>(points[p]));
                        segment->polygon_segments = 1;
                        l->children.push_back(segment);
                    }
                }
            }
            loops.push_back(l);
        }
        if (solid) {
            auto f = make<face>(*std::static_pointer_cast<face>(children[k]));
            copy_metadata(*children[k], *f);
            f->children = std::move(loops);
            result->children.push_back(f);
        } else {
            result->children.push_back(loops.front());
        }
    }
    return result;
}

loft::ptr loft::make_polygonal_sections(const ifcopenshell::geom::settings& settings) const {
    if (!polygonal(axis)) {
        throw std::runtime_error("Polygonal loft sections require a polygonal or interpolated directrix");
    }
    auto compatible = make_compatible_sections(settings);
    auto copy_metadata = [](const geom_item& source, geom_item& target) {
        target.instance = source.instance;
        target.matrix = source.matrix;
        target.surface_style = source.surface_style;
        target.orientation = source.orientation;
    };
    auto polygonal_loop = [&](const loop::ptr& source) {
        if (polygonal(source) && (!source->matrix || source->matrix->is_identity()) && source->orientation.value_or(true)) {
            return source;
        }
        if (source->tags) {
            if (polygonal(source)) return source;
            throw std::runtime_error("Tessellating curved profile boundaries with vertex tags is not supported");
        }
        auto sampled = source->to_polygon(settings);
        if (sampled.size() < 2) {
            throw std::runtime_error("Not enough tessellated profile vertices");
        }
        std::vector<point3::ptr> points;
        for (const auto& p : sampled) {
            points.push_back(make<point3>(p));
        }
        const auto tolerance = settings.get<ifcopenshell::geom::settings::Precision>().get();
        const bool closed = source->closed.value_or((points.front()->ccomponents() - points.back()->ccomponents()).norm() <= tolerance);
        if (closed && (points.front()->ccomponents() - points.back()->ccomponents()).norm() <= tolerance) {
            points.back() = points.front();
        }
        auto result = make<loop>(*source);
        copy_metadata(*source, *result);
        result->children = polygon_loop(std::move(points), closed, source->external.value_or(true))->children;
        for (auto& e : result->children) e->polygon_segments = 1;
        result->closed = closed;
        // to_polygon has already applied these to the vertices.
        result->matrix = nullptr;
        result->orientation = true;
        return result;
    };
    auto result = make<loft>(*this);
    copy_metadata(*this, *result);
    result->children.clear();
    for (const auto& child : compatible->children) {
        if (auto f = std::dynamic_pointer_cast<face>(child)) {
            if (f->basis && f->basis->kind() != PLANE) {
                throw std::runtime_error("Tessellating loft sections requires planar faces");
            }
            auto copy = make<face>(*f);
            copy_metadata(*f, *copy);
            copy->children.clear();
            for (const auto& l : f->children) {
                copy->children.push_back(polygonal_loop(l));
            }
            result->children.push_back(copy);
        } else if (auto l = std::dynamic_pointer_cast<loop>(child)) {
            result->children.push_back(polygonal_loop(l));
        } else {
            throw std::runtime_error("Loft sections must be faces or loops");
        }
    }
    return result;
}

shell::ptr loft::to_polyhedron() const {
    if (!is_polygonal() || children.size() < 2) {
        throw std::runtime_error("Loft requires at least two polygonal sections and a polygonal directrix");
    }
    auto s = make<shell>();
    s->instance = instance;
    s->matrix = matrix;
    s->surface_style = surface_style;
    const bool capped = children.front()->kind() == FACE;
    s->closed = capped;
    std::vector<std::vector<polygon_section>> sections;
    for (const auto& child : children) {
        if ((child->kind() == FACE) != capped) {
            throw std::runtime_error("Mixed surface and solid loft sections");
        }
        std::vector<polygon_section> section;
        if (auto f = std::dynamic_pointer_cast<face>(child)) {
            // Match exterior boundaries first, retaining inner-boundary order.
            for (bool exterior : {true, false}) {
                for (const auto& l : f->children) {
                    if (l->external.value_or(f->children.size() == 1) == exterior) {
                        section.push_back(section_polygon(l, f->matrix));
                    }
                }
            }
        } else {
            section.push_back(section_polygon(std::static_pointer_cast<loop>(child), nullptr));
        }
        if (capped && !section.empty()) {
            auto normal = [](const polygon_section& boundary) {
                Eigen::Vector3d n = Eigen::Vector3d::Zero();
                const auto& p = boundary.points;
                for (size_t i = 1; i + 1 < p.size(); ++i) {
                    n += (p[i]->ccomponents() - p.front()->ccomponents()).cross(p[i + 1]->ccomponents() - p.front()->ccomponents());
                }
                return n;
            };
            const Eigen::Vector3d outer_normal = normal(section.front());
            for (size_t i = 1; i < section.size(); ++i) {
                if (outer_normal.dot(normal(section[i])) < 0.) {
                    std::reverse(section[i].points.begin(), section[i].points.end());
                    std::reverse(section[i].tags.begin(), section[i].tags.end());
                }
            }
        }
        if (!sections.empty() && sections.back().size() != section.size()) {
            throw std::runtime_error("Loft profile boundary counts differ");
        }
        sections.push_back(std::move(section));
    }
    if (capped) {
        auto centroid = [](const polygon_section& section) {
            Eigen::Vector3d result = Eigen::Vector3d::Zero();
            for (const auto& p : section.points) {
                result += p->ccomponents();
            }
            return (result / section.points.size()).eval();
        };
        const auto& first = sections.front().front().points;
        Eigen::Vector3d normal = Eigen::Vector3d::Zero();
        for (size_t i = 1; i + 1 < first.size(); ++i) {
            normal += (first[i]->ccomponents() - first.front()->ccomponents()).cross(first[i + 1]->ccomponents() - first.front()->ccomponents());
        }
        const Eigen::Vector3d origin = centroid(sections.front().front());
        for (size_t i = 1; i < sections.size(); ++i) {
            const double sense = normal.dot(centroid(sections[i].front()) - origin);
            if (sense != 0.) {
                if (sense < 0.) {
                    for (auto& section : sections) {
                        for (auto& boundary : section) {
                            std::reverse(boundary.points.begin(), boundary.points.end());
                            std::reverse(boundary.tags.begin(), boundary.tags.end());
                        }
                    }
                }
                break;
            }
        }
    }
    if (capped) {
        for (size_t index : {size_t(0), sections.size() - 1}) {
            auto cap = make<face>();
            for (const auto& boundary : sections[index]) {
                if (!boundary.closed) {
                    throw std::runtime_error("Solid loft profile must be closed");
                }
                auto points = boundary.points;
                if (index == 0) {
                    std::reverse(points.begin(), points.end());
                }
                cap->children.push_back(polygon_loop(points, true, boundary.external));
            }
            s->children.push_back(cap);
        }
    }
    for (size_t i = 1; i < sections.size(); ++i) {
        for (size_t j = 0; j < sections[i].size(); ++j) {
            connect_sections(s, sections[i - 1][j], sections[i][j]);
        }
    }
    return s;
}

shell::ptr sweep_along_curve::to_polyhedron(const ifcopenshell::geom::settings& settings) const {
    const auto profile = std::dynamic_pointer_cast<face>(basis);
    if (!profile || profile->children.empty() || surface || direction) {
        throw std::runtime_error("Polygonal sweep requires a circular disk profile");
    }
    std::vector<double> radii;
    for (const auto& l : profile->children) {
        if (l->children.size() != 1) {
            throw std::runtime_error("Polygonal sweep requires concentric full circles");
        }
        const auto& e = l->children.front();
        auto c = std::dynamic_pointer_cast<circle>(e->basis);
        auto identity = [](const matrix4::ptr& m) { return !m || m->is_identity(); };
        if (!c || c->radius <= 0. || !identity(c->matrix) || !identity(l->matrix) ||
            !identity(profile->matrix) || !identity(e->matrix) ||
            e->start.index() != 2 || e->end.index() != 2 ||
            std::abs(std::abs(std::get<double>(e->end) - std::get<double>(e->start)) - 2. * polygon_pi) > 1.e-9) {
            throw std::runtime_error("Polygonal sweep requires concentric full circles");
        }
        radii.push_back(c->radius);
    }
    if (radii.size() > 2 || (radii.size() == 2 && radii[1] >= radii[0])) {
        throw std::runtime_error("Invalid swept disk radii");
    }
    std::vector<point3> polygon;
    if (auto l = std::dynamic_pointer_cast<loop>(curve)) {
        polygon = l->to_polygon(settings);
    } else if (auto e = std::dynamic_pointer_cast<trimmed_curve>(curve)) {
        polygon = e->to_polygon(settings);
    } else if (auto c = std::dynamic_pointer_cast<taxonomy::curve>(curve)) {
        if (c->kind() == LINE) {
            throw std::runtime_error("Swept disk directrix must be bounded");
        }
        polygon = c->to_polygon(settings);
    } else {
        throw std::runtime_error("Unsupported swept disk directrix");
    }
    const double tolerance = settings.get<ifcopenshell::geom::settings::Precision>().get();
    std::vector<Eigen::Vector3d> path;
    for (const auto& p : polygon) {
        if (path.empty() || (p.ccomponents() - path.back()).norm() > tolerance) {
            path.push_back(p.ccomponents());
        }
    }
    const bool closed = path.size() > 2 && (path.front() - path.back()).norm() < tolerance;
    if (closed) {
        path.pop_back();
    }
    if (path.size() < (closed ? 3u : 2u)) {
        throw std::runtime_error("Not enough swept disk directrix vertices");
    }
    auto c = make<circle>();
    c->radius = radii.front();
    const size_t count = c->to_polygon(settings).size() - 1;
    const size_t segment_count = path.size() - (closed ? 0 : 1);
    std::vector<Eigen::Vector3d> tangents, axes;
    std::vector<double> lengths;
    double total_length = 0.;
    for (size_t i = 0; i < segment_count; ++i) {
        Eigen::Vector3d delta = path[(i + 1) % path.size()] - path[i];
        lengths.push_back(delta.norm());
        total_length += lengths.back();
        tangents.push_back(delta.normalized());
    }
    axes.push_back(tangents.front().unitOrthogonal());
    for (size_t i = 1; i < tangents.size(); ++i) {
        if (tangents[i - 1].dot(tangents[i]) < -1. + 1.e-9) {
            throw std::runtime_error("Swept disk directrix reverses at a vertex");
        }
        axes.push_back(Eigen::Quaterniond::FromTwoVectors(tangents[i - 1], tangents[i]) * axes.back());
    }
    // Parallel transport gives the minimum rotation between consecutive segments.
    // Circular polygons are invariant under a cyclic shift of their vertices.
    // Distribute only the residual holonomy, at most half a polygon segment.
    if (closed) {
        if (tangents.back().dot(tangents.front()) < -1. + 1.e-9) {
            throw std::runtime_error("Swept disk directrix reverses at the seam");
        }
        Eigen::Vector3d last = Eigen::Quaterniond::FromTwoVectors(tangents.back(), tangents.front()) * axes.back();
        const double correction = std::remainder(
            std::atan2(tangents.front().dot(last.cross(axes.front())), last.dot(axes.front())), 2. * polygon_pi / count);
        double distance = 0.;
        for (size_t i = 1; i < axes.size(); ++i) {
            distance += lengths[i - 1];
            axes[i] = Eigen::AngleAxisd(correction * distance / total_length, tangents[i]) * axes[i];
        }
    }
    std::vector<std::vector<polygon_section>> sections;
    for (size_t i = 0; i < path.size(); ++i) {
        const size_t incoming = i == 0 ? (closed ? segment_count - 1 : 0) : i - 1;
        const size_t outgoing = i < segment_count ? i : segment_count - 1;
        const Eigen::Vector3d tangent = tangents[incoming];
        Eigen::Vector3d normal = (tangent + tangents[outgoing]).normalized();
        if (!closed && (i == 0 || i + 1 == path.size())) {
            normal = endpoint_tangent(curve, i != 0);
        }
        Eigen::Vector3d x = axes[incoming];
        if (closed && i == 0) {
            x = Eigen::Quaterniond::FromTwoVectors(tangents.front(), tangent) * axes.front();
        }
        const Eigen::Vector3d y = tangent.cross(x).normalized();
        std::vector<polygon_section> section;
        for (size_t r = 0; r < radii.size(); ++r) {
            polygon_section boundary;
            boundary.closed = true;
            boundary.external = r == 0;
            for (size_t j = 0; j < count; ++j) {
                const double angle = 2. * polygon_pi * j / count;
                Eigen::Vector3d offset = radii[r] * (std::cos(angle) * x + std::sin(angle) * y);
                // Intersect the incoming cylinder generators with the miter plane.
                offset -= tangent * (normal.dot(offset) / normal.dot(tangent));
                boundary.points.push_back(make<point3>((path[i] + offset).eval()));
            }
            section.push_back(std::move(boundary));
        }
        sections.push_back(std::move(section));
    }
    auto s = make<shell>();
    s->closed = true;
    s->instance = instance;
    s->matrix = matrix;
    s->surface_style = surface_style;
    for (size_t i = 0; i < segment_count; ++i) {
        const size_t next = (i + 1) % sections.size();
        size_t shift = 0;
        if (closed && next == 0) {
            const auto& tangent = tangents[i];
            auto perpendicular = [&](const Eigen::Vector3d& p) -> Eigen::Vector3d { return p - tangent * tangent.dot(p); };
            const Eigen::Vector3d a = perpendicular(sections[i][0].points.front()->ccomponents() - path[i]);
            double best = std::numeric_limits<double>::infinity();
            for (size_t j = 0; j < count; ++j) {
                const double distance = (a - perpendicular(sections[next][0].points[j]->ccomponents() - path[next])).squaredNorm();
                if (distance < best) {
                    best = distance;
                    shift = j;
                }
            }
        }
        for (size_t r = 0; r < radii.size(); ++r) {
            auto end = sections[next][r];
            std::rotate(end.points.begin(), end.points.begin() + shift, end.points.end());
            connect_sections(s, sections[i][r], end);
        }
    }
    if (!closed) {
        for (size_t index : {size_t(0), sections.size() - 1}) {
            if (radii.size() == 1) {
                auto center = make<point3>(path[index]);
                const auto& points = sections[index][0].points;
                for (size_t j = 0; j < count; ++j) {
                    if (index == 0) {
                        triangle(s, center, points[(j + 1) % count], points[j]);
                    } else {
                        triangle(s, center, points[j], points[(j + 1) % count]);
                    }
                }
            } else {
                const auto& outer = sections[index][0].points;
                const auto& inner = sections[index][1].points;
                for (size_t j = 0; j < count; ++j) {
                    const size_t k = (j + 1) % count;
                    if (index == 0) {
                        triangle(s, outer[j], inner[k], outer[k]);
                        triangle(s, outer[j], inner[j], inner[k]);
                    } else {
                        triangle(s, outer[j], outer[k], inner[k]);
                        triangle(s, outer[j], inner[k], inner[j]);
                    }
                }
            }
        }
    }
    return s;
}

namespace {
	bool compare(const trimmed_curve& a, const trimmed_curve& b);

	bool compare(const collection& a, const collection& b);

	bool compare(const loop& a, const loop& b);

	bool compare(const face& a, const face& b);

	bool compare(const shell& a, const shell& b);

	bool compare(const solid& a, const solid& b);

	bool compare(const loft& a, const loft& b);

	bool compare(const boolean_result& a, const boolean_result& b);

	template <typename T>
	bool compare(const eigen_base<T>& t, const eigen_base<T>& u) {
		if (t.components_ == nullptr && u.components_ == nullptr) {
			return false;
		}
		else if (t.components_ == nullptr && u.components_ != nullptr) {
			return true;
		}
		else if (t.components_ != nullptr && u.components_ == nullptr) {
			return false;
		}

		auto t_begin = t.components_->data();
		auto t_end = t.components_->data() + t.components_->size();

		auto u_begin = u.components_->data();
		auto u_end = u.components_->data() + u.components_->size();

		return std::lexicographical_compare(t_begin, t_end, u_begin, u_end);
	}

	bool compare_matrix(const matrix4::ptr& a, const matrix4::ptr& b) {
		const Eigen::Matrix4d am = a ? a->ccomponents() : Eigen::Matrix4d::Identity();
		const Eigen::Matrix4d bm = b ? b->ccomponents() : Eigen::Matrix4d::Identity();
		return std::lexicographical_compare(am.data(), am.data() + am.size(), bm.data(), bm.data() + bm.size());
	}

	bool compare(const line& a, const line& b) {
		return compare_matrix(a.matrix, b.matrix);
	}

	bool compare(const plane& a, const plane& b) {
		return compare_matrix(a.matrix, b.matrix);
	}

	bool compare(const circle& a, const circle& b) {
		if (a.radius == b.radius) {
			return compare_matrix(a.matrix, b.matrix);
		}
		return a.radius < b.radius;
	}

	bool compare(const ellipse& a, const ellipse& b) {
		if (a.radius == b.radius && a.radius2 == b.radius2) {
			return compare_matrix(a.matrix, b.matrix);
		}
		return
			std::tie(a.radius, a.radius2) <
			std::tie(b.radius, b.radius2);
	}

	bool compare(const bspline_curve& a, const bspline_curve& b) {
		const auto ad = std::tie(a.degree, a.multiplicities, a.knots, a.weights);
		const auto bd = std::tie(b.degree, b.multiplicities, b.knots, b.weights);
		if (ad != bd) {
			return ad < bd;
		}
		if (a.control_points.size() != b.control_points.size()) {
			return a.control_points.size() < b.control_points.size();
		}
		for (size_t i = 0; i < a.control_points.size(); ++i) {
			if (less(a.control_points[i], b.control_points[i])) return true;
			if (less(b.control_points[i], a.control_points[i])) return false;
		}
		return compare_matrix(a.matrix, b.matrix);
	}

	template <typename T>
	typename std::enable_if<std::is_base_of<item, T>::value, int>::type less_to_order(const T& a, const T& b) {
		const bool a_lt_b = compare(a, b);
		const bool b_lt_a = compare(b, a);
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	template <typename T>
	typename std::enable_if<!std::is_base_of<item, T>::value, int>::type less_to_order(const T& a, const T& b) {
		const bool a_lt_b = a < b;
		const bool b_lt_a = b < a;
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	template <typename T>
	int less_to_order_optional(const std::optional<T>& a, const std::optional<T>& b) {
		if (a && b) {
			return less_to_order(*a, *b);
		}
		else if (!a && !b) {
			return 0;
		}
		else if (a) {
			return 1;
		}
		else {
			return -1;
		}
	}

	int compare(const std::variant<boost::blank, point3::ptr, double>& a, const std::variant<boost::blank, point3::ptr, double>& b) {
		if (a.index() != b.index()) {
			return a.index() < b.index() ? -1 : 1;
		}
		bool a_lt_b, b_lt_a;
		if (a.index() == 0) {
			return 0;
		} else if (a.index() == 1) {
			a_lt_b = compare(*std::get<point3::ptr>(a), *std::get<point3::ptr>(b));
			b_lt_a = compare(*std::get<point3::ptr>(b), *std::get<point3::ptr>(a));
		} else {
			a_lt_b = std::less<double>()(std::get<double>(a), std::get<double>(b));
			b_lt_a = std::less<double>()(std::get<double>(b), std::get<double>(a));
		}
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	bool compare(const extrusion& a, const extrusion& b) {
		// @todo extrusions can also have non-identity matrices right? perhaps it's time
		//       for a dedicated transform node and not on the abstract geom_item.
		const int order[3] = {
			less_to_order(a.basis, b.basis),
			less_to_order(a.direction, b.direction),
			a.depth < b.depth ? -1 : (a.depth == b.depth ? 0 : 1)
		};
		auto it = std::find_if(std::begin(order), std::end(order), [](int x) { return x; });
		if (it == std::end(order)) return false;
		return *it == -1;
	}

	bool compare(const node&, const node&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const offset_curve&, const offset_curve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const revolve&, const revolve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const bspline_surface&, const bspline_surface&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const cylinder&, const cylinder&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const sphere&, const sphere&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const torus&, const torus&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const sweep_along_curve&, const sweep_along_curve&) {
		throw std::runtime_error("not implemented");
	}

    bool compare(const function_item&, const function_item&) {
        throw std::runtime_error("not implemented");
    }

    bool compare(const functor_item&, const functor_item&) {
        throw std::runtime_error("not implemented");
    }

	bool compare(const piecewise_function&, const piecewise_function&) {
		throw std::runtime_error("not implemented");
	}

   bool compare(const gradient_function&, const gradient_function&) {
        throw std::runtime_error("not implemented");
   }

   bool compare(const cant_function&, const cant_function&) {
       throw std::runtime_error("not implemented");
   }

   bool compare(const offset_function&, const offset_function&) {
       throw std::runtime_error("not implemented");
   }

	/* A compile-time for loop over the taxonomy kinds */
	template <size_t N>
	struct dispatch_comparison {
		static bool dispatch(const item* a, const item* b) {
			if (N == a->kind() && N == b->kind()) {
				auto A = static_cast<const type_by_kind::type<N>*>(a);
				auto B = static_cast<const type_by_kind::type<N>*>(b);
				return compare(*A, *B);
			}
			else {
				return dispatch_comparison<N + 1>::dispatch(a, b);
			}
		}
	};

	template <>
	struct dispatch_comparison<type_by_kind::max> {
		static bool dispatch(const item*, const item*) {
			return false;
		}
	};
}

ifcopenshell::geom::taxonomy::topology_error::~topology_error() = default;

bool ifcopenshell::geom::taxonomy::less(item::const_ptr a, item::const_ptr b) {
	if (a == b) {
		return false;
	}
	if (!a || !b) {
		return !a;
	}

	int a_kind = a->kind();
	int b_kind = b->kind();

	if (a_kind != b_kind) {
		return a_kind < b_kind;
	}

#ifdef TAXONOMY_USE_SHARED_PTR
	return dispatch_comparison<0>::dispatch(a.get(), b.get());
#endif
}


namespace {
	bool compare(const trimmed_curve& a, const trimmed_curve& b) {
		const auto a_sense = std::make_pair(a.orientation.value_or(true), a.curve_sense.value_or(true));
		const auto b_sense = std::make_pair(b.orientation.value_or(true), b.curve_sense.value_or(true));
		if (a_sense != b_sense) return a_sense < b_sense;
		if (compare_matrix(a.matrix, b.matrix)) return true;
		if (compare_matrix(b.matrix, a.matrix)) return false;
		std::size_t a_which_start = a.start.index();
		std::size_t a_which_end = a.end.index();
		std::size_t b_which_start = b.start.index();
		std::size_t b_which_end = b.end.index();
		if (std::tie(a_which_start, a_which_end) == std::tie(b_which_start, b_which_end)) {

			int start_state = compare(a.start, b.start);

			if (start_state == 0) {

				int end_state = compare(a.end, b.end);

				if (end_state == 0) {

					int a_has_basis = !!a.basis;
					int b_has_basis = !!b.basis;

					if (a_has_basis == b_has_basis) {

						if (!a_has_basis) {
							// Finally, equality
							return false;
						}
						else {
							return less(a.basis, b.basis);
						}

					}
					else {
						return a_has_basis < b_has_basis;
					}

				}
				else {
					return end_state == -1;
				}

			}
			else {
				return start_state == -1;
			}

		}
		else {
			return
				std::tie(a_which_start, a_which_end) < std::tie(b_which_start, b_which_end);
		}
	}

	template <typename T>
	bool compare_collection(const collection_base<T>& a, const collection_base<T>& b) {
		if (a.children.size() == b.children.size()) {
			auto at = a.children.begin();
			auto bt = b.children.begin();
			for (; at != a.children.end(); ++at, ++bt) {
				const bool a_lt_b = less(*at, *bt);
				const bool b_lt_a = less(*bt, *at);
				if (!a_lt_b && !b_lt_a) {
					// Elements equal.
					continue;
				}
				return a_lt_b;
			}
			// Vectors equal, compare matrix (in case of mapped items).
			return compare_matrix(a.matrix, b.matrix);
		}
		else {
			return a.children.size() < b.children.size();
		}
	}

	bool compare(const loop& a, const loop& b) {
		return compare_collection<edge>(a, b);
	}

	bool compare(const face& a, const face& b) {
		return compare_collection<loop>(a, b);
	}

	bool compare(const shell& a, const shell& b) {
		return compare_collection<face>(a, b);
	}

	bool compare(const solid& a, const solid& b) {
		return compare_collection<shell>(a, b);
	}

	bool compare(const loft& a, const loft& b) {
		return compare_collection<geom_item>(a, b);
	}

	bool compare(const collection& a, const collection& b) {
		return compare_collection<geom_item>(a, b);
	}

	bool compare(const boolean_result& a, const boolean_result& b) {
		return compare_collection<geom_item>(a, b);
	}
}

ifcopenshell::geom::taxonomy::solid::ptr ifcopenshell::geom::create_box(double dx, double dy, double dz) {
	return create_box(0., 0., 0., dx, dy, dz);
}

ifcopenshell::geom::taxonomy::solid::ptr ifcopenshell::geom::create_box(double x, double y, double z, double dx, double dy, double dz) {
	auto solid = make<taxonomy::solid>();
	auto shell = make<taxonomy::shell>();
	solid->children.push_back(shell);

	// x = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0,  z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + 0,  z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// x = dx
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + dx, y + 0,  z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0,  z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// y = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0,  y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0,  y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// y = dy
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// z = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// z = dz
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	return solid;
}

///////////////////
piecewise_function::piecewise_function(double start, const span_list& s, const express::base& instance) : function_item(instance), start_(start), spans_(s) {
}

piecewise_function::piecewise_function(double start, const std::vector<piecewise_function::ptr>& pwfs, const express::base& instance) : function_item(instance), start_(start) {
    for (auto& pwf : pwfs) {
        spans_.insert(spans_.end(), pwf->spans().begin(), pwf->spans().end());
    }
};

const piecewise_function::span_list& piecewise_function::spans() const { return spans_; }
bool piecewise_function::is_empty() const { return spans_.empty(); }
double piecewise_function::start() const { return start_; }
double piecewise_function::end() const { return start_ + length(); }
double piecewise_function::length() const {
    return std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s->length(); });

    // this is a secondary option where we only compute length once and cache it.
    // mutex is needed to prevent interruption of the accumulation if there is multi-threading
    // skipping this detail for now and just adding up the span lengths every time
    //if (!length_.has_value()) {
    //    length_ = std::accumulate(spans_.begin(), spans_.end(), 0.0, [](const auto& v, const auto& s) { return v + s->length(); });
    //}
    //return *length_;
}


gradient_function::gradient_function(piecewise_function::const_ptr horizontal, piecewise_function::const_ptr vertical, const express::base& instance) :
	function_item(instance), horizontal_(horizontal), vertical_(vertical) {
}
double gradient_function::start() const { return std::max(horizontal_->start(), vertical_->start()); }
double gradient_function::end() const { return std::min(horizontal_->end(), vertical_->end()); }
piecewise_function::const_ptr gradient_function::get_horizontal() const { return horizontal_; }
piecewise_function::const_ptr gradient_function::get_vertical() const { return vertical_; }


cant_function::cant_function(gradient_function::const_ptr gradient, piecewise_function::const_ptr cant, const express::base& instance) :
	function_item(instance), gradient_(gradient), cant_(cant) {
}
double cant_function::start() const { return std::max(gradient_->start(), cant_->start()); }
double cant_function::end() const { return std::min(gradient_->end(), cant_->end()); }
gradient_function::const_ptr cant_function::get_gradient() const { return gradient_; }
piecewise_function::const_ptr cant_function::get_cant() const { return cant_; }


offset_function::offset_function(function_item::const_ptr basis, piecewise_function::const_ptr offset, const express::base& instance) : function_item(instance),
                                                                                                                                                                       basis_(basis),
                                                                                                                                                                       offset_(offset) {
}
double offset_function::start() const { return basis_->start(); }
double offset_function::end() const { return basis_->end(); }
function_item::const_ptr offset_function::get_basis() const { return basis_; }
piecewise_function::const_ptr offset_function::get_offset() const { return offset_; }


ifcopenshell::geom::taxonomy::collection::ptr ifcopenshell::geom::flatten(const taxonomy::collection::ptr& deep) {
	auto flat = make<taxonomy::collection>();
	ifcopenshell::geom::visit<taxonomy::collection>(deep, [&flat](taxonomy::ptr i) {
		flat->children.push_back(taxonomy::cast<taxonomy::geom_item>(clone(i)));
		});
	return flat;
}

const std::string& ifcopenshell::geom::taxonomy::kind_to_string(kinds k) {
	using namespace std::string_literals;

	static std::string values[] = {
        "matrix4"s,
        "point3"s,
        "direction3"s,
        "line"s,
        "circle"s,
        "ellipse"s,
        "bspline_curve"s,
        "offset_curve"s,
        "plane"s,
        "cylinder"s,
        "sphere"s,
        "torus"s,
        "bspline_surface"s,
        "edge"s,
        "loop"s,
        "face"s,
        "shell"s,
        "solid"s,
        "loft"s,
        "extrusion"s,
        "revolve"s,
        "sweep_along_curve"s,
        "node"s,
        "collection"s,
        "boolean_result"s,
        "function_item"s,
        "functor_item"s,
        "piecewise_function"s,
        "gradient_function"s,
        "cant_function"s,
        "offset_function"s,
        "colour"s,
        "style"s,
	};

	return values[k];
}

IFC_GEOM_API std::atomic_uint32_t item::counter_(0);

void ifcopenshell::geom::taxonomy::item::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << kind_to_string(kind()) << std::endl;
}

void ifcopenshell::geom::taxonomy::matrix4::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geom::taxonomy::colour::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geom::taxonomy::style::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << "style" << std::endl;
	o << std::string(indent, ' ') << "     " << "name " << (name) << std::endl;
	if (diffuse.components_) {
		o << std::string(indent, ' ') << "     " << "diffuse" << std::endl;
		diffuse.print(o, indent + 5 + 7);
	}
	if (specular.components_) {
		o << std::string(indent, ' ') << "     " << "specular" << std::endl;
		specular.print(o, indent + 5 + 8);
	}
	// @todo
}

void ifcopenshell::geom::taxonomy::point3::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geom::taxonomy::direction3::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geom::taxonomy::line::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geom::taxonomy::circle::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
	o << std::string(indent + 4, ' ') << "radius " << radius << std::endl;
}

void ifcopenshell::geom::taxonomy::ellipse::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
	o << std::string(indent + 4, ' ') << "radii " << radius << " " << radius2 << std::endl;
}

void ifcopenshell::geom::taxonomy::trimmed_curve::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << kind_to_string(kind());
	if (!this->orientation.value_or(true)) {
		o << " [R]";
	} else {
		o << " [ ]";
	}
	if (!this->curve_sense.value_or(true)) {
		o << " [R]";
	} else {
		o << " [ ]";
	}
	o << std::endl;
	if (basis) {
		basis->print(o, indent + 4);
	}

	const std::variant<boost::blank, point3::ptr, double>* const start_end[2] = { &start, &end };
	for (int i = 0; i < 2; ++i) {
		o << std::string(indent + 4, ' ') << (i == 0 ? "start" : "end") << std::endl;
		if (start_end[i]->index() == 1) {
			std::get<point3::ptr>(*start_end[i])->print(o, indent + 4);
		} else if (start_end[i]->index() == 2) {
			o << std::string(indent + 4, ' ') << "parameter " << std::get<double>(*start_end[i]) << std::endl;
		}
	}

	if (instance) {
		std::ostringstream oss;
		instance.to_string(oss);
		o << std::string(indent + 4, ' ') << oss.str() << std::endl;
	}
}

void ifcopenshell::geom::taxonomy::extrusion::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << "extrusion " << depth << std::endl;
	direction->print(o, indent + 4);
	basis->print(o, indent + 4);
}

std::optional<face::ptr> ifcopenshell::geom::taxonomy::loop_to_face_upgrade_impl(ptr item) {
	std::optional<face::ptr> face_;
	auto loop_ = dcast<loop>(item);
		if (loop_) {
			// Move the loop placement to the face exactly once. Keep the source
			// boundary immutable, as it can be shared by mapped/derived profiles.
			auto boundary = make<loop>(*loop_);
			boundary->instance = loop_->instance;
			boundary->surface_style = loop_->surface_style;
			boundary->orientation = loop_->orientation;
			boundary->matrix = nullptr;
			boundary->external = true;
			face_ = make<face>();
			(*face_)->instance = loop_->instance;
			(*face_)->matrix = loop_->matrix;
			(*face_)->surface_style = loop_->surface_style;
			(*face_)->children = { boundary };
		}
	return face_;
}

std::optional<edge::ptr> ifcopenshell::geom::taxonomy::curve_to_edge_upgrade_impl(ptr item) {
	std::optional<edge::ptr> edge_;
	auto circle_ = dcast<circle>(item);
	auto ellipse_ = dcast<ellipse>(item);
	auto line_ = dcast<line>(item);
	auto bspline_curve_ = dcast<bspline_curve>(item);
	if (circle_ || ellipse_ || line_ || bspline_curve_) {
		edge_ = make<edge>();
		if (circle_) {
			(*edge_)->basis = circle_;
			(*edge_)->instance = circle_->instance;
		} else if (ellipse_) {
			(*edge_)->basis = ellipse_;
			(*edge_)->instance = ellipse_->instance;
		} else if (line_) {
			(*edge_)->basis = line_;
			(*edge_)->instance = line_->instance;
		} else if (bspline_curve_) {
			(*edge_)->basis = bspline_curve_;
			(*edge_)->instance = bspline_curve_->instance;
		}

		if (circle_ || ellipse_) {
			// @todo
			(*edge_)->start = 0.;
			(*edge_)->end = 2 * boost::math::constants::pi<double>();
		}
	}
	return edge_;
}

std::optional<loop::ptr> ifcopenshell::geom::taxonomy::curve_to_loop_upgrade_impl(ptr item) {
	std::optional<loop::ptr> loop_;
	auto circle_ = dcast<circle>(item);
	auto ellipse_ = dcast<ellipse>(item);
	auto line_ = dcast<line>(item);
	auto bspline_curve_ = dcast<bspline_curve>(item);
	if (circle_ || ellipse_ || line_ || bspline_curve_) {
		auto edge_ = make<edge>();
		if (circle_) {
			edge_->basis = circle_;
		} else if (ellipse_) {
			edge_->basis = ellipse_;
		} else if (line_) {
			edge_->basis = line_;
		} else if (bspline_curve_) {
			edge_->basis = bspline_curve_;
		}

		if (circle_ || ellipse_) {
			// @todo
			edge_->start = 0.;
			edge_->end = 2 * boost::math::constants::pi<double>();
		}

		loop_ = make<loop>();
		(*loop_)->children.push_back(edge_);
	}
	return loop_;
}

std::optional<loop::ptr> ifcopenshell::geom::taxonomy::edge_to_loop_upgrade_impl(ptr item) {
	std::optional<loop::ptr> loop_;
	auto edge_ = dcast<edge>(item);
	if (edge_) {
		loop_ = make<loop>();
		(*loop_)->children.push_back(edge_);
	}
	return loop_;
}

std::optional<face::ptr> ifcopenshell::geom::taxonomy::curve_to_face_upgrade_impl(ptr item) {
    std::optional<face::ptr> face_;
    auto circle_ = dcast<circle>(item);
    auto ellipse_ = dcast<ellipse>(item);
    auto line_ = dcast<line>(item);
    auto bspline_curve_ = dcast<bspline_curve>(item);

    if (circle_ || ellipse_ || line_ || bspline_curve_) {
        auto edge_ = make<edge>();
        if (circle_) {
            edge_->basis = circle_;
        } else if (ellipse_) {
            edge_->basis = ellipse_;
        } else if (line_) {
            edge_->basis = line_;
        } else if (bspline_curve_) {
            edge_->basis = bspline_curve_;
        }

        if (circle_ || ellipse_) {
            // @todo
            edge_->start = 0.;
            edge_->end = 2 * boost::math::constants::pi<double>();
        }

        auto loop_ = make<loop>();
        loop_->children.push_back(edge_);

        face_ = make<face>();
        (*face_)->instance = loop_->instance;
        (*face_)->matrix = loop_->matrix;
        (*face_)->children = { clone(loop_) };
    }
    return face_;
}

namespace {
	// @todo eliminate redundancy with cgal kernel
	void evaluate_curve(const circle::ptr& c, double u, point3& p) {
		Eigen::Vector4d xy{ c->radius * std::cos(u), c->radius * std::sin(u), 0, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	// @todo eliminate redundancy with cgal kernel
	void evaluate_curve_d1(const circle::ptr& c, double u, direction3& p) {
		Eigen::Vector4d xy{ -std::sin(u), cos(u), 0, 0. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	double project_onto_curve(const circle::ptr& c, const point3& p) {
		Eigen::Vector2d xy = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous()).head<2>();
		return std::atan2(xy(1), xy(0));
	}

	// A circular arc edge of a loop, starting at parameter s on the circle
	struct circle_edge_function : public span_function {
		circle_edge_function(circle::ptr circ, double s) : circ_(std::move(circ)), s_(s) {}

		Eigen::Matrix4d operator()(double u) const override {
			point3 P;
			direction3 d;
			evaluate_curve(circ_, u / circ_->radius + s_, P);
			evaluate_curve_d1(circ_, u / circ_->radius + s_, d);
			return matrix4(P.ccomponents(), circ_->matrix->ccomponents().col(2).head<3>(), d.ccomponents()).components();
		}

		circle::ptr circ_;
		double s_;
	};

	// A straight edge of a loop, from start in unit direction v
	struct line_edge_function : public span_function {
		line_edge_function(const Eigen::Vector3d& start, const Eigen::Vector3d& v) : start_(start), v_(v) {}

		Eigen::Matrix4d operator()(double u) const override {
			Eigen::Vector3d o(start_ + u * v_), axis(0, 0, 1), refDirection(v_);
			auto Y = axis.cross(refDirection).normalized();
			axis = refDirection.cross(Y).normalized();
			return make<matrix4>(o, axis, refDirection)->components();
		}

		Eigen::Vector3d start_, v_;
	};

	span_info loop_edge_info(span_curve curve) {
		span_info info;
		info.layout = span_layout::POLYLINE;
		info.curve = curve;
		return info;
	}
}


std::optional<function_item::ptr> ifcopenshell::geom::taxonomy::loop_to_function_item_upgrade_impl(ptr item) {
	std::optional<function_item::ptr> fi_;
	auto loop_ = dcast<loop>(item);
	if (loop_) {
		if (loop_->fi.has_value()) {
			fi_ = loop_->fi;
		} else {
         // piecewise_function is a specialization of function_item - callers don't need to know this detail
			piecewise_function::span_list spans;
			spans.reserve(loop_->children.size());
			for (auto& edge_ : loop_->children) {
				if (edge_->basis && edge_->basis->kind() == CIRCLE) {
					const circle::ptr circ = std::static_pointer_cast<circle>(edge_->basis);

					auto* s_pnt = std::get_if<point3::ptr>(&edge_->start);
                    auto* e_pnt = std::get_if<point3::ptr>(&edge_->end);
                    auto* s_param = std::get_if<double>(&edge_->start);
                    auto* e_param = std::get_if<double>(&edge_->end);

					if (!s_pnt && !s_param) {
						return std::nullopt;
					}
					if (!e_pnt && !e_param) {
						return std::nullopt;
					}

					double s = s_pnt ? project_onto_curve(circ, **s_pnt) : *s_param;
					double e = e_pnt ? project_onto_curve(circ, **e_pnt) : *e_param;

					auto l = std::fabs(s - e) * circ->radius;
					auto fn = std::make_shared<circle_edge_function>(circ, s);
					spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn, loop_edge_info(span_curve::CIRCLE), loop_->instance));
				} else if (edge_->start.index() == 1 && edge_->end.index() == 1) {
					if (edge_->basis && edge_->basis->kind() != LINE) {
						ifcopenshell::logger::root().message(ifcopenshell::logger::severity::LOG_WARNING, "UNS", 20, "Basis curve not supported - edge is treated as a straight line edge");
					}
					const auto& s = std::get<point3::ptr>(edge_->start)->ccomponents();
					const auto& e = std::get<point3::ptr>(edge_->end)->ccomponents();
					Eigen::Vector3d v = e - s;
					auto l = v.norm(); // the norm of a vector is a measure of its length
					v.normalize();     // normalize the vector so that it is a unit direction vector
					auto fn = std::make_shared<line_edge_function>(s, v);
					spans.emplace_back(taxonomy::make<taxonomy::functor_item>(l, fn, loop_edge_info(span_curve::LINE), loop_->instance));
				} else {
					ifcopenshell::logger::root().message(ifcopenshell::logger::severity::LOG_ERROR, "UNS", 21, "Basis curve not supported");
					return std::nullopt;
				}
			}
			fi_ = make<piecewise_function>(0.0,spans);
			loop_->fi = fi_;
		}
	}
    return fi_;
}
