/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "smlib_conversion_result.h"
#include "smlib_utils.h"

#include "../../../ifcgeom/representation.h"
#include "../../../ifcparse/logger.h"

#include <SmApiBrep.h>
#include <SmApiGeneral.h>
#include <SmApiPolygons.h>
#include <SmApiPrimitives.h>
#include <SmApiQueries.h>

#include <SmBrep.h>
#include <SmPointClass.h>
#include <SmPoly.h>

#include <algorithm>
#include <cmath>
#include <iomanip>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

using namespace ifcopenshell::geom;

namespace {
	inline Eigen::Vector3d to_eigen(const SmPoint3d& p) {
		return Eigen::Vector3d(p.x, p.y, p.z);
	}

	/// The vertices of a poly face's outer loop, in loop order.
	std::vector<SmPolyVertex*> polygon_vertices(SmPolyFace* face) {
		std::vector<SmPolyVertex*> result;
		SmPolyLoop* loop = face->GetOuterPolyLoop();
		if (!loop) {
			return result;
		}
		SmTArray<SmPolyEdge*> edges;
		loop->GetPolyEdges(edges);
		result.reserve(edges.GetSize());
		for (ULONG i = 0; i < edges.GetSize(); ++i) {
			SmPolyVertex* vertex = edges[i]->GetStartPolyVertex();
			if (vertex) {
				result.push_back(vertex);
			}
		}
		return result;
	}

	/// Area weighted, per polygon normal.
	Eigen::Vector3d polygon_normal(const std::vector<SmPolyVertex*>& loop) {
		Eigen::Vector3d sum = Eigen::Vector3d::Zero();
		if (loop.size() < 3) {
			return sum;
		}
		const Eigen::Vector3d a = to_eigen(loop[0]->GetPoint());
		for (size_t i = 1; i + 1 < loop.size(); ++i) {
			const Eigen::Vector3d b = to_eigen(loop[i]->GetPoint());
			const Eigen::Vector3d c = to_eigen(loop[i + 1]->GetPoint());
			sum += (b - a).cross(c - a);
		}
		return sum;
	}

	Eigen::Matrix3d scale_of(const Eigen::Matrix4d& matrix) {
		return matrix.block<3, 3>(0, 0);
	}

	/// The normal of the surface of a poly face at a vertex of the tessellation,
	/// which the tessellation records for every face a vertex is used by. The
	/// faces the tessellation records are the faces of the brep when it has been
	/// converted from the tessellation.
	Eigen::Vector3d surface_normal(SmPolyVertex* vertex, const SmPolyFace* face) {
		SmTArray<SmVector3d>& normals = vertex->GetNormalsRef();
		SmTArray<SmTopology*>& faces = vertex->GetFacesRef();
		const SmTopology* const original = face->GetOriginalFace();
		const ULONG n = (ULONG)(std::min)((size_t)normals.GetSize(), (size_t)faces.GetSize());
		for (ULONG i = 0; i < n; ++i) {
			if (faces[i] == face || (original && faces[i] == original)) {
				return Eigen::Vector3d(normals[i].x, normals[i].y, normals[i].z);
			}
		}
		return Eigen::Vector3d::Zero();
	}
}

smlib_shape::smlib_shape(SmBrep* brep)
	: brep_(brep), solid_(true) {
}

smlib_shape::smlib_shape(const smlib_shape& other)
	: conversion_result_shape(other), brep_(nullptr), solid_(other.solid_) {
	if (other.brep_) {
		SmBrep* copy = nullptr;
		if (SmApiBrepCopy(other.brep_, copy) == SM_SUCCESS) {
			brep_ = copy;
		}
	}
}

smlib_shape& smlib_shape::operator=(const smlib_shape& other) {
	if (this == &other) {
		return *this;
	}
	smlib_shape tmp(other);
	std::swap(brep_, tmp.brep_);
	std::swap(solid_, tmp.solid_);
	return *this;
}

smlib_shape::~smlib_shape() {
	delete brep_;
}

