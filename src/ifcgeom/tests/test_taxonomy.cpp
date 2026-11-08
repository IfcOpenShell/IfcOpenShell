// This file was generated with the assistance of an AI coding tool.

#include "ifcgeom/kernel_registry.h"
#include "ifcgeom/profile_helper.h"
#include "ifcparse/hierarchy_helper.h"
#include IFCGEOM_TEST_SCHEMA_HEADER

#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>
#include <iostream>
#include <numeric>

using namespace ifcopenshell::geom;
namespace tx = ifcopenshell::geom::taxonomy;
using vector3 = Eigen::Vector3d;
constexpr double pi = boost::math::constants::pi<double>();

namespace {
tx::loop::ptr polyline(std::initializer_list<vector3> coordinates, bool closed = false) {
    std::vector<tx::point3::ptr> points;
    for (const auto& p : coordinates) {
        points.push_back(tx::make<tx::point3>(p));
    }
    if (closed) {
        points.push_back(points.front());
    }
    auto l = polygon_from_points(points);
    l->closed = closed;
    return l;
}

tx::sweep_along_curve::ptr disk_sweep(tx::item::ptr path, bool hollow = false) {
    auto profile = tx::make<tx::face>();
    for (double radius : hollow ? std::vector<double>{0.4, 0.2} : std::vector<double>{0.4}) {
        auto circle = tx::make<tx::circle>();
        circle->radius = radius;
        circle->matrix = tx::make<tx::matrix4>();
        auto edge = tx::make<tx::edge>();
        edge->basis = circle;
        edge->start = 0.;
        edge->end = 2. * pi;
        auto loop = tx::make<tx::loop>();
        loop->children = {edge};
        loop->external = profile->children.empty();
        profile->children.push_back(loop);
    }
    return tx::make<tx::sweep_along_curve>(tx::make<tx::matrix4>(), profile, tx::item::ptr(), path);
}

struct mesh {
    std::vector<std::array<vector3, 3>> triangles;

    explicit mesh(const tx::shell::ptr& shell) {
        for (const auto& face : shell->children) {
            REQUIRE(face->children.size() == 1);
            const auto& edges = face->children.front()->children;
            REQUIRE(edges.size() == 3);
            triangles.push_back({std::get<tx::point3::ptr>(edges[0]->start)->ccomponents(),
                                 std::get<tx::point3::ptr>(edges[1]->start)->ccomponents(),
                                 std::get<tx::point3::ptr>(edges[2]->start)->ccomponents()});
        }
    }

    explicit mesh(const triangulation& t) {
        const auto& v = t.verts();
        const auto& f = t.faces();
        for (size_t i = 0; i < f.size(); i += 3) {
            std::array<vector3, 3> triangle;
            for (int j = 0; j < 3; ++j) {
                triangle[j] = vector3(v[3 * f[i + j]], v[3 * f[i + j] + 1], v[3 * f[i + j] + 2]);
            }
            triangles.push_back(triangle);
        }
    }

    double area() const {
        double result = 0.;
        for (const auto& t : triangles) {
            result += (t[1] - t[0]).cross(t[2] - t[0]).norm() / 2.;
        }
        return result;
    }

    double volume() const {
        double result = 0.;
        const vector3 origin = triangles.front()[0];
        for (const auto& t : triangles) {
            result += (t[0] - origin).dot((t[1] - origin).cross(t[2] - origin)) / 6.;
        }
        return result;
    }

