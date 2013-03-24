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

#ifndef IGESSERIALIZER_H
#define IGESSERIALIZER_H

#include <IGESControl_Controller.hxx>
#include <IGESControl_Writer.hxx>

#include "../ifcgeom/IfcGeomObjects.h"

#include "../ifcconvert/OpenCascadeBasedSerializer.h"

class IgesSerializer : public OpenCascadeBasedSerializer
{
private:
	IGESControl_Writer writer;	
public:
	explicit IgesSerializer(const std::string& out_filename) 
		: OpenCascadeBasedSerializer(out_filename) 
	{}
	virtual ~IgesSerializer() {}
	void writeShape(const TopoDS_Shape& shape) {
		writer.AddShape(shape);
	}
	void finalize() {
		writer.Write(out_filename.c_str());
	}
};

#endif