void smlib_shape::triangulate(settings settings, const taxonomy::matrix4& place, triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger) const {
	if (!brep_) {
		return;
	}
	smlib_ensure_context();

	SmPolyBrep* poly = nullptr;
	SmTessellationReport report;
	const SmTessellationParams params = smlib_tessellation_params(settings);
	const SmApiStatus status = SmApiTessellate(brep_, poly, params, TRUE, nullptr, &report);
	if (status != SM_SUCCESS || !poly) {
		logger.warning("SMLib kernel: failed to tessellate shape (" + std::to_string(status) + ")");
		delete poly;
		return;
	}
	if (report.failures.GetSize()) {
		logger.warning("SMLib kernel: " + std::to_string(report.failures.GetSize()) + " face(s) failed to tessellate");
	}

	const Eigen::Matrix4d transform = place.ccomponents();
	const bool flipped = scale_of(transform).determinant() < 0.;
	// As in the other kernels, normals are only calculated when vertices are
	// not welded, because welding by position merges the vertices of distinct
	// faces, which would smooth the edges between them.
	const bool emit_normals =
		!settings.get<settings::WeldVertices>().get() && !settings.get<settings::DontEmitNormals>().get();

	SmTArray<SmPolyVertex*> vertices;
	SmTArray<SmPolyFace*> faces;
	poly->GetPolyVertices(vertices);
	poly->GetPolyFaces(faces);

	std::vector<std::vector<SmPolyVertex*>> loops;
	// The face each polygon belongs to, which is the polygon itself except for
	// the triangles SMLib creates for a face with inner loops.
	std::vector<SmPolyFace*> loop_faces;
	loops.reserve((size_t)faces.GetSize());
	for (ULONG i = 0; i < faces.GetSize(); ++i) {
		SmTArray<SmPolyLoop*> poly_loops;
		faces[i]->GetPolyLoops(poly_loops);
		if (poly_loops.GetSize() > 1) {
			// A tessellated face that has not been split into triangles yet
			// carries its inner loops, which SMLib triangulates for us.
			SmTArray<SmPolyFace*> triangles;
			if (faces[i]->TriangulatePlanar(triangles) == SM_SUCCESS) {
				for (ULONG j = 0; j < triangles.GetSize(); ++j) {
					loops.push_back(polygon_vertices(triangles[j]));
					loop_faces.push_back(faces[i]);
				}
				continue;
			}
		}
		loops.push_back(polygon_vertices(faces[i]));
		loop_faces.push_back(faces[i]);
	}

	std::vector<Eigen::Vector3d> normals;
	if (emit_normals) {
		normals.reserve(loops.size());
		for (size_t i = 0; i < loops.size(); ++i) {
			normals.push_back(polygon_normal(loops[i]));
		}
	}

	const Eigen::Matrix3d linear = scale_of(transform);
	// A transform that mirrors reverses the winding of the polygons, so that
	// the normals that agree with it point the other way.
	const double mirror = flipped ? -1. : 1.;
	const auto emit_vertex = [&](const SmPolyVertex* vertex) {
		const Eigen::Vector3d p = to_eigen(vertex->GetPoint());
		const Eigen::Vector4d p2 = transform * Eigen::Vector4d(p(0), p(1), p(2), 1.);
		return t->addVertex(item_id, surface_style_id, p2(0), p2(1), p2(2));
	};

	std::vector<std::vector<int>> indices;
	indices.reserve(loops.size());
	if (emit_normals) {
		// Each polygon emits its own vertices, so that every one of them carries
		// the normal of the surface its polygon belongs to, rather than a normal
		// averaged over the polygons that happen to meet in the vertex.
		for (size_t i = 0; i < loops.size(); ++i) {
			std::vector<int> loop;
			loop.reserve(loops[i].size());
			for (auto* vertex : loops[i]) {
				loop.push_back(emit_vertex(vertex));
				Eigen::Vector3d n = surface_normal(vertex, loop_faces[i]);
				if (n.norm() <= 1.e-12) {
					// SMLib has no normal for the vertex, which happens for the
					// triangles it creates for a planar face with inner loops.
					n = normals[i];
				} else if (n.dot(normals[i]) < 0.) {
					// The normal of the surface has been recorded, the sense of
					// the polygon decides which of its two sides faces out.
					n = -n;
				}
				n = linear * (mirror * n);
				if (n.norm() > 1.e-12) {
					n.normalize();
				}
				t->addNormal(n(0), n(1), n(2));
			}
			indices.push_back(std::move(loop));
		}
	} else {
		std::map<const SmPolyVertex*, int> emitted;
		for (ULONG i = 0; i < vertices.GetSize(); ++i) {
			emitted[vertices[i]] = emit_vertex(vertices[i]);
		}
		for (const auto& loop : loops) {
			std::vector<int> ordered;
			ordered.reserve(loop.size());
			for (const auto* vertex : loop) {
				const auto it = emitted.find(vertex);
				ordered.push_back(it == emitted.end() ? -1 : it->second);
			}
			indices.push_back(std::move(ordered));
		}
	}

	for (auto& loop : indices) {
		// A loop that refers to a vertex that was not emitted is skipped rather
		// than emitted with invalid indices.
		if (loop.size() < 3 || std::any_of(loop.begin(), loop.end(), [](int index) { return index < 0; })) {
			continue;
		}
		if (flipped) {
			std::reverse(loop.begin(), loop.end());
		}
		for (size_t i = 1; i + 1 < loop.size(); ++i) {
			t->addFace(item_id, surface_style_id, loop[0], loop[i], loop[i + 1]);
		}
	}

	delete poly;
}

