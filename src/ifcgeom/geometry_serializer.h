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

// See ifcopenshell::geom::settings::NameTemplate for supported placeholders.
inline std::string format_name_template(const std::string& tmpl, const ifcopenshell::geom::element* o) {
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
				result += ifcopenshell::global_id(o->guid()).formatted();
			} catch (const std::exception&) {
				result += o->guid();
			}
			break;
		case 'T':
			result += o->type();
			break;
		case 't': {
			const express::entity& product = o->product();
			const ifcopenshell::entity* decl = product ? product.declaration().as_entity() : nullptr;
			ptrdiff_t idx = decl ? decl->attribute_index("Tag") : -1;
			if (idx >= 0) {
				ifcopenshell::attribute_value v = product.get_attribute_value((size_t) idx);
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
			result += std::to_string(o->id());
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
	virtual void write(const ifcopenshell::geom::native_element* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;
	virtual ifcopenshell::geom::element* read(ifcopenshell::file& f, const std::string& guid, const std::string& representation_id, read_type rt = READ_BREP) = 0;

    const ifcopenshell::geom::settings& settings() const { return settings_; }
	ifcopenshell::geom::settings& settings() { return settings_; }

    /// Returns ID for the object depending on the used setting.
    virtual std::string object_id(const ifcopenshell::geom::element* o)
    {
        if (settings_.get<ifcopenshell::geom::settings::NameTemplate>().has()) {
            return format_name_template(settings_.get<ifcopenshell::geom::settings::NameTemplate>().get(), o);
        }
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