    void require_closed() const {
        // Shared coordinates must have exactly two, oppositely directed incident faces.
        using key = std::array<double, 3>;
        std::map<std::pair<key, key>, std::pair<int, int>> incidence;
        for (const auto& t : triangles) {
            for (int j = 0; j < 3; ++j) {
                key a{t[j].x(), t[j].y(), t[j].z()};
                key b{t[(j + 1) % 3].x(), t[(j + 1) % 3].y(), t[(j + 1) % 3].z()};
                bool forward = a < b;
                auto& count = incidence[forward ? std::make_pair(a, b) : std::make_pair(b, a)];
                ++count.first;
                count.second += forward ? 1 : -1;
            }
        }
        for (const auto& edge : incidence) {
            REQUIRE(edge.second.first == 2);
            REQUIRE(edge.second.second == 0);
        }
    }
};

double point_triangle_distance_squared(const vector3& p, const std::array<vector3, 3>& t) {
    const vector3 ab = t[1] - t[0], ac = t[2] - t[0];
    const vector3 normal = ab.cross(ac);
    if (normal.squaredNorm() > 0.) {
        const vector3 q = p - normal * (normal.dot(p - t[0]) / normal.squaredNorm());
        if (normal.dot(ab.cross(q - t[0])) >= 0. &&
            normal.dot((t[2] - t[1]).cross(q - t[1])) >= 0. &&
            normal.dot((t[0] - t[2]).cross(q - t[2])) >= 0.) {
            return (p - q).squaredNorm();
        }
    }
    double best = std::numeric_limits<double>::infinity();
    for (int j = 0; j < 3; ++j) {
        const vector3 edge = t[(j + 1) % 3] - t[j];
        const double u = edge.squaredNorm() > 0. ? std::clamp(edge.dot(p - t[j]) / edge.squaredNorm(), 0., 1.) : 0.;
        best = std::min(best, (p - t[j] - u * edge).squaredNorm());
    }
    return best;
}

// A small bounding-volume tree keeps the bidirectional projection test practical
// for finely tessellated curved sweeps, without depending on a geometry backend.
struct mesh_projection {
    struct node {
        Eigen::AlignedBox3d box;
        size_t begin, end;
        int left = -1, right = -1;
    };
    const mesh& target;
    std::vector<size_t> order;
    std::vector<node> nodes;

    explicit mesh_projection(const mesh& target) : target(target), order(target.triangles.size()) {
        std::iota(order.begin(), order.end(), 0);
        build(0, order.size());
    }

    int build(size_t begin, size_t end) {
        node n;
        n.begin = begin;
        n.end = end;
        for (size_t i = begin; i < end; ++i) {
            for (const auto& p : target.triangles[order[i]]) {
                n.box.extend(p);
            }
        }
        const int id = static_cast<int>(nodes.size());
        nodes.push_back(n);
        if (end - begin > 8) {
            Eigen::Index axis;
            n.box.sizes().maxCoeff(&axis);
            const size_t middle = (begin + end) / 2;
            std::nth_element(order.begin() + begin, order.begin() + middle, order.begin() + end, [&](size_t a, size_t b) {
                const auto& x = target.triangles[a];
                const auto& y = target.triangles[b];
                return x[0][axis] + x[1][axis] + x[2][axis] < y[0][axis] + y[1][axis] + y[2][axis];
            });
            const int left = build(begin, middle), right = build(middle, end);
            nodes[id].left = left;
            nodes[id].right = right;
        }
        return id;
    }

    void nearest(int id, const vector3& p, double& best) const {
        const auto& n = nodes[id];
        if (n.box.squaredExteriorDistance(p) > best) {
            return;
        }
        if (n.left == -1) {
            for (size_t i = n.begin; i < n.end; ++i) {
                best = std::min(best, point_triangle_distance_squared(p, target.triangles[order[i]]));
            }
        } else {
            const bool left_first = nodes[n.left].box.squaredExteriorDistance(p) < nodes[n.right].box.squaredExteriorDistance(p);
            nearest(left_first ? n.left : n.right, p, best);
            nearest(left_first ? n.right : n.left, p, best);
        }
    }

    double deviation(const mesh& source) const {
        double worst = 0.;
        for (const auto& t : source.triangles) {
            const std::array<vector3, 7> samples{t[0], t[1], t[2], (t[0] + t[1]) / 2., (t[1] + t[2]) / 2., (t[2] + t[0]) / 2., (t[0] + t[1] + t[2]) / 3.};
            for (const auto& p : samples) {
                double best = std::numeric_limits<double>::infinity();
                nearest(0, p, best);
                worst = std::max(worst, best);
            }
        }
        return std::sqrt(worst);
    }
};
} // namespace

