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

#include "../ifcgeom_schema_agnostic/Serializer.h"
#include "../ifcgeom_schema_agnostic/IfcGeomElement.h"

class SerializerSettings : public IfcGeom::IteratorSettings
{
public:
    enum Setting : uint64_t
    {
        /// Use entity names instead of unique IDs for naming elements.
        /// Applicable for OBJ, DAE, and SVG output.
        USE_ELEMENT_NAMES = 1U << (IfcGeom::IteratorSettings::NUM_SETTINGS + 1U),
        /// Use entity GUIDs instead of unique IDs for naming elements.
        /// Applicable for OBJ, DAE, and SVG output.
        USE_ELEMENT_GUIDS = 1U << (IfcGeom::IteratorSettings::NUM_SETTINGS + 2U),
        /// Use material names instead of unique IDs for naming materials.
        /// Applicable for OBJ and DAE output.
        USE_MATERIAL_NAMES = 1U << (IfcGeom::IteratorSettings::NUM_SETTINGS + 3U),
		/// Use element types instead of unique IDs for naming elements.
		/// Applicable for DAE output.
		USE_ELEMENT_TYPES = 1U << (IfcGeom::IteratorSettings::NUM_SETTINGS + 4U),
		/// Order the elements using their IfcBuildingStorey parent
		/// Applicable for DAE output
		USE_ELEMENT_HIERARCHY = 1U << (IfcGeom::IteratorSettings::NUM_SETTINGS + 5U),
        /// Use step ids for naming elements.
		/// Applicable for OBJ, DAE, and SVG output.
		USE_ELEMENT_STEPIDS = 1U << (IfcGeom::IteratorSettings::NUM_SETTINGS + 6U),
		/// Use Y UP .
		/// Applicable for OBJ output.
		USE_Y_UP = 1ULL << (IfcGeom::IteratorSettings::NUM_SETTINGS + 7ULL),
		/// Number of different setting flags.
        NUM_SETTINGS = 7
    };

    SerializerSettings()
        : precision(DEFAULT_PRECISION) { }

    /// Sets the precision used to format floating-point values, 15 by default.
    /// Use a negative value to use the system's default precision (should be 6 typically).
    short precision;

    enum { DEFAULT_PRECISION = 15 };
};

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

    GeometrySerializer(const SerializerSettings& settings) : settings_(settings) {}
	virtual ~GeometrySerializer() {} 

	virtual bool isTesselated() const = 0;
	virtual void write(const IfcGeom::TriangulationElement* o) = 0;
	virtual void write(const IfcGeom::BRepElement* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;
	virtual IfcGeom::Element* read(IfcParse::IfcFile& f, const std::string& guid, const std::string& representation_id, read_type rt = READ_BREP) = 0;

    const SerializerSettings& settings() const { return settings_; }
    SerializerSettings& settings() { return settings_; }

    /// Returns ID for the object depending on the used setting.
    virtual std::string object_id(const IfcGeom::Element* o)
    {
        if (settings_.get(SerializerSettings::USE_ELEMENT_GUIDS)) return o->guid();
        if (settings_.get(SerializerSettings::USE_ELEMENT_NAMES)) return o->name();
		if (settings_.get(SerializerSettings::USE_ELEMENT_STEPIDS)) return "id-" + boost::lexical_cast<std::string>(o->id());
		return o->unique_id();
    }

protected:
    SerializerSettings settings_;
};

class WriteOnlyGeometrySerializer : public GeometrySerializer {
public:
	WriteOnlyGeometrySerializer(const SerializerSettings& settings) : GeometrySerializer(settings) {}

	virtual IfcGeom::Element* read(IfcParse::IfcFile&, const std::string&, const std::string&, read_type = READ_BREP) {
		throw std::runtime_error("Not supported");
	};
};

#endif