void smlib_shape::serialize(const taxonomy::matrix4& place, std::string& result) const {
	result.clear();
	if (!brep_) {
		return;
	}
	smlib_ensure_context();

	SmPolyBrep* poly = nullptr;
	SmTessellationReport report;
	SmTessellationParams params;
	if (SmApiTessellate(brep_, poly, params, TRUE, nullptr, &report) != SM_SUCCESS || !poly) {
		delete poly;
		return;
	}

	const Eigen::Matrix4d transform = place.ccomponents();

	SmTArray<SmPolyVertex*> vertices;
	SmTArray<SmPolyFace*> faces;
	poly->GetPolyVertices(vertices);
	poly->GetPolyFaces(faces);

	std::stringstream stream;
	stream << std::setprecision(17);
	for (ULONG i = 0; i < vertices.GetSize(); ++i) {
		const Eigen::Vector3d p = to_eigen(vertices[i]->GetPoint());
		const Eigen::Vector4d p2 = transform * Eigen::Vector4d(p(0), p(1), p(2), 1.);
		stream << "v " << p2(0) << " " << p2(1) << " " << p2(2) << "\n";
	}
	for (ULONG i = 0; i < faces.GetSize(); ++i) {
		const auto loop = polygon_vertices(faces[i]);
		if (loop.size() < 3) {
			continue;
		}
		stream << "f";
		for (const auto* vertex : loop) {
			for (ULONG j = 0; j < vertices.GetSize(); ++j) {
				if (vertices[j] == vertex) {
					stream << " " << j + 1;
					break;
				}
			}
		}
		stream << "\n";
	}
	result = stream.str();

	delete poly;
}

int smlib_shape::surface_genus() const {
	return 0;
}

bool smlib_shape::is_manifold() const {
	if (!brep_) {
		return false;
	}
	SmBoolean manifold_solid = FALSE;
	if (SmApiBrepIsManifoldSolid(brep_, manifold_solid) != SM_SUCCESS) {
		return solid_;
	}
	return manifold_solid != FALSE;
}

int smlib_shape::num_vertices() const {
	return brep_ ? (int)brep_->GetNumVertices() : 0;
}

int smlib_shape::num_edges() const {
	return brep_ ? (int)brep_->GetNumEdges() : 0;
}

int smlib_shape::num_faces() const {
	return brep_ ? (int)brep_->GetNumFaces() : 0;
}

double smlib_shape::bounding_box(void*& box_ptr) const {
	auto* box = static_cast<smlib_box*>(box_ptr);
	if (!box) {
		box = new smlib_box();
		box_ptr = box;
	}
	box->valid = false;
	if (!brep_) {
		return 0.;
	}
	smlib_ensure_context();
	SmPoint3d min, max;
	if (SmApiBrepBoundingBox(brep_, TRUE, min, max) != SM_SUCCESS) {
		return 0.;
	}
	box->min[0] = min.x;
	box->min[1] = min.y;
	box->min[2] = min.z;
	box->max[0] = max.x;
	box->max[1] = max.y;
	box->max[2] = max.z;
	box->valid = true;
	return (box->max[0] - box->min[0]) * (box->max[1] - box->min[1]) * (box->max[2] - box->min[2]);
}

std::pair<opaque_coordinate<3>, opaque_coordinate<3>> smlib_shape::bounding_box() const {
	void* box_ptr = nullptr;
	bounding_box(box_ptr);
	auto* box = static_cast<smlib_box*>(box_ptr);
	if (!box || !box->valid) {
		delete box;
		throw std::runtime_error("Invalid shape");
	}
	auto result = std::make_pair(
		opaque_coordinate<3>(opaque_number(box->min[0]), opaque_number(box->min[1]), opaque_number(box->min[2])),
		opaque_coordinate<3>(opaque_number(box->max[0]), opaque_number(box->max[1]), opaque_number(box->max[2])));
	delete box;
	return result;
}

