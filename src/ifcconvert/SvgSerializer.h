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

#include <sstream>
#include <string>
#include <limits>

#include "../ifcgeom/IfcGeomIterator.h"

#include "../ifcconvert/GeometrySerializer.h"
#include "../ifcconvert/util.h"

class SvgSerializer : public GeometrySerializer {
public:
	typedef std::pair<std::string, std::vector<util::string_buffer> > path_object;
protected:
	const char* getSymbolForUnitMagnitude(float mag);
	std::ofstream svg_file;
	double xmin, ymin, xmax, ymax, width, height;
	boost::optional<double> section_height;
	bool rescale;
	std::multimap<IfcSchema::IfcBuildingStorey*, path_object> paths;
	std::vector< SHARED_PTR<util::string_buffer::float_item> > xcoords;
	std::vector< SHARED_PTR<util::string_buffer::float_item> > ycoords;
	std::vector< SHARED_PTR<util::string_buffer::float_item> > radii;
	IfcParse::IfcFile* file;
public:
	explicit SvgSerializer(const std::string& out_filename)
		: GeometrySerializer()
		, svg_file(out_filename.c_str())
		, xmin(+std::numeric_limits<double>::infinity())
		, xmax(-std::numeric_limits<double>::infinity())
		, ymin(+std::numeric_limits<double>::infinity())
		, ymax(-std::numeric_limits<double>::infinity())
		, rescale(false)
		, file(0)
	{}
	virtual void addXCoordinate(const SHARED_PTR<util::string_buffer::float_item>& fi) { xcoords.push_back(fi); }
	virtual void addYCoordinate(const SHARED_PTR<util::string_buffer::float_item>& fi) { ycoords.push_back(fi); }
	virtual void addSizeComponent(const SHARED_PTR<util::string_buffer::float_item>& fi) { radii.push_back(fi); }
	virtual ~SvgSerializer() {}
	virtual void writeHeader();
	virtual void writeMaterial(const IfcGeom::SurfaceStyle& style) {}
	virtual bool ready();
	virtual void write(const IfcGeom::TriangulationElement<double>* o) {}
	virtual void write(const IfcGeom::BRepElement<double>* o);
	virtual void write(path_object& p, const TopoDS_Wire& wire);
	virtual path_object& start_path(IfcSchema::IfcBuildingStorey* storey, const std::string& id);
	virtual bool isTesselated() const { return false; }
	virtual void finalize();
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) {}
	virtual void setFile(IfcParse::IfcFile* f) { file = f; }
	virtual void setBoundingRectangle(double width, double height);
	virtual void setSectionHeight(double h) { section_height = h; }
};

#endif
