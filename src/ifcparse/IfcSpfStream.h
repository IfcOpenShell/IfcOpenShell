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
 * Reads a file and provides functions to access its                             *
 * contents randomly and character by character                                  *
 *                                                                               *
 ********************************************************************************/
 
#ifndef IFCSPFSTREAM_H
#define IFCSPFSTREAM_H

#include <fstream>
#include <string>

#ifdef USE_MMAP
#include <boost/iostreams/device/mapped_file.hpp>
#endif

#include "ifc_parse_api.h"

namespace IfcParse {
	/// The IfcSpfStream class represents a ISO 10303-21 IFC-SPF file in memory.
	/// The file is interpreted as a sequence of tokens which are lazily
	/// interpreted only when requested.
	class IFC_PARSE_API IfcSpfStream {
	private:
#ifdef USE_MMAP
		boost::iostreams::mapped_file_source mfs;
#endif
		FILE* stream;
		const char* buffer;
		unsigned int ptr;
		unsigned int len;
	public:
		bool valid;
		bool eof;
		unsigned int size;
#ifdef USE_MMAP
		IfcSpfStream(const std::string& fn, bool mmap=false);
#else
		IfcSpfStream(const std::string& fn);
#endif
		IfcSpfStream(std::istream& f, int len);
		IfcSpfStream(void* data, int len);
		~IfcSpfStream();
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
