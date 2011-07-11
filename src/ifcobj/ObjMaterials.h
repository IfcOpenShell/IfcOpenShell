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
 * This file defines materials in .mtl format for several IFC datatypes         *
 *                                                                              *
 ********************************************************************************/

#include <string>
#include <sstream>

class ObjMaterial {
private:
	std::string data;
public:
	ObjMaterial(const std::string& name,
		float Kd_r = 0.7f,float Kd_g = 0.7f,float Kd_b = 0.7f,
		float Ks_r = 0.2f,float Ks_g = 0.2f,float Ks_b = 0.2f, 
		float Ka_r = 0.1f,float Ka_g = 0.1f,float Ka_b = 0.1f,
		float Ns = 10.0f, float Tr = 1.0f) {
			std::stringstream ss;
			ss << "newmtl " << name << std::endl;
			ss << "Kd " << Kd_r << " " << Kd_g << " " << Kd_b << std::endl;
			ss << "Ks " << Ks_r << " " << Ks_g << " " << Ks_b << std::endl;
			ss << "Ka " << Ka_r << " " << Ka_g << " " << Ka_b << std::endl;
			ss << "Ns " << Ns << std::endl;
			ss << "Tr " << Tr << std::endl;
			ss << "d " << Tr << std::endl;
			ss << "D " << Tr << std::endl;
			data = ss.str();
	}
	friend ostream& operator<<(ostream& o, const ObjMaterial& m) {o << m.data; return o;}
};

ObjMaterial GetMaterial(const std::string& s) {
	if ( s == "IfcSite" ) { return ObjMaterial("IfcSite",0.75f,0.8f,0.65f); }
	if ( s == "IfcSlab" ) { return ObjMaterial("IfcSlab",0.4f,0.4f,0.4f); }
	if ( s == "IfcWallStandardCase" ) { return ObjMaterial("IfcWallStandardCase",0.9f,0.9f,0.9f); }
	if ( s == "IfcWall" ) { return ObjMaterial("IfcWall",0.9f,0.9f,0.9f); }
	if ( s == "IfcWindow" ) { return ObjMaterial("IfcWindow",0.75f,0.8f,0.75f,1.0f,1.0f,1.0f,0.0f,0.0f,0.0f,500.0f,0.3f); }
	if ( s == "IfcDoor" ) { return ObjMaterial("IfcDoor",0.55f,0.3f,0.15f); }
	if ( s == "IfcBeam" ) { return ObjMaterial("IfcBeam",0.75f,0.7f,0.7f); }
	if ( s == "IfcRailing" ) { return ObjMaterial("IfcRailing",0.65f,0.6f,0.6f); }
	if ( s == "IfcMember" ) { return ObjMaterial("IfcMember",0.65f,0.6f,0.6f); }
	if ( s == "IfcPlate" ) { return ObjMaterial("IfcPlate",0.8f,0.8f,0.8f); }
	return ObjMaterial(s);
}