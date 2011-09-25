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

#include <string>
#include <sstream>
#include <iomanip>

#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcFile.h"

#define FIRST_SOLIDUS						(1 << 1)
#define PAGE								(1 << 2)
#define ALPHABET							(1 << 3)
#define SECOND_SOLIDUS						(1 << 4)
#define ALPHABET_DEFINITION					(1 << 5)
#define APOSTROPHE							(1 << 6)
#define ARBITRARY							(1 << 7)
#define EXTENDED2							(1 << 8)
#define EXTENDED4							(1 << 9)
#define HEX(N)								(1 << (9+N))
#define THIRD_SOLIDUS						(1 << 18)
#define ENDEXTENDED_X						(1 << 19)
#define ENDEXTENDED_0						(1 << 20)
#define FOURTH_SOLIDUS						(1 << 21)
#define IGNORED_DIRECTIVE					(1 << 22)

// FIXME: These probably need to be less forgiving in terms of wrongly defined sequences
#define EXPECTS_ALPHABET(S)					(S & FIRST_SOLIDUS)
#define EXPECTS_PAGE(S)						(S & FIRST_SOLIDUS)
#define EXPECTS_ARBITRARY(S)				(S & FIRST_SOLIDUS)
#define EXPECTS_N_OR_F(S)					(S & FIRST_SOLIDUS && !(S & ARBITRARY) )
#define EXPECTS_ARBITRARY2(S)				(S & ARBITRARY && !(S & SECOND_SOLIDUS))
#define EXPECTS_ALPHABET_DEFINITION(S)		(S & FIRST_SOLIDUS && S & ALPHABET)
#define EXPECTS_SOLIDUS(S)					(S & ALPHABET_DEFINITION || S & PAGE || S & ARBITRARY || S & EXTENDED2 || S & EXTENDED4 || S & ENDEXTENDED_0 || S & IGNORED_DIRECTIVE || (S & EXTENDED4 && S & HEX(8)) || (S & EXTENDED2 && S & HEX(4)))
#define EXPECTS_CHARACTER(S)				(S & PAGE && S & SECOND_SOLIDUS)
#define EXPECTS_HEX(S)						(S & HEX(1) || S & HEX(3) || S & HEX(5) || S & HEX(6) || S & HEX(7) || (S & ARBITRARY && S & SECOND_SOLIDUS) || (S & EXTENDED2 && S & HEX(2)) || (S & EXTENDED4 && S & HEX(4)) )
#define EXPECTS_ENDEXTENDED_X(S)			(S & THIRD_SOLIDUS)
#define EXPECTS_ENDEXTENDED_0(S)			(S & ENDEXTENDED_X)

#define IS_VALID_ALPHABET_DEFINITION(C)		(C >= 0x40 && C <= 0x4A)
#define IS_HEXADECIMAL(C)					((C >= 0x30 && C <= 0x39 ) || (C >= 0x41 && C <= 0x46 ))
#define HEX_TO_INT(C)						((C >= 0x30 && C <= 0x39 ) ? C - 0x30 : (C+10) - 0x41)
#define CLEAR_HEX(C)						(C &= ~(HEX(1)&HEX(2)&HEX(3)&HEX(4)&HEX(5)&HEX(6)&HEX(7)&HEX(8)))

using namespace IfcParse;

