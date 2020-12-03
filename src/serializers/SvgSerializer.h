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

#include <HLRBRep_Algo.hxx>
#include <HLRBRep_HLRToShape.hxx>
#include <gp_Pln.hxx>

#include <sstream>
#include <string>
#include <limits>

typedef std::pair<IfcUtil::IfcBaseEntity*, std::string> drawing_key;

struct storey_sorter {
	bool operator()(const drawing_key& ad, const drawing_key& bd) const {
		if (ad.first == nullptr && bd.first != nullptr) {
			return false;
		} else if (bd.first == nullptr && ad.first != nullptr) {
			return true;
		} else if (ad.first == nullptr && bd.first == nullptr) {
			return std::less<std::string>()(ad.second, bd.second);
		}

		auto a = ad.first;
		auto b = bd.first;

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

struct horizontal_plan {
	IfcUtil::IfcBaseEntity* storey;
	double elevation, offset, next_elevation;
};

struct horizontal_plan_at_element {};

struct vertical_section {
	gp_Pln plane;
	std::string name;
	bool with_projection;
};

typedef boost::variant<horizontal_plan, horizontal_plan_at_element, vertical_section> section_data;

struct geometry_data {
	TopoDS_Shape compound_local;
	gp_Trsf trsf;
	IfcUtil::IfcBaseEntity* product;
	IfcUtil::IfcBaseEntity* storey;
	double storey_elevation;
	std::string ifc_name, svg_name;
};

class SvgSerializer : public GeometrySerializer {
public:
	typedef std::pair<std::string, std::vector<util::string_buffer> > path_object;
	typedef std::vector< boost::shared_ptr<util::string_buffer::float_item> > float_item_list;
protected:
	std::ofstream svg_file;
	double xmin, ymin, xmax, ymax, width, height;
	boost::optional<std::vector<section_data>> section_data_;
	boost::optional<std::vector<section_data>> deferred_section_data_;
	boost::optional<double> scale_, calculated_scale_, center_x_, center_y_;

	bool with_section_heights_from_storey_, rescale, print_space_names_, print_space_areas_;
	bool draw_door_arcs_, buffer_elements_, is_floor_plan_;

	IfcParse::IfcFile* file;
	IfcUtil::IfcBaseEntity* storey_;
	std::multimap<drawing_key, path_object, storey_sorter> paths;

	float_item_list xcoords, ycoords, radii;
	size_t xcoords_begin, ycoords_begin, radii_begin;

	boost::optional<std::string> section_ref_, elevation_ref_;
	
	std::list<geometry_data> element_buffer_;

	Handle(HLRBRep_Algo) hlr;
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
		, buffer_elements_(false)
		, is_floor_plan_(true)
		, file(0)
		, storey_(0)
		, xcoords_begin(0)
		, ycoords_begin(0)
		, radii_begin(0)
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
	void write(const geometry_data& data);
    path_object& start_path(IfcUtil::IfcBaseEntity* storey, const std::string& id);
	path_object& start_path(const std::string& drawing_name, const std::string& id);
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
	void resize();
	void setSectionRef(const boost::optional<std::string>& s) { 
		section_ref_ = s; 
		buffer_elements_ = true;
	}
	void setElevationRef(const boost::optional<std::string>& s) {
		elevation_ref_ = s; 
		buffer_elements_ = true;
	}
	void setScale(double s) { scale_ = s; }
	void setDrawingCenter(double x, double y) {
		center_x_ = x; center_y_ = y;
	}
    std::string nameElement(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element<real_t>* elem);
	std::string nameElement(const IfcUtil::IfcBaseEntity* elem);
	std::string idElement(const IfcUtil::IfcBaseEntity* elem);
	std::string object_id(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element<real_t>* o) {
		if (storey) {
			return idElement(storey) + "-" + GeometrySerializer::object_id(o);
		} else {
			return GeometrySerializer::object_id(o);
		}
	}
};

#endif
