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

#ifdef IFOPSH_WITH_OPENCASCADE

#ifndef OPENCASCADEBASEDSERIALIZER_H
#define OPENCASCADEBASEDSERIALIZER_H

#include "../serializers/serializers_api.h"
#include "../ifcgeom/Iterator.h"

#include "../ifcgeom/GeometrySerializer.h"

#include <TopoDS_Shape.hxx>

class SERIALIZERS_API open_cascade_based_serializer : public ifcopenshell::geom::write_only_geometry_serializer {
	open_cascade_based_serializer(const open_cascade_based_serializer&); //N/A
	open_cascade_based_serializer& operator =(const open_cascade_based_serializer&); //N/A
protected:
	const std::string out_filename;
	const char* getSymbolForUnitMagnitude(float mag);
public:
	explicit open_cascade_based_serializer(const std::string& out_filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr)
		: ifcopenshell::geom::write_only_geometry_serializer(settings, logger)
		, out_filename(out_filename)
	{}
	virtual ~open_cascade_based_serializer() {}
	void writeHeader() {}
	bool ready();
	virtual void writeShape(const std::string& name, const TopoDS_Shape& shape) = 0;
	void write(const ifcopenshell::geom::triangulation_element* /*o*/) {}
	void write(const ifcopenshell::geom::brep_element* o);
	bool isTesselated() const { return false; }
	void setFile(ifcopenshell::file&) {}
};

#endif
#endif
