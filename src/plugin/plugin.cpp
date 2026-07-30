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

#ifndef _WIN32
#include <dlfcn.h>
#else
#include <windows.h>
#endif

#include <boost/algorithm/string/predicate.hpp>
#include <boost/dll/shared_library.hpp>

#include <algorithm>
#include <filesystem>
#include <iostream>
#include <mutex>
#include <sstream>
#include <stdexcept>

namespace {
	using plugin_abi_fn = ifcopenshell::plugin::abi_info();
	using plugin_metadata_fn = ifcopenshell::plugin::metadata();

	std::mutex& configured_search_paths_mutex() {
		static std::mutex mutex;
		return mutex;
	}

	std::vector<std::string>& configured_search_paths() {
		static std::vector<std::string> paths;
		return paths;
	}

	std::string path_string(const std::filesystem::path& path) {
		return path.string();
	}

	void plugin_debug(const std::string& message) {
#ifdef IFOPSH_PLUGIN_DEBUG
#if defined(_MSC_VER) && defined(_UNICODE)
        std::wcerr << "[ifcopenshell.plugin] " << message.c_str() << std::endl;
#else
		std::cerr << "[ifcopenshell.plugin] " << message << std::endl;
#endif
#else
		static_cast<void>(message);
#endif
	}

	const char* plugin_kind_name(ifcopenshell::plugin::kind kind) {
		switch (kind) {
		case ifcopenshell::plugin::kind::parse_schema:
			return "parse_schema";
		case ifcopenshell::plugin::kind::mapping:
			return "mapping";
		case ifcopenshell::plugin::kind::kernel:
			return "kernel";
		case ifcopenshell::plugin::kind::tree:
			return "tree";
		case ifcopenshell::plugin::kind::document_serializer:
			return "document_serializer";
		case ifcopenshell::plugin::kind::geometry_serializer:
			return "geometry_serializer";
		case ifcopenshell::plugin::kind::opencascade_geometry_ifc_writer:
			return "opencascade_geometry_ifc_writer";
		case ifcopenshell::plugin::kind::linework_processing:
			return "linework_processing";
		default:
			return "unknown";
		}
	}

	std::vector<std::string> configured_search_paths_copy() {
		std::lock_guard<std::mutex> lock(configured_search_paths_mutex());
		return configured_search_paths();
	}

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

	std::string decorated_basename(const std::string& basename) {
		return boost::algorithm::istarts_with(basename, "ifcopenshell.") ? basename : "ifcopenshell." + basename;
	}

	std::vector<std::string> platform_basenames(const std::string& basename) {
		return {decorated_basename(basename)};
	}

#ifdef _WIN32
	struct dll_error_mode_guard {
		DWORD previous_ = 0;
		bool changed_ = false;

		dll_error_mode_guard() {
			changed_ = SetThreadErrorMode(SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX, &previous_) != 0;
		}

		~dll_error_mode_guard() {
			if (changed_) {
				SetThreadErrorMode(previous_, nullptr);
			}
		}
	};
#endif
}

