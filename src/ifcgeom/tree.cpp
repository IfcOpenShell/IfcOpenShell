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

#include "tree.h"

#include "iterator.h"
#include "../ifcparse/exception.h"

#include <boost/functional/hash.hpp>

#include <cstdio>
#include <unordered_set>

namespace {
	[[noreturn]] void unsupported_tree_operation(const std::string& backend_id, const std::string& operation) {
		throw ifcopenshell::exception("Tree backend '" + backend_id + "' does not support " + operation);
	}
}

ifcopenshell::geom::tree::~tree() = default;

void ifcopenshell::geom::tree::add_file(ifcopenshell::file&, const ifcopenshell::geom::settings&) {
	unsupported_tree_operation(backend_id(), "add_file()");
}

void ifcopenshell::geom::tree::add_file(ifcopenshell::geom::iterator& iterator) {
	if (!iterator.initialize()) {
		return;
	}

	do {
		auto element = iterator.get();
		add_element(element.get());
	} while (iterator.next());
}

void ifcopenshell::geom::tree::add_element(ifcopenshell::geom::element*) {
	unsupported_tree_operation(backend_id(), "add_element()");
}

std::vector<express::entity> ifcopenshell::geom::tree::select_box(const express::entity&, bool, double) const {
	unsupported_tree_operation(backend_id(), "select_box(entity)");
}

std::vector<express::entity> ifcopenshell::geom::tree::select_box(const tree_point&) const {
	unsupported_tree_operation(backend_id(), "select_box(point)");
}

std::vector<express::entity> ifcopenshell::geom::tree::select_box(const tree_box&, bool) const {
	unsupported_tree_operation(backend_id(), "select_box(bounds)");
}

std::vector<express::entity> ifcopenshell::geom::tree::select(const express::entity&, bool, double) const {
	unsupported_tree_operation(backend_id(), "select(entity)");
}

std::vector<express::entity> ifcopenshell::geom::tree::select(const ifcopenshell::geom::element*, bool, double) const {
	unsupported_tree_operation(backend_id(), "select(element)");
}

std::vector<express::entity> ifcopenshell::geom::tree::select(const tree_point&, double) const {
	unsupported_tree_operation(backend_id(), "select(point)");
}

std::vector<ifcopenshell::geom::ray_intersection_result> ifcopenshell::geom::tree::select_ray(const tree_point&, const tree_point&, double) const {
	unsupported_tree_operation(backend_id(), "select_ray()");
}

std::vector<ifcopenshell::geom::clash> ifcopenshell::geom::tree::clash_intersection_many(const std::vector<express::base>&, const std::vector<express::base>&, double, bool) const {
	unsupported_tree_operation(backend_id(), "clash_intersection_many()");
}

std::vector<ifcopenshell::geom::clash> ifcopenshell::geom::tree::clash_collision_many(const std::vector<express::base>&, const std::vector<express::base>&, bool) const {
	unsupported_tree_operation(backend_id(), "clash_collision_many()");
}

std::vector<ifcopenshell::geom::clash> ifcopenshell::geom::tree::clash_clearance_many(const std::vector<express::base>&, const std::vector<express::base>&, double, bool) const {
	unsupported_tree_operation(backend_id(), "clash_clearance_many()");
}

const std::vector<double>& ifcopenshell::geom::tree::distances() const {
	unsupported_tree_operation(backend_id(), "distances()");
}

const std::vector<double>& ifcopenshell::geom::tree::protrusion_distances() const {
	unsupported_tree_operation(backend_id(), "protrusion_distances()");
}

bool ifcopenshell::geom::tree::enable_face_styles() const {
	unsupported_tree_operation(backend_id(), "enable_face_styles()");
}

void ifcopenshell::geom::tree::enable_face_styles(bool) {
	unsupported_tree_operation(backend_id(), "enable_face_styles(bool)");
}

const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& ifcopenshell::geom::tree::styles() const {
	unsupported_tree_operation(backend_id(), "styles()");
}

std::string ifcopenshell::geom::tree::uint8_to_b64(const std::vector<uint8_t>& uuids_array) const {
	std::string hex_str;
	hex_str.reserve(uuids_array.size() * 2);

	for (auto byte : uuids_array) {
		char hex[3];
		std::snprintf(hex, sizeof(hex), "%02x", byte);
		hex_str.append(hex);
	}

	return hex_str;
}

bool ifcopenshell::geom::tree::is_manifold(const std::vector<int>& faces) {
	std::unordered_set<std::pair<size_t, size_t>, boost::hash<std::pair<size_t, size_t>>> directed_edges;

	for (size_t i = 0; i < faces.size(); i += 3) {
		for (size_t j = 0; j < 3; ++j) {
			const auto k = (j + 1) % 3;
			const std::pair<size_t, size_t> edge(faces[i + j], faces[i + k]);
			const auto it = directed_edges.find(edge);
			if (it != directed_edges.end()) {
				directed_edges.erase(it);
			} else {
				directed_edges.insert({ faces[i + k], faces[i + j] });
			}
		}
	}

	return directed_edges.empty();
}
