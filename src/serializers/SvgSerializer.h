/********************************************************************************
 *                                                                              *
 * Copyright 2015 IfcOpenShell and ROOT B.V.                                    *
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

#ifndef SVGSERIALIZER_H
#define SVGSERIALIZER_H

#include "../serializers/GeometrySerializer.h"
#include "../serializers/util.h"

#include "../ifcparse/utils.h"
#include "../ifcgeom/abstract_mapping.h"

#include <sstream>
#include <string>
#include <limits>

class SvgSerializer : public GeometrySerializer {
public:
	typedef std::pair<std::string, std::vector<util::string_buffer> > path_object;
protected:
	std::ofstream svg_file;
	double xmin, ymin, xmax, ymax, width, height;
	boost::optional<double> section_height;
	bool rescale;
	std::multimap<IfcUtil::IfcBaseEntity*, path_object> paths;
	std::vector< boost::shared_ptr<util::string_buffer::float_item> > xcoords;
	std::vector< boost::shared_ptr<util::string_buffer::float_item> > ycoords;
	std::vector< boost::shared_ptr<util::string_buffer::float_item> > radii;
	IfcParse::IfcFile* file;
	IfcUtil::IfcBaseEntity* storey_;
	ifcopenshell::geometry::abstract_mapping* mapping_;
public:
	SvgSerializer(const std::string& out_filename, const SerializerSettings& settings)
		: GeometrySerializer(settings)
		, svg_file(IfcUtil::path::from_utf8(out_filename).c_str())
		, xmin(+std::numeric_limits<double>::infinity())
		, ymin(+std::numeric_limits<double>::infinity())
		, xmax(-std::numeric_limits<double>::infinity())
		, ymax(-std::numeric_limits<double>::infinity())
		, rescale(false)
		, file(0)
		, storey_(0)
	{}
    void addXCoordinate(const boost::shared_ptr<util::string_buffer::float_item>& fi) { xcoords.push_back(fi); }
    void addYCoordinate(const boost::shared_ptr<util::string_buffer::float_item>& fi) { ycoords.push_back(fi); }
    void addSizeComponent(const boost::shared_ptr<util::string_buffer::float_item>& fi) { radii.push_back(fi); }
    void growBoundingBox(double x, double y) { if (x < xmin) xmin = x; if (x > xmax) xmax = x; if (y < ymin) ymin = y; if (y > ymax) ymax = y; }
    void writeHeader();
    bool ready();
    void write(const ifcopenshell::geometry::TriangulationElement* /*o*/) {}
    void write(const ifcopenshell::geometry::NativeElement* o);
    void write(path_object& p, const TopoDS_Wire& wire);
    path_object& start_path(IfcUtil::IfcBaseEntity* storey, const std::string& id);
    bool isTesselated() const { return false; }
    void finalize();
    void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile* f);
    void setBoundingRectangle(double width, double height);
	void setSectionHeight(double h, IfcUtil::IfcBaseEntity* storey = 0) { section_height = h; storey_ = storey; }
    std::string nameElement(const ifcopenshell::geometry::Element* elem);
    std::string nameElement(const IfcUtil::IfcBaseEntity* elem);
};

#endif
