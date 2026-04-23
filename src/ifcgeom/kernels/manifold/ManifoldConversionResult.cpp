#include "ManifoldConversionResult.h"

#include "../../../ifcgeom/IfcGeomRepresentation.h"

#include <Eigen/Dense>

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <unordered_map>

using IfcGeom::ConversionResultShape;
using IfcGeom::NumberNativeDouble;
using IfcGeom::OpaqueCoordinate;
using IfcGeom::OpaqueNumber;

namespace {
	using Mesh = manifold::MeshGL64;

	Mesh transform_mesh(const Mesh& mesh, const ifcopenshell::geometry::taxonomy::matrix4& place) {
		Mesh result = mesh;
		const auto& m = place.ccomponents();
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

	std::optional<manifold::Manifold> make_manifold(const Mesh& mesh) {
		manifold::Manifold solid(mesh);
		if (solid.Status() == manifold::Manifold::Error::NoError) {
			return solid;
		}
		return std::nullopt;
	}

	manifold::Box mesh_bbox(const Mesh& mesh) {
		if (!mesh.NumVert()) {
			return {};
		}
		manifold::Box box(
			manifold::vec3(
				mesh.vertProperties[0],
				mesh.vertProperties[1],
				mesh.vertProperties[2]),
			manifold::vec3(
				mesh.vertProperties[0],
				mesh.vertProperties[1],
				mesh.vertProperties[2]));
		for (size_t i = 1; i < mesh.NumVert(); ++i) {
			box.Union(manifold::vec3(
				mesh.vertProperties[i * mesh.numProp + 0],
				mesh.vertProperties[i * mesh.numProp + 1],
				mesh.vertProperties[i * mesh.numProp + 2]));
		}
		return box;
	}

	double bbox_volume(const manifold::Box& box) {
		if (!box.IsFinite()) {
			return 0.;
		}
		const auto size = box.Size();
		return size[0] * size[1] * size[2];
	}

	double triangle_area(const Mesh& mesh, size_t tri) {
		auto idx = [&](int corner) { return mesh.triVerts[tri * 3 + corner]; };
		auto point = [&](uint32_t i) {
			return Eigen::Vector3d(
				mesh.vertProperties[i * mesh.numProp + 0],
				mesh.vertProperties[i * mesh.numProp + 1],
				mesh.vertProperties[i * mesh.numProp + 2]);
		};
		const auto a = point(idx(0));
		const auto b = point(idx(1));
		const auto c = point(idx(2));
		return 0.5 * ((b - a).cross(c - a)).norm();
	}

	double mesh_area(const Mesh& mesh) {
		double area = 0.;
		for (size_t i = 0; i < mesh.NumTri(); ++i) {
			area += triangle_area(mesh, i);
		}
		return area;
	}

	double mesh_volume(const Mesh& mesh) {
		double volume = 0.;
		for (size_t i = 0; i < mesh.NumTri(); ++i) {
			auto idx = [&](int corner) { return mesh.triVerts[i * 3 + corner]; };
			auto point = [&](uint32_t v) {
				return Eigen::Vector3d(
					mesh.vertProperties[v * mesh.numProp + 0],
					mesh.vertProperties[v * mesh.numProp + 1],
					mesh.vertProperties[v * mesh.numProp + 2]);
			};
			const auto a = point(idx(0));
			const auto b = point(idx(1));
			const auto c = point(idx(2));
			volume += a.dot(b.cross(c)) / 6.;
		}
		return std::abs(volume);
	}

	struct EdgeHash {
		size_t operator()(const std::pair<uint32_t, uint32_t>& edge) const {
			return std::hash<uint64_t>()((uint64_t(edge.first) << 32) ^ uint64_t(edge.second));
		}
	};

	std::unordered_map<std::pair<uint32_t, uint32_t>, int, EdgeHash> count_edges(const Mesh& mesh) {
		std::unordered_map<std::pair<uint32_t, uint32_t>, int, EdgeHash> edges;
		for (size_t i = 0; i < mesh.NumTri(); ++i) {
			uint32_t tri[3] = {
				mesh.triVerts[i * 3 + 0],
				mesh.triVerts[i * 3 + 1],
				mesh.triVerts[i * 3 + 2]
			};
			for (int j = 0; j < 3; ++j) {
				auto a = tri[j];
				auto b = tri[(j + 1) % 3];
				if (a > b) {
					std::swap(a, b);
				}
				edges[{a, b}]++;
			}
		}
		return edges;
	}

	double mesh_length(const Mesh& mesh) {
		double length = 0.;
		auto edges = count_edges(mesh);
		for (const auto& pair : edges) {
			const auto a = pair.first.first;
			const auto b = pair.first.second;
			Eigen::Vector3d p(
				mesh.vertProperties[a * mesh.numProp + 0],
				mesh.vertProperties[a * mesh.numProp + 1],
				mesh.vertProperties[a * mesh.numProp + 2]);
			Eigen::Vector3d q(
				mesh.vertProperties[b * mesh.numProp + 0],
				mesh.vertProperties[b * mesh.numProp + 1],
				mesh.vertProperties[b * mesh.numProp + 2]);
			length += (q - p).norm();
		}
		return length;
	}

	int mesh_edges(const Mesh& mesh) {
		return (int)count_edges(mesh).size();
	}

	ifcopenshell::geometry::ManifoldPart make_part(const manifold::Manifold& solid) {
		return { solid.GetMeshGL64(), solid };
	}

	ifcopenshell::geometry::ManifoldPart make_box_part(const manifold::Box& box) {
		const auto size = box.Size();
		auto solid = manifold::Manifold::Cube(manifold::vec3(size[0], size[1], size[2]), false).Translate(box.min);
		return make_part(solid);
	}
}

ifcopenshell::geometry::ManifoldShape::ManifoldShape(const ManifoldPart& part)
	: parts_{ part } {}

ifcopenshell::geometry::ManifoldShape::ManifoldShape(ManifoldPart&& part)
	: parts_{ std::move(part) } {}

ifcopenshell::geometry::ManifoldShape::ManifoldShape(const std::vector<ManifoldPart>& parts)
	: parts_(parts) {}

ifcopenshell::geometry::ManifoldShape::ManifoldShape(std::vector<ManifoldPart>&& parts)
	: parts_(std::move(parts)) {}

std::optional<manifold::Manifold> ifcopenshell::geometry::ManifoldShape::as_manifold() const {
	if (parts_.empty()) {
		return std::nullopt;
	}
	std::vector<manifold::Manifold> solids;
	solids.reserve(parts_.size());
	for (const auto& part : parts_) {
		if (!part.solid) {
			return std::nullopt;
		}
		solids.push_back(*part.solid);
	}
	if (solids.size() == 1) {
		return solids.front();
	}
	return manifold::Manifold::BatchBoolean(solids, manifold::OpType::Add);
}

void ifcopenshell::geometry::ManifoldShape::Triangulate(ifcopenshell::geometry::Settings, const ifcopenshell::geometry::taxonomy::matrix4& place, IfcGeom::Representation::Triangulation* t, int item_id, int surface_style_id) const {
	for (const auto& part : parts_) {
		auto mesh = transform_mesh(part.mesh, place);
		std::vector<int> indices(mesh.NumVert());
		for (size_t i = 0; i < mesh.NumVert(); ++i) {
			indices[i] = t->addVertex(
				item_id,
				surface_style_id,
				mesh.vertProperties[i * mesh.numProp + 0],
				mesh.vertProperties[i * mesh.numProp + 1],
				mesh.vertProperties[i * mesh.numProp + 2]);
		}
		auto edges = count_edges(mesh);
		for (size_t i = 0; i < mesh.NumTri(); ++i) {
			t->addFace(
				item_id,
				surface_style_id,
				indices[mesh.triVerts[i * 3 + 0]],
				indices[mesh.triVerts[i * 3 + 1]],
				indices[mesh.triVerts[i * 3 + 2]]);
		}
		for (const auto& edge : edges) {
			if (edge.second == 1) {
				t->registerEdge(item_id, indices[edge.first.first], indices[edge.first.second]);
			}
		}
	}
}

void ifcopenshell::geometry::ManifoldShape::Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string& result) const {
	std::stringstream stream;
	stream << std::setprecision(17);
	size_t offset = 0;
	for (const auto& part : parts_) {
		auto mesh = transform_mesh(part.mesh, place);
		for (size_t i = 0; i < mesh.NumVert(); ++i) {
			stream << "v "
				<< mesh.vertProperties[i * mesh.numProp + 0] << " "
				<< mesh.vertProperties[i * mesh.numProp + 1] << " "
				<< mesh.vertProperties[i * mesh.numProp + 2] << "\n";
		}
		for (size_t i = 0; i < mesh.NumTri(); ++i) {
			stream << "f "
				<< mesh.triVerts[i * 3 + 0] + 1 + offset << " "
				<< mesh.triVerts[i * 3 + 1] + 1 + offset << " "
				<< mesh.triVerts[i * 3 + 2] + 1 + offset << "\n";
		}
		offset += mesh.NumVert();
	}
	result = stream.str();
}