TEST_CASE("Taxonomy conic polygons respect settings and curve senses", "[taxonomy]") {
    settings settings;
    settings.set("circle-segments", 64);
    auto c = tx::make<tx::circle>();
    c->radius = 2.;
    c->matrix = tx::make<tx::matrix4>();
    REQUIRE(c->to_polygon(settings).size() == 65);
    auto e = tx::make<tx::edge>();
    e->basis = c;
    e->start = 0.;
    e->end = pi / 2.;
    REQUIRE(e->to_polygon(settings).size() == 17);
    e->curve_sense = false;
    auto points = e->to_polygon(settings);
    REQUIRE(points.size() == 49);
    REQUIRE(points.front().ccomponents().isApprox(vector3(2., 0., 0.)));
    e->orientation = false;
    REQUIRE(e->to_polygon(settings).front().ccomponents().isApprox(points.back().ccomponents()));

    settings.set("circle-segments", 0);
    settings.set("mesher-linear-deflection", 0.001);
    settings.set("mesher-angular-deflection", 0.5);
    points = c->to_polygon(settings);
    const double angle = 2. * pi / (points.size() - 1);
    REQUIRE(2. * (1. - std::cos(angle / 2.)) <= 0.001);
    auto ellipse = tx::make<tx::ellipse>();
    ellipse->radius = 4.;
    ellipse->radius2 = 1.;
    auto arc = tx::make<tx::edge>();
    arc->basis = ellipse;
    arc->start = tx::make<tx::point3>(4. / std::sqrt(2.), 1. / std::sqrt(2.), 0.);
    arc->end = tx::make<tx::point3>(0., 1., 0.);
    auto elliptic = arc->to_polygon(settings);
    REQUIRE(elliptic.front().ccomponents().isApprox(std::get<tx::point3::ptr>(arc->start)->ccomponents()));
}

TEST_CASE("Taxonomy untrimmed conic edges cover a full turn", "[taxonomy][conic]") {
    settings settings;
    settings.set("circle-segments", 64);
    auto circle = tx::make<tx::circle>();
    circle->radius = 2.;
    auto ellipse = tx::make<tx::ellipse>();
    ellipse->radius = 2.;
    ellipse->radius2 = 0.5;
    for (const tx::curve::ptr& basis : std::vector<tx::curve::ptr>{circle, ellipse}) {
        auto edge = tx::make<tx::edge>();
        edge->basis = basis;
        auto points = edge->to_polygon(settings);
        REQUIRE(points.size() == 65);
        REQUIRE(points.front().ccomponents().isApprox(points.back().ccomponents()));
        REQUIRE(points[16].ccomponents().x() == Catch::Approx(0.).margin(1.e-12));
        REQUIRE(points[16].ccomponents().y() == Catch::Approx(basis == circle ? 2. : 0.5));
        edge->reverse();
        auto reversed = edge->to_polygon(settings);
        REQUIRE(reversed[1].ccomponents().isApprox(points[points.size() - 2].ccomponents()));
        edge->start = 0.;
        REQUIRE_THROWS(edge->to_polygon(settings));
    }
    auto line = tx::make<tx::edge>();
    line->basis = tx::make<tx::line>();
    REQUIRE_THROWS(line->to_polygon(settings));
}

