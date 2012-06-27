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
 * Implementation of character decoding as described in ISO 10303-21 table 2 and *
 * table 4                                                                       *
 *                                                                               *
 ********************************************************************************/
 
#ifndef IFCCHARACTERDECODER_H
#define IFCCHARACTERDECODER_H

#include <string>
#include <sstream>

#ifdef HAVE_ICU
#include "unicode/ucnv.h"
#else
typedef unsigned int UChar32;
#endif

#include "../ifcparse/IfcFile.h"

namespace IfcParse {

	class IfcCharacterDecoder {
	private:
		IfcParse::File* file;
#ifdef HAVE_ICU
		static UConverter* destination;
		static UConverter* converter;
		static int previous_codepage;
		static UErrorCode status;
#endif
		void addChar(std::stringstream& s,const UChar32& ch);
	public:
//#ifdef HAVE_ICU
    enum ConversionMode {DEFAULT,UTF8,LATIN,JSON,PYTHON};
		static ConversionMode mode;
//#else
		static char substitution_character;
//#endif
		IfcCharacterDecoder(IfcParse::File* file);
		~IfcCharacterDecoder();
		void dryRun();
		operator std::string();
	};

}

#endif