void smlib_shape::set_box(void* box_ptr) {
	auto* box = static_cast<smlib_box*>(box_ptr);
	if (!box || !box->valid) {
		throw std::runtime_error("Invalid shape");
	}
	smlib_ensure_context();
	SmBrep* brep = nullptr;
	if (SmApiCreateBox(
			SmPoint3d(box->min[0], box->min[1], box->min[2]),
			box->max[0] - box->min[0],
			box->max[1] - box->min[1],
			box->max[2] - box->min[2],
			brep) != SM_SUCCESS) {
		throw std::runtime_error("Invalid shape");
	}
	delete brep_;
	brep_ = brep;
	solid_ = true;
}

opaque_number smlib_shape::length() {
	if (!brep_) {
		throw std::runtime_error("Invalid shape");
	}
	smlib_ensure_context();
	SmPolyBrep* poly = nullptr;
	SmTessellationReport report;
	SmTessellationParams params;
	if (SmApiTessellate(brep_, poly, params, TRUE, nullptr, &report) != SM_SUCCESS || !poly) {
		delete poly;
		throw std::runtime_error("Invalid shape");
	}
	SmTArray<SmPolyFace*> faces;
	poly->GetPolyFaces(faces);
	double total = 0.;
	std::map<std::pair<SmPolyVertex*, SmPolyVertex*>, int> seen;
	for (ULONG i = 0; i < faces.GetSize(); ++i) {
		const auto loop = polygon_vertices(faces[i]);
		for (size_t j = 0; j < loop.size(); ++j) {
			SmPolyVertex* a = loop[j];
			SmPolyVertex* b = loop[(j + 1) % loop.size()];
			if (a == b || seen[{ std::min(a, b), std::max(a, b) }]++ > 0) {
				continue;
			}
			total += (to_eigen(a->GetPoint()) - to_eigen(b->GetPoint())).norm();
		}
	}
	delete poly;
	return opaque_number(total);
}

opaque_number smlib_shape::area() {
	if (!brep_) {
		throw std::runtime_error("Invalid shape");
	}
	smlib_ensure_context();
	double value = 0.;
	if (SmApiBrepComputeArea(brep_, 1.e-3, value) == SM_SUCCESS && value > 0.) {
		return opaque_number(value);
	}

	SmPolyBrep* poly = nullptr;
	SmTessellationReport report;
	SmTessellationParams params;
	if (SmApiTessellate(brep_, poly, params, TRUE, nullptr, &report) != SM_SUCCESS || !poly) {
		delete poly;
		throw std::runtime_error("Invalid shape");
	}
	value = 0.;
	SmTArray<SmPolyFace*> faces;
	poly->GetPolyFaces(faces);
	for (ULONG i = 0; i < faces.GetSize(); ++i) {
		value += polygon_normal(polygon_vertices(faces[i])).norm() / 2.;
	}
	delete poly;
	return opaque_number(value);
}

opaque_number smlib_shape::volume() {
	if (!brep_) {
		throw std::runtime_error("Invalid shape");
	}
	smlib_ensure_context();
	double value = 0.;
	if (SmApiBrepComputeVolume(brep_, 1.e-3, value) == SM_SUCCESS && std::abs(value) > 1.e-9) {
		return opaque_number(std::abs(value));
	}

	// The exact integration fails on shapes that were assembled from faces;
	// fall back to the volume of the tessellation.
	SmPolyBrep* poly = nullptr;
	SmTessellationReport report;
	SmTessellationParams params;
	if (SmApiTessellate(brep_, poly, params, TRUE, nullptr, &report) != SM_SUCCESS || !poly) {
		delete poly;
		throw std::runtime_error("Invalid shape");
	}
	value = 0.;
	if (SmApiPolyBrepComputeVolume(poly, value) != SM_SUCCESS) {
		delete poly;
		throw std::runtime_error("Invalid shape");
	}
	delete poly;
	return opaque_number(std::abs(value));
}

opaque_coordinate<3> smlib_shape::position() {
	throw std::runtime_error("Invalid shape");
}

opaque_coordinate<3> smlib_shape::axis() {
	throw std::runtime_error("Invalid shape");
}

