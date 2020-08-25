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

#include <sstream>
#include <string>
#include <limits>

struct storey_sorter {
	bool operator()(IfcUtil::IfcBaseEntity* a, IfcUtil::IfcBaseEntity* b) const {
		const bool a_is_storey = a->declaration().is("IfcBuildingStorey");
		const bool b_is_storey = b->declaration().is("IfcBuildingStorey");
		if (a_is_storey && b_is_storey) {
			boost::optional<double> a_elev, b_elev;
			try {
				a_elev = static_cast<double>(*a->get("Elevation"));
				b_elev = static_cast<double>(*b->get("Elevation"));
			} catch (...) {};
			if (a_elev && b_elev) {
				if (std::equal_to<double>()(*a_elev, *b_elev)) {
					return std::less<unsigned int>()(a->data().id(), b->data().id());
				} else {
					return std::less<double>()(*a_elev, *b_elev);
				}
			}

			boost::optional<std::string> a_name, b_name;
			try {
				a_name = static_cast<std::string>(*a->get("Name"));
				b_name = static_cast<std::string>(*b->get("Name"));
			} catch (...) {};
			if (a_name && b_name) {
				if (std::equal_to<std::string>()(*a_name, *b_name)) {
					return std::less<unsigned int>()(a->data().id(), b->data().id());
				} else {
					return std::less<std::string>()(*a_name, *b_name);
				}
			}
		}
		return std::less<IfcUtil::IfcBaseEntity*>()(a, b);
	}
};

class SvgSerializer : public GeometrySerializer {
public:
	typedef std::pair<std::string, std::vector<util::string_buffer> > path_object;
protected:
	std::ofstream svg_file;
	double xmin, ymin, xmax, ymax, width, height;
	boost::optional<std::vector<std::pair<std::pair<double, double>, IfcUtil::IfcBaseEntity*>>> section_heights;
	boost::optional<double> scale_;
	bool rescale, print_space_names_, print_space_areas_, draw_door_arcs_, with_section_heights_from_storey_;
	std::multimap<IfcUtil::IfcBaseEntity*, path_object, storey_sorter> paths;
	std::vector< boost::shared_ptr<util::string_buffer::float_item> > xcoords;
	std::vector< boost::shared_ptr<util::string_buffer::float_item> > ycoords;
	std::vector< boost::shared_ptr<util::string_buffer::float_item> > radii;
	IfcParse::IfcFile* file;
	IfcUtil::IfcBaseEntity* storey_;
public:
	SvgSerializer(const std::string& out_filename, const SerializerSettings& settings)
		: GeometrySerializer(settings)
		, svg_file(IfcUtil::path::from_utf8(out_filename).c_str())
		, xmin(+std::numeric_limits<double>::infinity())
		, ymin(+std::numeric_limits<double>::infinity())
		, xmax(-std::numeric_limits<double>::infinity())
		, ymax(-std::numeric_limits<double>::infinity())
		, with_section_heights_from_storey_(false)
		, rescale(false)
		, print_space_names_(false)
		, print_space_areas_(false)
		, draw_door_arcs_(false)
		, file(0)
		, storey_(0)
	{}
    void addXCoordinate(const boost::shared_ptr<util::string_buffer::float_item>& fi) { xcoords.push_back(fi); }
    void addYCoordinate(const boost::shared_ptr<util::string_buffer::float_item>& fi) { ycoords.push_back(fi); }
    void addSizeComponent(const boost::shared_ptr<util::string_buffer::float_item>& fi) { radii.push_back(fi); }
    void growBoundingBox(double x, double y) { if (x < xmin) xmin = x; if (x > xmax) xmax = x; if (y < ymin) ymin = y; if (y > ymax) ymax = y; }
    void writeHeader();
    bool ready();
    void write(const IfcGeom::TriangulationElement<real_t>* /*o*/) {}
    void write(const IfcGeom::BRepElement<real_t>* o);
    void write(path_object& p, const TopoDS_Wire& wire);
    path_object& start_path(IfcUtil::IfcBaseEntity* storey, const std::string& id);
    bool isTesselated() const { return false; }
    void finalize();
    void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile* f);
    void setBoundingRectangle(double width, double height);
	void setSectionHeight(double h, IfcUtil::IfcBaseEntity* storey = 0);
	void setSectionHeightsFromStoreys(double offset=1.);
	void setPrintSpaceNames(bool b) { print_space_names_ = b; }
	void setPrintSpaceAreas(bool b) { print_space_areas_ = b; }
	void setDrawDoorArcs(bool b) { draw_door_arcs_ = b; }
	void setScale(double s) { scale_ = s; }
    std::string nameElement(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element<real_t>* elem);
	std::string nameElement(const IfcUtil::IfcBaseEntity* elem);
	std::string idElement(const IfcUtil::IfcBaseEntity* elem);
	std::string object_id(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element<real_t>* o) {
		return idElement(storey) + "-" + GeometrySerializer::object_id(o);
	}
};

#endif
