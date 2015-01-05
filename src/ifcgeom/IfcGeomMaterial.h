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

#ifndef IFCGEOMMATERIAL_H
#define IFCGEOMMATERIAL_H

#include <string>

#include "../ifcgeom/IfcGeomRenderStyles.h"

namespace IfcGeom {	

	class Material {
	private:
		const IfcGeom::SurfaceStyle* style;
	public:
		explicit Material(const IfcGeom::SurfaceStyle* style = 0); // TODO default constructor for vector?
		// Material(const Material& other);
		// Material& operator=(const Material& other);
		bool hasDiffuse() const;
		bool hasSpecular() const;
		bool hasTransparency() const;
		bool hasSpecularity() const;
		const double* diffuse() const;
		const double* specular() const;
		double transparency() const;
		double specularity() const;
		const std::string name() const;
		bool operator==(const Material& other) const;
	};

}

#endif