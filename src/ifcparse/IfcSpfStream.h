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
 
/*********************************************************************************
 *                                                                               *
 * Reads a file in chunks of BUF_SIZE and provides functions to access its       *
 * contents randomly and character by character                                  *
 *                                                                               *
 ********************************************************************************/
 
#ifndef IFCSPFSTREAM_H
#define IFCSPFSTREAM_H

#include <fstream>
#include <string>

// As of IfcOpenShell version 0.3.0 the paging functionality, which
// loads a file on disk into multiple chunks, has been disabled.
// It proved to be an inefficient way of working with large files,
// as often these did not facilitate to be parsed in a sequential 
// manner efficiently. To enable the paging functionality uncomment
// the following statement.
// #define BUF_SIZE (8 * 1024 * 1024)

namespace IfcParse {
	/// The IfcSpfStream class represents a ISO 10303-21 IFC-SPF file in memory.
	/// The file is interpreted as a sequence of tokens which are lazily
	/// interpreted only when requested. If the size of the file is
	/// larger than BUF_SIZE, the file is split into seperate pages, of
	/// which only one is simultaneously kept in memory, for files
	/// that define their entities not in a sequential nature, this is
	/// detrimental for the performance of the parser.
	class IfcSpfStream {
	private:
		FILE* stream;
		char* buffer;
		unsigned int ptr;
		unsigned int len;
		void ReadBuffer(bool inc=true);
#ifdef BUF_SIZE
		unsigned int offset;
		bool paging;
#endif
	public:
		bool valid;
		bool eof;
		unsigned int size;
		IfcSpfStream(const std::string& fn);
		IfcSpfStream(std::istream& f, int len);
		IfcSpfStream(void* data, int len);
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
