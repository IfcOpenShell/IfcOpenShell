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

	const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& empty_style_vector() {
		static const std::vector<ifcopenshell::geometry::taxonomy::style::ptr> values;
		return values;
	}

	std::vector<express::Entity> to_product_entities(const std::vector<express::Base>& instances) {
		std::vector<express::Entity> entities;
		entities.reserve(instances.size());

		for (const auto& instance : instances) {
			if (!instance) {
				throw ifcopenshell::exception("All instances should be of type IfcProduct");
			}

			auto entity = instance.as<express::Entity>();
			if (!entity || !instance.declaration().is("IfcProduct")) {
				throw ifcopenshell::exception("All instances should be of type IfcProduct");
			}
			entities.push_back(entity);
		}

		return entities;
	}
}

class IfcGeom::tree::impl {
public:
	impl() = default;

	explicit impl(const std::string& backend_id)
		: backend_id_(backend_id)
	{}

	ifcopenshell::geometry::trees::abstract_tree& backend() const {
		if (!backend_) {
			if (backend_id_.empty()) {
				throw ifcopenshell::exception("No geometry tree backend configured");
			}
			backend_ = ifcopenshell::geometry::trees::construct(backend_id_);
		}
		return *backend_;
	}

	ifcopenshell::geometry::trees::abstract_tree& backend(const std::string& default_backend_id) const {
		if (backend_id_.empty()) {
			backend_id_ = default_backend_id;
		}
		return backend();
	}

	ifcopenshell::geometry::trees::abstract_tree& backend_for_element(IfcGeom::Element* element) const {
		if (dynamic_cast<IfcGeom::BRepElement*>(element)) {
			return backend(default_selection_backend_id);
		}

		if (dynamic_cast<IfcGeom::TriangulationElement*>(element)) {
			return backend(default_clash_backend_id);
		}

		throw ifcopenshell::exception("Unsupported tree element type");
	}

	const ifcopenshell::geometry::trees::abstract_tree* backend_or_null() const {
		return backend_.get();
	}

private:
	mutable std::string backend_id_;
	mutable std::unique_ptr<ifcopenshell::geometry::trees::abstract_tree> backend_;
};

IfcGeom::tree::tree()
	: impl_(new impl())
{}

IfcGeom::tree::tree(const std::string& backend_id)
	: impl_(new impl(backend_id))
{}

IfcGeom::tree::tree(ifcopenshell::file& file)
	: tree()
{
	add_file(file, ifcopenshell::geometry::Settings{});
}

IfcGeom::tree::tree(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings)
	: tree()
{
	add_file(file, settings);
}

IfcGeom::tree::tree(IfcGeom::Iterator& iterator)
	: tree()
{
	add_file(iterator);
}

IfcGeom::tree::~tree() = default;

IfcGeom::tree::tree(tree&& other) noexcept = default;

IfcGeom::tree& IfcGeom::tree::operator=(tree&& other) noexcept = default;

void IfcGeom::tree::add_file(ifcopenshell::file& file, const ifcopenshell::geometry::Settings& settings) {
	impl_->backend(default_selection_backend_id).add_file(file, settings);
}

void IfcGeom::tree::add_file(IfcGeom::Iterator& iterator) {
	if (!iterator.initialize()) {
		return;
	}

	do {
		add_element(iterator.get());
	} while (iterator.next());
}

void IfcGeom::tree::add_element(IfcGeom::Element* element) {
	if (!element) {
		return;
	}

	impl_->backend_for_element(element).add_element(element);
}

std::vector<express::Entity> IfcGeom::tree::select_box(const express::Entity& entity, bool completely_within, double extend) const {
	return impl_->backend(default_selection_backend_id).select_box(entity, completely_within, extend);
}

std::vector<express::Entity> IfcGeom::tree::select_box(const tree_point& point) const {
	return impl_->backend(default_selection_backend_id).select_box(point);
}

std::vector<express::Entity> IfcGeom::tree::select_box(const tree_box& bounds, bool completely_within) const {
	return impl_->backend(default_selection_backend_id).select_box(bounds, completely_within);
}

std::vector<express::Entity> IfcGeom::tree::select(const express::Entity& entity, bool completely_within, double extend) const {
	return impl_->backend(default_selection_backend_id).select(entity, completely_within, extend);
}

std::vector<express::Entity> IfcGeom::tree::select(const IfcGeom::Element* element, bool completely_within, double extend) const {
	return impl_->backend(default_selection_backend_id).select(element, completely_within, extend);
}

std::vector<express::Entity> IfcGeom::tree::select(const tree_point& point, double extend) const {
	return impl_->backend(default_selection_backend_id).select(point, extend);
}

std::vector<IfcGeom::ray_intersection_result> IfcGeom::tree::select_ray(const tree_point& origin, const tree_point& direction, double length) const {
	return impl_->backend(default_selection_backend_id).select_ray(origin, direction, length);
}

std::vector<IfcGeom::clash> IfcGeom::tree::clash_intersection_many(const std::vector<express::Base>& set_a, const std::vector<express::Base>& set_b, double tolerance, bool check_all) const {
	return impl_->backend(default_clash_backend_id).clash_intersection_many(to_product_entities(set_a), to_product_entities(set_b), tolerance, check_all);
}

std::vector<IfcGeom::clash> IfcGeom::tree::clash_collision_many(const std::vector<express::Base>& set_a, const std::vector<express::Base>& set_b, bool allow_touching) const {
	return impl_->backend(default_clash_backend_id).clash_collision_many(to_product_entities(set_a), to_product_entities(set_b), allow_touching);
}

std::vector<IfcGeom::clash> IfcGeom::tree::clash_clearance_many(const std::vector<express::Base>& set_a, const std::vector<express::Base>& set_b, double clearance, bool check_all) const {
	return impl_->backend(default_clash_backend_id).clash_clearance_many(to_product_entities(set_a), to_product_entities(set_b), clearance, check_all);
}

const std::vector<double>& IfcGeom::tree::distances() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->distances() : empty_double_vector();
}

const std::vector<double>& IfcGeom::tree::protrusion_distances() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->protrusion_distances() : empty_double_vector();
}

bool IfcGeom::tree::enable_face_styles() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->enable_face_styles() : false;
}

void IfcGeom::tree::enable_face_styles(bool enable) {
	impl_->backend(default_selection_backend_id).enable_face_styles(enable);
}

const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& IfcGeom::tree::styles() const {
	const auto* backend = impl_->backend_or_null();
	return backend ? backend->styles() : empty_style_vector();
}

#ifdef WITH_HDF5
void IfcGeom::tree::write_h5() {
	impl_->backend(default_clash_backend_id).write_h5();
}
#endif

std::string IfcGeom::tree::uint8_to_b64(const std::vector<uint8_t>& uuids_array) const {
	std::string hex_str;
	hex_str.reserve(uuids_array.size() * 2);

	for (auto byte : uuids_array) {
		char hex[3];
		std::snprintf(hex, sizeof(hex), "%02x", byte);
		hex_str.append(hex);
	}

	return hex_str;
}

bool IfcGeom::tree::is_manifold(const std::vector<int>& faces) {
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
