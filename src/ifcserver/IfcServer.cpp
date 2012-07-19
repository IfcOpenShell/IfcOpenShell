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

#include "../ifcgeom/IfcGeomObjects.h"

#if defined(WIN32) && !defined(__CYGWIN__)
#include <io.h>
#include <fcntl.h>
#endif

#define PRODUCT ("IfcOpenShell-0.2.3")
#define ACK ("y")
#define NEG ("n")
#define CONFIRM ("ok")
#define CLOSED ("No opened file")
#define QUIT ("Bye :)")
#define UNKNOWN ("Unknown command")

void send_msg(const char* c) {
	std::cout.write(c,strlen(c));
	std::cout.flush();
}

void send_msg(const std::string& s) {
	std::cout << s << std::flush;
}

int main ( int argc, char** argv ) {
#if defined(WIN32) && !defined(__CYGWIN__)
	_setmode(_fileno(stdout), _O_BINARY);
	std::cout.setf(std::ios_base::binary);
#endif
	bool has_more = false;
	send_msg(PRODUCT);
	const IfcGeomObjects::IfcGeomObject* ifc_geom = 0;
	while (1) {
		std::string command;
		std::cin >> command;
		if ( command == "load" ) {
			std::string fn;
			std::getline(std::cin,fn);
			fn = fn.erase(0,fn.find_first_not_of(" "));
			has_more = IfcGeomObjects::Init(fn.c_str(),true,0,&std::cerr);
			send_msg(has_more ? ACK : NEG);
		} else if ( command == "loadstdin" ) {
			send_msg(CONFIRM);
			int len;
			std::cin >> len;
			send_msg(CONFIRM);
			has_more = IfcGeomObjects::Init(std::cin,len,true,0,&std::cerr);
			send_msg(has_more ? ACK : NEG);
		} else if ( command == "get" ) {
			if ( ! has_more ) send_msg(CLOSED);
			else {
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
			if ( ifc_geom ) send_msg(ifc_geom->type);
			else send_msg(CLOSED);
		} else if ( command == "guid" ) {
			if ( ifc_geom ) send_msg(ifc_geom->guid);
			else send_msg(CLOSED);
		} else if ( command == "next" ) {
			if ( !has_more ) send_msg(CLOSED);
			else {
				has_more = IfcGeomObjects::Next();
				if ( ! has_more )
					IfcGeomObjects::CleanUp();
				send_msg(has_more ? ACK : NEG);
			}
		} else if ( command == "quit" || command == "exit" ) {
			send_msg(QUIT);
			break;
		} else {
			send_msg(UNKNOWN);
		}
	}
	return 0;
}
