#include "manifold_kernel.h"

#include "../../../ifcparse/logger.h"

#include <Eigen/Dense>
#include <manifold/polygon.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <limits>
#include <optional>
#include <sstream>
#include <unordered_map>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;

namespace {
	using mesh_type = manifold::MeshGL64;
	using part = ifcopenshell::geom::manifold_part;

	std::string manifold_error_string(manifold::Manifold::Error error) {
		switch (error) {
		case manifold::Manifold::Error::NoError:
			return "no error";
		case manifold::Manifold::Error::NonFiniteVertex:
			return "non-finite vertex";
		case manifold::Manifold::Error::NotManifold:
			return "not manifold";
		case manifold::Manifold::Error::VertexOutOfBounds:
			return "vertex out of bounds";
		case manifold::Manifold::Error::PropertiesWrongLength:
			return "properties wrong length";
		case manifold::Manifold::Error::MissingPositionProperties:
			return "missing position properties";
		case manifold::Manifold::Error::MergeVectorsDifferentLengths:
			return "merge vectors different lengths";
		case manifold::Manifold::Error::MergeIndexOutOfBounds:
			return "merge index out of bounds";
		case manifold::Manifold::Error::TransformWrongLength:
			return "transform wrong length";
		case manifold::Manifold::Error::RunIndexWrongLength:
			return "run index wrong length";
		case manifold::Manifold::Error::FaceIDWrongLength:
			return "face id wrong length";
		case manifold::Manifold::Error::InvalidConstruction:
			return "invalid construction";
		case manifold::Manifold::Error::ResultTooLarge:
			return "result too large";
		}
		return "unknown error";
	}

	struct vertex_key {
		long long x;
		long long y;
		long long z;

		bool operator==(const vertex_key& other) const {
			return x == other.x && y == other.y && z == other.z;
		}
	};

