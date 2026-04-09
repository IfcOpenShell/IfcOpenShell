#include "PassthroughConversionResult.h"

#include "../../../ifcgeom/IfcGeomRepresentation.h"

#include <Eigen/Dense>

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <numeric>
#include <sstream>
#include <unordered_map>

using namespace ifcopenshell::geometry;

namespace {
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

	struct EdgeKey {
		int a;
		int b;

		bool operator==(const EdgeKey& other) const {
			return a == other.a && b == other.b;
		}
	};

	struct EdgeKeyHash {
		size_t operator()(const EdgeKey& key) const {
			auto h = std::hash<int>()(key.a);
			h ^= std::hash<int>()(key.b) + 0x9e3779b97f4a7c15ull + (h << 6) + (h >> 2);
			return h;
		}
	};

	struct Box {
		bool valid = false;
		Eigen::Vector3d min = Eigen::Vector3d::Zero();
		Eigen::Vector3d max = Eigen::Vector3d::Zero();
	};

	struct MeshData {
		std::vector<Eigen::Vector3d> vertices;
		std::vector<std::array<int, 3>> triangles;
		std::unordered_map<EdgeKey, int, EdgeKeyHash> edge_counts;
		std::unordered_map<VertexKey, int, VertexKeyHash> vertex_map;
	};

	VertexKey make_vertex_key(const Eigen::Vector3d& p) {
		constexpr double scale = 1.e9;
		return {
			(long long)std::llround(p(0) * scale),
			(long long)std::llround(p(1) * scale),
			(long long)std::llround(p(2) * scale)
		};
	}

	EdgeKey make_edge_key(int a, int b) {
		return a < b ? EdgeKey{ a, b } : EdgeKey{ b, a };
	}

	Eigen::Matrix4d item_matrix(const taxonomy::geom_item::ptr& item) {
		if (item && item->matrix) {
			return item->matrix->ccomponents();
		}
		return Eigen::Matrix4d::Identity();
	}

