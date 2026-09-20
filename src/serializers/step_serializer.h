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

#ifndef STEPSERIALIZER_H
#define STEPSERIALIZER_H

#include <STEPControl_Writer.hxx>
#include <Interface_Static.hxx>

#include "../ifcgeom/iterator.h"

#include "../serializers/open_cascade_based_serializer.h"

class step_serializer : public open_cascade_based_serializer
{
private:
	STEPControl_Writer writer;
public:
	explicit step_serializer(const std::string& out_filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr)
		: open_cascade_based_serializer(out_filename, settings, logger)
	{}
	virtual ~step_serializer() {}
	void writeShape(const std::string& name, const TopoDS_Shape& shape) {
		std::stringstream ss;
		std::streambuf *sb = std::cout.rdbuf(ss.rdbuf());
		Interface_Static::SetCVal("write.step.product.name", name.c_str());
		writer.Transfer(shape, STEPControl_AsIs);
		std::cout.rdbuf(sb);
	}
	void finalize() {
		std::stringstream ss;
		std::streambuf *sb = std::cout.rdbuf(ss.rdbuf());
		writer.Write(out_filename.c_str());
		std::cout.rdbuf(sb);
	}
	void setUnitNameAndMagnitude(const std::string& /*name*/, float magnitude) {
		const char* symbol = getSymbolForUnitMagnitude(magnitude);
		if (symbol) {
			// Interface_Static::SetCVal("xstep.cascade.unit", symbol);
			Interface_Static::SetCVal("write.step.unit", symbol);
		}
	}
};

#endif
#endif
