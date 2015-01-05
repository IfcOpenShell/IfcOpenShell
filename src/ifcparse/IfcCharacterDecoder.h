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

#include "../ifcparse/IfcSpfStream.h"

namespace IfcParse {

	class IfcCharacterDecoder {
	private:
		IfcParse::IfcSpfStream* file;
#ifdef HAVE_ICU
		static UConverter* destination;
		static UConverter* converter;
		static UConverter* compatibility_converter;
		static int previous_codepage;
		static UErrorCode status;
#endif
		void addChar(std::stringstream& s,const UChar32& ch);
	public:
#ifdef HAVE_ICU
		enum ConversionMode {DEFAULT,UTF8,LATIN,JSON,PYTHON};
		static ConversionMode mode;

		// Many BIM software (eg. Revit, ArchiCAD, ...) has wrong behavior to encode characters.
		// It just translate to extended string in system default code page, not unicode.
		// If you want to process these strings, set true.
		static bool compatibility_mode;
		static std::string compatibility_charset;

#else
		static char substitution_character;
#endif
		IfcCharacterDecoder(IfcParse::IfcSpfStream* file);
		~IfcCharacterDecoder();
		void dryRun();
		operator std::string();
	};

}

namespace IfcWrite {

	class IfcCharacterEncoder {
	private:
		std::string str;
#ifdef HAVE_ICU
		static UErrorCode status;
		static UConverter* converter;
#endif
	public:
		IfcCharacterEncoder(const std::string& input);
		~IfcCharacterEncoder();
		operator std::string();
	};

}

#endif
