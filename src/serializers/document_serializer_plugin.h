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

#ifndef IFCOPENSHELL_DOCUMENT_SERIALIZER_PLUGIN_H
#define IFCOPENSHELL_DOCUMENT_SERIALIZER_PLUGIN_H

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Serializer.h"
#include "../ifcparse/file.h"
#include "../plugin/plugin.h"

#include <boost/function.hpp>
#include <boost/shared_ptr.hpp>

#include <filesystem>
#include <map>
#include <string>
#include <vector>

namespace ifcopenshell {
namespace serializers {

struct SERIALIZERS_API document_serializer_info {
	std::string format;
	std::string name;
	std::string description;
	std::string schema_name;
	bool supports_ifc_file = true;
	bool supports_input_filename = false;
	bool writes_final_output = false;
};

struct SERIALIZERS_API document_serializer_context {
	ifcopenshell::file* file = nullptr;
	std::string input_filename;
	std::string output_filename;
	std::string schema_name;
	bool stream = false;
	int dialect = 0;
	// Supertype names to skip when streaming entities into the serializer.
	// Currently only honoured by the RocksDB serializer; consumers building
	// lossy/read-only databases pass e.g. {"IfcRepresentationItem"} to drop
	// geometry definitions.
	std::vector<std::string> skip_supertypes;
};

class SERIALIZERS_API document_serializer_registry {
public:
	typedef boost::function<boost::shared_ptr<Serializer>(const document_serializer_context&)> create_fn;

	void bind(const document_serializer_info& info, create_fn create, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
	const document_serializer_info* find(const std::string& format, const std::string& schema_name = std::string()) const;
	boost::shared_ptr<Serializer> create(const std::string& format, const document_serializer_context& context) const;
	std::vector<document_serializer_info> serializers() const;

private:
	struct entry {
		document_serializer_info info_;
		create_fn create_;
		ifcopenshell::plugin::module module_;
	};

	const entry* find_entry_(const std::string& format, const std::string& schema_name) const;

	friend SERIALIZERS_API bool load_document_serializer_plugin(document_serializer_registry& registry, const std::string& format, const std::string& schema_name);

	std::map<std::string, std::vector<entry>> entries_;
};

typedef void register_document_serializer_plugin_fn(document_serializer_registry&, const ifcopenshell::plugin::module&);

SERIALIZERS_API const char* document_serializer_plugin_registration_symbol();
SERIALIZERS_API ifcopenshell::plugin::metadata document_serializer_plugin_metadata(const std::string& format, const std::string& schema_name = std::string());
SERIALIZERS_API std::filesystem::path document_serializer_plugin_directory();
SERIALIZERS_API void load_document_serializer_plugins(document_serializer_registry& registry);
SERIALIZERS_API bool load_document_serializer_plugin(document_serializer_registry& registry, const std::string& format, const std::string& schema_name = std::string());
SERIALIZERS_API document_serializer_registry& document_serializer_registry_instance();

}
}

#endif
