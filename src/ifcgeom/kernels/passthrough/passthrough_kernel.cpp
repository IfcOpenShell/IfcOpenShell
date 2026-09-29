#include "passthrough_kernel.h"

#include <Eigen/Dense>

#include <algorithm>
#include <array>
#include <cmath>
#include <numeric>
#include <unordered_map>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;

namespace {
	taxonomy::style::ptr fallback_style(const taxonomy::geom_item::ptr& item, const taxonomy::geom_item::ptr& fallback) {
		if (item && item->surface_style) {
			return item->surface_style;
		}
		if (fallback && fallback->surface_style) {
			return fallback->surface_style;
		}
		return nullptr;
	}

	bool loop_points(const taxonomy::loop::ptr& loop, std::vector<Eigen::Vector3d>& points) {
		points.clear();
		if (!loop) {
			return false;
		}
		points.reserve(loop->children.size());
		for (const auto& edge : loop->children) {
			if (edge->basis && edge->basis->kind() != taxonomy::LINE) {
				return false;
			}
			if (edge->start.index() != 1 || edge->end.index() != 1) {
				return false;
			}
			points.push_back(std::get<taxonomy::point3::ptr>(edge->start)->ccomponents());
		}
		return points.size() >= 3;
	}

	bool shell_supported(const taxonomy::shell::ptr& shell) {
		if (!shell || shell->children.empty()) {
			return false;
		}
		std::vector<Eigen::Vector3d> points;
		for (const auto& face : shell->children) {
			if (!face || face->children.size() != 1) {
				return false;
			}
			const auto& loop = face->children.front();
			if (!loop || loop->children.size() < 3 || loop->children.size() > 4) {
				return false;
			}
			if (!loop_points(loop, points)) {
				return false;
			}
		}
		return true;
	}

	bool extrusion_supported_face(const taxonomy::face::ptr& face, std::vector<Eigen::Vector3d>& points) {
		return face && face->children.size() == 1 && loop_points(face->children.front(), points);
	}

	bool polygon_basis(const std::vector<Eigen::Vector3d>& points, double precision, Eigen::Vector3d& origin, Eigen::Vector3d& x, Eigen::Vector3d& y, Eigen::Vector3d& normal, std::vector<Eigen::Vector2d>& projected) {
		if (points.size() < 3) {
			return false;
		}
		origin = points.front();
		normal.setZero();
		for (size_t i = 0; i < points.size(); ++i) {
			const auto& a = points[i];
			const auto& b = points[(i + 1) % points.size()];
			normal(0) += (a(1) - b(1)) * (a(2) + b(2));
			normal(1) += (a(2) - b(2)) * (a(0) + b(0));
			normal(2) += (a(0) - b(0)) * (a(1) + b(1));
		}
		if (normal.norm() <= precision) {
			return false;
		}
		normal.normalize();
		x = Eigen::Vector3d::Zero();
		for (size_t i = 1; i < points.size(); ++i) {
			auto candidate = points[i] - origin;
			auto planar = candidate - normal * normal.dot(candidate);
			if (planar.norm() > precision) {
				x = planar.normalized();
				break;
			}
		}
		if (x.squaredNorm() < 1.e-12) {
			return false;
		}
		y = normal.cross(x).normalized();
		projected.clear();
		projected.reserve(points.size());
		for (const auto& point : points) {
			auto v = point - origin;
			if (std::abs(normal.dot(v)) > precision) {
				return false;
			}
			projected.push_back(Eigen::Vector2d(v.dot(x), v.dot(y)));
		}
		return true;
	}

	double signed_area(const std::vector<Eigen::Vector2d>& points) {
		double area = 0.;
		for (size_t i = 0; i < points.size(); ++i) {
			const auto& a = points[i];
			const auto& b = points[(i + 1) % points.size()];
			area += a(0) * b(1) - a(1) * b(0);
		}
		return 0.5 * area;
	}

	double triangle_cross(const Eigen::Vector2d& a, const Eigen::Vector2d& b, const Eigen::Vector2d& c) {
		return (b(0) - a(0)) * (c(1) - a(1)) - (b(1) - a(1)) * (c(0) - a(0));
	}

	bool point_in_triangle(const Eigen::Vector2d& p, const Eigen::Vector2d& a, const Eigen::Vector2d& b, const Eigen::Vector2d& c, double eps) {
		auto c1 = triangle_cross(a, b, p);
		auto c2 = triangle_cross(b, c, p);
		auto c3 = triangle_cross(c, a, p);
		auto has_neg = c1 < -eps || c2 < -eps || c3 < -eps;
		auto has_pos = c1 > eps || c2 > eps || c3 > eps;
		return !(has_neg && has_pos);
	}

	bool triangulate_polygon(const std::vector<Eigen::Vector2d>& polygon, double precision, std::vector<std::array<int, 3>>& triangles) {
		triangles.clear();
		if (polygon.size() < 3) {
			return false;
		}
		std::vector<int> indices(polygon.size());
		std::iota(indices.begin(), indices.end(), 0);
		auto orientation = signed_area(polygon);
		if (std::abs(orientation) <= precision * precision) {
			return false;
		}
		auto is_convex = [&](int a, int b, int c) {
			auto cross = triangle_cross(polygon[a], polygon[b], polygon[c]);
			return orientation > 0. ? cross > precision : cross < -precision;
		};
		while (indices.size() > 3) {
			bool clipped = false;
			for (size_t i = 0; i < indices.size(); ++i) {
				auto prev = indices[(i + indices.size() - 1) % indices.size()];
				auto curr = indices[i];
				auto next = indices[(i + 1) % indices.size()];
				if (!is_convex(prev, curr, next)) {
					continue;
				}
				bool contains = false;
				for (auto idx : indices) {
					if (idx == prev || idx == curr || idx == next) {
						continue;
					}
					if (point_in_triangle(polygon[idx], polygon[prev], polygon[curr], polygon[next], precision)) {
						contains = true;
						break;
					}
				}
				if (contains) {
					continue;
				}
				triangles.push_back({ prev, curr, next });
				indices.erase(indices.begin() + (ptrdiff_t)i);
				clipped = true;
				break;
			}
			if (!clipped) {
				return false;
			}
		}
		triangles.push_back({ indices[0], indices[1], indices[2] });
		return true;
	}