TEST_CASE("Conic extrusion kernels preserve full profiles and reversed annular arcs", "[taxonomy][conic]") {
    hierarchy_helper<IfcSchema> file;
    std::vector<std::string> backends;
#ifdef TAXONOMY_TEST_MANIFOLD
    backends.push_back("manifold");
#endif
#ifdef TAXONOMY_TEST_CGAL
    backends.push_back("cgal");
#endif
    for (const auto& backend : backends) {
        for (int segments : {0, 64}) {
            settings settings;
            settings.set("circle-segments", segments);
            settings.set("mesher-linear-deflection", 0.001);
            for (int profile : {0, 1, 2}) {
                CAPTURE(backend, segments, profile);
                auto face = tx::make<tx::face>();
                auto loop = tx::make<tx::loop>();
                loop->closed = true;
                loop->external = true;
                double expected_volume;
                if (profile < 2) {
                    auto edge = tx::make<tx::edge>();
                    if (profile == 0) {
                        auto circle = tx::make<tx::circle>();
                        circle->radius = 2.;
                        circle->matrix = tx::make<tx::matrix4>();
                        edge->basis = circle;
                        edge->start = 0.;
                        edge->end = 2. * pi;
                        expected_volume = 16. * pi;
                    } else {
                        auto ellipse = tx::make<tx::ellipse>();
                        ellipse->radius = 2.;
                        ellipse->radius2 = 0.5;
                        ellipse->matrix = tx::make<tx::matrix4>();
                        edge->basis = ellipse;
                        expected_volume = 4. * pi;
                    }
                    loop->children = {edge};
                } else {
                    const double start = -1. / 3., end = 1. / 3.;
                    auto arc = [&](double radius) {
                        auto circle = tx::make<tx::circle>();
                        circle->radius = radius;
                        circle->matrix = tx::make<tx::matrix4>();
                        auto edge = tx::make<tx::edge>();
                        edge->basis = circle;
                        edge->start = start;
                        edge->end = end;
                        return edge;
                    };
                    auto point = [](double radius, double angle) {
                        return tx::make<tx::point3>(radius * std::cos(angle), radius * std::sin(angle), 0.);
                    };
                    auto inner = arc(17.85);
                    inner->reverse();
                    loop->children = {
                        arc(18.15), tx::make<tx::edge>(point(18.15, end), point(17.85, end)), inner, tx::make<tx::edge>(point(17.85, start), point(18.15, start))};
                    expected_volume = 14.4;
                }
                face->children = {loop};
                auto extrusion = tx::make<tx::extrusion>(
                    tx::make<tx::matrix4>(), face, tx::make<tx::direction3>(0., 0., 1.), 4.);
                extrusion->instance = file.create<IfcSchema::IfcBuildingElementProxy>();
                auto kernel = kernels::construct(nullptr, backend, settings);
                kernel->propagate_exceptions = true;
                std::vector<conversion_result> converted;
                REQUIRE(kernel->convert(extrusion, converted));
                REQUIRE(converted.size() == 1);
                REQUIRE(converted.front().shape()->volume().to_double() == Catch::Approx(expected_volume).epsilon(0.005));
            }
        }
    }
}

TEST_CASE("Taxonomy lofts connect corresponding vertices and preserve placement", "[taxonomy]") {
    auto loft = tx::make<tx::loft>();
    auto a = polyline({{0., 0., 0.}, {1., 0., 0.}, {1., 1., 0.}, {0., 1., 0.}}, true);
    auto b = polyline({{0., 0., 2.}, {1., 0., 2.}, {1., 1., 2.}, {0., 1., 2.}}, true);
    for (auto l : {a, b}) {
        auto f = tx::make<tx::face>();
        f->children = {l};
        loft->children.push_back(f);
    }
    REQUIRE(loft->is_polygonal());
    auto shell = loft->to_polyhedron();
    REQUIRE(shell->closed.value());
    REQUIRE(shell->children.size() == 10);
    auto curve = tx::make<tx::circle>();
    loft->axis = curve;
    REQUIRE_FALSE(loft->is_polygonal());
    loft->axis = nullptr;
    a->children.front()->basis = curve;
    REQUIRE_FALSE(loft->is_polygonal());
    REQUIRE_THROWS(loft->to_polyhedron());

    loft->children.clear();
    a = polyline({{0., 0., 0.}, {1., 0., 0.}, {1., 0., 0.}, {2., 0., 0.}});
    b = polyline({{0., 0., 1.}, {1., 0., 1.}, {1.5, 0., 1.}, {2., 0., 1.}});
    a->tags = {"a", "b", "c", "d"};
    b->tags = {"a", "b", "c", "d"};
    a->matrix = tx::make<tx::matrix4>();
    a->matrix->components()(1, 3) = 3.;
    b->matrix = a->matrix;
    loft->children = {a, b};
    shell = loft->to_polyhedron();
    REQUIRE_FALSE(shell->closed.value());
    REQUIRE(shell->children.size() == 5);
    REQUIRE(std::get<tx::point3::ptr>(shell->children.front()->children.front()->children.front()->start)->ccomponents().y() == 3.);
    a->orientation = false;
    b->orientation = false;
    REQUIRE(loft->to_polyhedron()->children.size() == 5);
    a->orientation = true;
    b->orientation = true;
    b->tags = {"x", "b", "c", "d"};
    REQUIRE_THROWS(loft->to_polyhedron());
}

