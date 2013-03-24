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

/********************************************************************************
 *                                                                              *
 * This file defines default materials for several IFC datatypes                *
 *                                                                              *
 ********************************************************************************/

#ifndef SURFACESTYLE_H
#define SURFACESTYLE_H

#include <string>
#include <sstream>

#include <array>

class SurfaceStyle {
public:
	class ColorComponent {
	private:
		std::array<double, 3> data;
	public:
		ColorComponent(double r, double g, double b) {
			data[0] = r; data[1] = g; data[2] = b;
		}
		const double& R() const { return data[0]; }
		const double& G() const { return data[1]; }
		const double& B() const { return data[2]; }
		double& R() { return data[0]; }
		double& G() { return data[1]; }
		double& B() { return data[2]; }
	};
private:
	std::string name;
	ColorComponent diffuse, specular, ambient;
	double transparency;
	double specularity;
public:
	SurfaceStyle(const std::string& name,
				 double dr = 0.7,  double dg = 0.7, double db = 0.7,
			 	 double sr = 0.2,  double sg = 0.2, double sb = 0.2, 
			 	 double ar = 0.1,  double ag = 0.1, double ab = 0.1,
				 double Ns = 10.0, double Tr = 1.0)
		: name(name) 
		, diffuse(dr, dg, db)
		, specular(sr, sg, sb)
		, ambient(ar, ag, ab)
		, transparency(Tr)
		, specularity(Ns)
	{}
	const std::string& Name() const { return name; }
	const ColorComponent& Diffuse() const { return diffuse; }
	const ColorComponent& Specular() const { return specular; }
	const ColorComponent& Ambient() const { return ambient; }
	double Transparency() const { return transparency; }
	double Specularity() const { return specularity; }
};

SurfaceStyle GetDefaultMaterial(const std::string& s);

#endif