namespace ifcopenshell {
namespace plugin {
PLUGIN_API void set_search_paths(const std::vector<std::string>& paths);
PLUGIN_API std::vector<std::string> search_paths();
PLUGIN_API void clear_search_paths();
PLUGIN_API std::filesystem::path add_search_paths_or_default(manager& manager, std::filesystem::path (*default_search_path)());
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
	plugin_debug("add_search_path " + path_string(path));
	search_paths_.push_back(path);
}

const std::vector<std::filesystem::path>& ifcopenshell::plugin::manager::search_paths() const {
	return search_paths_;
}

std::vector<std::filesystem::path> ifcopenshell::plugin::manager::discover(const std::string& basename_prefix) const {
	std::vector<std::filesystem::path> result;
	const auto suffix = boost::dll::shared_library::suffix().string();
	const auto basename_prefixes = platform_basenames(basename_prefix);

	plugin_debug("discover prefix='" + basename_prefix + "' suffix='" + suffix + "' search_paths=" + std::to_string(search_paths_.size()));
	for (const auto& search_path : search_paths_) {
		if (!std::filesystem::exists(search_path) || !std::filesystem::is_directory(search_path)) {
			plugin_debug("discover skip missing/non-directory search path " + path_string(search_path));
			continue;
		}

		plugin_debug("discover scan " + path_string(search_path));
		for (const auto& entry : std::filesystem::directory_iterator(search_path)) {
			if (!entry.is_regular_file()) {
				continue;
			}

			const auto filename = entry.path().filename().string();
			if (!boost::algorithm::iends_with(filename, suffix)) {
				continue;
			}

			const auto basename = filename.substr(0, filename.size() - suffix.size());
			if (!std::any_of(basename_prefixes.begin(), basename_prefixes.end(), [&basename](const std::string& prefix) {
				return boost::algorithm::istarts_with(basename, prefix);
			})) {
				continue;
			}

			plugin_debug("discover candidate " + path_string(entry.path()));
			result.push_back(entry.path());
		}
	}

	std::sort(result.begin(), result.end());
	result.erase(std::unique(result.begin(), result.end()), result.end());
	plugin_debug("discover result count=" + std::to_string(result.size()));
	return result;
}

std::vector<std::filesystem::path> ifcopenshell::plugin::manager::discover_exact(const std::string& basename) const {
	std::vector<std::filesystem::path> result;
	const auto suffix = boost::dll::shared_library::suffix().string();
	const auto basename_candidates = platform_basenames(basename);

	plugin_debug("discover_exact basename='" + basename + "' suffix='" + suffix + "' search_paths=" + std::to_string(search_paths_.size()));
	for (const auto& search_path : search_paths_) {
		if (!std::filesystem::exists(search_path) || !std::filesystem::is_directory(search_path)) {
			plugin_debug("discover_exact skip missing/non-directory search path " + path_string(search_path));
			continue;
		}

		for (const auto& candidate : basename_candidates) {
			const auto path = search_path / (candidate + suffix);
			plugin_debug("discover_exact probe " + path_string(path));
			if (std::filesystem::is_regular_file(path)) {
				plugin_debug("discover_exact candidate " + path_string(path));
				result.push_back(path);
			}
		}
	}

	std::sort(result.begin(), result.end());
	result.erase(std::unique(result.begin(), result.end()), result.end());
	plugin_debug("discover_exact result count=" + std::to_string(result.size()));
	return result;
}

ifcopenshell::plugin::module ifcopenshell::plugin::manager::load(const std::filesystem::path& path) const {
	plugin_debug("load " + path_string(path));
#ifdef _WIN32
	dll_error_mode_guard error_mode_guard;
	const auto load_mode = boost::dll::load_mode::load_with_altered_search_path;
#elif defined(__EMSCRIPTEN__)
	// Pyodide side modules resolve shared IfcOpenShell symbols from modules loaded earlier.
	const auto load_mode = boost::dll::load_mode::rtld_global;
#else
	const auto load_mode = boost::dll::load_mode::default_mode;
#endif
	auto library = std::make_shared<boost::dll::shared_library>(path, load_mode);
	auto abi = library->get_alias<plugin_abi_fn>("ifcopenshell_plugin_abi_v1")();
	validate_abi(abi);
	auto metadata = library->get_alias<plugin_metadata_fn>("ifcopenshell_plugin_metadata_v1")();
	plugin_debug(std::string("load metadata kind=") + plugin_kind_name(metadata.kind_) +
		" id='" + metadata.id + "' schema='" + metadata.schema + "' format='" + metadata.format + "'");

	auto data = std::make_shared<module::data>();
	data->metadata_ = metadata;
	data->path_ = path;
	data->library_ = std::move(library);
	return module(data);
}

PLUGIN_API void ifcopenshell::plugin::set_search_paths(const std::vector<std::string>& paths) {
	std::lock_guard<std::mutex> lock(configured_search_paths_mutex());
	configured_search_paths() = paths;
	plugin_debug("set configured search paths count=" + std::to_string(configured_search_paths().size()));
	for (const auto& path : configured_search_paths()) {
		plugin_debug("configured search path " + path);
	}
}

PLUGIN_API std::vector<std::string> ifcopenshell::plugin::search_paths() {
	const auto paths = configured_search_paths_copy();
	plugin_debug("get configured search paths count=" + std::to_string(paths.size()));
	return paths;
}

PLUGIN_API void ifcopenshell::plugin::clear_search_paths() {
	std::lock_guard<std::mutex> lock(configured_search_paths_mutex());
	configured_search_paths().clear();
	plugin_debug("cleared configured search paths");
}

PLUGIN_API std::filesystem::path ifcopenshell::plugin::add_search_paths_or_default(
	manager& manager, std::filesystem::path (*default_search_path)())
{
	const auto paths = configured_search_paths_copy();
	if (!paths.empty()) {
		plugin_debug("using configured plugin search paths; default module directory will not be resolved");
		for (const auto& path : paths) {
			manager.add_search_path(path);
		}
		return {};
	}

	plugin_debug("using default plugin search path from module directory");
	const auto path = default_search_path();
	manager.add_search_path(path);

	// Static libraries place their anchor in the executable. For a normal
	// Unix install this resolves to $prefix/bin, while shared plug-ins are
	// installed in $prefix/lib. Windows installs DLL plug-ins in bin already.
#ifndef _WIN32
	if (path.filename() == "bin") {
		const auto lib = path.parent_path() / "lib";
		if (std::filesystem::exists(lib)) {
			manager.add_search_path(lib);
		}
	}
#endif

	// Bundle-aware fallback search paths. The primary search path is
	// dirname(libIfcParse) which works for the flat layouts we get on
	// Linux ($prefix/lib/) and Windows ($prefix/bin/) — plug-ins live
	// next to libIfcParse there. macOS app bundles put libIfcParse
	// somewhere inside Contents/ (Frameworks/ by macdeployqt
	// convention, MacOS/ if the install rule co-locates it with the
	// exe) and the plug-ins typically live in a sibling directory,
	// not the same one. Probe the Apple-canonical PlugIns/ first,
	// then Frameworks/ (where macdeployqt deposits non-Qt @rpath
	// deps) and MacOS/ (next-to-exe layout). Duplicate primary paths
	// are harmless — discover_exact short-circuits on first hit.
#ifdef __APPLE__
	if (!path.empty()) {
		const auto parent = path.parent_path();
		manager.add_search_path(parent / "PlugIns");
		manager.add_search_path(parent / "Frameworks");
		manager.add_search_path(parent / "MacOS");
	}
#endif

	return path;
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
	plugin_debug("validate_abi plugin_api=" + std::to_string(abi.plugin_api_version) +
		" host_api=" + std::to_string(host.plugin_api_version) +
		" plugin_compiler='" + abi.compiler_id + " " + abi.compiler_version + "'" +
		" host_compiler='" + host.compiler_id + " " + host.compiler_version + "'" +
		" plugin_pointer_size=" + std::to_string(abi.pointer_size) +
		" host_pointer_size=" + std::to_string(host.pointer_size) +
		" plugin_debug=" + std::to_string(abi.debug_build) +
		" host_debug=" + std::to_string(host.debug_build));
	if (abi.plugin_api_version == host.plugin_api_version &&
		abi.pointer_size == host.pointer_size &&
		abi.debug_build == host.debug_build &&
		abi.compiler_id == host.compiler_id &&
		abi.compiler_version == host.compiler_version) {
		plugin_debug("validate_abi compatible");
		return;
	}

	std::ostringstream stream;
	stream << "Incompatible plugin ABI";
	stream << " (plugin api " << abi.plugin_api_version << ", host api " << host.plugin_api_version << ")";
	stream << " (plugin compiler " << abi.compiler_id << " " << abi.compiler_version;
	stream << ", host compiler " << host.compiler_id << " " << host.compiler_version << ")";
	stream << " (plugin pointer size " << abi.pointer_size << ", host pointer size " << host.pointer_size << ")";
	stream << " (plugin debug " << abi.debug_build << ", host debug " << host.debug_build << ")";
	plugin_debug(stream.str());
	throw std::runtime_error(stream.str());
}

std::filesystem::path ifcopenshell::plugin::module_directory(const void* symbol) {
	plugin_debug("resolve module_directory for symbol " + std::to_string(reinterpret_cast<std::uintptr_t>(symbol)));
#ifdef _WIN32
	HMODULE module_handle = nullptr;
	if (!GetModuleHandleExW(
		GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
		reinterpret_cast<LPCWSTR>(symbol),
		&module_handle)) {
		plugin_debug("module_directory failed in GetModuleHandleExW");
		throw std::runtime_error("Unable to resolve module path");
	}

	wchar_t buffer[MAX_PATH];
	const DWORD length = GetModuleFileNameW(module_handle, buffer, MAX_PATH);
	if (length == 0) {
		plugin_debug("module_directory failed in GetModuleFileNameW");
		throw std::runtime_error("Unable to read module filename");
	}

	const auto directory = std::filesystem::path(std::wstring(buffer, length)).parent_path();
	plugin_debug("module_directory resolved " + path_string(directory));
	return directory;
#else
	Dl_info info;
	if (dladdr(symbol, &info) == 0 || !info.dli_fname) {
		plugin_debug("module_directory failed in dladdr");
		throw std::runtime_error("Unable to resolve module path");
	}

	const auto directory = std::filesystem::path(info.dli_fname).parent_path();
	plugin_debug("module_directory resolved " + path_string(directory));
	return directory;
#endif
}
