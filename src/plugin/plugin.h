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

#ifndef IFCOPENSHELL_PLUGIN_H
#define IFCOPENSHELL_PLUGIN_H

#include "plugin_api.h"

#include <boost/dll/shared_library.hpp>

#include <cstdint>
#include <filesystem>
#include <memory>
#include <string>
#include <vector>

namespace ifcopenshell {
namespace plugin {

enum class kind {
	parse_schema,
	mapping,
	kernel,
	tree,
	document_serializer,
	geometry_serializer,
	opencascade_geometry_ifc_writer,
	linework_processing
};

struct PLUGIN_API abi_info {
	uint32_t plugin_api_version = 1;
	uint32_t pointer_size = sizeof(void*);
	bool debug_build = false;
	std::string compiler_id;
	std::string compiler_version;
	std::string ifcopenshell_version;
};

struct PLUGIN_API metadata {
	kind kind_ = kind::kernel;
	std::string id;
	std::string schema;
	std::string format;
};

class PLUGIN_API module {
public:
	module();
	explicit module(const metadata& metadata);

	static module builtin(const metadata& metadata);

	const metadata& meta() const;
	const std::filesystem::path& path() const;
	bool is_dynamic() const;
	bool is_loaded() const;

	template <typename T>
	decltype(auto) get_alias(const char* name) const {
		return library().get_alias<T>(name);
	}

private:
	struct data;
	std::shared_ptr<data> data_;

	explicit module(std::shared_ptr<data> data);
	boost::dll::shared_library& library() const;

	friend class manager;
};

class PLUGIN_API manager {
public:
	manager();

	void add_search_path(const std::filesystem::path& path);
	const std::vector<std::filesystem::path>& search_paths() const;

	std::vector<std::filesystem::path> discover(const std::string& basename_prefix) const;
	std::vector<std::filesystem::path> discover_exact(const std::string& basename) const;
	module load(const std::filesystem::path& path) const;

private:
	std::vector<std::filesystem::path> search_paths_;
};

PLUGIN_API abi_info host_abi();
PLUGIN_API void validate_abi(const abi_info& abi);
PLUGIN_API std::filesystem::path module_directory(const void* symbol);
PLUGIN_API void set_search_paths(const std::vector<std::string>& paths);
PLUGIN_API std::vector<std::string> search_paths();
PLUGIN_API void clear_search_paths();

}
}

#endif
