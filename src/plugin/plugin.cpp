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

#include "plugin.h"

#include <boost/algorithm/string/predicate.hpp>
#include <boost/dll/shared_library.hpp>

#include <algorithm>
#include <filesystem>
#include <sstream>
#include <stdexcept>

namespace {
	using plugin_abi_fn = ifcopenshell::plugin::abi_info();
	using plugin_metadata_fn = ifcopenshell::plugin::metadata();

	std::string compiler_id() {
#if defined(_MSC_VER)
		return "msvc";
#elif defined(__clang__)
		return "clang";
#elif defined(__GNUC__)
		return "gcc";
#else
		return "unknown";
#endif
	}

	std::string compiler_version() {
#if defined(_MSC_FULL_VER)
		return std::to_string(_MSC_FULL_VER);
#elif defined(__clang_major__) && defined(__clang_minor__) && defined(__clang_patchlevel__)
		return std::to_string(__clang_major__) + "." + std::to_string(__clang_minor__) + "." + std::to_string(__clang_patchlevel__);
#elif defined(__GNUC__) && defined(__GNUC_MINOR__) && defined(__GNUC_PATCHLEVEL__)
		return std::to_string(__GNUC__) + "." + std::to_string(__GNUC_MINOR__) + "." + std::to_string(__GNUC_PATCHLEVEL__);
#else
		return "unknown";
#endif
	}

	bool is_debug_build() {
#if defined(NDEBUG)
		return false;
#else
		return true;
#endif
	}
}

struct ifcopenshell::plugin::module::data {
	metadata metadata_;
	std::filesystem::path path_;
	std::shared_ptr<boost::dll::shared_library> library_;
};

ifcopenshell::plugin::module::module()
	: data_(std::make_shared<data>())
{}

ifcopenshell::plugin::module::module(const metadata& metadata)
	: data_(std::make_shared<data>())
{
	data_->metadata_ = metadata;
}

ifcopenshell::plugin::module::module(std::shared_ptr<data> data)
	: data_(std::move(data))
{}

ifcopenshell::plugin::module ifcopenshell::plugin::module::builtin(const metadata& metadata) {
	return module(metadata);
}

const ifcopenshell::plugin::metadata& ifcopenshell::plugin::module::meta() const {
	return data_->metadata_;
}

const std::filesystem::path& ifcopenshell::plugin::module::path() const {
	return data_->path_;
}

bool ifcopenshell::plugin::module::is_dynamic() const {
	return data_->library_ != nullptr;
}

bool ifcopenshell::plugin::module::is_loaded() const {
	return data_->library_ && data_->library_->is_loaded();
}

boost::dll::shared_library& ifcopenshell::plugin::module::library() const {
	if (!data_->library_) {
		throw std::runtime_error("Plugin module is not dynamic");
	}
	return *data_->library_;
}

ifcopenshell::plugin::manager::manager() = default;

void ifcopenshell::plugin::manager::add_search_path(const std::filesystem::path& path) {
	search_paths_.push_back(path);
}

const std::vector<std::filesystem::path>& ifcopenshell::plugin::manager::search_paths() const {
	return search_paths_;
}

std::vector<std::filesystem::path> ifcopenshell::plugin::manager::discover(const std::string& basename_prefix) const {
	std::vector<std::filesystem::path> result;
	const auto suffix = boost::dll::shared_library::suffix().string();
	const auto prefixed_basename = "lib" + basename_prefix;

	for (const auto& search_path : search_paths_) {
		if (!std::filesystem::exists(search_path) || !std::filesystem::is_directory(search_path)) {
			continue;
		}

		for (const auto& entry : std::filesystem::directory_iterator(search_path)) {
			if (!entry.is_regular_file()) {
				continue;
			}

			const auto filename = entry.path().filename().string();
			if (!boost::algorithm::iends_with(filename, suffix)) {
				continue;
			}
			if (!boost::algorithm::istarts_with(filename, basename_prefix) &&
				!boost::algorithm::istarts_with(filename, prefixed_basename)) {
				continue;
			}

			result.push_back(entry.path());
		}
	}

	std::sort(result.begin(), result.end());
	result.erase(std::unique(result.begin(), result.end()), result.end());
	return result;
}

ifcopenshell::plugin::module ifcopenshell::plugin::manager::load(const std::filesystem::path& path) const {
	auto library = std::make_shared<boost::dll::shared_library>(path, boost::dll::load_mode::default_mode);
	auto abi = library->get_alias<plugin_abi_fn>("ifcopenshell_plugin_abi_v1")();
	validate_abi(abi);
	auto metadata = library->get_alias<plugin_metadata_fn>("ifcopenshell_plugin_metadata_v1")();

	auto data = std::make_shared<module::data>();
	data->metadata_ = metadata;
	data->path_ = path;
	data->library_ = std::move(library);
	return module(data);
}

ifcopenshell::plugin::abi_info ifcopenshell::plugin::host_abi() {
	abi_info abi;
	abi.debug_build = is_debug_build();
	abi.compiler_id = compiler_id();
	abi.compiler_version = compiler_version();
	abi.ifcopenshell_version = PLUGIN_IFCOPENSHELL_VERSION;
	return abi;
}

void ifcopenshell::plugin::validate_abi(const abi_info& abi) {
	const auto host = host_abi();
	if (abi.plugin_api_version == host.plugin_api_version &&
		abi.pointer_size == host.pointer_size &&
		abi.debug_build == host.debug_build &&
		abi.compiler_id == host.compiler_id &&
		abi.compiler_version == host.compiler_version) {
		return;
	}

	std::ostringstream stream;
	stream << "Incompatible plugin ABI";
	stream << " (plugin api " << abi.plugin_api_version << ", host api " << host.plugin_api_version << ")";
	stream << " (plugin compiler " << abi.compiler_id << " " << abi.compiler_version;
	stream << ", host compiler " << host.compiler_id << " " << host.compiler_version << ")";
	stream << " (plugin pointer size " << abi.pointer_size << ", host pointer size " << host.pointer_size << ")";
	stream << " (plugin debug " << abi.debug_build << ", host debug " << host.debug_build << ")";
	throw std::runtime_error(stream.str());
}
