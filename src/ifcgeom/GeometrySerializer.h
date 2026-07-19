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

#ifndef GEOMETRYSERIALIZER_H
#define GEOMETRYSERIALIZER_H

#include "../ifcgeom/Serializer.h"
#include "../ifcgeom/IfcGeomElement.h"
#include <fstream>

namespace ifcopenshell {
namespace geometry {
inline namespace settings {

	struct UseElementNames : public SettingBase<UseElementNames, bool> {
		static constexpr const char* const name = "use-element-names";
		static constexpr const char* const description = "Use entity instance IfcRoot.Name instead of unique IDs for naming elements upon serialization. "
			"Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementGuids : public SettingBase<UseElementGuids, bool> {
		static constexpr const char* const name = "use-element-guids";
		static constexpr const char* const description = "Use entity instance IfcRoot.GlobalId instead of unique IDs for naming elements upon serialization. "
			"Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementStepIds : public SettingBase<UseElementStepIds, bool> {
		static constexpr const char* const name = "use-element-step-ids";
		static constexpr const char* const description = "Use the numeric step identifier (entity instance name) for naming elements upon serialization. "
			"Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementTypes : public SettingBase<UseElementTypes, bool> {
		static constexpr const char* const name = "use-element-types";
		static constexpr const char* const description = "Use element types instead of unique IDs for naming elements upon serialization. "
			"Applicable to DAE output.";
		static constexpr bool defaultvalue = false;
	};

	struct NameTemplate : public SettingBase<NameTemplate, std::string> {
		static constexpr const char* const name = "name-template";
		static constexpr const char* const description = "Generic printf/find-style template to derive per-entity identifiers/names upon serialization, "
			"superseding --use-element-names, --use-element-guids, --use-element-step-ids, and --use-element-types when specified. "
			"Recognized placeholders: %N (IfcRoot.Name), %G (GlobalId, compressed IFC form), "
			"%g (GlobalId, uncompressed/decoded UUID form), %T (entity class, e.g. IfcWall), "
			"%t (Tag attribute, empty when not applicable), %i (numeric STEP instance id), "
			"%u (the default unique id scheme), and %% (a literal percent sign). "
			"Example: --name-template '%T-%N (%G)'. Applicable for OBJ, DAE, GLTF, STP, SVG, and TTL output.";
	};

	struct UseYUp : public SettingBase<UseYUp, bool> {
		static constexpr const char* const name = "y-up";
		static constexpr const char* const description = "Change the 'up' axis to positive Y, default is Z UP. Applicable to OBJ output.";
		static constexpr bool defaultvalue = false;
	};

	struct WriteGltfEcef : public SettingBase<WriteGltfEcef, bool> {
		static constexpr const char* const name = "ecef";
		static constexpr const char* const description = "Write glTF in Earth-Centered Earth-Fixed coordinates. Requires PROJ.";
		static constexpr bool defaultvalue = false;
	};

	struct FloatingPointDigits : public SettingBase<FloatingPointDigits, int> {
		static constexpr const char* const name = "digits";
		static constexpr const char* const description = "Sets the precision to be used to format floating-point values, 15 by default. "
			"Use a negative value to use the system's default precision (should be 6 typically). "
			"Applicable for OBJ and DAE output. For DAE output, value >= 15 means that up to 16 decimals are used, "
			" and any other value means that 6 or 7 decimals are used.";
		static constexpr int defaultvalue = 15;
	};

	struct BaseUri : public SettingBase<BaseUri, std::string> {
		static constexpr const char* const name = "base-uri";
		static constexpr const char* const description = "Base URI for products to be used in RDF-based serializations.";
	};

	struct WktUseSection : public SettingBase<WktUseSection, bool> {
		static constexpr const char* const name = "wkt-use-section";
		static constexpr const char* const description = "Use a geometrical section rather than full polyhedral output and footprint in TTL WKT";
		static constexpr bool defaultvalue = false;
	};

	struct SeparateZUpNode : public SettingBase<SeparateZUpNode, bool> {
        static constexpr const char* const name = "separate-z-up-node";
        static constexpr const char* const description = "Introduce a separate Z-Up node into the GlTF hierarchy instead of multiplying the transform into the root node matrices";
        static constexpr bool defaultvalue = false;
    };
}

class SerializerSettings : public SettingsContainer <
	// @todo should we use tuple_cat here to unify the settings into a single class?
    std::tuple<UseElementNames, UseElementGuids, UseElementStepIds, UseElementTypes, NameTemplate, UseYUp, WriteGltfEcef, FloatingPointDigits, BaseUri, WktUseSection, SeparateZUpNode>>
{};

}
}

namespace ifcopenshell {
namespace geometry {

