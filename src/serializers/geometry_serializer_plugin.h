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
#include "../ifcgeom/geometry_serializer.h"
#include "../plugin/plugin.h"

#include <functional>
#include <memory>

#include <filesystem>
#include <map>
#include <string>
#include <vector>

namespace ifcopenshell {
namespace serializers {

using ifcopenshell::geom::geometry_serializer;

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
	ifcopenshell::geom::settings& settings;
	const stream_or_filename* output_stream = nullptr;
	const stream_or_filename* output_temp_stream = nullptr;
};

class SERIALIZERS_API geometry_serializer_registry {
public:
	typedef std::function<std::shared_ptr<geometry_serializer>(const geometry_serializer_context&)> create_fn;
	typedef std::function<void(geometry_serializer_context&)> configure_fn;

	void bind(const geometry_serializer_info& info, create_fn create, configure_fn configure = configure_fn(), const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
	bool has(const std::string& extension) const;
	const geometry_serializer_info* find(const std::string& extension) const;
	void configure(const std::string& extension, geometry_serializer_context& context) const;
	std::shared_ptr<geometry_serializer> create(const std::string& extension, const geometry_serializer_context& context) const;
	std::vector<geometry_serializer_info> serializers() const;

private:
	struct entry {
		ifcopenshell::plugin::module module_;
		geometry_serializer_info info_;
		create_fn create_;
		configure_fn configure_;
	};

	friend SERIALIZERS_API bool load_geometry_serializer_plugin(geometry_serializer_registry& registry, const std::string& extension);

	std::map<std::string, entry> entries_;
};

SERIALIZERS_API geometry_serializer_registry& geometry_serializer_registry_instance();

class SERIALIZERS_API PluginGeometrySerializer : public GeometrySerializer {
public:
	PluginGeometrySerializer(
		const std::string& extension,
		const std::string& output_filename,
		const std::string& output_temp_filename,
		ifcopenshell::geometry::Settings& geometry_settings,
		const ifcopenshell::geometry::SerializerSettings& serializer_settings
	)
		: GeometrySerializer(geometry_settings, serializer_settings)
	{
		geometry_serializer_context context{
			output_filename,
			output_temp_filename.empty() ? output_filename : output_temp_filename,
			geometry_settings,
			serializer_settings
		};
		initialize_(extension, context);
	}

	PluginGeometrySerializer(
		const std::string& extension,
		const stream_or_filename& output_filename,
		const stream_or_filename& output_temp_filename,
		ifcopenshell::geometry::Settings& geometry_settings,
		const ifcopenshell::geometry::SerializerSettings& serializer_settings
	)
		: GeometrySerializer(geometry_settings, serializer_settings)
	{
		const auto output_filename_string = output_filename.filename().value_or("");
		const auto output_temp_filename_string = output_temp_filename.filename().value_or(output_filename_string);
		geometry_serializer_context context{
			output_filename_string,
			output_temp_filename_string,
			geometry_settings,
			serializer_settings,
			&output_filename,
			&output_temp_filename
		};
		initialize_(extension, context);
	}

	bool ready() override { return serializer_->ready(); }
	bool is_streaming() const override { return serializer_->is_streaming(); }
	bool isTesselated() const override { return serializer_->isTesselated(); }
	void writeHeader() override { serializer_->writeHeader(); }
	void finalize() override { serializer_->finalize(); }
	void setFile(ifcopenshell::file* file) override { serializer_->setFile(file); }
	void setUnitNameAndMagnitude(const std::string& name, float magnitude) override { serializer_->setUnitNameAndMagnitude(name, magnitude); }
	void write(const IfcGeom::TriangulationElement* element) override { serializer_->write(element); }
	void write(const IfcGeom::BRepElement* element) override { serializer_->write(element); }

	IfcGeom::Element* read(
		ifcopenshell::file& file,
		const std::string& guid,
		const std::string& representation_id,
		GeometrySerializer::read_type type
	) override {
		return serializer_->read(file, guid, representation_id, type);
	}

private:
	void initialize_(const std::string& extension, geometry_serializer_context& context) {
		auto& registry = geometry_serializer_registry_instance();
		registry.configure(extension, context);
		geometry_settings_ = context.geometry_settings;
		serializer_ = registry.create(extension, context);
	}

	boost::shared_ptr<GeometrySerializer> serializer_;
};

typedef void register_geometry_serializer_plugin_fn(geometry_serializer_registry&, const ifcopenshell::plugin::module&);

SERIALIZERS_API const char* geometry_serializer_plugin_registration_symbol();
SERIALIZERS_API ifcopenshell::plugin::metadata geometry_serializer_plugin_metadata(const std::string& format);
SERIALIZERS_API std::filesystem::path geometry_serializer_plugin_directory();
SERIALIZERS_API void load_geometry_serializer_plugins(geometry_serializer_registry& registry);
SERIALIZERS_API bool load_geometry_serializer_plugin(geometry_serializer_registry& registry, const std::string& extension);

}
}

#endif