	struct vertex_key_hash {
		size_t operator()(const vertex_key& key) const {
			auto h = std::hash<long long>()(key.x);
			h ^= std::hash<long long>()(key.y) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			h ^= std::hash<long long>()(key.z) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct mesh_builder {
		double precision;
        double dilation = 0.;
		std::vector<Eigen::Vector3d> vertices;
		std::unordered_map<vertex_key, uint64_t, vertex_key_hash> vertex_map;
		std::vector<uint64_t> tri_verts;
		std::vector<uint64_t> face_ids;

		explicit mesh_builder(double p) : precision(p > 0. ? p : 1.e-9) {}

		vertex_key key(const Eigen::Vector3d& p) const {
			return {
				(long long)std::llround(p(0) / precision),
				(long long)std::llround(p(1) / precision),
				(long long)std::llround(p(2) / precision)
			};
		}

		uint64_t add_vertex(const Eigen::Vector3d& p) {
			auto entry = vertex_map.find(key(p));
			if (entry != vertex_map.end()) {
				return entry->second;
			}
			auto idx = (uint64_t)vertices.size();
			vertices.push_back(p);
			vertex_map.insert({ key(p), idx });
			return idx;
		}

		void add_triangle(uint64_t a, uint64_t b, uint64_t c, uint64_t face_id) {
			if (a == b || b == c || c == a) {
				return;
			}
			tri_verts.push_back(a);
			tri_verts.push_back(b);
			tri_verts.push_back(c);
			face_ids.push_back(face_id);
		}

		mesh_type build() const {
			mesh_type mesh;
			mesh.numProp = 3;

			std::vector<size_t> vertex_use_count(vertices.size(), 0);
            std::vector<Eigen::Vector3d> vertex_normals(vertices.size(), Eigen::Vector3d::Zero());

			for (size_t i = 0; i < tri_verts.size(); i += 3) {
                for (size_t j = 0; j < 3; ++j) {
                    vertex_use_count[tri_verts[i + j]]++;
                    // Calculate triangle normal
                    Eigen::Vector3d normal = (vertices[tri_verts[i + 1]] - vertices[tri_verts[i]]).cross(vertices[tri_verts[i + 2]] - vertices[tri_verts[i]]) / 2.;
                    vertex_normals[tri_verts[i + j]] += normal;
                }
            }

			for (auto& v : vertex_normals) {
				if (v.norm() > 0) {
					v.normalize();
				}
            }

			mesh.vertProperties.reserve(vertices.size() * 3);

			for (size_t i = 0; i < vertices.size(); ++i) {
                auto slightly_dilated = vertices[i] + vertex_normals[i] * dilation;
				mesh.vertProperties.push_back(slightly_dilated(0));
				mesh.vertProperties.push_back(slightly_dilated(1));
				mesh.vertProperties.push_back(slightly_dilated(2));
			}

			mesh.triVerts = tri_verts;
			mesh.faceID = face_ids;
			mesh.tolerance = precision;
			return mesh;
		}
	};

	struct loop_point {
		Eigen::Vector3d xyz;
		manifold::vec2 uv;
	};

	using loop_polygon = std::vector<loop_point>;

	struct edge_key {
		uint64_t a;
		uint64_t b;

		bool operator==(const edge_key& other) const {
			return a == other.a && b == other.b;
		}
	};

	struct edge_key_hash {
		size_t operator()(const edge_key& key) const {
			auto h = std::hash<uint64_t>()(key.a);
			h ^= std::hash<uint64_t>()(key.b) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct face_key {
		uint64_t a;
		uint64_t b;
		uint64_t c;

		bool operator==(const face_key& other) const {
			return a == other.a && b == other.b && c == other.c;
		}
	};

	struct face_key_hash {
		size_t operator()(const face_key& key) const {
			auto h = std::hash<uint64_t>()(key.a);
			h ^= std::hash<uint64_t>()(key.b) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			h ^= std::hash<uint64_t>()(key.c) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct edge_use_count {
		size_t forward = 0;
		size_t reverse = 0;
	};

	struct mesh_diagnostics {
		size_t vertices = 0;
		size_t triangles = 0;
		size_t unique_edges = 0;
		size_t invalid_indices = 0;
		size_t nonfinite_vertices = 0;
		size_t degenerate_triangles = 0;
		size_t zero_area_triangles = 0;
		size_t duplicate_faces = 0;
		size_t boundary_edges = 0;
		size_t nonmanifold_edges = 0;
		size_t orientation_conflicts = 0;
		long long euler_characteristic = 0;
		bool has_bounds = false;
		Eigen::Vector3d bounds_min = Eigen::Vector3d::Zero();
		Eigen::Vector3d bounds_max = Eigen::Vector3d::Zero();
		double min_edge = std::numeric_limits<double>::infinity();
		double max_edge = 0.;
		double min_area = std::numeric_limits<double>::infinity();
		double max_area = 0.;
	};

	struct shell_diagnostics {
		size_t faces = 0;
		size_t loops = 0;
		size_t edges = 0;
		size_t faces_with_inner_loops = 0;
		size_t max_loops_per_face = 0;
		size_t non_planar_faces = 0;
		size_t non_polygonal_edges = 0;
		size_t implicit_vertices = 0;
	};

	std::optional<Eigen::Vector3d> explicit_point(const taxonomy::edge::ptr& edge) {
		if (edge->start.index() != 1) {
			return std::nullopt;
		}
		return std::get<taxonomy::point3::ptr>(edge->start)->ccomponents();
	}

	void evaluate_curve(const taxonomy::line::ptr& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ 0, 0, u, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	void evaluate_curve(const taxonomy::circle::ptr& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ c->radius * std::cos(u), c->radius * std::sin(u), 0, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	void evaluate_curve(const taxonomy::ellipse::ptr& c, double u, taxonomy::point3& p) {
		Eigen::Vector4d xy{ c->radius * std::cos(u), c->radius2 * std::sin(u), 0, 1. };
		p.components() = (c->matrix->ccomponents() * xy).head<3>();
	}

	void project_onto_curve(const taxonomy::line::ptr& c, const taxonomy::point3& p, double& u) {
		u = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous())(2);
	}

	void project_onto_curve(const taxonomy::circle::ptr& c, const taxonomy::point3& p, double& u) {
		Eigen::Vector2d xy = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous()).head<2>();
		u = std::atan2(xy(1), xy(0));
	}

	void project_onto_curve(const taxonomy::ellipse::ptr& c, const taxonomy::point3& p, double& u) {
		Eigen::Vector2d xy = (c->matrix->ccomponents().inverse() * p.ccomponents().homogeneous()).head<2>();
		u = std::atan2(xy(1), xy(0));
	}

	taxonomy::item::ptr effective_curve_basis(const taxonomy::edge::ptr& edge) {
		auto basis = edge ? edge->basis : nullptr;
		while (basis && basis->kind() == taxonomy::EDGE) {
			auto nested = taxonomy::dcast<taxonomy::edge>(basis);
			if (!nested || nested == edge) {
				break;
			}
			basis = nested->basis;
		}
		return basis;
	}

	bool resolve_curve_parameter(const taxonomy::item::ptr& curve, const std::variant<boost::blank, taxonomy::point3::ptr, double>& trim, double& u) {
		if (auto value = std::get_if<double>(&trim)) {
			u = *value;
			return std::isfinite(u);
		}
		if (auto point = std::get_if<taxonomy::point3::ptr>(&trim)) {
			if (auto line = taxonomy::dcast<taxonomy::line>(curve)) {
				project_onto_curve(line, **point, u);
				return std::isfinite(u);
			}
			if (auto circle = taxonomy::dcast<taxonomy::circle>(curve)) {
				project_onto_curve(circle, **point, u);
				return std::isfinite(u);
			}
			if (auto ellipse = taxonomy::dcast<taxonomy::ellipse>(curve)) {
				project_onto_curve(ellipse, **point, u);
				return std::isfinite(u);
			}
		}
		return false;
	}

	bool basis_from_points(const std::vector<Eigen::Vector3d>& points, Eigen::Vector3d& origin, Eigen::Vector3d& x, Eigen::Vector3d& y) {
		if (points.size() < 3) {
			return false;
		}
		Eigen::Vector3d normal = Eigen::Vector3d::Zero();
		for (size_t i = 0; i < points.size(); ++i) {
			const auto& a = points[i];
			const auto& b = points[(i + 1) % points.size()];
			normal(0) += (a(1) - b(1)) * (a(2) + b(2));
			normal(1) += (a(2) - b(2)) * (a(0) + b(0));
			normal(2) += (a(0) - b(0)) * (a(1) + b(1));
		}
		if (normal.norm() < 1.e-12) {
			return false;
		}
		origin = points.front();
		x = points[1] - points.front();
		x -= normal.normalized() * x.dot(normal.normalized());
		if (x.norm() < 1.e-12) {
			return false;
		}
		x.normalize();
		y = normal.normalized().cross(x).normalized();
		return true;
	}

	bool edge_supported(const taxonomy::edge::ptr& edge) {
		return edge && (!edge->basis || edge->basis->kind() == taxonomy::LINE) && edge->start.index() == 1;
	}

	bool extrusion_edge_supported(const taxonomy::edge::ptr& edge) {
		if (!edge) {
			return false;
		}
		if (!edge->basis) {
			return edge->start.index() == 1 && edge->end.index() == 1;
		}
		auto basis = effective_curve_basis(edge);
		if (!basis) {
			return false;
		}
		if (basis->kind() != taxonomy::LINE && basis->kind() != taxonomy::CIRCLE && basis->kind() != taxonomy::ELLIPSE) {
			return false;
		}
		const bool full_curve = edge->start.index() == 0 && edge->end.index() == 0 && (basis->kind() == taxonomy::CIRCLE || basis->kind() == taxonomy::ELLIPSE);
		if (full_curve) {
			return true;
		}
		return edge->start.index() != 0 && edge->end.index() != 0;
	}

	bool loop_supported(const taxonomy::loop::ptr& loop) {
		if (!loop || loop->children.size() < 3 || !loop->is_polyhedron()) {
			return false;
		}
		for (const auto& edge : loop->children) {
			if (!edge_supported(edge)) {
				return false;
			}
		}
		return true;
	}

	bool face_supported(const taxonomy::face::ptr& face) {
		if (!face || face->children.empty()) {
			return false;
		}
		if (face->basis && face->basis->kind() != taxonomy::PLANE) {
			return false;
		}
		for (const auto& loop : face->children) {
			if (!loop_supported(loop)) {
				return false;
			}
		}
		return true;
	}

	bool extrusion_face_supported(const taxonomy::face::ptr& face) {
		if (!face || face->children.empty()) {
			return false;
		}
		if (face->basis && face->basis->kind() != taxonomy::PLANE) {
			return false;
		}
		for (const auto& loop : face->children) {
			if (!loop || loop->children.empty()) {
				return false;
			}
			for (const auto& edge : loop->children) {
				if (!extrusion_edge_supported(edge)) {
					return false;
				}
			}
		}
		return true;
	}

	bool append_extrusion_loop_points(const taxonomy::loop::ptr& loop, int circle_segments, double precision, std::vector<Eigen::Vector3d>& points);
	bool loop_polygon_from_points(const std::vector<Eigen::Vector3d>& points, const Eigen::Vector3d& origin, const Eigen::Vector3d& x, const Eigen::Vector3d& y, double precision, loop_polygon& polygon);
	double signed_area(const loop_polygon& polygon);

	bool extrusion_face_polygons(const taxonomy::face::ptr& face, int circle_segments, double precision, Eigen::Vector3d& origin, Eigen::Vector3d& x, Eigen::Vector3d& y, std::vector<loop_polygon>& polygons, size_t& outer_index) {
		polygons.clear();
		outer_index = 0;
		if (!extrusion_face_supported(face)) {
			return false;
		}
		std::vector<Eigen::Vector3d> basis_points;
		double basis_area = 0.;
		std::vector<std::vector<Eigen::Vector3d>> loops;
		loops.reserve(face->children.size());
		for (const auto& loop : face->children) {
			std::vector<Eigen::Vector3d> points;
			if (!append_extrusion_loop_points(loop, circle_segments, precision, points)) {
				return false;
			}
			Eigen::Vector3d loop_origin;
			Eigen::Vector3d loop_x;
			Eigen::Vector3d loop_y;
			if (!basis_from_points(points, loop_origin, loop_x, loop_y)) {
				return false;
			}
			loop_polygon polygon;
			if (!loop_polygon_from_points(points, loop_origin, loop_x, loop_y, precision, polygon)) {
				return false;
			}
			const auto area = std::fabs(signed_area(polygon));
			if (area > basis_area) {
				basis_area = area;
				basis_points = points;
			}
			loops.push_back(std::move(points));
		}
		if (!basis_from_points(basis_points, origin, x, y)) {
			return false;
		}
		double outer_area = 0.;
		polygons.reserve(loops.size());
		for (const auto& points : loops) {
			loop_polygon polygon;
			if (!loop_polygon_from_points(points, origin, x, y, precision, polygon)) {
				return false;
			}
			const auto area = signed_area(polygon);
			if (std::fabs(area) > std::fabs(outer_area)) {
				outer_area = area;
				outer_index = polygons.size();
			}
			polygons.push_back(std::move(polygon));
		}
		if (polygons.empty() || std::fabs(outer_area) <= precision * precision) {
			return false;
		}
		return true;
	}

	bool shell_supported(const taxonomy::shell::ptr& shell) {
		if (!shell || shell->children.empty()) {
			return false;
		}
		for (const auto& face : shell->children) {
			if (!face_supported(face)) {
				return false;
			}
		}
		return true;
	}

	bool face_basis(const taxonomy::face::ptr& face, Eigen::Vector3d& origin, Eigen::Vector3d& x, Eigen::Vector3d& y) {
		double best_score = -1.;
		std::vector<Eigen::Vector3d> best_points;
		for (const auto& loop : face->children) {
			std::vector<Eigen::Vector3d> points;
			points.reserve(loop->children.size());
			for (const auto& edge : loop->children) {
				auto point = explicit_point(edge);
				if (!point) {
					return false;
				}
				if (!points.empty()) {
					const auto d = points.back() - *point;
					if (d.squaredNorm() <= 1.e-24) {
						continue;
					}
				}
				points.push_back(*point);
			}
			if (points.size() > 1) {
				const auto d = points.front() - points.back();
				if (d.squaredNorm() <= 1.e-24) {
					points.pop_back();
				}
			}
			if (points.size() < 3) {
				continue;
			}
			Eigen::Vector3d normal = Eigen::Vector3d::Zero();
			for (size_t i = 0; i < points.size(); ++i) {
				const auto& a = points[i];
				const auto& b = points[(i + 1) % points.size()];
				normal(0) += (a(1) - b(1)) * (a(2) + b(2));
				normal(1) += (a(2) - b(2)) * (a(0) + b(0));
				normal(2) += (a(0) - b(0)) * (a(1) + b(1));
			}
			const auto score = normal.squaredNorm();
			if (score <= 1.e-24 || score <= best_score) {
				continue;
			}
			best_score = score;
			best_points = std::move(points);
		}
		return basis_from_points(best_points, origin, x, y);
	}

	double signed_area(const manifold::SimplePolygonIdx& polygon) {
		double area = 0.;
		for (size_t i = 0; i < polygon.size(); ++i) {
			const auto& a = polygon[i].pos;
			const auto& b = polygon[(i + 1) % polygon.size()].pos;
			area += a[0] * b[1] - b[0] * a[1];
		}
		return 0.5 * area;
	}

	Eigen::Vector3d mesh_vertex(const mesh_type& mesh, size_t index) {
		return Eigen::Vector3d(
			mesh.vertProperties[index * mesh.numProp + 0],
			mesh.vertProperties[index * mesh.numProp + 1],
			mesh.vertProperties[index * mesh.numProp + 2]);
	}

	std::string format_number(double value) {
		std::ostringstream ss;
		ss << std::setprecision(6) << value;
		return ss.str();
	}

	std::string format_vector(const Eigen::Vector3d& value) {
		return "(" + format_number(value(0)) + ", " + format_number(value(1)) + ", " + format_number(value(2)) + ")";
	}

	mesh_diagnostics diagnose_mesh(const mesh_type& mesh, double precision) {
		mesh_diagnostics diagnostics;
		diagnostics.vertices = mesh.NumVert();
		diagnostics.triangles = mesh.NumTri();
		std::unordered_map<edge_key, edge_use_count, edge_key_hash> edge_use_count;
		std::unordered_map<face_key, size_t, face_key_hash> face_use_count;
		for (size_t i = 0; i < diagnostics.vertices; ++i) {
			auto p = mesh_vertex(mesh, i);
			if (!std::isfinite(p(0)) || !std::isfinite(p(1)) || !std::isfinite(p(2))) {
				diagnostics.nonfinite_vertices++;
				continue;
			}
			if (!diagnostics.has_bounds) {
				diagnostics.has_bounds = true;
				diagnostics.bounds_min = p;
				diagnostics.bounds_max = p;
			} else {
				diagnostics.bounds_min = diagnostics.bounds_min.cwiseMin(p);
				diagnostics.bounds_max = diagnostics.bounds_max.cwiseMax(p);
			}
		}
		for (size_t i = 0; i < diagnostics.triangles; ++i) {
			auto a = mesh.triVerts[i * 3 + 0];
			auto b = mesh.triVerts[i * 3 + 1];
			auto c = mesh.triVerts[i * 3 + 2];
			if (a >= diagnostics.vertices || b >= diagnostics.vertices || c >= diagnostics.vertices) {
				diagnostics.invalid_indices++;
				continue;
			}
			auto pa = mesh_vertex(mesh, (size_t)a);
			auto pb = mesh_vertex(mesh, (size_t)b);
			auto pc = mesh_vertex(mesh, (size_t)c);
			const auto ab = (pb - pa).norm();
			const auto bc = (pc - pb).norm();
			const auto ca = (pa - pc).norm();
			if (std::isfinite(ab) && ab > 0.) {
				diagnostics.min_edge = std::min(diagnostics.min_edge, ab);
				diagnostics.max_edge = std::max(diagnostics.max_edge, ab);
			}
			if (std::isfinite(bc) && bc > 0.) {
				diagnostics.min_edge = std::min(diagnostics.min_edge, bc);
				diagnostics.max_edge = std::max(diagnostics.max_edge, bc);
			}
			if (std::isfinite(ca) && ca > 0.) {
				diagnostics.min_edge = std::min(diagnostics.min_edge, ca);
				diagnostics.max_edge = std::max(diagnostics.max_edge, ca);
			}
			if (a == b || b == c || c == a) {
				diagnostics.degenerate_triangles++;
				continue;
			}
			const auto area = 0.5 * ((pb - pa).cross(pc - pa)).norm();
			if (std::isfinite(area)) {
				diagnostics.min_area = std::min(diagnostics.min_area, area);
				diagnostics.max_area = std::max(diagnostics.max_area, area);
				if (area <= precision * precision) {
					diagnostics.zero_area_triangles++;
				}
			}
			std::array<uint64_t, 3> face = { a, b, c };
			std::sort(face.begin(), face.end());
			const face_key face_key{ face[0], face[1], face[2] };
			auto face_it = face_use_count.find(face_key);
			if (face_it == face_use_count.end()) {
				face_use_count.insert({ face_key, 1 });
			} else {
				face_it->second++;
				diagnostics.duplicate_faces++;
			}
			std::array<edge_key, 3> edges = {
				edge_key{ std::min(a, b), std::max(a, b) },
				edge_key{ std::min(b, c), std::max(b, c) },
				edge_key{ std::min(c, a), std::max(c, a) }
			};
			std::array<bool, 3> forward = {
				a < b,
				b < c,
				c < a
			};
			for (const auto& edge : edges) {
				if (edge.a == edge.b) {
					continue;
				}
			}
			for (size_t j = 0; j < edges.size(); ++j) {
				const auto& edge = edges[j];
				auto& use = edge_use_count[edge];
				if (forward[j]) {
					use.forward++;
				} else {
					use.reverse++;
				}
			}
		}
		for (const auto& entry : edge_use_count) {
			const auto total = entry.second.forward + entry.second.reverse;
			if (total == 1) {
				diagnostics.boundary_edges++;
			} else if (total > 2) {
				diagnostics.nonmanifold_edges++;
			} else if (entry.second.forward != 1 || entry.second.reverse != 1) {
				diagnostics.orientation_conflicts++;
			}
		}
		diagnostics.unique_edges = edge_use_count.size();
		diagnostics.euler_characteristic = (long long)diagnostics.vertices - (long long)diagnostics.unique_edges + (long long)diagnostics.triangles;
		return diagnostics;
	}

	shell_diagnostics diagnose_shell(const taxonomy::shell::ptr& shell) {
		shell_diagnostics diagnostics;
		diagnostics.faces = shell->children.size();
		for (const auto& face : shell->children) {
			diagnostics.max_loops_per_face = std::max(diagnostics.max_loops_per_face, face->children.size());
			if (face->children.size() > 1) {
				diagnostics.faces_with_inner_loops++;
			}
			diagnostics.loops += face->children.size();
			if (face->basis && face->basis->kind() != taxonomy::PLANE) {
				diagnostics.non_planar_faces++;
			}
			for (const auto& loop : face->children) {
				diagnostics.edges += loop->children.size();
				for (const auto& edge : loop->children) {
					if (edge->basis && edge->basis->kind() != taxonomy::LINE) {
						diagnostics.non_polygonal_edges++;
					}
					if (edge->start.index() != 1) {
						diagnostics.implicit_vertices++;
					}
				}
			}
		}
		return diagnostics;
	}

	std::string mesh_diagnostics_string(const mesh_diagnostics& diagnostics) {
		std::ostringstream ss;
		ss << "verts=" << diagnostics.vertices
			<< " tris=" << diagnostics.triangles
			<< " unique_edges=" << diagnostics.unique_edges
			<< " euler=" << diagnostics.euler_characteristic
			<< " invalid_idx=" << diagnostics.invalid_indices
			<< " nonfinite_verts=" << diagnostics.nonfinite_vertices
			<< " degenerate_tris=" << diagnostics.degenerate_triangles
			<< " zero_area_tris=" << diagnostics.zero_area_triangles
			<< " duplicate_faces=" << diagnostics.duplicate_faces
			<< " boundary_edges=" << diagnostics.boundary_edges
			<< " nonmanifold_edges=" << diagnostics.nonmanifold_edges
			<< " orientation_conflicts=" << diagnostics.orientation_conflicts;
		if (diagnostics.has_bounds) {
			ss << " bbox_min=" << format_vector(diagnostics.bounds_min)
				<< " bbox_max=" << format_vector(diagnostics.bounds_max);
		}
		if (std::isfinite(diagnostics.min_edge)) {
			ss << " min_edge=" << format_number(diagnostics.min_edge);
		}
		if (diagnostics.max_edge > 0.) {
			ss << " max_edge=" << format_number(diagnostics.max_edge);
		}
		if (std::isfinite(diagnostics.min_area)) {
			ss << " min_area=" << format_number(diagnostics.min_area);
		}
		if (diagnostics.max_area > 0.) {
			ss << " max_area=" << format_number(diagnostics.max_area);
		}
		return ss.str();
	}

	std::string shell_diagnostics_string(const shell_diagnostics& diagnostics) {
		std::ostringstream ss;
		ss << "faces=" << diagnostics.faces
			<< " loops=" << diagnostics.loops
			<< " edges=" << diagnostics.edges
			<< " faces_with_inner_loops=" << diagnostics.faces_with_inner_loops
			<< " max_loops_per_face=" << diagnostics.max_loops_per_face
			<< " non_planar_faces=" << diagnostics.non_planar_faces
			<< " non_polygonal_edges=" << diagnostics.non_polygonal_edges
			<< " implicit_vertices=" << diagnostics.implicit_vertices;
		return ss.str();
	}

	std::string matrix_diagnostics_string(const taxonomy::matrix4::ptr& place) {
		const auto& m = place->ccomponents();
		const auto linear = m.block<3, 3>(0, 0);
		const auto c0 = linear.col(0);
		const auto c1 = linear.col(1);
		const auto c2 = linear.col(2);
		std::ostringstream ss;
		ss << "det=" << format_number(linear.determinant())
			<< " scale=(" << format_number(c0.norm()) << ", " << format_number(c1.norm()) << ", " << format_number(c2.norm()) << ")"
			<< " dot=(" << format_number(c0.dot(c1)) << ", " << format_number(c0.dot(c2)) << ", " << format_number(c1.dot(c2)) << ")"
			<< " translation=" << format_vector(m.col(3).head<3>());
		return ss.str();
	}

	std::string solid_shell_failure_diagnosis(const part& part, const mesh_diagnostics& before, const mesh_diagnostics& after, manifold::Manifold::Error before_status, manifold::Manifold::Error after_status) {
		const bool before_problematic =
			!part.solid ||
			before_status != manifold::Manifold::Error::NoError ||
			before.invalid_indices != 0 ||
			before.nonfinite_vertices != 0 ||
			before.degenerate_triangles != 0 ||
			before.zero_area_triangles != 0 ||
			before.boundary_edges != 0 ||
			before.nonmanifold_edges != 0;
		const bool after_problematic =
			after_status != manifold::Manifold::Error::NoError ||
			after.invalid_indices != 0 ||
			after.nonfinite_vertices != 0 ||
			after.degenerate_triangles != 0 ||
			after.zero_area_triangles != 0 ||
			after.boundary_edges != 0 ||
			after.nonmanifold_edges != 0;
		if (before_problematic) {
			return "shell is already problematic before transform";
		}
		if (after_problematic) {
			return "shell is valid before transform, failure is likely introduced by transform or precision collapse";
		}
		return "shell looks clean before and after mesh inspection, issue may be in manifold validation details";
	}

	void log_solid_shell_transform_failure(const taxonomy::shell::ptr& shell, const part& before_part, const mesh_type& after_mesh, const taxonomy::matrix4::ptr& place, double precision, manifold::Manifold::Error before_status, manifold::Manifold::Error after_status) {
		const auto shell_info = diagnose_shell(shell);
		const auto before = diagnose_mesh(before_part.mesh, precision);
		const auto after = diagnose_mesh(after_mesh, precision);
		ifcopenshell::logger::root().warning(
			"Manifold kernel: solid shell manifold validation failed; before_transform=" +
			std::string(before_part.solid ? "solid" : "mesh-only") +
			" (" + manifold_error_string(before_status) + "), after_transform=(" + manifold_error_string(after_status) + ")",
			shell->instance);
		ifcopenshell::logger::root().warning("Manifold kernel: solid shell diagnosis: " + solid_shell_failure_diagnosis(before_part, before, after, before_status, after_status), shell->instance);
		ifcopenshell::logger::root().warning("Manifold kernel: solid shell input: " + shell_diagnostics_string(shell_info), shell->instance);
		ifcopenshell::logger::root().warning("Manifold kernel: solid shell mesh before transform: " + mesh_diagnostics_string(before), shell->instance);
		ifcopenshell::logger::root().warning("Manifold kernel: solid shell transform: " + matrix_diagnostics_string(place), shell->instance);
		ifcopenshell::logger::root().warning("Manifold kernel: solid shell mesh after transform: " + mesh_diagnostics_string(after), shell->instance);
	}

	double signed_area(const manifold::SimplePolygon& polygon) {
		double area = 0.;
		for (size_t i = 0; i < polygon.size(); ++i) {
			const auto& a = polygon[i];
			const auto& b = polygon[(i + 1) % polygon.size()];
			area += a[0] * b[1] - b[0] * a[1];
		}
		return 0.5 * area;
	}

	double signed_area(const loop_polygon& polygon) {
		double area = 0.;
		for (size_t i = 0; i < polygon.size(); ++i) {
			const auto& a = polygon[i].uv;
			const auto& b = polygon[(i + 1) % polygon.size()].uv;
			area += a[0] * b[1] - b[0] * a[1];
		}
		return 0.5 * area;
	}

	void extend_points(std::vector<Eigen::Vector3d>& points, const std::vector<taxonomy::point3>& edge_points, double precision) {
		if (edge_points.empty()) {
			return;
		}
		const auto merge_tolerance = std::max(precision, 1.e-5);
		size_t offset = 0;
		if (!points.empty() && (points.back() - edge_points.front().ccomponents()).norm() < merge_tolerance) {
			offset = 1;
		}
		for (size_t i = offset; i < edge_points.size(); ++i) {
			const auto point = edge_points[i].ccomponents();
			if (!points.empty() && (points.back() - point).norm() < merge_tolerance) {
				continue;
			}
			points.push_back(point);
		}
	}

	bool append_extrusion_edge_points(const taxonomy::edge::ptr& edge, int circle_segments, double precision, std::vector<Eigen::Vector3d>& points) {
		if (!edge) {
			return false;
		}
		const auto two_pi = 2. * std::acos(-1.);
		std::vector<taxonomy::point3> edge_points;
		if (!edge->basis) {
			if (edge->start.index() != 1 || edge->end.index() != 1) {
				return false;
			}
			edge_points.push_back(*std::get<taxonomy::point3::ptr>(edge->start));
			edge_points.push_back(*std::get<taxonomy::point3::ptr>(edge->end));
			extend_points(points, edge_points, precision);
			return true;
		}
		auto basis = effective_curve_basis(edge);
		if (!basis) {
			return false;
		}
		double a;
		double b;
		const bool full_conic = edge->start.index() == 0 && edge->end.index() == 0 && (basis->kind() == taxonomy::CIRCLE || basis->kind() == taxonomy::ELLIPSE);
		if (full_conic) {
			a = 0.;
			b = two_pi;
		} else {
			if (!resolve_curve_parameter(basis, edge->start, a) || !resolve_curve_parameter(basis, edge->end, b)) {
				return false;
			}
		}
		const bool reverse = !edge->curve_sense.value_or(true);
		if (reverse) {
			std::swap(a, b);
		}
		taxonomy::point3 point;
		if (auto line = taxonomy::dcast<taxonomy::line>(basis)) {
			evaluate_curve(line, a, point);
			edge_points.push_back(point);
			evaluate_curve(line, b, point);
			edge_points.push_back(point);
		} else if (auto circle = taxonomy::dcast<taxonomy::circle>(basis)) {
			a = std::fmod(a, two_pi);
			b = std::fmod(b, two_pi);
			if (b <= a) {
				b += two_pi;
			}
			const auto num_segments = std::max(1, (int)std::ceil(std::fabs(a - b) / two_pi * circle_segments));
			const auto du = (b - a) / num_segments;
			evaluate_curve(circle, a, point);
			edge_points.push_back(point);
			for (int i = 1; i < num_segments; ++i) {
				evaluate_curve(circle, a + du * i, point);
				edge_points.push_back(point);
			}
			evaluate_curve(circle, b, point);
			edge_points.push_back(point);
		} else if (auto ellipse = taxonomy::dcast<taxonomy::ellipse>(basis)) {
			a = std::fmod(a, two_pi);
			b = std::fmod(b, two_pi);
			if (b <= a) {
				b += two_pi;
			}
			const auto num_segments = std::max(1, (int)std::ceil(std::fabs(a - b) / two_pi * circle_segments));
			const auto du = (b - a) / num_segments;
			evaluate_curve(ellipse, a, point);
			edge_points.push_back(point);
			for (int i = 1; i < num_segments; ++i) {
				evaluate_curve(ellipse, a + du * i, point);
				edge_points.push_back(point);
			}
			evaluate_curve(ellipse, b, point);
			edge_points.push_back(point);
		} else {
			return false;
		}
		if (reverse) {
			std::reverse(edge_points.begin(), edge_points.end());
		}
		extend_points(points, edge_points, precision);
		return true;
	}

	bool append_extrusion_loop_points(const taxonomy::loop::ptr& loop, int circle_segments, double precision, std::vector<Eigen::Vector3d>& points) {
		points.clear();
		if (!loop || loop->children.empty()) {
			return false;
		}
		for (const auto& edge : loop->children) {
			if (!append_extrusion_edge_points(edge, circle_segments, precision, points)) {
				return false;
			}
		}
		if (points.size() > 1) {
			const auto merge_tolerance = std::max(precision, 1.e-5);
			if ((points.front() - points.back()).norm() < merge_tolerance) {
				points.pop_back();
			}
		}
		return points.size() >= 3;
	}

	bool loop_polygon_from_points(const std::vector<Eigen::Vector3d>& points, const Eigen::Vector3d& origin, const Eigen::Vector3d& x, const Eigen::Vector3d& y, double precision, loop_polygon& polygon) {
		polygon.clear();
		polygon.reserve(points.size());
		for (const auto& point : points) {
			if (!polygon.empty()) {
				const auto d = polygon.back().xyz - point;
				if (d.squaredNorm() <= precision * precision) {
					continue;
				}
			}
			auto v = point - origin;
			polygon.push_back({ point, manifold::vec2(v.dot(x), v.dot(y)) });
		}
		if (polygon.size() > 1) {
			const auto d = polygon.front().xyz - polygon.back().xyz;
			if (d.squaredNorm() <= precision * precision) {
				polygon.pop_back();
			}
		}
		return polygon.size() >= 3;
	}

	bool append_simple_loop(const taxonomy::loop::ptr& loop, const Eigen::Vector3d& origin, const Eigen::Vector3d& x, const Eigen::Vector3d& y, double precision, loop_polygon& polygon) {
		polygon.clear();
		polygon.reserve(loop->children.size());
		for (const auto& edge : loop->children) {
			if (edge->basis && edge->basis->kind() != taxonomy::LINE) {
				return false;
			}
			auto point = explicit_point(edge);
			if (!point) {
				return false;
			}
			if (!polygon.empty()) {
				const auto d = polygon.back().xyz - *point;
				if (d.squaredNorm() <= precision * precision) {
					continue;
				}
			}
			auto v = *point - origin;
			polygon.push_back({ *point, manifold::vec2(v.dot(x), v.dot(y)) });
		}
		if (polygon.size() > 1) {
			const auto d = polygon.front().xyz - polygon.back().xyz;
			if (d.squaredNorm() <= precision * precision) {
				polygon.pop_back();
			}
		}
		if (polygon.size() < 3) {
			return false;
		}
		return true;
	}

	void reverse_loop(loop_polygon& polygon) {
		std::reverse(polygon.begin(), polygon.end());
	}

	void append_loop(const loop_polygon& loop_polygon, mesh_builder& builder, manifold::PolygonsIdx& polygons) {
		manifold::SimplePolygonIdx polygon;
		polygon.reserve(loop_polygon.size());
		for (const auto& point : loop_polygon) {
			manifold::PolyVert poly_vert;
			poly_vert.pos = point.uv;
			poly_vert.idx = (int)builder.add_vertex(point.xyz);
			polygon.push_back(poly_vert);
		}
		polygons.push_back(std::move(polygon));
	}

	bool append_face(const taxonomy::face::ptr& face, mesh_builder& builder, uint64_t face_id) {
		if (!face_supported(face)) {
			return false;
		}
		Eigen::Vector3d origin;
		Eigen::Vector3d x;
		Eigen::Vector3d y;
		if (!face_basis(face, origin, x, y)) {
			return false;
		}
		std::vector<loop_polygon> loops;
		loops.reserve(face->children.size());
		size_t outer_index = 0;
		double outer_area = 0.;
		manifold::PolygonsIdx polygons;
		polygons.reserve(face->children.size());
		for (const auto& loop : face->children) {
			loop_polygon loop_polygon;
			if (!append_simple_loop(loop, origin, x, y, builder.precision, loop_polygon)) {
				return false;
			}
			const auto area = signed_area(loop_polygon);
			if (std::abs(area) > std::abs(outer_area)) {
				outer_area = area;
				outer_index = loops.size();
			}
			loops.push_back(std::move(loop_polygon));
		}
		if (loops.empty() || std::abs(outer_area) < 1.e-12) {
			return false;
		}
		for (size_t i = 0; i < loops.size(); ++i) {
			if (i != outer_index && signed_area(loops[i]) * outer_area > 0.) {
				reverse_loop(loops[i]);
			}
			append_loop(loops[i], builder, polygons);
		}
		auto triangles = manifold::TriangulateIdx(polygons, builder.precision, true);
		for (const auto& tri : triangles) {
			builder.add_triangle((uint32_t)tri[0], (uint32_t)tri[1], (uint32_t)tri[2], face_id);
		}
		return !triangles.empty();
	}

	bool shell_to_mesh(const taxonomy::shell::ptr& shell, double precision, mesh_type& mesh, double dilation) {
		mesh_builder builder(precision);
        builder.dilation = dilation;
		uint64_t face_id = 0;
		bool any = false;
		for (const auto& face : shell->children) {
			if (!append_face(face, builder, face_id++)) {
				return false;
			}
			any = true;
		}
		if (!any) {
			return false;
		}
		mesh = builder.build();
		return mesh.NumTri() > 0;
	}

	std::optional<part> part_from_mesh(const mesh_type& mesh, bool require_manifold, manifold::Manifold::Error* status_ptr = nullptr) {
		auto solid = std::optional<manifold::Manifold>{};
		manifold::Manifold candidate(mesh);
		auto status = candidate.Status();
		if (status_ptr) {
			*status_ptr = status;
		}
		if (status == manifold::Manifold::Error::NoError) {
			solid = candidate;
		}
		if (!solid && require_manifold) {
			return std::nullopt;
		}
		if (solid) {
            return *solid;
		}
		return mesh;
	}

	std::optional<part> part_from_shell(const taxonomy::shell::ptr& shell, double precision, double dilation, manifold::Manifold::Error* status_ptr = nullptr) {
		mesh_type mesh;
		if (!shell_to_mesh(shell, precision, mesh, dilation)) {
			return std::nullopt;
		}
		return part_from_mesh(mesh, false, status_ptr);
	}

	mesh_type transform_mesh(const mesh_type& mesh, const taxonomy::matrix4::ptr& place);
    std::optional<part> part_from_extrusion(const taxonomy::extrusion::ptr& extrusion, double precision, double dilation, int circle_segments);

	Eigen::Matrix4d matrix_or_identity(const taxonomy::matrix4::ptr& matrix) {
		return matrix ? matrix->ccomponents() : Eigen::Matrix4d::Identity();
	}

	Eigen::Vector3d transform_point(const Eigen::Matrix4d& matrix, const Eigen::Vector3d& point) {
		return (matrix * point.homogeneous()).head<3>();
	}

	Eigen::Vector3d transform_vector(const Eigen::Matrix4d& matrix, const Eigen::Vector3d& vector) {
		return matrix.block<3, 3>(0, 0) * vector;
	}

	taxonomy::face::ptr halfspace_face(const taxonomy::solid::ptr& solid) {
		if (!solid || !solid->instance.declaration().is("IfcHalfSpaceSolid") || solid->children.size() != 1) {
			return nullptr;
		}
		const auto& shell = solid->children.front();
		if (!shell || shell->children.size() != 1) {
			return nullptr;
		}
		auto face = shell->children.front();
		if (!face || !face->basis || face->basis->kind() != taxonomy::PLANE || face->children.size() > 1) {
			return nullptr;
		}
		return face;
	}

	bool explicit_loop_polygon(const taxonomy::loop::ptr& loop, const Eigen::Matrix4d& transform, const Eigen::Vector3d& plane_origin, const Eigen::Vector3d& x, const Eigen::Vector3d& y, double precision, loop_polygon& polygon) {
		polygon.clear();
		if (!loop || loop->children.size() < 3) {
			return false;
		}
		polygon.reserve(loop->children.size());
		for (const auto& edge : loop->children) {
			if (!edge || (edge->basis && edge->basis->kind() != taxonomy::LINE) || edge->start.index() != 1) {
				return false;
			}
			auto point = transform_point(transform, std::get<taxonomy::point3::ptr>(edge->start)->ccomponents());
			if (!polygon.empty() && (polygon.back().xyz - point).squaredNorm() <= precision * precision) {
				continue;
			}
			auto delta = point - plane_origin;
			polygon.push_back({ point, manifold::vec2(delta.dot(x), delta.dot(y)) });
		}
		if (polygon.size() > 1 && (polygon.front().xyz - polygon.back().xyz).squaredNorm() <= precision * precision) {
			polygon.pop_back();
		}
		return polygon.size() >= 3;
	}

	std::array<Eigen::Vector3d, 8> box_corners(const manifold::Box& box) {
		return {
			Eigen::Vector3d(box.min[0], box.min[1], box.min[2]),
			Eigen::Vector3d(box.min[0], box.min[1], box.max[2]),
			Eigen::Vector3d(box.min[0], box.max[1], box.min[2]),
			Eigen::Vector3d(box.min[0], box.max[1], box.max[2]),
			Eigen::Vector3d(box.max[0], box.min[1], box.min[2]),
			Eigen::Vector3d(box.max[0], box.min[1], box.max[2]),
			Eigen::Vector3d(box.max[0], box.max[1], box.min[2]),
			Eigen::Vector3d(box.max[0], box.max[1], box.max[2])
		};
	}

	struct halfspace_build_state {
		bool unchanged = false;
		double depth = 0.;
	};

	std::optional<part> part_from_polygon_extrusion(std::vector<loop_polygon> polygons, size_t outer_index, const Eigen::Vector3d& plane_normal, const Eigen::Vector3d& direction, double depth, double precision, double dilation) {
		if (depth < precision || polygons.empty() || outer_index >= polygons.size()) {
			return std::nullopt;
		}
		auto dir = direction;
		if (dir.norm() < 1.e-12) {
			return std::nullopt;
		}
		dir.normalize();
		auto normal = plane_normal;
		if (normal.norm() < 1.e-12) {
			return std::nullopt;
		}
		normal.normalize();
		auto outer_area = signed_area(polygons[outer_index]);
		if (std::abs(outer_area) <= precision * precision) {
			return std::nullopt;
		}
		if (outer_area < 0.) {
			reverse_loop(polygons[outer_index]);
			outer_area = -outer_area;
		}
		for (size_t i = 0; i < polygons.size(); ++i) {
			if (i != outer_index && signed_area(polygons[i]) * outer_area > 0.) {
				reverse_loop(polygons[i]);
			}
		}
		auto direction_sign = normal.dot(dir);
		if (std::abs(direction_sign) < 1.e-9) {
			return std::nullopt;
		}
		auto offset = dir * depth;
		mesh_builder builder(precision);
        builder.dilation = dilation;
		std::vector<std::vector<uint64_t>> bottoms;
		std::vector<std::vector<uint64_t>> tops;
		std::unordered_map<uint64_t, uint64_t> top_by_bottom;
		manifold::PolygonsIdx polygon_idx;
		polygon_idx.reserve(polygons.size());
		bottoms.reserve(polygons.size());
		tops.reserve(polygons.size());
		for (const auto& polygon : polygons) {
			manifold::SimplePolygonIdx loop_idx;
			loop_idx.reserve(polygon.size());
			bottoms.emplace_back();
			tops.emplace_back();
			bottoms.back().reserve(polygon.size());
			tops.back().reserve(polygon.size());
			for (const auto& point : polygon) {
				auto bottom = builder.add_vertex(point.xyz);
				auto top = builder.add_vertex(point.xyz + offset);
				bottoms.back().push_back(bottom);
				tops.back().push_back(top);
				top_by_bottom.insert({ bottom, top });
				loop_idx.push_back({ point.uv, (int)bottom });
			}
			polygon_idx.push_back(std::move(loop_idx));
		}
		auto triangles = manifold::TriangulateIdx(polygon_idx, precision, true);
		if (triangles.empty()) {
			return std::nullopt;
		}
		for (const auto& tri : triangles) {
			auto a = (uint64_t)tri[0];
			auto b = (uint64_t)tri[1];
			auto c = (uint64_t)tri[2];
			if (direction_sign > 0.) {
				builder.add_triangle(c, b, a, 0);
				builder.add_triangle(top_by_bottom[a], top_by_bottom[b], top_by_bottom[c], 1);
			} else {
				builder.add_triangle(a, b, c, 0);
				builder.add_triangle(top_by_bottom[c], top_by_bottom[b], top_by_bottom[a], 1);
			}
		}
		uint64_t face_id = 2;
		for (size_t k = 0; k < polygons.size(); ++k) {
			for (size_t i = 0; i < polygons[k].size(); ++i) {
				auto j = (i + 1) % polygons[k].size();
				if (direction_sign > 0.) {
					builder.add_triangle(bottoms[k][i], bottoms[k][j], tops[k][j], face_id);
					builder.add_triangle(bottoms[k][i], tops[k][j], tops[k][i], face_id);
				} else {
					builder.add_triangle(bottoms[k][i], tops[k][j], bottoms[k][j], face_id);
					builder.add_triangle(bottoms[k][i], tops[k][i], tops[k][j], face_id);
				}
				++face_id;
			}
		}
		return part_from_mesh(builder.build(), true);
	}

	std::optional<part> part_from_halfspace_solid(halfspace_build_state& state, const taxonomy::solid::ptr& solid, const taxonomy::face::ptr& face,const manifold::Box& reference_box, double precision, double dilation) {

        auto plane = taxonomy::cast<taxonomy::plane>(face->basis);

		// @todo verify order
        const auto transform = matrix_or_identity(solid->matrix) * matrix_or_identity(plane->matrix);
        const auto extrusion_dir = matrix_or_identity(solid->matrix).col(2).head<3>().eval();

		Eigen::Vector3d x = transform.col(0).head<3>();
        Eigen::Vector3d y = transform.col(1).head<3>();
        Eigen::Vector3d normal = transform.col(2).head<3>();
        Eigen::Vector3d origin = transform.col(3).head<3>();

		auto project_along_global_z = [&](const Eigen::Vector3d& p)
            -> std::optional<loop_point> {
            Eigen::Vector3d hit;

            if (std::abs(normal.z()) > precision) {
                const double t = normal.dot(origin - p) / normal.z();
                hit = p + Eigen::Vector3d(0., 0., t);
            } else {
                return std::nullopt;
            }

            const auto delta = hit - origin;
            return std::make_optional(loop_point{
                hit,
                manifold::vec2(delta.dot(x), delta.dot(y))});
        };

		const auto inside_sign = face->orientation.value_or(false) ? +1. : -1.;
		double u_min = std::numeric_limits<double>::infinity();
		double u_max = -std::numeric_limits<double>::infinity();
		double v_min = std::numeric_limits<double>::infinity();
		double v_max = -std::numeric_limits<double>::infinity();
		double max_depth = 0.;
		for (const auto& corner : box_corners(reference_box)) {
			const auto delta = corner - origin;
			const auto u = delta.dot(x);
			const auto v = delta.dot(y);

			u_min = std::min(u_min, u);
			u_max = std::max(u_max, u);
			v_min = std::min(v_min, v);
			v_max = std::max(v_max, v);

			// Keep in mind that extrusion direction is not necessarily parallel to plane normal, so we need to project corner onto plane along global z and measure distance along extrusion direction
			if (auto proj = project_along_global_z(corner)) {
                auto w = (corner - proj->xyz).dot(extrusion_dir);
                max_depth = std::max(max_depth, inside_sign * w);
            }
        }
		state.depth = max_depth;
		if (max_depth <= precision * 20. || max_depth <= 0.00002) {
			state.unchanged = true;
			return std::nullopt;
		}
		const auto diagonal = Eigen::Vector3d(reference_box.max[0] - reference_box.min[0], reference_box.max[1] - reference_box.min[1], reference_box.max[2] - reference_box.min[2]).norm();
		const auto margin = std::max(precision * 100., diagonal * 1.e-6);
		loop_polygon polygon;
		if (face->children.empty()) {
			polygon = {
				{ origin + x * (u_min - margin) + y * (v_min - margin), manifold::vec2(u_min - margin, v_min - margin) },
				{ origin + x * (u_max + margin) + y * (v_min - margin), manifold::vec2(u_max + margin, v_min - margin) },
				{ origin + x * (u_max + margin) + y * (v_max + margin), manifold::vec2(u_max + margin, v_max + margin) },
				{ origin + x * (u_min - margin) + y * (v_max + margin), manifold::vec2(u_min - margin, v_max + margin) }
			};
        } else {
            auto& loop = face->children.front();
            for (auto& e : loop->children) {
                if (auto point = explicit_point(e)) {
                    auto transformed = transform_point(matrix_or_identity(face->matrix), *point);
                    if (auto ppoint = project_along_global_z(transformed)) {
                        polygon.push_back(*ppoint);
                    } else {
                        return std::nullopt;
					}
				} else {
                    return std::nullopt;
				}
			}
		}

		return part_from_polygon_extrusion({std::move(polygon)}, 0, normal, extrusion_dir * -inside_sign, max_depth + margin, precision, dilation);
	}

	std::optional<part> part_from_extrusion(const taxonomy::extrusion::ptr& extrusion, double precision, double dilation, int circle_segments) {
		if (extrusion->depth < precision) {
			return std::nullopt;
		}
		auto face = std::dynamic_pointer_cast<taxonomy::face>(extrusion->basis);
		if (!extrusion_face_supported(face)) {
			return std::nullopt;
		}
		Eigen::Vector3d origin;
		Eigen::Vector3d x;
		Eigen::Vector3d y;
		std::vector<loop_polygon> polygons;
		size_t outer_index = 0;
		if (!extrusion_face_polygons(face, circle_segments, precision, origin, x, y, polygons, outer_index)) {
			return std::nullopt;
		}
		auto normal = x.cross(y);
		if (normal.norm() < 1.e-12) {
			return std::nullopt;
		}
		return part_from_polygon_extrusion(std::move(polygons), outer_index, normal, extrusion->direction->ccomponents(), extrusion->depth, precision, dilation);
	}

	bool extrusion_supported(const taxonomy::extrusion::ptr& extrusion, double precision) {
		if (!extrusion || extrusion->depth < precision || !extrusion->direction) {
			return false;
		}
		auto face = std::dynamic_pointer_cast<taxonomy::face>(extrusion->basis);
		if (!extrusion_face_supported(face)) {
			return false;
		}
		Eigen::Vector3d origin;
		Eigen::Vector3d x;
		Eigen::Vector3d y;
		std::vector<loop_polygon> polygons;
		size_t outer_index = 0;
		if (!extrusion_face_polygons(face, settings::CircleSegments::defaultvalue, precision, origin, x, y, polygons, outer_index)) {
			return false;
		}
		auto dir = extrusion->direction->ccomponents();
		if (dir.norm() < 1.e-12) {
			return false;
		}
		dir.normalize();
		auto normal = x.cross(y);
		if (normal.norm() < 1.e-12) {
			return false;
		}
		normal.normalize();
		if (std::abs(normal.dot(dir)) < 1.e-9) {
			return false;
		}
		return !polygons.empty();
	}

	mesh_type transform_mesh(const mesh_type& mesh, const taxonomy::matrix4::ptr& place) {
		const auto& m = place->ccomponents();
		mesh_type result = mesh;
		const bool flip = m.block<3, 3>(0, 0).determinant() < 0.;
		for (size_t i = 0; i < mesh.NumVert(); ++i) {
			Eigen::Vector4d v(
				mesh.vertProperties[i * mesh.numProp + 0],
				mesh.vertProperties[i * mesh.numProp + 1],
				mesh.vertProperties[i * mesh.numProp + 2],
				1.);
			auto v2 = m * v;
			result.vertProperties[i * result.numProp + 0] = v2(0);
			result.vertProperties[i * result.numProp + 1] = v2(1);
			result.vertProperties[i * result.numProp + 2] = v2(2);
		}
		if (flip) {
			for (size_t i = 0; i < mesh.NumTri(); ++i) {
				std::swap(result.triVerts[i * 3 + 1], result.triVerts[i * 3 + 2]);
			}
		}
		result.runTransform.clear();
		return result;
	}

	taxonomy::style::ptr fallback_style(const taxonomy::geom_item::ptr& item, const std::vector<ifcopenshell::geom::conversion_result>& results) {
		if (item->surface_style) {
			return item->surface_style;
		}
		for (const auto& result : results) {
			if (result.hasStyle()) {
				return result.style_ptr();
			}
		}
		return nullptr;
	}

	std::optional<manifold::Manifold> result_to_manifold(const ifcopenshell::geom::conversion_result& result) {
		auto moved = std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(result.apply_transform());
		auto* shape = dynamic_cast<ifcopenshell::geom::manifold_shape*>(moved.get());
		if (!shape) {
			return std::nullopt;
		}
		return shape->as_manifold();
	}

	std::optional<manifold::Manifold> results_to_operand(const std::vector<ifcopenshell::geom::conversion_result>& results) {
		std::vector<manifold::Manifold> operands;
		for (const auto& result : results) {
			auto operand = result_to_manifold(result);
			if (operand) {
				operands.push_back(*operand);
			}
		}
		if (operands.empty()) {
			return std::nullopt;
		}
		if (operands.size() == 1) {
			return operands.front();
		}
		return manifold::Manifold::BatchBoolean(operands, manifold::OpType::Add);
	}

	std::optional<manifold::Box> results_bbox(const std::vector<ifcopenshell::geom::conversion_result>& results) {
		bool any = false;
		manifold::Box bbox;
		for (const auto& result : results) {
			auto operand = result_to_manifold(result);
			if (!operand) {
				return std::nullopt;
			}
			auto part_box = operand->BoundingBox();
			if (!part_box.IsFinite()) {
				return std::nullopt;
			}
			if (!any) {
				bbox = part_box;
				any = true;
			} else {
				bbox.Union(part_box.min);
				bbox.Union(part_box.max);
			}
		}
		if (!any) {
			return std::nullopt;
		}
		return bbox;
	}

	std::optional<manifold::Manifold> boolean_result_from_operands(const std::vector<manifold::Manifold>& operands, taxonomy::boolean_result::operation_type operation) {
		if (operands.empty()) {
			return std::nullopt;
		}
		if (operands.size() == 1) {
			return operands.front();
		}
		switch (operation) {
		case taxonomy::boolean_result::UNION:
			return manifold::Manifold::BatchBoolean(operands, manifold::OpType::Add);
		case taxonomy::boolean_result::INTERSECTION:
			return manifold::Manifold::BatchBoolean(operands, manifold::OpType::Intersect);
		case taxonomy::boolean_result::SUBTRACTION:
			return manifold::Manifold::BatchBoolean(operands, manifold::OpType::Subtract);
		}
		return std::nullopt;
	}
}

bool manifold_kernel::convert_impl(const taxonomy::extrusion::ptr extrusion, std::vector<ifcopenshell::geom::conversion_result>& results) {
	auto part = part_from_extrusion(extrusion, settings_.get<settings::Precision>().get(), dilation_hack, settings_.get<settings::CircleSegments>().get());
	if (!part) {
		ifcopenshell::logger::root().warning("Manifold kernel: failed to convert extrusion, requires planar bounds with line, circle or ellipse edges", extrusion->instance);
		return false;
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		extrusion->instance.id(),
		extrusion->matrix,
		new ifcopenshell::geom::manifold_shape(std::move(*part)),
		extrusion->surface_style));
	return true;
}

bool manifold_kernel::convert_impl(const taxonomy::shell::ptr shell, std::vector<ifcopenshell::geom::conversion_result>& results) {
	manifold::Manifold::Error status = manifold::Manifold::Error::NoError;
	auto part = part_from_shell(shell, settings_.get<settings::Precision>().get(), dilation_hack, &status);
	if (!part) {
		ifcopenshell::logger::root().warning("Manifold kernel: failed to convert shell, requires planar polygonal faces with explicit vertices", shell->instance);
		return false;
	}
	if (!part->solid) {
		ifcopenshell::logger::root().notice("Manifold kernel: shell converted as mesh only (" + manifold_error_string(status) + ")", shell->instance);
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		shell->instance.id(),
		shell->matrix,
		new ifcopenshell::geom::manifold_shape(std::move(*part)),
		shell->surface_style));
	return true;
}

bool manifold_kernel::convert_impl(const taxonomy::solid::ptr solid, std::vector<ifcopenshell::geom::conversion_result>& results) {
	std::vector<manifold::Manifold> shells;
	for (const auto& shell : solid->children) {
		const auto precision = settings_.get<settings::Precision>().get();
		manifold::Manifold::Error before_status = manifold::Manifold::Error::NoError;
		auto part = part_from_shell(shell, precision, dilation_hack, &before_status);
		if (!part) {
			ifcopenshell::logger::root().warning("Manifold kernel: failed to convert solid shell, requires planar polygonal faces with explicit vertices", shell->instance);
			return false;
		}
		auto place = shell->matrix ? shell->matrix : taxonomy::make<taxonomy::matrix4>();
		auto transformed_mesh = transform_mesh(part->mesh, place);
		manifold::Manifold::Error after_status = manifold::Manifold::Error::NoError;
		auto transformed = part_from_mesh(transformed_mesh, true, &after_status);
		if (!transformed || !transformed->solid) {
			log_solid_shell_transform_failure(shell, *part, transformed_mesh, place, precision, before_status, after_status);
			return false;
		}
		shells.push_back(*transformed->solid);
	}
	if (shells.empty()) {
		return false;
	}
	auto result = shells.front();
	for (size_t i = 1; i < shells.size(); ++i) {
		result -= shells[i];
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		solid->instance.id(),
		solid->matrix,
		new ifcopenshell::geom::manifold_shape(result),
		solid->surface_style));
	return true;
}

bool manifold_kernel::convert_impl(const taxonomy::boolean_result::ptr br, std::vector<ifcopenshell::geom::conversion_result>& results) {
	std::vector<manifold::Manifold> operands;
	taxonomy::style::ptr style;
	std::optional<manifold::Box> first_bbox;
	const auto precision = settings_.get<settings::Precision>().get();
	bool first = true;
	for (const auto& child : br->children) {
		std::optional<manifold::Manifold> operand;
		auto solid = std::dynamic_pointer_cast<taxonomy::solid>(child);
        taxonomy::face::ptr face = solid ? halfspace_face(solid) : nullptr;
		// @todo reset upon exceptions
        dilation_hack = first ? 0. : precision * 10.;
		if (!first && br->operation == taxonomy::boolean_result::SUBTRACTION && face) {
			if (!first_bbox) {
				ifcopenshell::logger::root().warning("Manifold kernel: cannot fit halfspace operand without a valid first operand bounds", child->instance);
				return false;
			}
			halfspace_build_state state;
            auto part = part_from_halfspace_solid(state, solid, face, *first_bbox, precision, dilation_hack);
			if (!part) {
				if (state.unchanged && br->operation == taxonomy::boolean_result::SUBTRACTION) {
					ifcopenshell::logger::root().warning("Manifold kernel: halfspace subtraction yields unchanged volume", child->instance);
					continue;
				}
				ifcopenshell::logger::root().warning("Manifold kernel: failed to fit halfspace boolean operand to first operand bounds", child->instance);
				return false;
			}
			if (!part->solid) {
				ifcopenshell::logger::root().warning("Manifold kernel: fitted halfspace operand is not a valid manifold solid", child->instance);
				return false;
			}
			operand = *part->solid;
			if (!style && child->surface_style) {
				style = child->surface_style;
			}
		} else {
			std::vector<ifcopenshell::geom::conversion_result> converted;
			if (!abstract_kernel::convert(child, converted)) {
				ifcopenshell::logger::root().warning("Manifold kernel: failed to convert boolean operand", child->instance);
				return false;
			}
			operand = results_to_operand(converted);
			if (!operand) {
				ifcopenshell::logger::root().warning("Manifold kernel: boolean operand is not a valid manifold solid", child->instance);
				return false;
			}
			if (!style) {
				style = fallback_style(child, converted);
			}
		}
		if (!operand) {
			return false;
		}
		if (first) {
			auto bbox = operand->BoundingBox();
			if (!bbox.IsFinite()) {
				ifcopenshell::logger::root().warning("Manifold kernel: first boolean operand has no valid bounds", child->instance);
				return false;
			}
			first_bbox = bbox;
		}
		operands.push_back(*operand);
		first = false;
	}
    dilation_hack = 0.;
	auto result = boolean_result_from_operands(operands, br->operation);
	if (!result || result->IsEmpty()) {
		ifcopenshell::logger::root().warning("Manifold kernel: boolean operation produced no result", br->instance);
		return false;
	}
	results.emplace_back(ifcopenshell::geom::conversion_result(
		br->instance.id(),
		br->matrix,
		new ifcopenshell::geom::manifold_shape(*result),
		br->surface_style ? br->surface_style : style));
	return true;
}

bool manifold_kernel::convert_openings(const express::base&, const std::vector<std::pair<taxonomy::ptr, taxonomy::matrix4>>& openings, const std::vector<ifcopenshell::geom::conversion_result>& entity_shapes, const taxonomy::matrix4& entity_trsf, std::vector<ifcopenshell::geom::conversion_result>& cut_shapes) {
	std::vector<manifold::Manifold> opening_operands;
	auto entity_bbox = results_bbox(entity_shapes);
	if (!entity_bbox) {
		ifcopenshell::logger::root().warning("Manifold kernel: host shape has no valid bounds for halfspace fitting");
		return false;
	}
    dilation_hack = settings_.get<settings::Precision>().get() * 10.;
	for (const auto& opening : openings) {
		const auto relative = taxonomy::make<taxonomy::matrix4>(entity_trsf.ccomponents().inverse() * opening.second.ccomponents());
		std::vector<ifcopenshell::geom::conversion_result> converted;
		if (!abstract_kernel::convert(opening.first, converted)) {
			ifcopenshell::logger::root().warning("Manifold kernel: failed to convert opening operand", opening.first->instance);
			return false;
		}
		for (const auto& result : converted) {
			auto moved = std::unique_ptr<ifcopenshell::geom::conversion_result_shape>(result.shape()->moved(taxonomy::make<taxonomy::matrix4>(relative->ccomponents() * result.placement()->ccomponents())));
			auto* shape = dynamic_cast<ifcopenshell::geom::manifold_shape*>(moved.get());
			if (!shape) {
				ifcopenshell::logger::root().warning("Manifold kernel: opening result is not a manifold shape");
				return false;
			}
			auto operand = shape->as_manifold();
			if (!operand) {
				ifcopenshell::logger::root().warning("Manifold kernel: opening result is not a valid manifold solid", opening.first->instance);
				return false;
			}
			opening_operands.push_back(*operand);
		}
	}
    dilation_hack = 0.;
	if (opening_operands.empty()) {
		return false;
	}
	auto opening_union = manifold::Manifold::BatchBoolean(opening_operands, manifold::OpType::Add);
	for (const auto& entity_shape : entity_shapes) {
		auto operand = result_to_manifold(entity_shape);
		if (!operand) {
			ifcopenshell::logger::root().warning("Manifold kernel: host shape is not a valid manifold solid");
			return false;
		}
		auto result = *operand - opening_union;
		cut_shapes.emplace_back(ifcopenshell::geom::conversion_result(
			entity_shape.ItemId(),
			new ifcopenshell::geom::manifold_shape(result),
			entity_shape.style_ptr()));
	}
	return !cut_shapes.empty();
}
