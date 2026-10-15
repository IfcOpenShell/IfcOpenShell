// This file was generated with the assistance of an AI coding tool.

#include "ifcgeom/representation.h"

#include <algorithm>
#include <catch2/catch_test_macros.hpp>
#include <memory>
#include <vector>

namespace {

using triangulation = ifcopenshell::geom::triangulation;

std::unique_ptr<triangulation> empty_triangulation() {
    ifcopenshell::geom::settings settings;
    return std::unique_ptr<triangulation>(triangulation::empty(settings));
}

int add_vertex(triangulation& geometry, double x, double y, double z = 0.) {
    const int index = geometry.addVertex(0, 0, x, y, z);
    geometry.addNormal(0., 0., 1.);
    geometry.uvs_ref().push_back(x);
    geometry.uvs_ref().push_back(y);
    return index;
}

std::vector<std::unique_ptr<triangulation>> take_ownership(std::vector<triangulation*> geometries) {
    std::vector<std::unique_ptr<triangulation>> result;
    result.reserve(geometries.size());
    for (auto* geometry : geometries) {
        result.emplace_back(geometry);
    }
    return result;
}

std::unique_ptr<triangulation> adjacent_quads(bool with_holes_encoding) {
    auto geometry = empty_triangulation();
    add_vertex(*geometry, 0., 0.);
    add_vertex(*geometry, 1., 0.);
    add_vertex(*geometry, 2., 0.);
    add_vertex(*geometry, 0., 1.);
    add_vertex(*geometry, 1., 1.);
    add_vertex(*geometry, 2., 1.);

    if (with_holes_encoding) {
        geometry->addFace(10, 1, std::vector<std::vector<int>>{{0, 1, 4, 3}});
        geometry->addFace(20, 2, std::vector<std::vector<int>>{{1, 2, 5, 4}});
    } else {
        geometry->addFace(10, 1, std::vector<int>{0, 1, 4, 3});
        geometry->addFace(20, 2, std::vector<int>{1, 2, 5, 4});
    }
    return geometry;
}

} // namespace

TEST_CASE("Triangulation extraction compacts vertices and preserves metadata", "[ifcgeom][triangulation]") {
    auto geometry = empty_triangulation();
    add_vertex(*geometry, 0., 0.);
    add_vertex(*geometry, 1., 0.);
    add_vertex(*geometry, 1., 1.);
    add_vertex(*geometry, 2., 1.);
    add_vertex(*geometry, 2., 2.);
    add_vertex(*geometry, 9., 9.);
    geometry->addFace(100, 7, 0, 1, 2);
    geometry->addFace(200, 8, 2, 3, 4);

    REQUIRE(geometry->dimensionality() == 2);

    std::unique_ptr<triangulation> face(geometry->extract(2, {1}));
    REQUIRE(face->dimensionality() == 2);
    REQUIRE(face->verts() == std::vector<double>{1., 1., 0., 2., 1., 0., 2., 2., 0.});
    REQUIRE(face->faces() == std::vector<int>{0, 1, 2});
    REQUIRE(face->item_ids() == std::vector<int>{200});
    REQUIRE(face->material_ids() == std::vector<int>{8});
    REQUIRE(face->normals().size() == 9);
    REQUIRE(face->uvs().size() == 6);

    std::unique_ptr<triangulation> points(geometry->extract(0, {5, 1}));
    REQUIRE(points->dimensionality() == 0);
    REQUIRE(points->verts() == std::vector<double>{9., 9., 0., 1., 0., 0.});
    REQUIRE(points->edges().empty());
    REQUIRE(points->faces().empty());
    REQUIRE(points->normals().size() == 6);
    REQUIRE(points->uvs().size() == 4);
}