void IfcCharacterDecoder::addChar(std::stringstream& s,const UChar32& ch) {
	if ( destination ) {
		char* extraction_buffer = new char[4];
		UnicodeString(ch).extract(extraction_buffer,4,destination,status);
		s << extraction_buffer;
		delete extraction_buffer;
	} else {
		std::stringstream s2;
		s2 << "\\u" << std::hex << std::setw(4) << std::setfill('0') << (int) ch;
		s << s2.str();
	}
}
IfcCharacterDecoder::IfcCharacterDecoder(IfcParse::File* f) {
	file = f;
	if ( ! destination && mode == UTF8 ) {
		destination = ucnv_open("utf-8", &status);
	} else if ( ! destination && mode == LATIN ) {
		destination = ucnv_open("iso-8859-1", &status);
	}
}
IfcCharacterDecoder::~IfcCharacterDecoder() {
	if ( destination ) ucnv_close(destination);
	if ( converter ) ucnv_close(converter);
}
IfcCharacterDecoder::operator std::string() {
	unsigned int parse_state = 0;
	std::stringstream s;
	s.put('\'');
	char current_char;
	int codepage = 1;
	unsigned int hex = 0;
	unsigned int hex_count = 0;
	while ( current_char = file->Peek() ) {
		if ( EXPECTS_CHARACTER(parse_state) ) {
			if ( previous_codepage != codepage ) {
				if ( converter ) ucnv_close(converter);
				char encoder[11] = {'i','s','o','-','8','8','5','9','-',codepage + 0x30};
				converter = ucnv_open(encoder, &status);
			}
			const char characters[2] = { current_char + 0x80 };
			const char* char_array = &characters[0];
			UChar32 ch = ucnv_getNextUChar(converter,&char_array,char_array+1,&status);
			addChar(s,ch);
			parse_state = 0;
		} else if ( current_char == '\'' && ! parse_state ) {
			parse_state = APOSTROPHE;
		} else if ( current_char == '\\' && ! parse_state ) {
			parse_state = FIRST_SOLIDUS;
		} else if ( current_char == '\\' && EXPECTS_SOLIDUS(parse_state) ) {
			if ( parse_state & ALPHABET_DEFINITION || 
				parse_state & IGNORED_DIRECTIVE || 
				parse_state & ENDEXTENDED_0 ) parse_state = hex = hex_count = 0;
			else if ( parse_state & HEX(3) ) parse_state += THIRD_SOLIDUS;
			else parse_state += SECOND_SOLIDUS;
		} else if ( current_char == 'X' && EXPECTS_ENDEXTENDED_X(parse_state) ) {
			parse_state += ENDEXTENDED_X;
		} else if ( current_char == '0' && EXPECTS_ENDEXTENDED_0(parse_state) ) {
			parse_state += ENDEXTENDED_0;
		} else if ( current_char == 'X' && EXPECTS_ARBITRARY(parse_state) ) {
			parse_state += ARBITRARY;
		} else if ( current_char == '2' && EXPECTS_ARBITRARY2(parse_state) ) {
			parse_state += EXTENDED2;
		} else if ( current_char == '4' && EXPECTS_ARBITRARY2(parse_state) ) {
			parse_state += EXTENDED2 + EXTENDED4;
		} else if ( current_char == 'P' && EXPECTS_ALPHABET(parse_state) ) {
			parse_state += ALPHABET;
		} else if ( (current_char == 'N' || current_char == 'F') && EXPECTS_N_OR_F(parse_state) ) {
			parse_state += IGNORED_DIRECTIVE;
		} else if ( IS_VALID_ALPHABET_DEFINITION(current_char) && EXPECTS_ALPHABET_DEFINITION(parse_state) ) {
			codepage = current_char - 0x40;
			parse_state += ALPHABET_DEFINITION;
		} else if ( current_char == 'S' && EXPECTS_PAGE(parse_state) ) {
			parse_state += PAGE;
		} else if ( IS_HEXADECIMAL(current_char) && EXPECTS_HEX(parse_state) ) {
			hex <<= 4;
			parse_state += HEX((++hex_count));
			hex += HEX_TO_INT(current_char);
			if ( (hex_count == 2 && !(parse_state & EXTENDED2)) ||
				(hex_count == 4 && !(parse_state & EXTENDED4)) ||
				(hex_count == 8) ) {
					addChar(s,(UChar32) hex);
					if ( hex_count == 2 ) parse_state = 0;
					else CLEAR_HEX(parse_state);
					hex = hex_count = 0;
			}
		} else if ( parse_state && !(
			(current_char == '\\' && parse_state == FIRST_SOLIDUS) ||
			(current_char == '\'' && parse_state == APOSTROPHE)
			) ) {
				if ( parse_state == APOSTROPHE && current_char != '\'' ) break;
				throw IfcException("Invalid character encountered");
		} else {
			parse_state = hex = hex_count = 0;
			s.put(current_char);
		}
		file->Inc();
	}
	s.put('\'');
	return s.str();
}