int ifcopenshell::geometry::ManifoldShape::surface_genus() const {
	int genus = 0;
	for (const auto& part : parts_) {
		if (!part.solid) {
			return 0;
		}
		genus += part.solid->Genus();
	}
	return genus;
}

bool ifcopenshell::geometry::ManifoldShape::is_manifold() const {
	return std::all_of(parts_.begin(), parts_.end(), [](const auto& part) { return part.solid.has_value(); });
}

int ifcopenshell::geometry::ManifoldShape::num_vertices() const {
	size_t total = 0;
	for (const auto& part : parts_) {
		total += part.mesh.NumVert();
	}
	return (int)total;
}

int ifcopenshell::geometry::ManifoldShape::num_edges() const {
	int total = 0;
	for (const auto& part : parts_) {
		total += part.solid ? (int)part.solid->NumEdge() : mesh_edges(part.mesh);
	}
	return total;
}

int ifcopenshell::geometry::ManifoldShape::num_faces() const {
	size_t total = 0;
	for (const auto& part : parts_) {
		total += part.solid ? part.solid->NumTri() : part.mesh.NumTri();
	}
	return (int)total;
}

double ifcopenshell::geometry::ManifoldShape::bounding_box(void*& box_ptr) const {
	bool initialized = false;
	auto* box = static_cast<manifold::Box*>(box_ptr);
	if (!box) {
		box = new manifold::Box();
		box_ptr = box;
	}
	for (const auto& part : parts_) {
		auto bbox = part.solid ? part.solid->BoundingBox() : mesh_bbox(part.mesh);
		if (!bbox.IsFinite()) {
			continue;
		}
		if (!initialized) {
			*box = bbox;
			initialized = true;
		} else {
			box->Union(bbox.min);
			box->Union(bbox.max);
		}
	}
	return initialized ? bbox_volume(*box) : 0.;
}