opaque_coordinate<4> smlib_shape::plane_equation() {
	throw std::runtime_error("Invalid shape");
}

std::vector<conversion_result_shape*> smlib_shape::convex_decomposition() {
	throw std::runtime_error("Not implemented");
}

conversion_result_shape* smlib_shape::halfspaces() {
	throw std::runtime_error("Not implemented");
}

conversion_result_shape* smlib_shape::box() {
	void* box_ptr = nullptr;
	bounding_box(box_ptr);
	auto* box = static_cast<smlib_box*>(box_ptr);
	if (!box || !box->valid) {
		delete box;
		throw std::runtime_error("Invalid shape");
	}
	auto* result = new smlib_shape();
	result->set_box(box);
	delete box;
	return result;
}

conversion_result_shape* smlib_shape::solid() {
	return new smlib_shape(*this);
}

conversion_result_shape* smlib_shape::wrap_in_compound() {
	return new smlib_shape(*this);
}

std::vector<conversion_result_shape*> smlib_shape::vertices() {
	throw std::runtime_error("Not implemented");
}

std::vector<conversion_result_shape*> smlib_shape::edges() {
	throw std::runtime_error("Not implemented");
}

std::vector<conversion_result_shape*> smlib_shape::facets() {
	throw std::runtime_error("Not implemented");
}

namespace {
	conversion_result_shape* boolean_with(const smlib_shape& lhs, conversion_result_shape* other, long operation) {
		auto* rhs = dynamic_cast<smlib_shape*>(other);
		if (!rhs || !lhs.brep() || !rhs->brep()) {
			throw std::runtime_error("Invalid shape");
		}
		SmBrep* result = smlib_brep_boolean(lhs.brep(), rhs->brep(), operation);
		if (!result) {
			throw std::runtime_error("Boolean operation failed");
		}
		return new smlib_shape(result);
	}
}

conversion_result_shape* smlib_shape::add(conversion_result_shape* other) {
	return boolean_with(*this, other, SM_BO_UNION);
}

conversion_result_shape* smlib_shape::subtract(conversion_result_shape* other) {
	return boolean_with(*this, other, SM_BO_DIFFERENCE);
}

conversion_result_shape* smlib_shape::intersect(conversion_result_shape* other) {
	return boolean_with(*this, other, SM_BO_INTERSECTION);
}

conversion_result_shape* smlib_shape::concat(conversion_result_shape* other) {
	// SMLib has no representation for a compound of disjoint bodies, so the
	// operands are merged instead.
	return boolean_with(*this, other, SM_BO_MERGE);
}

std::size_t smlib_shape::map(opaque_coordinate<4>&, opaque_coordinate<4>&) {
	throw std::runtime_error("Not implemented");
}

std::size_t smlib_shape::map(const std::vector<opaque_coordinate<4>>&, const std::vector<opaque_coordinate<4>>&) {
	throw std::runtime_error("Not implemented");
}

conversion_result_shape* smlib_shape::moved(taxonomy::matrix4::ptr place) const {
	auto* result = new smlib_shape(*this);
	if (!place || !result->brep_) {
		return result;
	}
	SmAxis2Placement placement;
	smlib_placement_from_matrix(place->ccomponents(), placement);
	if (SmApiTransform(result->brep_, placement) != SM_SUCCESS) {
		delete result;
		throw std::runtime_error("Unable to move shape");
	}
	return result;
}

bool smlib_shape::surface_area_along_direction(double, const taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const {
	along_x = along_y = along_z = 0.;
	if (!brep_) {
		return false;
	}
	smlib_ensure_context();
	SmPolyBrep* poly = nullptr;
	SmTessellationReport report;
	SmTessellationParams params;
	if (SmApiTessellate(brep_, poly, params, TRUE, nullptr, &report) != SM_SUCCESS || !poly) {
		delete poly;
		return false;
	}
	SmTArray<SmPolyFace*> faces;
	poly->GetPolyFaces(faces);
	for (ULONG i = 0; i < faces.GetSize(); ++i) {
		const Eigen::Vector3d sum = polygon_normal(polygon_vertices(faces[i]));
		const double area = sum.norm() / 2.;
		if (area <= 0.) {
			continue;
		}
		const Eigen::Vector3d normal = sum / sum.norm();
		along_x += area * std::abs(normal(0));
		along_y += area * std::abs(normal(1));
		along_z += area * std::abs(normal(2));
	}
	delete poly;
	return true;
}
