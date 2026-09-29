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

#ifndef IGESSERIALIZER_H
#define IGESSERIALIZER_H

#include "open_cascade_based_serializer.h"
#include "../ifcparse/logger.h"

#include <IGESControl_Writer.hxx>
#include <Interface_Static.hxx>

class iges_serializer : public open_cascade_based_serializer
{
private:
	IGESControl_Writer writer;
public:
    /// @note IGESControl_Controller::Init() must be called prior to instantiating iges_serializer.
    /// See http://tracker.dev.opencascade.org/view.php?id=23679 for more information.
    iges_serializer(const std::string& out_filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr)
        : open_cascade_based_serializer(out_filename, settings, logger)
	{}
	virtual ~iges_serializer() {}
	void writeShape(const std::string&, const TopoDS_Shape& shape) {
		writer.AddShape(shape);
	}
	void finalize() {
		writer.Write(out_filename.c_str());
	}
	void setUnitNameAndMagnitude(const std::string& /*name*/, float magnitude) {
		const char* symbol = getSymbolForUnitMagnitude(magnitude);
		if (symbol) {
			Interface_Static::SetCVal("xstep.cascade.unit", symbol);
			Interface_Static::SetCVal("write.iges.unit", symbol);
		}
	}
};

#endif
#endif