std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> ifcopenshell::geometry::ManifoldShape::bounding_box() const {
	void* box_ptr = nullptr;
	bounding_box(box_ptr);
	auto* box = static_cast<manifold::Box*>(box_ptr);
	if (!box || !box->IsFinite()) {
		delete box;
		throw std::runtime_error("Invalid shape");
	}
	auto result = std::make_pair(
		OpaqueCoordinate<3>(
			new NumberNativeDouble(box->min[0]),
			new NumberNativeDouble(box->min[1]),
			new NumberNativeDouble(box->min[2])),
		OpaqueCoordinate<3>(
			new NumberNativeDouble(box->max[0]),
			new NumberNativeDouble(box->max[1]),
			new NumberNativeDouble(box->max[2])));
	delete box;
	return result;
}

void ifcopenshell::geometry::ManifoldShape::set_box(void* box_ptr) {
	auto* box = static_cast<manifold::Box*>(box_ptr);
	if (!box || !box->IsFinite()) {
		throw std::runtime_error("Invalid shape");
	}
	parts_ = { make_box_part(*box) };
}

OpaqueNumber* ifcopenshell::geometry::ManifoldShape::length() {
	double total = 0.;
	for (const auto& part : parts_) {
		total += mesh_length(part.mesh);
	}
	return new NumberNativeDouble(total);
}

OpaqueNumber* ifcopenshell::geometry::ManifoldShape::area() {
	double total = 0.;
	for (const auto& part : parts_) {
		total += part.solid ? part.solid->SurfaceArea() : mesh_area(part.mesh);
	}
	return new NumberNativeDouble(total);
}

OpaqueNumber* ifcopenshell::geometry::ManifoldShape::volume() {
	double total = 0.;
	for (const auto& part : parts_) {
		total += part.solid ? part.solid->Volume() : mesh_volume(part.mesh);
	}
	return new NumberNativeDouble(total);
}

OpaqueCoordinate<3> ifcopenshell::geometry::ManifoldShape::position() {
	throw std::runtime_error("Invalid shape");
}

OpaqueCoordinate<3> ifcopenshell::geometry::ManifoldShape::axis() {
	throw std::runtime_error("Invalid shape");
}