TEST_CASE("Taxonomy disk sweep meshes are closed and untwisted", "[taxonomy]") {
    settings settings;
    settings.set("circle-segments", 64);
    auto path = polyline({{0., 0., 0.}, {4., 0., 0.}, {4., 3., 0.}, {4., 3., 2.}});
    auto sweep = disk_sweep(path, true);
    mesh result(sweep->to_polyhedron(settings));
    result.require_closed();
    REQUIRE(result.volume() == Catch::Approx(pi * (0.16 - 0.04) * 9.).epsilon(0.002));
    auto reversal = disk_sweep(polyline({{0., 0., 0.}, {1., 0., 0.}, {0., 0., 0.}}));
    REQUIRE_THROWS(reversal->to_polyhedron(settings));
    auto closed = disk_sweep(polyline({{0., 0., 0.}, {4., 0., 0.}, {5., 3., 1.}, {1., 4., 3.}, {-2., 2., 1.}}, true), true);
    mesh periodic(closed->to_polyhedron(settings));
    periodic.require_closed();
    const auto path_points = std::static_pointer_cast<tx::loop>(closed->curve)->to_polygon(settings);
    double length = 0.;
    for (size_t i = 1; i < path_points.size(); ++i) {
        length += (path_points[i].ccomponents() - path_points[i - 1].ccomponents()).norm();
    }
    REQUIRE(periodic.volume() == Catch::Approx(pi * 0.12 * length).epsilon(0.002));
}

TEST_CASE("Geometry kernels consume taxonomy polygonal lofts and disk sweeps", "[taxonomy][kernels]") {
    hierarchy_helper<IfcSchema> file;
    std::vector<std::string> backends;
#ifdef TAXONOMY_TEST_OPENCASCADE
    backends.push_back("opencascade");
#endif
#ifdef TAXONOMY_TEST_CGAL
    backends.push_back("cgal");
#endif
#ifdef TAXONOMY_TEST_CGAL_SIMPLE
    backends.push_back("cgal-simple");
#endif
#ifdef TAXONOMY_TEST_MANIFOLD
    backends.push_back("manifold");
#endif
    settings settings;
    settings.set("cache-shapes", false);
    settings.set("reorient-shells", true);
    settings.set("circle-segments", 64);
    auto loft = tx::make<tx::loft>();
    loft->instance = file.create<IfcSchema::IfcBuildingElementProxy>();
    for (double z : {0., 2.}) {
        auto f = tx::make<tx::face>();
        auto outer = polyline({{0., 0., z}, {3., 0., z}, {3., 3., z}, {0., 3., z}}, true);
        auto inner = polyline({{1., 1., z}, {2., 1., z}, {2., 2., z}, {1., 2., z}}, true);
        inner->external = false;
        f->children = {outer, inner};
        loft->children.push_back(f);
    }
    auto sweep = disk_sweep(polyline({{0., 0., 0.}, {4., 0., 0.}, {4., 3., 0.}, {4., 3., 2.}}), true);
    sweep->instance = file.create<IfcSchema::IfcBuildingElementProxy>();
    for (const auto& backend : backends) {
        CAPTURE(backend);
        auto kernel = kernels::construct(nullptr, backend, settings);
        kernel->propagate_exceptions = true;
        std::vector<conversion_result> converted;
        REQUIRE(kernel->convert(loft, converted));
        REQUIRE(converted.size() == 1);
        REQUIRE(converted.front().shape()->volume().to_double() == Catch::Approx(16.).epsilon(1.e-6));
        REQUIRE(converted.front().shape()->area().to_double() == Catch::Approx(48.).epsilon(1.e-6));
        converted.clear();
        REQUIRE(kernel->convert(sweep, converted));
        REQUIRE(converted.size() == 1);
        REQUIRE(converted.front().shape()->volume().to_double() == Catch::Approx(pi * 0.12 * 9.).epsilon(0.002));
    }
}

