#include "ManifoldKernel.h"

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

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;

namespace {
	using Mesh = manifold::MeshGL64;
	using Part = ifcopenshell::geometry::ManifoldPart;

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

	struct VertexKey {
		long long x;
		long long y;
		long long z;

		bool operator==(const VertexKey& other) const {
			return x == other.x && y == other.y && z == other.z;
		}
	};

	struct VertexKeyHash {
		size_t operator()(const VertexKey& key) const {
			auto h = std::hash<long long>()(key.x);
			h ^= std::hash<long long>()(key.y) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			h ^= std::hash<long long>()(key.z) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct MeshBuilder {
		double precision;
		std::vector<Eigen::Vector3d> vertices;
		std::unordered_map<VertexKey, uint64_t, VertexKeyHash> vertex_map;
		std::vector<uint64_t> tri_verts;
		std::vector<uint64_t> face_ids;

		explicit MeshBuilder(double p) : precision(p > 0. ? p : 1.e-9) {}

		VertexKey key(const Eigen::Vector3d& p) const {
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

		Mesh build() const {
			Mesh mesh;
			mesh.numProp = 3;
			mesh.vertProperties.reserve(vertices.size() * 3);
			for (const auto& vertex : vertices) {
				mesh.vertProperties.push_back(vertex(0));
				mesh.vertProperties.push_back(vertex(1));
				mesh.vertProperties.push_back(vertex(2));
			}
			mesh.triVerts = tri_verts;
			mesh.faceID = face_ids;
			mesh.tolerance = precision;
			return mesh;
		}
	};

	struct LoopPoint {
		Eigen::Vector3d xyz;
		manifold::vec2 uv;
	};

	using LoopPolygon = std::vector<LoopPoint>;

	struct EdgeKey {
		uint64_t a;
		uint64_t b;

		bool operator==(const EdgeKey& other) const {
			return a == other.a && b == other.b;
		}
	};

	struct EdgeKeyHash {
		size_t operator()(const EdgeKey& key) const {
			auto h = std::hash<uint64_t>()(key.a);
			h ^= std::hash<uint64_t>()(key.b) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct FaceKey {
		uint64_t a;
		uint64_t b;
		uint64_t c;

		bool operator==(const FaceKey& other) const {
			return a == other.a && b == other.b && c == other.c;
		}
	};

	struct FaceKeyHash {
		size_t operator()(const FaceKey& key) const {
			auto h = std::hash<uint64_t>()(key.a);
			h ^= std::hash<uint64_t>()(key.b) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			h ^= std::hash<uint64_t>()(key.c) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct EdgeUseCount {
		size_t forward = 0;
		size_t reverse = 0;
	};

	struct MeshDiagnostics {
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

	struct ShellDiagnostics {
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

	bool face_supported(const taxonomy::face::ptr& face) {
		if (face->basis && face->basis->kind() != taxonomy::PLANE) {
			return false;
		}
		for (const auto& loop : face->children) {
			if (!loop->is_polyhedron()) {
				return false;
			}
			for (const auto& edge : loop->children) {
				if (edge->start.index() != 1) {
					return false;
				}
			}
		}
		return true;
	}

	bool extrusion_face_supported(const taxonomy::face::ptr& face) {
		return face && face->children.size() == 1 && face_supported(face);
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
		if (best_points.size() < 3) {
			return false;
		}
		Eigen::Vector3d normal = Eigen::Vector3d::Zero();
		for (size_t i = 0; i < best_points.size(); ++i) {
			const auto& a = best_points[i];
			const auto& b = best_points[(i + 1) % best_points.size()];
			normal(0) += (a(1) - b(1)) * (a(2) + b(2));
			normal(1) += (a(2) - b(2)) * (a(0) + b(0));
			normal(2) += (a(0) - b(0)) * (a(1) + b(1));
		}
		if (normal.norm() < 1.e-12) {
			return false;
		}
		origin = best_points.front();
		x = best_points[1] - best_points.front();
		x -= normal.normalized() * x.dot(normal.normalized());
		if (x.norm() < 1.e-12) {
			return false;
		}
		x.normalize();
		y = normal.normalized().cross(x).normalized();
		return true;
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

	Eigen::Vector3d mesh_vertex(const Mesh& mesh, size_t index) {
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

	MeshDiagnostics diagnose_mesh(const Mesh& mesh, double precision) {
		MeshDiagnostics diagnostics;
		diagnostics.vertices = mesh.NumVert();
		diagnostics.triangles = mesh.NumTri();
		std::unordered_map<EdgeKey, EdgeUseCount, EdgeKeyHash> edge_use_count;
		std::unordered_map<FaceKey, size_t, FaceKeyHash> face_use_count;
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
			const FaceKey face_key{ face[0], face[1], face[2] };
			auto face_it = face_use_count.find(face_key);
			if (face_it == face_use_count.end()) {
				face_use_count.insert({ face_key, 1 });
			} else {
				face_it->second++;
				diagnostics.duplicate_faces++;
			}
			std::array<EdgeKey, 3> edges = {
				EdgeKey{ std::min(a, b), std::max(a, b) },
				EdgeKey{ std::min(b, c), std::max(b, c) },
				EdgeKey{ std::min(c, a), std::max(c, a) }
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

	ShellDiagnostics diagnose_shell(const taxonomy::shell::ptr& shell) {
		ShellDiagnostics diagnostics;
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

	std::string mesh_diagnostics_string(const MeshDiagnostics& diagnostics) {
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

	std::string shell_diagnostics_string(const ShellDiagnostics& diagnostics) {
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

	std::string solid_shell_failure_diagnosis(const Part& part, const MeshDiagnostics& before, const MeshDiagnostics& after, manifold::Manifold::Error before_status, manifold::Manifold::Error after_status) {
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

	void log_solid_shell_transform_failure(const taxonomy::shell::ptr& shell, const Part& before_part, const Mesh& after_mesh, const taxonomy::matrix4::ptr& place, double precision, manifold::Manifold::Error before_status, manifold::Manifold::Error after_status) {
		const auto shell_info = diagnose_shell(shell);
		const auto before = diagnose_mesh(before_part.mesh, precision);
		const auto after = diagnose_mesh(after_mesh, precision);
		logger::warning(
			"Manifold kernel: solid shell manifold validation failed; before_transform=" +
			std::string(before_part.solid ? "solid" : "mesh-only") +
			" (" + manifold_error_string(before_status) + "), after_transform=(" + manifold_error_string(after_status) + ")",
			shell->instance);
		logger::warning("Manifold kernel: solid shell diagnosis: " + solid_shell_failure_diagnosis(before_part, before, after, before_status, after_status), shell->instance);
		logger::warning("Manifold kernel: solid shell input: " + shell_diagnostics_string(shell_info), shell->instance);
		logger::warning("Manifold kernel: solid shell mesh before transform: " + mesh_diagnostics_string(before), shell->instance);
		logger::warning("Manifold kernel: solid shell transform: " + matrix_diagnostics_string(place), shell->instance);
		logger::warning("Manifold kernel: solid shell mesh after transform: " + mesh_diagnostics_string(after), shell->instance);
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

	double signed_area(const LoopPolygon& polygon) {
		double area = 0.;
		for (size_t i = 0; i < polygon.size(); ++i) {
			const auto& a = polygon[i].uv;
			const auto& b = polygon[(i + 1) % polygon.size()].uv;
			area += a[0] * b[1] - b[0] * a[1];
		}
		return 0.5 * area;
	}

	bool append_simple_loop(const taxonomy::loop::ptr& loop, const Eigen::Vector3d& origin, const Eigen::Vector3d& x, const Eigen::Vector3d& y, double precision, LoopPolygon& polygon) {
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

	void reverse_loop(LoopPolygon& polygon) {
		std::reverse(polygon.begin(), polygon.end());
	}

	void append_loop(const LoopPolygon& loop_polygon, MeshBuilder& builder, manifold::PolygonsIdx& polygons) {
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

	bool append_face(const taxonomy::face::ptr& face, MeshBuilder& builder, uint64_t face_id) {
		if (!face_supported(face)) {
			return false;
		}
		Eigen::Vector3d origin;
		Eigen::Vector3d x;
		Eigen::Vector3d y;
		if (!face_basis(face, origin, x, y)) {
			return false;
		}
		std::vector<LoopPolygon> loops;
		loops.reserve(face->children.size());
		size_t outer_index = 0;
		double outer_area = 0.;
		manifold::PolygonsIdx polygons;
		polygons.reserve(face->children.size());
		for (const auto& loop : face->children) {
			LoopPolygon loop_polygon;
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

	bool shell_to_mesh(const taxonomy::shell::ptr& shell, double precision, Mesh& mesh) {
		MeshBuilder builder(precision);
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

	std::optional<Part> part_from_mesh(const Mesh& mesh, bool require_manifold, manifold::Manifold::Error* status_ptr = nullptr) {
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
			return Part{ solid->GetMeshGL64(), solid };
		}
		return Part{ mesh, std::nullopt };
	}

	std::optional<Part> part_from_shell(const taxonomy::shell::ptr& shell, double precision, manifold::Manifold::Error* status_ptr = nullptr) {
		Mesh mesh;
		if (!shell_to_mesh(shell, precision, mesh)) {
			return std::nullopt;
		}
		return part_from_mesh(mesh, false, status_ptr);
	}

	Mesh transform_mesh(const Mesh& mesh, const taxonomy::matrix4::ptr& place);

	std::optional<Part> part_from_extrusion(const taxonomy::extrusion::ptr& extrusion, double precision) {
		if (extrusion->depth < precision) {
			return std::nullopt;
		}
		auto face = taxonomy::dcast<taxonomy::face>(extrusion->basis);
		if (!extrusion_face_supported(face)) {
			return std::nullopt;
		}
		Eigen::Vector3d origin;
		Eigen::Vector3d x;
		Eigen::Vector3d y;
		if (!face_basis(face, origin, x, y)) {
			return std::nullopt;
		}
		auto dir = extrusion->direction->ccomponents();
		if (dir.norm() < 1.e-12) {
			return std::nullopt;
		}
		dir.normalize();
		auto normal = x.cross(y);
		if (normal.norm() < 1.e-12) {
			return std::nullopt;
		}
		normal.normalize();
		auto direction_sign = normal.dot(dir);
		if (std::abs(direction_sign) < 1.e-9) {
			return std::nullopt;
		}
		LoopPolygon polygon;
		if (!append_simple_loop(face->children.front(), origin, x, y, precision, polygon)) {
			return std::nullopt;
		}
		manifold::SimplePolygonIdx polygon_idx;
		polygon_idx.reserve(polygon.size());
		for (size_t i = 0; i < polygon.size(); ++i) {
			polygon_idx.push_back({ polygon[i].uv, (int)i });
		}
		manifold::PolygonsIdx polygons = { polygon_idx };
		auto triangles = manifold::TriangulateIdx(polygons, precision, true);
		if (triangles.empty()) {
			return std::nullopt;
		}
		auto offset = dir * extrusion->depth;
		MeshBuilder builder(precision);
		std::vector<uint64_t> bottom;
		std::vector<uint64_t> top;
		bottom.reserve(polygon.size());
		top.reserve(polygon.size());
		for (const auto& point : polygon) {
			bottom.push_back(builder.add_vertex(point.xyz));
			top.push_back(builder.add_vertex(point.xyz + offset));
		}
		for (const auto& tri : triangles) {
			auto a = (size_t)tri[0];
			auto b = (size_t)tri[1];
			auto c = (size_t)tri[2];
			if (direction_sign > 0.) {
				builder.add_triangle(bottom[c], bottom[b], bottom[a], 0);
				builder.add_triangle(top[a], top[b], top[c], 1);
			} else {
				builder.add_triangle(bottom[a], bottom[b], bottom[c], 0);
				builder.add_triangle(top[c], top[b], top[a], 1);
			}
		}
		for (size_t i = 0; i < polygon.size(); ++i) {
			auto j = (i + 1) % polygon.size();
			if (direction_sign > 0.) {
				builder.add_triangle(bottom[i], bottom[j], top[j], 2 + (uint64_t)i);
				builder.add_triangle(bottom[i], top[j], top[i], 2 + (uint64_t)i);
			} else {
				builder.add_triangle(bottom[i], top[j], bottom[j], 2 + (uint64_t)i);
				builder.add_triangle(bottom[i], top[i], top[j], 2 + (uint64_t)i);
			}
		}
		return part_from_mesh(builder.build(), true);
	}

	Mesh transform_mesh(const Mesh& mesh, const taxonomy::matrix4::ptr& place) {
		const auto& m = place->ccomponents();
		Mesh result = mesh;
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

	taxonomy::style::ptr fallback_style(const taxonomy::geom_item::ptr& item, const IfcGeom::ConversionResults& results) {
		if (item->surface_style) {
			return item->surface_style;
		}
		for (const auto& result : results) {
			if (result.hasStyle()) {
				return result.StylePtr();
			}
		}
		return nullptr;
	}

	std::optional<manifold::Manifold> result_to_manifold(const IfcGeom::ConversionResult& result) {
		auto moved = std::unique_ptr<IfcGeom::ConversionResultShape>(result.apply_transform());
		auto* shape = dynamic_cast<ifcopenshell::geometry::ManifoldShape*>(moved.get());
		if (!shape) {
			return std::nullopt;
		}
		return shape->as_manifold();
	}

	std::optional<manifold::Manifold> results_to_operand(const IfcGeom::ConversionResults& results) {
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

	std::optional<manifold::Manifold> boolean_result_from_operands(const std::vector<manifold::Manifold>& operands, taxonomy::boolean_result::operation_t operation) {
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

bool ManifoldKernel::convert_impl(const taxonomy::extrusion::ptr extrusion, IfcGeom::ConversionResults& results) {
	auto part = part_from_extrusion(extrusion, settings_.get<settings::Precision>().get());
	if (!part) {
		logger::warning("Manifold kernel: failed to convert extrusion, only simple extrusions with a single polygonal outer bound are supported", extrusion->instance);
		return false;
	}
	results.emplace_back(IfcGeom::ConversionResult(
		extrusion->instance.id(),
		extrusion->matrix,
		new ifcopenshell::geometry::ManifoldShape(std::move(*part)),
		extrusion->surface_style));
	return true;
}

bool ManifoldKernel::convert_impl(const taxonomy::shell::ptr shell, IfcGeom::ConversionResults& results) {
	manifold::Manifold::Error status = manifold::Manifold::Error::NoError;
	auto part = part_from_shell(shell, settings_.get<settings::Precision>().get(), &status);
	if (!part) {
		logger::warning("Manifold kernel: failed to convert shell, requires planar polygonal faces with explicit vertices", shell->instance);
		return false;
	}
	if (!part->solid) {
		logger::notice("Manifold kernel: shell converted as mesh only (" + manifold_error_string(status) + ")", shell->instance);
	}
	results.emplace_back(IfcGeom::ConversionResult(
		shell->instance.id(),
		shell->matrix,
		new ifcopenshell::geometry::ManifoldShape(std::move(*part)),
		shell->surface_style));
	return true;
}

bool ManifoldKernel::convert_impl(const taxonomy::solid::ptr solid, IfcGeom::ConversionResults& results) {
	std::vector<manifold::Manifold> shells;
	for (const auto& shell : solid->children) {
		const auto precision = settings_.get<settings::Precision>().get();
		manifold::Manifold::Error before_status = manifold::Manifold::Error::NoError;
		auto part = part_from_shell(shell, precision, &before_status);
		if (!part) {
			logger::warning("Manifold kernel: failed to convert solid shell, requires planar polygonal faces with explicit vertices", shell->instance);
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
	results.emplace_back(IfcGeom::ConversionResult(
		solid->instance.id(),
		solid->matrix,
		new ifcopenshell::geometry::ManifoldShape(Part{ result.GetMeshGL64(), result }),
		solid->surface_style));
	return true;
}

bool ManifoldKernel::convert_impl(const taxonomy::boolean_result::ptr br, IfcGeom::ConversionResults& results) {
	std::vector<manifold::Manifold> operands;
	taxonomy::style::ptr style;
	for (const auto& child : br->children) {
		IfcGeom::ConversionResults converted;
		if (!AbstractKernel::convert(child, converted)) {
			logger::warning("Manifold kernel: failed to convert boolean operand", child->instance);
			return false;
		}
		auto operand = results_to_operand(converted);
		if (!operand) {
			logger::warning("Manifold kernel: boolean operand is not a valid manifold solid", child->instance);
			return false;
		}
		operands.push_back(*operand);
		if (!style) {
			style = fallback_style(child, converted);
		}
	}
	auto result = boolean_result_from_operands(operands, br->operation);
	if (!result || result->IsEmpty()) {
		logger::warning("Manifold kernel: boolean operation produced no result", br->instance);
		return false;
	}
	results.emplace_back(IfcGeom::ConversionResult(
		br->instance.id(),
		br->matrix,
		new ifcopenshell::geometry::ManifoldShape(Part{ result->GetMeshGL64(), *result }),
		br->surface_style ? br->surface_style : style));
	return true;
}

bool ManifoldKernel::convert_openings(const express::Base&, const std::vector<std::pair<taxonomy::ptr, taxonomy::matrix4>>& openings, const IfcGeom::ConversionResults& entity_shapes, const taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes) {
	std::vector<manifold::Manifold> opening_operands;
	for (const auto& opening : openings) {
		IfcGeom::ConversionResults converted;
		if (!AbstractKernel::convert(opening.first, converted)) {
			logger::warning("Manifold kernel: failed to convert opening operand", opening.first->instance);
			return false;
		}
		const auto relative = taxonomy::make<taxonomy::matrix4>(entity_trsf.ccomponents().inverse() * opening.second.ccomponents());
		for (const auto& result : converted) {
			auto moved = std::unique_ptr<IfcGeom::ConversionResultShape>(result.Shape()->moved(taxonomy::make<taxonomy::matrix4>(relative->ccomponents() * result.Placement()->ccomponents())));
			auto* shape = dynamic_cast<ifcopenshell::geometry::ManifoldShape*>(moved.get());
			if (!shape) {
				logger::warning("Manifold kernel: opening result is not a manifold shape");
				return false;
			}
			auto operand = shape->as_manifold();
			if (!operand) {
				logger::warning("Manifold kernel: opening result is not a valid manifold solid", opening.first->instance);
				return false;
			}
			opening_operands.push_back(*operand);
		}
	}
	if (opening_operands.empty()) {
		return false;
	}
	auto opening_union = manifold::Manifold::BatchBoolean(opening_operands, manifold::OpType::Add);
	for (const auto& entity_shape : entity_shapes) {
		auto operand = result_to_manifold(entity_shape);
		if (!operand) {
			logger::warning("Manifold kernel: host shape is not a valid manifold solid");
			return false;
		}
		auto result = *operand - opening_union;
		cut_shapes.emplace_back(IfcGeom::ConversionResult(
			entity_shape.ItemId(),
			new ifcopenshell::geometry::ManifoldShape(Part{ result.GetMeshGL64(), result }),
			entity_shape.StylePtr()));
	}
	return !cut_shapes.empty();
}
