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

#include "Iterator.h"
#include "tree_registry.h"
#include "../ifcparse/exception.h"

#include <boost/functional/hash.hpp>

#include <cstdio>
#include <limits>
#include <unordered_set>

namespace {
	constexpr const char* default_selection_backend_id = "opencascade.brep";
	constexpr const char* default_clash_backend_id = "opencascade.trianglebvh";

	const std::vector<double>& empty_double_vector() {
		static const std::vector<double> values;
		return values;
	}

	const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& empty_style_vector() {
		static const std::vector<ifcopenshell::geom::taxonomy::style::ptr> values;
		return values;
	}

	std::vector<express::entity> to_product_entities(const std::vector<express::base>& instances) {
		std::vector<express::entity> entities;
		entities.reserve(instances.size());

		for (const auto& instance : instances) {
			if (!instance) {
				throw ifcopenshell::exception("All instances should be of type IfcProduct");
			}

			auto entity = instance.as<express::entity>();
			if (!entity || !instance.declaration().is("IfcProduct")) {
				throw ifcopenshell::exception("All instances should be of type IfcProduct");
			}
			entities.push_back(entity);
		}

		return entities;
	}
}

class ifcopenshell::geom::tree::impl {
public:
	impl() = default;

	explicit impl(const std::string& backend_id)
		: backend_id_(backend_id)
	{}

	ifcopenshell::geom::trees::abstract_tree& backend() const {
		if (!backend_) {
			if (backend_id_.empty()) {
				throw ifcopenshell::exception("No geometry tree backend configured");
			}
			backend_ = ifcopenshell::geom::trees::construct(backend_id_);
		}
		return *backend_;
	}

	ifcopenshell::geom::trees::abstract_tree& backend(const std::string& default_backend_id) const {
		if (backend_id_.empty()) {
			backend_id_ = default_backend_id;
		}
		return backend();
	}

	ifcopenshell::geom::trees::abstract_tree& backend_for_element(ifcopenshell::geom::element* element) const {
		if (dynamic_cast<ifcopenshell::geom::brep_element*>(element)) {
			return backend(default_selection_backend_id);
		}

		if (dynamic_cast<ifcopenshell::geom::triangulation_element*>(element)) {
			return backend(default_clash_backend_id);
		}

		throw ifcopenshell::exception("Unsupported tree element type");
	}

	const ifcopenshell::geom::trees::abstract_tree* backend_or_null() const {
		return backend_.get();
	}

private:
	mutable std::string backend_id_;
	mutable std::unique_ptr<ifcopenshell::geom::trees::abstract_tree> backend_;
};

ifcopenshell::geom::tree::tree()
	: impl_(new impl())
{}

ifcopenshell::geom::tree::tree(const std::string& backend_id)
	: impl_(new impl(backend_id))
{}

ifcopenshell::geom::tree::tree(ifcopenshell::file& file)
	: tree()
{
	add_file(file, ifcopenshell::geom::settings{});
}

ifcopenshell::geom::tree::tree(ifcopenshell::file& file, const ifcopenshell::geom::settings& settings)
	: tree()
{
	add_file(file, settings);
}

ifcopenshell::geom::tree::tree(ifcopenshell::geom::iterator& iterator)
	: tree()
{
	add_file(iterator);
}

ifcopenshell::geom::tree::~tree() = default;

ifcopenshell::geom::tree::tree(tree&& other) noexcept = default;

ifcopenshell::geom::tree& ifcopenshell::geom::tree::operator=(tree&& other) noexcept = default;

void ifcopenshell::geom::tree::add_file(ifcopenshell::file& file, const ifcopenshell::geom::settings& settings) {
	impl_->backend(default_selection_backend_id).add_file(file, settings);
}

void ifcopenshell::geom::tree::add_file(ifcopenshell::geom::iterator& iterator) {
	if (!iterator.initialize()) {
		return;
	}

	do {
		add_element(iterator.get());
	} while (iterator.next());
}

void ifcopenshell::geom::tree::add_element(ifcopenshell::geom::element* element) {
	if (!element) {
		return;
	}

	impl_->backend_for_element(element).add_element(element);
}

std::vector<express::entity> ifcopenshell::geom::tree::select_box(const express::entity& entity, bool completely_within, double extend) const {
	return impl_->backend(default_selection_backend_id).select_box(entity, completely_within, extend);
}

std::vector<express::entity> ifcopenshell::geom::tree::select_box(const tree_point& point) const {
	return impl_->backend(default_selection_backend_id).select_box(point);
}

std::vector<express::entity> ifcopenshell::geom::tree::select_box(const tree_box& bounds, bool completely_within) const {
	return impl_->backend(default_selection_backend_id).select_box(bounds, completely_within);
}

std::vector<express::entity> ifcopenshell::geom::tree::select(const express::entity& entity, bool completely_within, double extend) const {
	return impl_->backend(default_selection_backend_id).select(entity, completely_within, extend);
}

std::vector<express::entity> ifcopenshell::geom::tree::select(const ifcopenshell::geom::element* element, bool completely_within, double extend) const {
	return impl_->backend(default_selection_backend_id).select(element, completely_within, extend);
}

std::vector<express::entity> ifcopenshell::geom::tree::select(const tree_point& point, double extend) const {
	return impl_->backend(default_selection_backend_id).select(point, extend);
}

std::vector<ifcopenshell::geom::ray_intersection_result> ifcopenshell::geom::tree::select_ray(const tree_point& origin, const tree_point& direction, double length) const {
	return impl_->backend(default_selection_backend_id).select_ray(origin, direction, length);
}

std::vector<ifcopenshell::geom::clash> ifcopenshell::geom::tree::clash_intersection_many(const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, double tolerance, bool check_all) const {
	return impl_->backend(default_clash_backend_id).clash_intersection_many(to_product_entities(set_a), to_product_entities(set_b), tolerance, check_all);
}

std::vector<ifcopenshell::geom::clash> ifcopenshell::geom::tree::clash_collision_many(const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, bool allow_touching) const {
	return impl_->backend(default_clash_backend_id).clash_collision_many(to_product_entities(set_a), to_product_entities(set_b), allow_touching);
}

std::vector<ifcopenshell::geom::clash> ifcopenshell::geom::tree::clash_clearance_many(const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, double clearance, bool check_all) const {
	return impl_->backend(default_clash_backend_id).clash_clearance_many(to_product_entities(set_a), to_product_entities(set_b), clearance, check_all);
}

const std::vector<double>& ifcopenshell::geom::tree::distances() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->distances() : empty_double_vector();
}

const std::vector<double>& ifcopenshell::geom::tree::protrusion_distances() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->protrusion_distances() : empty_double_vector();
}

bool ifcopenshell::geom::tree::enable_face_styles() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->enable_face_styles() : false;
}

void ifcopenshell::geom::tree::enable_face_styles(bool enable) {
	impl_->backend(default_selection_backend_id).enable_face_styles(enable);
}

const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& ifcopenshell::geom::tree::styles() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->styles() : empty_style_vector();
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
