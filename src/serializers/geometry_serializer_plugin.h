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

#ifndef IFCOPENSHELL_GEOMETRY_SERIALIZER_PLUGIN_H
#define IFCOPENSHELL_GEOMETRY_SERIALIZER_PLUGIN_H

#include "../serializers/serializers_api.h"
#include "../ifcgeom/GeometrySerializer.h"
#include "../plugin/plugin.h"

#include <boost/function.hpp>
#include <boost/shared_ptr.hpp>

#include <filesystem>
#include <map>
#include <string>
#include <vector>

namespace ifcopenshell {
namespace serializers {

struct SERIALIZERS_API geometry_serializer_info {
	std::string format;
	std::string name;
	std::string description;
	std::vector<std::string> extensions;
	std::vector<std::string> kernel_ids;
	bool supports_triangulation = false;
	bool supports_brep = false;
	bool supports_user_element_hierarchy = false;
	bool bypass_properties = true;
	bool requires_ascii_temp_file = false;
	bool writes_final_output = false;
};

struct SERIALIZERS_API geometry_serializer_context {
	std::string output_filename;
	std::string output_temp_filename;
	ifcopenshell::geometry::Settings& geometry_settings;
	const ifcopenshell::geometry::SerializerSettings& serializer_settings;
	const stream_or_filename* output_stream = nullptr;
	const stream_or_filename* output_temp_stream = nullptr;
};

class SERIALIZERS_API geometry_serializer_registry {
public:
	typedef boost::function<boost::shared_ptr<GeometrySerializer>(const geometry_serializer_context&)> create_fn;
	typedef boost::function<void(geometry_serializer_context&)> configure_fn;

	void bind(const geometry_serializer_info& info, create_fn create, configure_fn configure = configure_fn(), const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
	bool has(const std::string& extension) const;
	const geometry_serializer_info* find(const std::string& extension) const;
	void configure(const std::string& extension, geometry_serializer_context& context) const;
	boost::shared_ptr<GeometrySerializer> create(const std::string& extension, const geometry_serializer_context& context) const;
	std::vector<geometry_serializer_info> serializers() const;

private:
	struct entry {
		geometry_serializer_info info_;
		create_fn create_;
		configure_fn configure_;
		ifcopenshell::plugin::module module_;
	};

	friend SERIALIZERS_API bool load_geometry_serializer_plugin(geometry_serializer_registry& registry, const std::string& extension);

	std::map<std::string, entry> entries_;
};

typedef void register_geometry_serializer_plugin_fn(geometry_serializer_registry&, const ifcopenshell::plugin::module&);

SERIALIZERS_API const char* geometry_serializer_plugin_registration_symbol();
SERIALIZERS_API ifcopenshell::plugin::metadata geometry_serializer_plugin_metadata(const std::string& format);
SERIALIZERS_API std::filesystem::path geometry_serializer_plugin_directory();
SERIALIZERS_API void load_geometry_serializer_plugins(geometry_serializer_registry& registry);
SERIALIZERS_API bool load_geometry_serializer_plugin(geometry_serializer_registry& registry, const std::string& extension);
SERIALIZERS_API geometry_serializer_registry& geometry_serializer_registry_instance();

}
}

#endif
