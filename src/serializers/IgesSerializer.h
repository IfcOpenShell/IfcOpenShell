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

#include "OpenCascadeBasedSerializer.h"
#include "../ifcparse/IfcLogger.h"

#include <IGESControl_Writer.hxx>

#ifndef HAVE_CONFIG_H
/// @note this is brittle, but apparently the only way to differentiate OCCT
/// from OCE. In the latter including this header fails for some versions.
#include <Interface_Static.hxx>
#endif

class IgesSerializer : public OpenCascadeBasedSerializer
{
private:
	IGESControl_Writer writer;
public:
    /// @note IGESControl_Controller::Init() must be called prior to instantiating IgesSerializer.
    /// See http://tracker.dev.opencascade.org/view.php?id=23679 for more information.
    IgesSerializer(const std::string& out_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
        : OpenCascadeBasedSerializer(out_filename, geometry_settings, settings)
	{}
	virtual ~IgesSerializer() {}
	void writeShape(const std::string&, const TopoDS_Shape& shape) {
		writer.AddShape(shape);
	}
	void finalize() {
		writer.Write(out_filename.c_str());
	}
	void setUnitNameAndMagnitude(const std::string& /*name*/, float magnitude) {
		const char* symbol = getSymbolForUnitMagnitude(magnitude);
		if (symbol) {
#ifdef HAVE_CONFIG_H
			Logger::Warning("Setting IGES units not supported on OCE");
#else
			Interface_Static::SetCVal("xstep.cascade.unit", symbol);
			Interface_Static::SetCVal("write.iges.unit", symbol);
#endif
		}
	}
};

#endif
#endif
