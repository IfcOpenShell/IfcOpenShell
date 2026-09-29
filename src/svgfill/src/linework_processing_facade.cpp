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

// This file was generated with the assistance of an AI coding tool.

#include "linework_processing_plugin.h"

#include "../../plugin/plugin.h"

#include <mutex>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace ifcopenshell {
namespace plugin {
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
}
}

namespace {
struct provider_state {
	ifcopenshell::plugin::module module;
	svgfill::linework_processing_plugin::api api;
};

std::filesystem::path plugin_directory() {
	return ifcopenshell::plugin::module_directory(reinterpret_cast<const void*>(&svgfill::svg_to_line_segments));
}

void validate(const svgfill::linework_processing_plugin::api& api) {
	if (!api.svg_to_line_segments ||
		!api.line_segments_to_polygons ||
		!api.line_segments_to_polygons_with_progress ||
		!api.polygons_to_svg_groups ||
		!api.polygons_to_svg ||
		!api.svg_to_polygons ||
		!api.arrange_polygons ||
		!api.create_arrangement ||
		!api.destroy_arrangement) {
		throw std::runtime_error("Incomplete linework processing plugin API");
	}
}

provider_state& provider() {
	static provider_state state;
	static std::once_flag once;

	std::call_once(once, [] {
		ifcopenshell::plugin::manager manager;
		ifcopenshell::plugin::add_search_paths_or_default(manager, &plugin_directory);

		for (const auto& path : manager.discover_exact(svgfill::linework_processing_plugin::id)) {
			auto module = manager.load(path);
			if (module.meta().kind_ != ifcopenshell::plugin::kind::linework_processing ||
				module.meta().id != svgfill::linework_processing_plugin::id) {
				continue;
			}

			auto register_plugin = module.get_alias<svgfill::linework_processing_plugin::register_linework_processing_plugin_fn>(
				svgfill::linework_processing_plugin::registration_symbol);
			register_plugin(state.api);
			validate(state.api);
			state.module = std::move(module);
			return;
		}

		std::ostringstream stream;
		stream << "Unable to load " << svgfill::linework_processing_plugin::id << " linework processing plugin";
		throw std::runtime_error(stream.str());
	});

	return state;
}
}

bool svgfill::svg_to_line_segments(
	const std::string& data,
	const std::optional<std::string>& class_name,
	std::vector<std::vector<line_segment_2>>& segments)
{
	return provider().api.svg_to_line_segments(data, class_name, segments);
}

bool svgfill::line_segments_to_polygons(
	solver s,
	double eps,
	const std::vector<std::vector<line_segment_2>>& segments,
	std::vector<std::vector<polygon_2>>& polygons)
{
	return provider().api.line_segments_to_polygons(s, eps, segments, polygons);
}

bool svgfill::line_segments_to_polygons(
	solver s,
	double eps,
	const std::vector<std::vector<line_segment_2>>& segments,
	std::vector<std::vector<polygon_2>>& polygons,
	std::function<void(float)>& progress)
{
	return provider().api.line_segments_to_polygons_with_progress(s, eps, segments, polygons, progress);
}

std::string svgfill::polygons_to_svg(const std::vector<std::vector<polygon_2>>& polygons, bool random_color) {
	return provider().api.polygons_to_svg_groups(polygons, random_color);
}

std::string svgfill::polygons_to_svg(const std::vector<polygon_2>& polygons, bool random_color) {
	return provider().api.polygons_to_svg(polygons, random_color);
}

bool svgfill::svg_to_polygons(
	const std::string& data,
	const std::optional<std::string>& class_name,
	std::vector<polygon_2>& polygons)
{
	return provider().api.svg_to_polygons(data, class_name, polygons);
}

bool svgfill::arrange_polygons(
	arrange_polygon_settings settings,
	const std::vector<polygon_2>& polygons,
	std::vector<polygon_2>& arranged,
	ifcopenshell::logger& logger)
{
	return provider().api.arrange_polygons(settings, polygons, arranged, logger);
}

void svgfill::context::add(const std::vector<line_segment_2>& segments) {
	segments_.insert(segments_.end(), segments.begin(), segments.end());
}

bool svgfill::context::build() {
	arr_ = provider().api.create_arrangement(solver_);
	return arr_ && (*arr_)(eps_, segments_, progress_);
}

void svgfill::context::merge(const std::vector<int>& edge_indices) {
	arr_->merge(edge_indices);
}

void svgfill::context::write(std::vector<std::vector<polygon_2>>& p) {
	std::vector<polygon_2> polygons;
	arr_->write(polygons, progress_);
	p.push_back(polygons);
}

svgfill::context::~context() {
	if (arr_) {
		provider().api.destroy_arrangement(arr_);
	}
}