	// See ifcopenshell::geometry::settings::NameTemplate for supported placeholders.
	inline std::string format_name_template(const std::string& tmpl, const IfcGeom::Element* o) {
		std::string result;
		result.reserve(tmpl.size());
		for (std::string::size_type i = 0; i < tmpl.size(); ++i) {
			char c = tmpl[i];
			if (c != '%' || i + 1 >= tmpl.size()) {
				result += c;
				continue;
			}
			char spec = tmpl[++i];
			switch (spec) {
			case 'N':
				result += o->name();
				break;
			case 'G':
				result += o->guid();
				break;
			case 'g':
				try {
					result += IfcParse::IfcGlobalId(o->guid()).formatted();
				} catch (const std::exception&) {
					result += o->guid();
				}
				break;
			case 'T':
				result += o->type();
				break;
			case 't': {
				const IfcUtil::IfcBaseEntity* product = o->product();
				const IfcParse::entity* decl = product ? product->declaration().as_entity() : nullptr;
				ptrdiff_t idx = decl ? decl->attribute_index("Tag") : -1;
				if (idx >= 0) {
					AttributeValue v = product->get_attribute_value((size_t) idx);
					if (!v.isNull()) {
						try {
							result += (std::string) v;
						} catch (const std::exception&) {
						}
					}
				}
				break;
			}
			case 'i':
				result += boost::lexical_cast<std::string>(o->id());
				break;
			case 'u':
				result += o->unique_id();
				break;
			case '%':
				result += '%';
				break;
			default:
				result += '%';
				result += spec;
				break;
			}
		}
		return result;
	}

}
}

class stream_or_filename {
private:
	std::shared_ptr<std::ofstream> ofs_;
	std::shared_ptr<std::ostringstream> oss_;
	boost::optional<std::string> filename_;

public:
	std::ostream& stream;

	stream_or_filename(const std::string& fn)
		: ofs_(new std::ofstream(IfcUtil::path::from_utf8(fn).c_str()))
		, stream(*ofs_)
	{}

	stream_or_filename()
		: oss_(new std::ostringstream)
		, stream(*oss_)
	{}

	std::string get_value() const {
		return oss_->str();
	}

	boost::optional<std::string> filename() const {
		return filename_;
	}

	bool is_ready() {
		if (ofs_) {
			return ofs_->is_open();
		} else {
			return true;
		}
	}
};

class GeometrySerializer : public Serializer {
public:
	enum read_type { READ_BREP, READ_TRIANGULATION };

    GeometrySerializer(const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings, Logger& logger = Logger::Root())
		: Serializer(logger)
		, geometry_settings_(geometry_settings)
		, settings_(settings)
	{}
	virtual ~GeometrySerializer() {} 

	virtual bool isTesselated() const = 0;
	virtual void write(const IfcGeom::TriangulationElement* o) = 0;
	virtual void write(const IfcGeom::BRepElement* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;
	virtual IfcGeom::Element* read(IfcParse::IfcFile& f, const std::string& guid, const std::string& representation_id, read_type rt = READ_BREP) = 0;

    const ifcopenshell::geometry::SerializerSettings& settings() const { return settings_; }
	ifcopenshell::geometry::SerializerSettings& settings() { return settings_; }

	const ifcopenshell::geometry::Settings& geometry_settings() const { return geometry_settings_; }
	ifcopenshell::geometry::Settings& geometry_settings() { return geometry_settings_; }

    /// Returns ID for the object depending on the used setting.
    virtual std::string object_id(const IfcGeom::Element* o)
    {
        if (settings_.get<ifcopenshell::geometry::settings::NameTemplate>().has()) {
            return ifcopenshell::geometry::format_name_template(settings_.get<ifcopenshell::geometry::settings::NameTemplate>().get(), o);
        }
        if (settings_.get<ifcopenshell::geometry::settings::UseElementGuids>().get()) return o->guid();
        if (settings_.get<ifcopenshell::geometry::settings::UseElementNames>().get()) return o->name();
		if (settings_.get<ifcopenshell::geometry::settings::UseElementStepIds>().get()) return "id-" + boost::lexical_cast<std::string>(o->id());
		return o->unique_id();
    }

protected:
	ifcopenshell::geometry::Settings geometry_settings_;
	ifcopenshell::geometry::SerializerSettings settings_;
};

class WriteOnlyGeometrySerializer : public GeometrySerializer {
public:
	WriteOnlyGeometrySerializer(const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings, Logger& logger = Logger::Root()) : GeometrySerializer(geometry_settings, settings, logger) {}

	virtual IfcGeom::Element* read(IfcParse::IfcFile&, const std::string&, const std::string&, read_type = READ_BREP) {
		throw std::runtime_error("Not supported");
	};
};

#endif