	Eigen::Vector3d transform_point(const Eigen::Matrix4d& m, const Eigen::Vector3d& p) {
		Eigen::Vector4d v(p(0), p(1), p(2), 1.);
		return (m * v).head<3>();
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

	bool face_points(const taxonomy::face::ptr& face, std::vector<Eigen::Vector3d>& points) {
		if (!face || face->children.size() != 1) {
			return false;
		}
		const auto& loop = face->children.front();
		if (!loop || loop->children.size() < 3 || loop->children.size() > 4) {
			return false;
		}
		return loop_points(loop, points);
	}

	int add_vertex(MeshData& mesh, const Eigen::Vector3d& p) {
		auto key = make_vertex_key(p);
		auto it = mesh.vertex_map.find(key);
		if (it != mesh.vertex_map.end()) {
			return it->second;
		}
		auto idx = (int)mesh.vertices.size();
		mesh.vertices.push_back(p);
		mesh.vertex_map.insert({ key, idx });
		return idx;
	}

	void add_face(MeshData& mesh, const std::vector<int>& indices) {
		if (indices.size() == 3) {
			mesh.triangles.push_back({ indices[0], indices[1], indices[2] });
		} else if (indices.size() == 4) {
			mesh.triangles.push_back({ indices[0], indices[1], indices[2] });
			mesh.triangles.push_back({ indices[0], indices[2], indices[3] });
		}
		for (size_t i = 0; i < indices.size(); ++i) {
			mesh.edge_counts[make_edge_key(indices[i], indices[(i + 1) % indices.size()])]++;
		}
	}

	MeshData build_mesh(const std::vector<PassthroughPart>& parts, const taxonomy::matrix4* place = nullptr) {
		MeshData mesh;
		auto external = place ? place->ccomponents() : Eigen::Matrix4d::Identity();
		std::vector<Eigen::Vector3d> points;
		for (const auto& part : parts) {
			if (!part.shell) {
				continue;
			}
			auto part_matrix = part.matrix ? part.matrix->ccomponents() : Eigen::Matrix4d::Identity();
			for (const auto& face : part.shell->children) {
				if (!face_points(face, points)) {
					continue;
				}
				auto total = external * part_matrix * item_matrix(face) * item_matrix(face->children.front());
				std::vector<int> indices;
				indices.reserve(points.size());
				for (const auto& point : points) {
					indices.push_back(add_vertex(mesh, transform_point(total, point)));
				}
				add_face(mesh, indices);
			}
		}
		return mesh;
	}

	double triangle_area(const Eigen::Vector3d& a, const Eigen::Vector3d& b, const Eigen::Vector3d& c) {
		return 0.5 * ((b - a).cross(c - a)).norm();
	}

	double mesh_area(const MeshData& mesh) {
		double total = 0.;
		for (const auto& tri : mesh.triangles) {
			total += triangle_area(mesh.vertices[tri[0]], mesh.vertices[tri[1]], mesh.vertices[tri[2]]);
		}
		return total;
	}

	double mesh_volume(const MeshData& mesh) {
		double total = 0.;
		for (const auto& tri : mesh.triangles) {
			const auto& a = mesh.vertices[tri[0]];
			const auto& b = mesh.vertices[tri[1]];
			const auto& c = mesh.vertices[tri[2]];
			total += a.dot(b.cross(c));
		}
		return std::abs(total) / 6.;
	}

	double mesh_length(const MeshData& mesh) {
		double total = 0.;
		for (const auto& edge : mesh.edge_counts) {
			total += (mesh.vertices[edge.first.a] - mesh.vertices[edge.first.b]).norm();
		}
		return total;
	}

	void update_box(Box& box, const MeshData& mesh) {
		for (const auto& vertex : mesh.vertices) {
			if (!box.valid) {
				box.valid = true;
				box.min = vertex;
				box.max = vertex;
			} else {
				box.min = box.min.cwiseMin(vertex);
				box.max = box.max.cwiseMax(vertex);
			}
		}
	}

	double box_volume(const Box& box) {
		if (!box.valid) {
			return 0.;
		}
		auto size = box.max - box.min;
		return size(0) * size(1) * size(2);
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

	taxonomy::shell::ptr make_box_shell(const Eigen::Vector3d& min, const Eigen::Vector3d& max) {
		auto shell = taxonomy::make<taxonomy::shell>();
		shell->closed = true;
		const Eigen::Vector3d p000(min(0), min(1), min(2));
		const Eigen::Vector3d p100(max(0), min(1), min(2));
		const Eigen::Vector3d p110(max(0), max(1), min(2));
		const Eigen::Vector3d p010(min(0), max(1), min(2));
		const Eigen::Vector3d p001(min(0), min(1), max(2));
		const Eigen::Vector3d p101(max(0), min(1), max(2));
		const Eigen::Vector3d p111(max(0), max(1), max(2));
		const Eigen::Vector3d p011(min(0), max(1), max(2));
		shell->children.push_back(make_face({ p000, p010, p110, p100 }));
		shell->children.push_back(make_face({ p001, p101, p111, p011 }));
		shell->children.push_back(make_face({ p000, p100, p101, p001 }));
		shell->children.push_back(make_face({ p100, p110, p111, p101 }));
		shell->children.push_back(make_face({ p110, p010, p011, p111 }));
		shell->children.push_back(make_face({ p010, p000, p001, p011 }));
		return shell;
	}

	PassthroughPart normalize_part(const PassthroughPart& part) {
		return {
			part.shell,
			part.matrix ? taxonomy::make<taxonomy::matrix4>(part.matrix->ccomponents()) : taxonomy::make<taxonomy::matrix4>(),
			part.manifold
		};
	}

	std::vector<PassthroughPart> normalize_parts(const std::vector<PassthroughPart>& parts) {
		std::vector<PassthroughPart> result;
		result.reserve(parts.size());
		for (const auto& part : parts) {
			result.push_back(normalize_part(part));
		}
		return result;
	}
}

ifcopenshell::geometry::PassthroughShape::PassthroughShape(const PassthroughPart& part)
	: parts_{ normalize_part(part) } {}

ifcopenshell::geometry::PassthroughShape::PassthroughShape(PassthroughPart&& part)
	: parts_{ normalize_part(part) } {}

ifcopenshell::geometry::PassthroughShape::PassthroughShape(const std::vector<PassthroughPart>& parts)
	: parts_(normalize_parts(parts)) {}

ifcopenshell::geometry::PassthroughShape::PassthroughShape(std::vector<PassthroughPart>&& parts)
	: parts_(normalize_parts(parts)) {}

void ifcopenshell::geometry::PassthroughShape::Triangulate(ifcopenshell::geometry::Settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id) const {
	auto mesh = build_mesh(parts_, &place);
	std::vector<int> indices(mesh.vertices.size());
	for (size_t i = 0; i < mesh.vertices.size(); ++i) {
		indices[i] = t->addVertex(item_id, surface_style_id, mesh.vertices[i](0), mesh.vertices[i](1), mesh.vertices[i](2));
	}
	for (const auto& tri : mesh.triangles) {
		t->addFace(item_id, surface_style_id, indices[tri[0]], indices[tri[1]], indices[tri[2]]);
	}
	for (const auto& edge : mesh.edge_counts) {
		if (edge.second == 1) {
			t->registerEdge(item_id, indices[edge.first.a], indices[edge.first.b]);
		}
	}
}

void ifcopenshell::geometry::PassthroughShape::Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string& result) const {
	auto mesh = build_mesh(parts_, &place);
	std::stringstream stream;
	for (const auto& vertex : mesh.vertices) {
		stream << "v " << vertex(0) << " " << vertex(1) << " " << vertex(2) << "\n";
	}
	for (const auto& tri : mesh.triangles) {
		stream << "f " << tri[0] + 1 << " " << tri[1] + 1 << " " << tri[2] + 1 << "\n";
	}
	result = stream.str();
}

int ifcopenshell::geometry::PassthroughShape::surface_genus() const {
	return 0;
}

bool ifcopenshell::geometry::PassthroughShape::is_manifold() const {
	return std::all_of(parts_.begin(), parts_.end(), [](const auto& part) { return part.manifold; });
}

int ifcopenshell::geometry::PassthroughShape::num_vertices() const {
	return (int)build_mesh(parts_).vertices.size();
}

int ifcopenshell::geometry::PassthroughShape::num_edges() const {
	return (int)build_mesh(parts_).edge_counts.size();
}

int ifcopenshell::geometry::PassthroughShape::num_faces() const {
	return (int)build_mesh(parts_).triangles.size();
}

double ifcopenshell::geometry::PassthroughShape::bounding_box(void*& box_ptr) const {
	auto* box = static_cast<Box*>(box_ptr);
	if (!box) {
		box = new Box();
		box_ptr = box;
	} else {
		*box = Box();
	}
	update_box(*box, build_mesh(parts_));
	return box_volume(*box);
}

std::pair<IfcGeom::OpaqueCoordinate<3>, IfcGeom::OpaqueCoordinate<3>> ifcopenshell::geometry::PassthroughShape::bounding_box() const {
	void* box_ptr = nullptr;
	bounding_box(box_ptr);
	auto* box = static_cast<Box*>(box_ptr);
	if (!box || !box->valid) {
		delete box;
		throw std::runtime_error("Invalid shape");
	}
	auto result = std::make_pair(
		IfcGeom::OpaqueCoordinate<3>(
			new IfcGeom::NumberNativeDouble(box->min(0)),
			new IfcGeom::NumberNativeDouble(box->min(1)),
			new IfcGeom::NumberNativeDouble(box->min(2))),
		IfcGeom::OpaqueCoordinate<3>(
			new IfcGeom::NumberNativeDouble(box->max(0)),
			new IfcGeom::NumberNativeDouble(box->max(1)),
			new IfcGeom::NumberNativeDouble(box->max(2))));
	delete box;
	return result;
}

void ifcopenshell::geometry::PassthroughShape::set_box(void* box_ptr) {
	auto* box = static_cast<Box*>(box_ptr);
	if (!box || !box->valid) {
		throw std::runtime_error("Invalid shape");
	}
	parts_ = { { make_box_shell(box->min, box->max), taxonomy::make<taxonomy::matrix4>(), true } };
}

IfcGeom::OpaqueNumber* ifcopenshell::geometry::PassthroughShape::length() {
	return new IfcGeom::NumberNativeDouble(mesh_length(build_mesh(parts_)));
}

IfcGeom::OpaqueNumber* ifcopenshell::geometry::PassthroughShape::area() {
	return new IfcGeom::NumberNativeDouble(mesh_area(build_mesh(parts_)));
}

IfcGeom::OpaqueNumber* ifcopenshell::geometry::PassthroughShape::volume() {
	return new IfcGeom::NumberNativeDouble(is_manifold() ? mesh_volume(build_mesh(parts_)) : 0.);
}

IfcGeom::OpaqueCoordinate<3> ifcopenshell::geometry::PassthroughShape::position() {
	throw std::runtime_error("Invalid shape");
}

IfcGeom::OpaqueCoordinate<3> ifcopenshell::geometry::PassthroughShape::axis() {
	throw std::runtime_error("Invalid shape");
}

IfcGeom::OpaqueCoordinate<4> ifcopenshell::geometry::PassthroughShape::plane_equation() {
	throw std::runtime_error("Invalid shape");
}

std::vector<IfcGeom::ConversionResultShape*> ifcopenshell::geometry::PassthroughShape::convex_decomposition() {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::halfspaces() {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::box() {
	void* box_ptr = nullptr;
	bounding_box(box_ptr);
	auto* box = static_cast<Box*>(box_ptr);
	if (!box || !box->valid) {
		delete box;
		throw std::runtime_error("Invalid shape");
	}
	auto* result = new PassthroughShape(PassthroughPart{ make_box_shell(box->min, box->max), taxonomy::make<taxonomy::matrix4>(), true });
	delete box;
	return result;
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::solid() {
	if (!is_manifold()) {
		throw std::runtime_error("Invalid shape");
	}
	return new PassthroughShape(parts_);
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::wrap_in_compound() {
	return new PassthroughShape(parts_);
}

std::vector<IfcGeom::ConversionResultShape*> ifcopenshell::geometry::PassthroughShape::vertices() {
	throw std::runtime_error("Not implemented");
}

std::vector<IfcGeom::ConversionResultShape*> ifcopenshell::geometry::PassthroughShape::edges() {
	throw std::runtime_error("Not implemented");
}

std::vector<IfcGeom::ConversionResultShape*> ifcopenshell::geometry::PassthroughShape::facets() {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::add(IfcGeom::ConversionResultShape*) {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::subtract(IfcGeom::ConversionResultShape*) {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::intersect(IfcGeom::ConversionResultShape*) {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::concat(IfcGeom::ConversionResultShape* other) {
	auto* rhs = dynamic_cast<PassthroughShape*>(other);
	if (!rhs) {
		throw std::runtime_error("Invalid shape");
	}
	auto parts = parts_;
	parts.insert(parts.end(), rhs->parts_.begin(), rhs->parts_.end());
	return new PassthroughShape(std::move(parts));
}

void ifcopenshell::geometry::PassthroughShape::map(IfcGeom::OpaqueCoordinate<4>&, IfcGeom::OpaqueCoordinate<4>&) {
	throw std::runtime_error("Not implemented");
}

void ifcopenshell::geometry::PassthroughShape::map(const std::vector<IfcGeom::OpaqueCoordinate<4>>&, const std::vector<IfcGeom::OpaqueCoordinate<4>>&) {
	throw std::runtime_error("Not implemented");
}

IfcGeom::ConversionResultShape* ifcopenshell::geometry::PassthroughShape::moved(ifcopenshell::geometry::taxonomy::matrix4::ptr place) const {
	std::vector<PassthroughPart> moved_parts;
	moved_parts.reserve(parts_.size());
	for (const auto& part : parts_) {
		auto matrix = part.matrix ? taxonomy::make<taxonomy::matrix4>(place->ccomponents() * part.matrix->ccomponents()) : taxonomy::make<taxonomy::matrix4>(place->ccomponents());
		moved_parts.push_back({ part.shell, matrix, part.manifold });
	}
	return new PassthroughShape(std::move(moved_parts));
}

bool ifcopenshell::geometry::PassthroughShape::surface_area_along_direction(double, const ifcopenshell::geometry::taxonomy::matrix4::ptr& place, double& along_x, double& along_y, double& along_z) const {
	along_x = along_y = along_z = 0.;
	auto mesh = build_mesh(parts_, place.get());
	for (const auto& tri : mesh.triangles) {
		const auto& a = mesh.vertices[tri[0]];
		const auto& b = mesh.vertices[tri[1]];
		const auto& c = mesh.vertices[tri[2]];
		auto n = (b - a).cross(c - a);
		auto norm = n.norm();
		if (norm < 1.e-12) {
			continue;
		}
		auto tri_area = 0.5 * norm;
		n /= norm;
		along_x += tri_area * std::abs(n(0));
		along_y += tri_area * std::abs(n(1));
		along_z += tri_area * std::abs(n(2));
	}
	return true;
}