TEST_CASE("Wire incidence is lazy, invalidated, and used by signed angular decomposition", "[ifcgeom][triangulation]") {
    auto geometry = empty_triangulation();
    add_vertex(*geometry, 0., 0.);
    add_vertex(*geometry, 1., 0.);
    add_vertex(*geometry, 2., 0.);
    add_vertex(*geometry, 2., 1.);
    geometry->addEdge(10, 1, 0, 1);
    geometry->addEdge(20, 2, 1, 2);
    geometry->addEdge(30, 3, 2, 3);

    REQUIRE(geometry->dimensionality() == 1);
    REQUIRE(geometry->v2e().at(3) == std::vector<int>{2});

    geometry->addEdge(40, 4, 3, 2);
    REQUIRE(geometry->v2e().at(3) == std::vector<int>{2, 3});

    std::unique_ptr<triangulation> edge(geometry->extract(1, {1}));
    REQUIRE(edge->dimensionality() == 1);
    REQUIRE(edge->edges() == std::vector<int>{0, 1});
    REQUIRE(edge->edges_item_ids() == std::vector<int>{20});
    REQUIRE(edge->material_ids() == std::vector<int>{2});

    auto components = take_ownership(geometry->angular_decomposition(10.));
    REQUIRE(components.size() == 3);
    std::vector<std::size_t> component_sizes;
    for (const auto& component : components) {
        component_sizes.push_back(component->edges().size() / 2);
    }
    std::sort(component_sizes.begin(), component_sizes.end());
    REQUIRE(component_sizes == std::vector<std::size_t>{1, 1, 2});
}

TEST_CASE("Angular decomposition supports every face encoding", "[ifcgeom][triangulation]") {
    SECTION("Triangles") {
        auto geometry = empty_triangulation();
        add_vertex(*geometry, 0., 0.);
        add_vertex(*geometry, 1., 0.);
        add_vertex(*geometry, 1., 1.);
        add_vertex(*geometry, 0., 1.);
        geometry->addFace(10, 1, 0, 1, 2);
        geometry->addFace(20, 2, 0, 2, 3);

        auto components = take_ownership(geometry->angular_decomposition(1.));
        REQUIRE(components.size() == 1);
        REQUIRE(components.front()->faces().size() == 6);
    }

    SECTION("Polyhedra without holes") {
        auto geometry = adjacent_quads(false);
        auto components = take_ownership(geometry->angular_decomposition(1.));
        REQUIRE(components.size() == 1);
        REQUIRE(components.front()->polyhedral_faces_without_holes().size() == 2);
    }

    SECTION("Polyhedra with holes") {
        auto geometry = adjacent_quads(true);
        auto components = take_ownership(geometry->angular_decomposition(1.));
        REQUIRE(components.size() == 1);
        REQUIRE(components.front()->polyhedral_faces_with_holes().size() == 2);
    }
}

TEST_CASE("Face decomposition uses signed normals", "[ifcgeom][triangulation]") {
    auto geometry = empty_triangulation();
    add_vertex(*geometry, 0., 0.);
    add_vertex(*geometry, 1., 0.);
    add_vertex(*geometry, 0., 1.);
    add_vertex(*geometry, 1., 1.);
    geometry->addFace(10, 1, 0, 1, 2);
    REQUIRE(geometry->e2f().at(triangulation::edge(1, 2)) == std::vector<int>{0});
    geometry->addFace(20, 2, 1, 2, 3);
    REQUIRE(geometry->e2f().at(triangulation::edge(1, 2)) == std::vector<int>{0, 1});

    auto components = take_ownership(geometry->angular_decomposition(1.));
    REQUIRE(components.size() == 2);
}

TEST_CASE("Face boundary includes holes and excludes shared edges", "[ifcgeom][triangulation]") {
    SECTION("Inner and outer bounds") {
        auto geometry = empty_triangulation();
        add_vertex(*geometry, 0., 0.);
        add_vertex(*geometry, 4., 0.);
        add_vertex(*geometry, 4., 4.);
        add_vertex(*geometry, 0., 4.);
        add_vertex(*geometry, 1., 1.);
        add_vertex(*geometry, 1., 3.);
        add_vertex(*geometry, 3., 3.);
        add_vertex(*geometry, 3., 1.);
        geometry->addFace(42, 5, std::vector<std::vector<int>>{{0, 1, 2, 3}, {4, 5, 6, 7}});

        std::unique_ptr<triangulation> boundary(geometry->boundary());
        REQUIRE(boundary->dimensionality() == 1);
        REQUIRE(boundary->edges().size() == 16);
        REQUIRE(boundary->verts().size() == 24);
        REQUIRE(boundary->edges_item_ids() == std::vector<int>(8, 42));
        REQUIRE(boundary->material_ids() == std::vector<int>(8, 5));
    }

    SECTION("Shared polygon edge") {
        auto geometry = adjacent_quads(false);
        REQUIRE(geometry->e2f().at(triangulation::edge(1, 4)) == std::vector<int>{0, 1});

        std::unique_ptr<triangulation> boundary(geometry->boundary());
        REQUIRE(boundary->edges().size() == 12);
        REQUIRE(boundary->verts().size() == 18);
    }
}
