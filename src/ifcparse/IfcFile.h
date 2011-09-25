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
 *                                                                               *
 * Reads a file in chunks of BUF_SIZE and provides functions to access its       *
 * contents randomly and character by character                                  *
 *                                                                               *
 ********************************************************************************/
 
#ifndef IFCFILE_H
#define IFCFILE_H

#include <fstream>
#include <string>

const int BUF_SIZE = (32 * 1024 * 1024);

namespace IfcParse {

	class File {
	private:
		std::ifstream stream;
		char* buffer;
		unsigned int ptr;
		unsigned int len;
		unsigned int offset;
		void ReadBuffer(bool inc=true);
		bool paging;
	public:
		bool valid;
		bool eof;
		unsigned int size;
		File(const std::string& fn);
		File(std::istream& f, int len);
		char Peek();
		char Read(unsigned int offset);
		void Inc();		
		void Close();
		void Seek(unsigned int offset);
		unsigned int Tell();
	};
}

#endif