	taxonomy::face::ptr make_face(const std::vector<Eigen::Vector3d>& points) {
		auto face = taxonomy::make<taxonomy::face>();
		auto loop = taxonomy::make<taxonomy::loop>();
		loop->external = true;
		loop->closed = true;
		std::vector<taxonomy::point3::ptr> vertices;
		vertices.reserve(points.size());
		for (const auto& point : points) {
			vertices.push_back(taxonomy::make<taxonomy::point3>(point));
		}
		for (size_t i = 0; i < vertices.size(); ++i) {
			loop->children.push_back(taxonomy::make<taxonomy::edge>(vertices[i], vertices[(i + 1) % vertices.size()]));
		}
		face->children.push_back(loop);
		return face;
	}

	taxonomy::shell::ptr shell_from_extrusion(const taxonomy::extrusion::ptr& extrusion, double precision) {
		if (!extrusion || extrusion->depth <= precision) {
			return nullptr;
		}
		auto face = taxonomy::dcast<taxonomy::face>(extrusion->basis);
		std::vector<Eigen::Vector3d> base_points;
		if (!extrusion_supported_face(face, base_points)) {
			return nullptr;
		}
		Eigen::Vector3d origin;
		Eigen::Vector3d x;
		Eigen::Vector3d y;
		Eigen::Vector3d normal;
		std::vector<Eigen::Vector2d> projected;
		if (!polygon_basis(base_points, precision, origin, x, y, normal, projected)) {
			return nullptr;
		}
		auto direction = extrusion->direction ? extrusion->direction->ccomponents() : Eigen::Vector3d::Zero();
		if (direction.norm() <= precision) {
			return nullptr;
		}
		direction.normalize();
		if (std::abs(normal.dot(direction)) <= precision) {
			return nullptr;
		}
		std::vector<std::array<int, 3>> cap_triangles;
		if (!triangulate_polygon(projected, precision, cap_triangles)) {
			return nullptr;
		}
		auto offset = direction * extrusion->depth;
		auto shell = taxonomy::make<taxonomy::shell>();
		shell->instance = extrusion->instance;
		shell->closed = true;
		shell->surface_style = extrusion->surface_style;
		auto aligned = normal.dot(direction) > 0.;
		for (const auto& tri : cap_triangles) {
			if (aligned) {
				shell->children.push_back(make_face({ base_points[tri[2]], base_points[tri[1]], base_points[tri[0]] }));
				shell->children.push_back(make_face({ base_points[tri[0]] + offset, base_points[tri[1]] + offset, base_points[tri[2]] + offset }));
			} else {
				shell->children.push_back(make_face({ base_points[tri[0]], base_points[tri[1]], base_points[tri[2]] }));
				shell->children.push_back(make_face({ base_points[tri[2]] + offset, base_points[tri[1]] + offset, base_points[tri[0]] + offset }));
			}
		}
		for (size_t i = 0; i < base_points.size(); ++i) {
			auto j = (i + 1) % base_points.size();
			if (aligned) {
				shell->children.push_back(make_face({ base_points[i], base_points[j], base_points[j] + offset, base_points[i] + offset }));
			} else {
				shell->children.push_back(make_face({ base_points[i], base_points[i] + offset, base_points[j] + offset, base_points[j] }));
			}
		}
		return shell;
	}
}

bool passthrough_kernel::convert_impl(const taxonomy::shell::ptr shell, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!shell_supported(shell)) {
		return false;
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		shell->instance.id(),
		shell->matrix,
		new ifcopenshell::geom::passthrough_shape(passthrough_part{ shell, taxonomy::make<taxonomy::matrix4>(), shell->closed.value_or(false) }),
		shell->surface_style));
	return true;
}

bool passthrough_kernel::convert_impl(const taxonomy::solid::ptr solid, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (!solid || solid->children.size() != 1) {
		return false;
	}
	auto shell = solid->children.front();
	if (!shell_supported(shell)) {
		return false;
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		solid->instance.id(),
		solid->matrix,
		new ifcopenshell::geom::passthrough_shape(passthrough_part{
			shell,
			shell->matrix ? taxonomy::make<taxonomy::matrix4>(shell->matrix->ccomponents()) : taxonomy::make<taxonomy::matrix4>(),
			true
		}),
		fallback_style(solid, shell)));
	return true;
}

bool passthrough_kernel::convert_impl(const taxonomy::extrusion::ptr extrusion, std::vector<ifcopenshell::geom::conversion_result>& results) {
	auto shell = shell_from_extrusion(extrusion, settings_.get<settings::Precision>().get());
	if (!shell) {
		return false;
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		extrusion->instance.id(),
		extrusion->matrix,
		new ifcopenshell::geom::passthrough_shape(passthrough_part{ shell, taxonomy::make<taxonomy::matrix4>(), true }),
		extrusion->surface_style));
	return true;
}

bool passthrough_kernel::convert_openings(const express::base&, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>&,
	const std::vector<ifcopenshell::geom::conversion_result>&, const ifcopenshell::geom::taxonomy::matrix4&, std::vector<ifcopenshell::geom::conversion_result>&) {
	return false;
}