void IfcCharacterDecoder::dryRun() {
	unsigned int parse_state = 0;
	char current_char;
	unsigned int hex_count = 0;
	while ( current_char = file->Peek() ) {
		if ( EXPECTS_CHARACTER(parse_state) ) {
			parse_state = 0;
		} else if ( current_char == '\'' && ! parse_state ) {
			parse_state = APOSTROPHE;
		} else if ( current_char == '\\' && ! parse_state ) {
			parse_state = FIRST_SOLIDUS;
		} else if ( current_char == '\\' && EXPECTS_SOLIDUS(parse_state) ) {
			if ( parse_state & ALPHABET_DEFINITION || 
				parse_state & IGNORED_DIRECTIVE || 
				parse_state & ENDEXTENDED_0 ) parse_state = hex_count = 0;
			else if ( parse_state & HEX(3) ) parse_state += THIRD_SOLIDUS;
			else parse_state += SECOND_SOLIDUS;
		} else if ( current_char == 'X' && EXPECTS_ENDEXTENDED_X(parse_state) ) {
			parse_state += ENDEXTENDED_X;
		} else if ( current_char == '0' && EXPECTS_ENDEXTENDED_0(parse_state) ) {
			parse_state += ENDEXTENDED_0;
		} else if ( current_char == 'X' && EXPECTS_ARBITRARY(parse_state) ) {
			parse_state += ARBITRARY;
		} else if ( current_char == '2' && EXPECTS_ARBITRARY2(parse_state) ) {
			parse_state += EXTENDED2;
		} else if ( current_char == '4' && EXPECTS_ARBITRARY2(parse_state) ) {
			parse_state += EXTENDED2 + EXTENDED4;
		} else if ( current_char == 'P' && EXPECTS_ALPHABET(parse_state) ) {
			parse_state += ALPHABET;
		} else if ( (current_char == 'N' || current_char == 'F') && EXPECTS_N_OR_F(parse_state) ) {
			parse_state += IGNORED_DIRECTIVE;
		} else if ( IS_VALID_ALPHABET_DEFINITION(current_char) && EXPECTS_ALPHABET_DEFINITION(parse_state) ) {
			parse_state += ALPHABET_DEFINITION;
		} else if ( current_char == 'S' && EXPECTS_PAGE(parse_state) ) {
			parse_state += PAGE;
		} else if ( IS_HEXADECIMAL(current_char) && EXPECTS_HEX(parse_state) ) {
			parse_state += HEX((++hex_count));
			if ( (hex_count == 2 && !(parse_state & EXTENDED2)) ||
				(hex_count == 4 && !(parse_state & EXTENDED4)) ||
				(hex_count == 8) ) {
					if ( hex_count == 2 ) parse_state = 0;
					else CLEAR_HEX(parse_state);
					hex_count = 0;
			}
		} else if ( parse_state && !(
			(current_char == '\\' && parse_state == FIRST_SOLIDUS) ||
			(current_char == '\'' && parse_state == APOSTROPHE)
			) ) {
				if ( parse_state == APOSTROPHE && current_char != '\'' ) break;
				throw IfcException("Invalid character encountered");
		} else {
			parse_state = hex_count = 0;
		}
		file->Inc();
	}
}

UConverter* IfcCharacterDecoder::destination = 0;
UConverter* IfcCharacterDecoder::converter = 0;
int IfcCharacterDecoder::previous_codepage = -1;
UErrorCode IfcCharacterDecoder::status = U_ZERO_ERROR;
IfcCharacterDecoder::ConversionMode IfcCharacterDecoder::mode = IfcCharacterDecoder::JSON;