#ifdef TAXONOMY_TEST_OPENCASCADE
TEST_CASE("Taxonomy disk sweeps agree with OpenCascade", "[taxonomy][opencascade]") {
    hierarchy_helper<IfcSchema> file;
    settings settings;
    settings.set("circle-segments", 128);
    settings.set("mesher-linear-deflection", 0.001);
    settings.set("mesher-angular-deflection", 0.05);
    auto circle = tx::make<tx::circle>();
    circle->radius = 4.;
    circle->matrix = tx::make<tx::matrix4>();
    auto arc = tx::make<tx::edge>();
    arc->basis = circle;
    arc->start = 0.;
    arc->end = pi / 2.;
    auto curved = tx::make<tx::loop>();
    curved->children = {arc};
    auto closed = tx::make<tx::loop>();
    auto full = tx::make<tx::edge>();
    full->basis = circle;
    full->start = 0.;
    full->end = 2. * pi;
    closed->children = {full};
    const std::vector<std::pair<std::string, tx::loop::ptr>> cases{
        {"straight", polyline({{0., 0., 0.}, {0., 0., 5.}})},
        {"corner", polyline({{0., 0., 0.}, {4., 0., 0.}, {4., 3., 0.}})},
        {"nonplanar", polyline({{0., 0., 0.}, {4., 0., 0.}, {4., 3., 0.}, {4., 3., 2.}})},
        {"arc", curved},
        {"closed circle", closed},
        {"large coordinates", polyline({{10000., 20000., 30000.}, {10000., 20000., 30005.}})}};
    for (const auto& entry : cases) {
        for (bool hollow : {false, true}) {
            CAPTURE(entry.first, hollow);
            auto sweep = disk_sweep(entry.second, hollow);
            sweep->instance = file.create<IfcSchema::IfcBuildingElementProxy>();
            const mesh polygonal(sweep->to_polyhedron(settings));
            polygonal.require_closed();
            auto kernel = kernels::construct(nullptr, "opencascade", settings);
            kernel->propagate_exceptions = true;
            std::vector<conversion_result> converted;
            REQUIRE(kernel->convert(sweep, converted));
            REQUIRE(converted.size() == 1);
            double exact_area = converted.front().shape()->area().to_double();
            const double exact_volume = converted.front().shape()->volume().to_double();
            std::unique_ptr<triangulation> triangles(converted.front().shape()->triangulate(settings));
            mesh reference(*triangles);
            if (entry.first == "closed circle") {
                REQUIRE(exact_area == Catch::Approx(4. * pi * pi * 4. * (hollow ? 0.6 : 0.4)).epsilon(1.e-6));
                REQUIRE(exact_volume == Catch::Approx(2. * pi * pi * 4. * (hollow ? 0.12 : 0.16)).epsilon(1.e-6));
                // No triangles may span the cross-section at the closed seam.
                REQUIRE(std::none_of(reference.triangles.begin(), reference.triangles.end(), [](const auto& t) {
                    return std::all_of(t.begin(), t.end(), [](const vector3& p) { return std::abs(p.y()) < 1.e-6 && p.x() > 3.5; });
                }));
            }
            REQUIRE(polygonal.area() == Catch::Approx(exact_area).epsilon(0.002));
            REQUIRE(polygonal.volume() == Catch::Approx(exact_volume).epsilon(0.002));
            REQUIRE_FALSE(reference.triangles.empty());
            const double forward = mesh_projection(reference).deviation(polygonal);
            const double reverse = mesh_projection(polygonal).deviation(reference);
            std::cout << entry.first << (hollow ? " hollow" : " solid")
                      << ": area=" << std::abs(polygonal.area() / exact_area - 1.)
                      << " volume=" << std::abs(polygonal.volume() / exact_volume - 1.)
                      << " distances=" << forward << "," << reverse << '\n';
            REQUIRE(forward < 0.003);
            REQUIRE(reverse < 0.003);
        }
    }
}
#endif
