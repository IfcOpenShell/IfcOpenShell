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
 * This examples exposes the IfcOpenShell API through a command-based stdin     *
 * interface                                                                    *
 *                                                                              *
 ********************************************************************************/

#include <iostream>

#include "../ifcparse/IfcGeomObjects.h"

#if defined(WIN32) && !defined(__CYGWIN__)
#include <io.h>
#include <fcntl.h>
#endif

int main ( int argc, char** argv ) {
#if defined(WIN32) && !defined(__CYGWIN__)
	_setmode(_fileno(stdout), _O_BINARY);
	std::cout.setf(std::ios_base::binary);
#endif
	bool has_more = false;
	std::cout.write("IfcOpenShell-0.2.0",18);
	std::cout.flush();
	const IfcGeomObjects::IfcGeomObject* ifc_geom = 0;
	while (1) {
		std::string command;
		std::cin >> command;
		if ( command == "load" ) {
			std::string fn;
			std::getline(std::cin,fn);
			fn = fn.erase(0,fn.find_first_not_of(" "));
			has_more = IfcGeomObjects::Init(fn.c_str(),true,0,&std::cerr);
			std::cout.write(has_more ? "y" : "n",1);
			std::cout.flush();
		} else if ( command == "loadstdin" ) {
			std::cout << "ok" << std::flush;
			int len;
			std::cin >> len;
			std::cout << "ok" << std::flush;
			has_more = IfcGeomObjects::Init(std::cin,len,true,0,&std::cerr);
			std::cout.write(has_more ? "y" : "n",1);
			std::cout.flush();
		} else if ( command == "get" ) {
			if ( !has_more ) {
				std::cout << "Not loaded" << std::flush;
			} else {
				ifc_geom = IfcGeomObjects::Get();
				const int vcount = ifc_geom->mesh->verts.size() / 3;
				std::cout.write((char*)&vcount,sizeof(int));
				std::cout.write((char*)&ifc_geom->mesh->verts[0],sizeof(float)*vcount*3);
				const int fcount = ifc_geom->mesh->faces.size() / 3;
				std::cout.write((char*)&fcount,sizeof(int));
				std::cout.write((char*)&ifc_geom->mesh->faces[0],sizeof(int)*fcount*3);
				std::cout.flush();
			}
		} else if ( command == "type" ) {
			if ( ! ifc_geom ) {
				std::cout << "Not loaded" << std::flush;
			} else {
				std::cout << ifc_geom->type << std::flush;			
			}
		} else if ( command == "guid" ) {
			if ( ! ifc_geom ) {
				std::cout << "Not loaded" << std::flush;
			} else {
				std::cout << ifc_geom->name << std::flush;			
			}
		} else if ( command == "next" ) {
			if ( !has_more ) {
				std::cout << "Not loaded" << std::flush;
			} else {
				has_more = IfcGeomObjects::Next();
				std::cout.write(has_more ? "y" : "n",1);
				std::cout.flush();
			}
		} else if ( command == "quit" || command == "exit" ) {
			std::cout << "Bye" << std::flush;
			break;
		} else {
			std::cout << "Unknown command " << command << std::flush;
		}
	}
}
