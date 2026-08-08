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

#include "../ifcgeom/serializer.h"
#include "../ifcgeom/element.h"
#include "../ifcparse/logger.h"
#include <fstream>

class IFC_GEOM_API stream_or_filename {
private:
	std::shared_ptr<std::ofstream> ofs_;
	std::shared_ptr<std::ostringstream> oss_;
	std::optional<std::string> filename_;

public:
	std::ostream& stream;

	stream_or_filename(const std::string& fn)
		: ofs_(new std::ofstream(ifcopenshell::path::from_utf8(fn).c_str()))
		, filename_(fn)
		, stream(*ofs_)
	{}

	stream_or_filename()
		: oss_(new std::ostringstream)
		, stream(*oss_)
	{}

	std::string get_value() const {
		return oss_->str();
	}

	std::optional<std::string> filename() const {
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

namespace ifcopenshell::geom {

class IFC_GEOM_API geometry_serializer : public serializer {
public:
	enum read_type { READ_BREP, READ_TRIANGULATION };

    geometry_serializer(const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr)
        : serializer(ifcopenshell::logger_or_root(logger))
		, settings_(settings)
	{}
	virtual ~geometry_serializer() {}

	virtual bool isTesselated() const = 0;
	virtual void write(const ifcopenshell::geom::triangulation_element* o) = 0;
	virtual void write(const ifcopenshell::geom::brep_element* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;
	virtual ifcopenshell::geom::element* read(ifcopenshell::file& f, const std::string& guid, const std::string& representation_id, read_type rt = READ_BREP) = 0;

    const ifcopenshell::geom::settings& settings() const { return settings_; }
	ifcopenshell::geom::settings& settings() { return settings_; }

    /// Returns ID for the object depending on the used setting.
    virtual std::string object_id(const ifcopenshell::geom::element* o)
    {
        if (settings_.get<ifcopenshell::geom::settings::UseElementGuids>().get()) return o->guid();
        if (settings_.get<ifcopenshell::geom::settings::UseElementNames>().get()) return o->name();
		if (settings_.get<ifcopenshell::geom::settings::UseElementStepIds>().get()) return "id-" + boost::lexical_cast<std::string>(o->id());
		return o->unique_id();
    }

protected:
	ifcopenshell::geom::settings settings_;
};

class IFC_GEOM_API write_only_geometry_serializer : public geometry_serializer {
public:
	write_only_geometry_serializer(const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr) : geometry_serializer(settings, logger) {}

	virtual ifcopenshell::geom::element* read(ifcopenshell::file&, const std::string&, const std::string&, read_type = READ_BREP) {
		throw std::runtime_error("Not supported");
	};
};

} // namespace ifcopenshell::geom

#endif