OpaqueCoordinate<4> ifcopenshell::geometry::ManifoldShape::plane_equation() {
	throw std::runtime_error("Invalid shape");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::ManifoldShape::convex_decomposition() {
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::halfspaces() {
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::box() {
	void* box_ptr = nullptr;
	bounding_box(box_ptr);
	auto* box = static_cast<manifold::Box*>(box_ptr);
	if (!box || !box->IsFinite()) {
		delete box;
		throw std::runtime_error("Invalid shape");
	}
	auto* result = new ManifoldShape(make_box_part(*box));
	delete box;
	return result;
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::solid() {
	if (!is_manifold()) {
		throw std::runtime_error("Invalid shape");
	}
	return new ManifoldShape(parts_);
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::wrap_in_compound() {
	return new ManifoldShape(parts_);
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::ManifoldShape::vertices() {
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::ManifoldShape::edges() {
	throw std::runtime_error("Not implemented");
}

std::vector<ConversionResultShape*> ifcopenshell::geometry::ManifoldShape::facets() {
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::add(ConversionResultShape* other) {
	auto* rhs = dynamic_cast<ManifoldShape*>(other);
	if (!rhs) {
		throw std::runtime_error("Invalid shape");
	}
	auto a = as_manifold();
	auto b = rhs->as_manifold();
	if (!a || !b) {
		throw std::runtime_error("Invalid shape");
	}
	return new ManifoldShape(make_part(*a + *b));
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::subtract(ConversionResultShape* other) {
	auto* rhs = dynamic_cast<ManifoldShape*>(other);
	if (!rhs) {
		throw std::runtime_error("Invalid shape");
	}
	auto a = as_manifold();
	auto b = rhs->as_manifold();
	if (!a || !b) {
		throw std::runtime_error("Invalid shape");
	}
	return new ManifoldShape(make_part(*a - *b));
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::intersect(ConversionResultShape* other) {
	auto* rhs = dynamic_cast<ManifoldShape*>(other);
	if (!rhs) {
		throw std::runtime_error("Invalid shape");
	}
	auto a = as_manifold();
	auto b = rhs->as_manifold();
	if (!a || !b) {
		throw std::runtime_error("Invalid shape");
	}
	return new ManifoldShape(make_part(*a ^ *b));
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::concat(ConversionResultShape* other) {
	auto* rhs = dynamic_cast<ManifoldShape*>(other);
	if (!rhs) {
		throw std::runtime_error("Invalid shape");
	}
	auto parts = parts_;
	parts.insert(parts.end(), rhs->parts_.begin(), rhs->parts_.end());
	return new ManifoldShape(std::move(parts));
}

void ifcopenshell::geometry::ManifoldShape::map(OpaqueCoordinate<4>&, OpaqueCoordinate<4>&) {
	throw std::runtime_error("Not implemented");
}

void ifcopenshell::geometry::ManifoldShape::map(const std::vector<OpaqueCoordinate<4>>&, const std::vector<OpaqueCoordinate<4>>&) {
	throw std::runtime_error("Not implemented");
}

ConversionResultShape* ifcopenshell::geometry::ManifoldShape::moved(ifcopenshell::geometry::taxonomy::matrix4::ptr place) const {
	std::vector<ManifoldPart> moved_parts;
	moved_parts.reserve(parts_.size());
	for (const auto& part : parts_) {
		auto mesh = transform_mesh(part.mesh, *place);
		auto solid = part.solid ? make_manifold(mesh) : std::nullopt;
		if (part.solid && !solid) {
			throw std::runtime_error("Failed to transform shape");
		}
		moved_parts.push_back({ std::move(mesh), std::move(solid) });
	}
	return new ManifoldShape(std::move(moved_parts));
}

bool ifcopenshell::geometry::ManifoldShape::surface_area_along_direction(double, const ifcopenshell::geometry::taxonomy::matrix4::ptr& place, double& along_x, double& along_y, double& along_z) const {
	along_x = along_y = along_z = 0.;
	for (const auto& part : parts_) {
		auto mesh = transform_mesh(part.mesh, *place);
		for (size_t i = 0; i < mesh.NumTri(); ++i) {
			auto point = [&](uint32_t v) {
				return Eigen::Vector3d(
					mesh.vertProperties[v * mesh.numProp + 0],
					mesh.vertProperties[v * mesh.numProp + 1],
					mesh.vertProperties[v * mesh.numProp + 2]);
			};
			const auto a = point(mesh.triVerts[i * 3 + 0]);
			const auto b = point(mesh.triVerts[i * 3 + 1]);
			const auto c = point(mesh.triVerts[i * 3 + 2]);
			auto n = (b - a).cross(c - a);
			const auto norm = n.norm();
			if (norm < 1.e-12) {
				continue;
			}
			const auto area = 0.5 * norm;
			n /= norm;
			along_x += area * std::abs(n(0));
			along_y += area * std::abs(n(1));
			along_z += area * std::abs(n(2));
		}
	}
	return true;
}
