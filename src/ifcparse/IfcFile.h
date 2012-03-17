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

const int BUF_SIZE = (128 * 1024 * 1024);

namespace IfcParse {
	/// The File class represents a ISO 10303-21 IFC-SPF file in memory.
	/// The file is interpreted as a sequence of tokens which are lazily
	/// interpreted only when requested. If the size of the file is
	/// larger than BUF_SIZE, the file is split into seperate pages, of
	/// which only one is simultaneously kept in memory, for files
	/// that define their entities not in a sequential nature, this is
	/// detrimental for the performance of the parser.
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
		File(void* data, int len);
		/// Returns the character at the cursor 
		char Peek();
		/// Returns the character at specified offset
		char Read(unsigned int offset);
		/// Increment the file cursor and reads new page if necessary
		void Inc();
		void Close();
		/// Moves the file cursor to an arbitrary offset in the file
		void Seek(unsigned int offset);
		/// Returns the cursor position
		unsigned int Tell();
	};
}

#endif
