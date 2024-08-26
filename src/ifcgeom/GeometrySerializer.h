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
}

class SerializerSettings : public SettingsContainer <
	// @todo should we use tuple_cat here to unify the settings into a single class?
	std::tuple<UseElementNames, UseElementGuids, UseElementStepIds, UseElementTypes, UseYUp, WriteGltfEcef, FloatingPointDigits>
>
{};

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

    GeometrySerializer(const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
		: geometry_settings_(geometry_settings)
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
	WriteOnlyGeometrySerializer(const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings) : GeometrySerializer(geometry_settings, settings) {}

	virtual IfcGeom::Element* read(IfcParse::IfcFile&, const std::string&, const std::string&, read_type = READ_BREP) {
		throw std::runtime_error("Not supported");
	};
};

#endif
