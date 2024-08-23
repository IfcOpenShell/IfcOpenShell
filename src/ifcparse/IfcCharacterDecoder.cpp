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

#include "IfcCharacterDecoder.h"

#include "IfcException.h"
#include "IfcSpfStream.h"

#include <codecvt>
#include <iomanip>
#include <sstream>
#include <string>
#include <algorithm>

#define FIRST_SOLIDUS (1 << 1)
#define PAGE (1 << 2)
#define ALPHABET (1 << 3)
#define SECOND_SOLIDUS (1 << 4)
#define ALPHABET_DEFINITION (1 << 5)
#define APOSTROPHE (1 << 6)
#define ARBITRARY (1 << 7)
#define EXTENDED2 (1 << 8)
#define EXTENDED4 (1 << 9)
#define HEX(N) (1 << (9 + (N)))
#define THIRD_SOLIDUS (1 << 18)
#define ENDEXTENDED_X (1 << 19)
#define ENDEXTENDED_0 (1 << 20)
#define IGNORED_DIRECTIVE (1 << 22)
#define ENCOUNTERED_HEX (1 << 23)

// FIXME: These probably need to be less forgiving in terms of wrongly defined sequences
#define EXPECTS_ALPHABET(S) ((S) & FIRST_SOLIDUS)
#define EXPECTS_PAGE(S) ((S) & FIRST_SOLIDUS)
#define EXPECTS_ARBITRARY(S) ((S) & FIRST_SOLIDUS)
#define EXPECTS_N_OR_F(S) ((S) & FIRST_SOLIDUS && !((S) & ARBITRARY))
#define EXPECTS_ARBITRARY2(S) ((S) & ARBITRARY && !((S) & SECOND_SOLIDUS))
#define EXPECTS_ALPHABET_DEFINITION(S) ((S) & FIRST_SOLIDUS && (S) & ALPHABET)
#define EXPECTS_SOLIDUS(S) ((S) & ALPHABET_DEFINITION || (S) & PAGE || (S) & ARBITRARY || (S) & EXTENDED2 || (S) & EXTENDED4 || (S) & ENDEXTENDED_0 || (S) & IGNORED_DIRECTIVE || ((S) & EXTENDED4 && (S) & HEX(8)) || ((S) & EXTENDED2 && (S) & HEX(4)))
#define EXPECTS_CHARACTER(S) ((S) & PAGE && (S) & SECOND_SOLIDUS)
#define EXPECTS_HEX(S) ((S) & HEX(1) || (S) & HEX(3) || (S) & HEX(5) || (S) & HEX(6) || (S) & HEX(7) || ((S) & ARBITRARY && (S) & SECOND_SOLIDUS) || ((S) & EXTENDED2 && (S) & HEX(2)) || ((S) & EXTENDED4 && (S) & HEX(4)))
#define EXPECTS_ENDEXTENDED_X(S) ((S) & THIRD_SOLIDUS)
#define EXPECTS_ENDEXTENDED_0(S) ((S) & ENDEXTENDED_X)

#define IS_VALID_ALPHABET_DEFINITION(C) ((C) >= 0x41 && (C) <= 0x49)
#define IS_HEXADECIMAL(C) (((C) >= 0x30 && (C) <= 0x39) || ((C) >= 0x41 && (C) <= 0x46))
#define HEX_TO_INT(C) (((C) >= 0x30 && (C) <= 0x39) ? (C) - 0x30 : ((C) + 10) - 0x41)
#define CLEAR_HEX(C) ((C) &= ~(HEX(1) | HEX(2) | HEX(3) | HEX(4) | HEX(5) | HEX(6) | HEX(7) | HEX(8)))

using namespace IfcParse;

IfcCharacterDecoder::IfcCharacterDecoder(IfcParse::IfcSpfStream* stream) {
    stream_ = stream;
    codepage_ = 0;
}

IfcCharacterDecoder::~IfcCharacterDecoder() {
}

namespace {
unsigned int reference_helper = 0;

class pure_impure_helper {
  private:
    bool pure_;
    IfcParse::IfcSpfStream* stream_;
    unsigned int& pointer_;
    std::wstring builder_;

    char peek() {
        if (pure_) {
            return stream_->peek_at(pointer_);
        }
        return stream_->Peek();
    }

    unsigned int tell() {
        if (pure_) {
            return pointer_;
        }
        return stream_->Tell();
    }

    void increment() {
        if (pure_) {
            stream_->increment_at(pointer_);
        } else {
            stream_->Inc();
        }
    }

  public:
    pure_impure_helper(IfcParse::IfcSpfStream* stream)
        : pure_(false),
          stream_(stream),
          pointer_(reference_helper) {}

    pure_impure_helper(IfcParse::IfcSpfStream* stream, unsigned int& pointer)
        : pure_(true),
          stream_(stream),
          pointer_(pointer) {}

    std::string get(IfcParse::IfcCharacterDecoder::ConversionMode mode, char substitution_character) {
        unsigned int parse_state = 0;
        builder_.clear();
        builder_.push_back('\'');
        char current_char;
        int codepage = 1;
        unsigned int hex = 0;
        unsigned int hex_count = 0;

        while ((current_char = peek()) != 0) {
            if (EXPECTS_CHARACTER(parse_state)) {
                builder_.push_back(IfcUtil::convert_codepage(codepage, current_char + 0x80));
                parse_state = 0;
            } else if (current_char == '\'' && (parse_state == 0U)) {
                parse_state = APOSTROPHE;
            } else if (current_char == '\\' && (parse_state == 0U)) {
                parse_state = FIRST_SOLIDUS;
            } else if (current_char == '\\' && EXPECTS_SOLIDUS(parse_state)) {
                if (((parse_state & ALPHABET_DEFINITION) != 0U) ||
                    ((parse_state & IGNORED_DIRECTIVE) != 0U) ||
                    ((parse_state & ENDEXTENDED_0) != 0U)) {
                    parse_state = hex = hex_count = 0;
                } else if ((parse_state & ENCOUNTERED_HEX) != 0U) {
                    parse_state += THIRD_SOLIDUS;
                    parse_state -= ENCOUNTERED_HEX;
                } else {
                    parse_state += SECOND_SOLIDUS;
                }
            } else if (current_char == 'X' && EXPECTS_ENDEXTENDED_X(parse_state)) {
                parse_state += ENDEXTENDED_X;
            } else if (current_char == '0' && EXPECTS_ENDEXTENDED_0(parse_state)) {
                parse_state += ENDEXTENDED_0;
            } else if (current_char == 'X' && EXPECTS_ARBITRARY(parse_state)) {
                parse_state += ARBITRARY;
            } else if (current_char == '2' && EXPECTS_ARBITRARY2(parse_state)) {
                parse_state += EXTENDED2;
            } else if (current_char == '4' && EXPECTS_ARBITRARY2(parse_state)) {
                parse_state += EXTENDED2 + EXTENDED4;
            } else if (current_char == 'P' && EXPECTS_ALPHABET(parse_state)) {
                parse_state += ALPHABET;
            } else if ((current_char == 'N' || current_char == 'F') && EXPECTS_N_OR_F(parse_state)) {
                parse_state += IGNORED_DIRECTIVE;
            } else if (IS_VALID_ALPHABET_DEFINITION(current_char) && EXPECTS_ALPHABET_DEFINITION(parse_state)) {
                codepage = current_char - 0x40;
                parse_state += ALPHABET_DEFINITION;
            } else if (current_char == 'S' && EXPECTS_PAGE(parse_state)) {
                parse_state += PAGE;
            } else if (IS_HEXADECIMAL(current_char) && EXPECTS_HEX(parse_state)) {
                hex <<= 4;
                parse_state += HEX((++hex_count));
                hex += HEX_TO_INT(current_char);
                if ((hex_count == 2 && ((parse_state & EXTENDED2) == 0U)) ||
                    (hex_count == 4 && ((parse_state & EXTENDED4) == 0U)) ||
                    (hex_count == 8)) {
                    builder_.push_back(hex);
                    if (hex_count == 2) {
                        parse_state = 0;
                    } else {
                        CLEAR_HEX(parse_state);
                        parse_state |= ENCOUNTERED_HEX;
                    }
                    hex = hex_count = 0;
                }
            } else if ((parse_state != 0U) && !(
                                                  (current_char == '\\' && parse_state == FIRST_SOLIDUS) ||
                                                  (current_char == '\'' && parse_state == APOSTROPHE))) {
                if (parse_state == APOSTROPHE && current_char != '\'') {
                    break;
                }
                throw IfcInvalidTokenException(tell(), current_char);
            } else {
                parse_state = hex = hex_count = 0;
                builder_.push_back(current_char);
            }
            increment();
        }
        builder_.push_back('\'');

        if (mode == IfcParse::IfcCharacterDecoder::UTF8) {
            if (builder_.empty()) {
                static std::string empty;
                return empty;
            }
            auto iter = std::max_element(builder_.begin(), builder_.end());
            if (*iter <= 0x7e) {
                std::string result(builder_.begin(), builder_.end());
                return result;
            }
            return IfcUtil::convert_utf8(builder_);
        }
        if (mode == IfcParse::IfcCharacterDecoder::SUBSTITUTE) {
            std::string result;
            result.reserve(builder_.size());
            std::transform(builder_.begin(), builder_.end(), std::back_inserter(result), [&substitution_character](wchar_t character) {
                if (character >= 0x20 && character <= 0x7e) {
                    return (char)character;
                }
                return substitution_character;
            });
            return result;
        }
        if (mode == IfcParse::IfcCharacterDecoder::ESCAPE) {
            std::stringstream stream;
            stream << std::hex << std::setw(4) << std::setfill('0');
            std::for_each(builder_.begin(), builder_.end(), [&stream](wchar_t character) {
                if (character >= 0x20 && character <= 0x7e) {
                    stream.put((char)character);
                } else {
                    stream << "\\u" << character;
                }
            });
            return stream.str();
        }
        throw IfcParse::IfcException("Invalid conversion mode");
    }
};
} // namespace

IfcCharacterDecoder::operator std::string() {
    return pure_impure_helper(stream_).get(mode, substitution_character);
}

std::string IfcCharacterDecoder::get(unsigned int& ptr) {
    return pure_impure_helper(stream_, ptr).get(mode, substitution_character);
}

void IfcCharacterDecoder::skip() {
    unsigned int parse_state = 0;
    char current_char;
    unsigned int hex_count = 0;
    while ((current_char = stream_->Peek()) != 0) {
        if (EXPECTS_CHARACTER(parse_state)) {
            parse_state = 0;
        } else if (current_char == '\'' && (parse_state == 0U)) {
            parse_state = APOSTROPHE;
        } else if (current_char == '\\' && (parse_state == 0U)) {
            parse_state = FIRST_SOLIDUS;
        } else if (current_char == '\\' && EXPECTS_SOLIDUS(parse_state)) {
            if (((parse_state & ALPHABET_DEFINITION) != 0U) ||
                ((parse_state & IGNORED_DIRECTIVE) != 0U) ||
                ((parse_state & ENDEXTENDED_0) != 0U)) {
                parse_state = hex_count = 0;
            } else if ((parse_state & ENCOUNTERED_HEX) != 0U) {
                parse_state += THIRD_SOLIDUS;
                parse_state -= ENCOUNTERED_HEX;
            } else {
                parse_state += SECOND_SOLIDUS;
            }
        } else if (current_char == 'X' && EXPECTS_ENDEXTENDED_X(parse_state)) {
            parse_state += ENDEXTENDED_X;
        } else if (current_char == '0' && EXPECTS_ENDEXTENDED_0(parse_state)) {
            parse_state += ENDEXTENDED_0;
        } else if (current_char == 'X' && EXPECTS_ARBITRARY(parse_state)) {
            parse_state += ARBITRARY;
        } else if (current_char == '2' && EXPECTS_ARBITRARY2(parse_state)) {
            parse_state += EXTENDED2;
        } else if (current_char == '4' && EXPECTS_ARBITRARY2(parse_state)) {
            parse_state += EXTENDED2 + EXTENDED4;
        } else if (current_char == 'P' && EXPECTS_ALPHABET(parse_state)) {
            parse_state += ALPHABET;
        } else if ((current_char == 'N' || current_char == 'F') && EXPECTS_N_OR_F(parse_state)) {
            parse_state += IGNORED_DIRECTIVE;
        } else if (IS_VALID_ALPHABET_DEFINITION(current_char) && EXPECTS_ALPHABET_DEFINITION(parse_state)) {
            parse_state += ALPHABET_DEFINITION;
        } else if (current_char == 'S' && EXPECTS_PAGE(parse_state)) {
            parse_state += PAGE;
        } else if (IS_HEXADECIMAL(current_char) && EXPECTS_HEX(parse_state)) {
            parse_state += HEX((++hex_count));
            if ((hex_count == 2 && ((parse_state & EXTENDED2) == 0U)) ||
                (hex_count == 4 && ((parse_state & EXTENDED4) == 0U)) ||
                (hex_count == 8)) {
                if (hex_count == 2) {
                    parse_state = 0;
                } else {
                    CLEAR_HEX(parse_state);
                    parse_state |= ENCOUNTERED_HEX;
                }
                hex_count = 0;
            }
        } else if ((parse_state != 0U) && !(
                                              (current_char == '\\' && parse_state == FIRST_SOLIDUS) ||
                                              (current_char == '\'' && parse_state == APOSTROPHE))) {
            if (parse_state == APOSTROPHE && current_char != '\'') {
                break;
            }
            throw IfcInvalidTokenException(stream_->Tell(), current_char);
        } else {
            parse_state = hex_count = 0;
        }
        stream_->Inc();
    }
}

IfcCharacterDecoder::ConversionMode IfcCharacterDecoder::mode = IfcCharacterDecoder::UTF8;
char IfcCharacterDecoder::substitution_character = '_';

IfcCharacterEncoder::IfcCharacterEncoder(const std::string& input)
    : str_(IfcUtil::convert_utf8_to_utf32(input)) {}

IfcCharacterEncoder::operator std::string() {
    std::ostringstream oss;
    oss.put('\'');

    // Either 2 or 4 to uses \X2 or \X4 respectively.
    // Currently hardcoded to 4, but \X2 might be
    // sufficient for nearly all purposes.
    const int num_bytes = (str_.empty() || (*std::max_element(str_.begin(), str_.end()) > 0xffff)) ? 4 : 2;
    const std::string num_bytes_str = std::string(1, num_bytes + 0x30);

    bool in_extended = false;

    for (auto it = str_.begin(); it != str_.end(); ++it) {
        auto character = *it;
        const bool within_spf_range = character >= 0x20 && character <= 0x7e;
        if (in_extended && within_spf_range) {
            oss << "\\X0\\";
        } else if (!in_extended && !within_spf_range) {
            oss << "\\X" << num_bytes_str << "\\";
        }
        if (within_spf_range) {
            oss.put((char)character);
            if (character == '\\' || character == '\'') {
                oss.put((char)character);
            }
        } else {
            oss << std::hex << std::setw(num_bytes * 2) << std::uppercase << std::setfill('0') << (int)character;
        }
        in_extended = !within_spf_range;
    }

    if (in_extended) {
        oss << "\\X0\\";
    }

    oss.put('\'');
    return oss.str();
}

/*
Generate with:

import codecs, string
codecs.register_error('zero', lambda e: (chr(0),e.start + 1))
def _():
	for i in range(1,17):
		try:
			chrs = bytes(range(256)).decode('iso-8859-%d' % i, errors='zero')
		except: chrs = "\x00" * 256
		yield str(list(map(ord, chrs))).translate(string.maketrans("[]", "{}"))

"{%s}" % ",".join(_())
*/
std::wstring::value_type IfcUtil::convert_codepage(int codepage, int character) {
    if (codepage < 1 || codepage > 16 || codepage == 12) {
        throw IfcParse::IfcException("Invalid codepage");
    }
    if (character < 0 || character > 255) {
        throw IfcParse::IfcException("Invalid character ordinal");
    }
    // NOLINTBEGIN(readability-magic-numbers)
    static std::array<std::array<wchar_t, 256>, 16> codepage_data = {{{{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 260, 728, 321, 164, 317, 346, 167, 168, 352, 350, 356, 377, 173, 381, 379, 176, 261, 731, 322, 180, 318, 347, 711, 184, 353, 351, 357, 378, 733, 382, 380, 340, 193, 194, 258, 196, 313, 262, 199, 268, 201, 280, 203, 282, 205, 206, 270, 272, 323, 327, 211, 212, 336, 214, 215, 344, 366, 218, 368, 220, 221, 354, 223, 341, 225, 226, 259, 228, 314, 263, 231, 269, 233, 281, 235, 283, 237, 238, 271, 273, 324, 328, 243, 244, 337, 246, 247, 345, 367, 250, 369, 252, 253, 355, 729}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 294, 728, 163, 164, 0, 292, 167, 168, 304, 350, 286, 308, 173, 0, 379, 176, 295, 178, 179, 180, 181, 293, 183, 184, 305, 351, 287, 309, 189, 0, 380, 192, 193, 194, 0, 196, 266, 264, 199, 200, 201, 202, 203, 204, 205, 206, 207, 0, 209, 210, 211, 212, 288, 214, 215, 284, 217, 218, 219, 220, 364, 348, 223, 224, 225, 226, 0, 228, 267, 265, 231, 232, 233, 234, 235, 236, 237, 238, 239, 0, 241, 242, 243, 244, 289, 246, 247, 285, 249, 250, 251, 252, 365, 349, 729}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 260, 312, 342, 164, 296, 315, 167, 168, 352, 274, 290, 358, 173, 381, 175, 176, 261, 731, 343, 180, 297, 316, 711, 184, 353, 275, 291, 359, 330, 382, 331, 256, 193, 194, 195, 196, 197, 198, 302, 268, 201, 280, 203, 278, 205, 206, 298, 272, 325, 332, 310, 212, 213, 214, 215, 216, 370, 218, 219, 220, 360, 362, 223, 257, 225, 226, 227, 228, 229, 230, 303, 269, 233, 281, 235, 279, 237, 238, 299, 273, 326, 333, 311, 244, 245, 246, 247, 248, 371, 250, 251, 252, 361, 363, 729}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 173, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 8470, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 167, 1118, 1119}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 0, 0, 0, 164, 0, 0, 0, 0, 0, 0, 0, 1548, 173, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1563, 0, 0, 0, 1567, 0, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1576, 1577, 1578, 1579, 1580, 1581, 1582, 1583, 1584, 1585, 1586, 1587, 1588, 1589, 1590, 1591, 1592, 1593, 1594, 0, 0, 0, 0, 0, 1600, 1601, 1602, 1603, 1604, 1605, 1606, 1607, 1608, 1609, 1610, 1611, 1612, 1613, 1614, 1615, 1616, 1617, 1618, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 8216, 8217, 163, 8364, 8367, 166, 167, 168, 169, 890, 171, 172, 173, 0, 8213, 176, 177, 178, 179, 900, 901, 902, 183, 904, 905, 906, 187, 908, 189, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 0, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 0}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 0, 162, 163, 164, 165, 166, 167, 168, 169, 215, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 247, 187, 188, 189, 190, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8215, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496, 1497, 1498, 1499, 1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510, 1511, 1512, 1513, 1514, 0, 0, 8206, 8207, 0}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 286, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 304, 350, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 287, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 305, 351, 255}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 260, 274, 290, 298, 296, 310, 167, 315, 272, 352, 358, 381, 173, 362, 330, 176, 261, 275, 291, 299, 297, 311, 183, 316, 273, 353, 359, 382, 8213, 363, 331, 256, 193, 194, 195, 196, 197, 198, 302, 268, 201, 280, 203, 278, 205, 206, 207, 208, 325, 332, 211, 212, 213, 214, 360, 216, 370, 218, 219, 220, 221, 222, 223, 257, 225, 226, 227, 228, 229, 230, 303, 269, 233, 281, 235, 279, 237, 238, 239, 240, 326, 333, 243, 244, 245, 246, 361, 248, 371, 250, 251, 252, 253, 254, 312}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 3585, 3586, 3587, 3588, 3589, 3590, 3591, 3592, 3593, 3594, 3595, 3596, 3597, 3598, 3599, 3600, 3601, 3602, 3603, 3604, 3605, 3606, 3607, 3608, 3609, 3610, 3611, 3612, 3613, 3614, 3615, 3616, 3617, 3618, 3619, 3620, 3621, 3622, 3623, 3624, 3625, 3626, 3627, 3628, 3629, 3630, 3631, 3632, 3633, 3634, 3635, 3636, 3637, 3638, 3639, 3640, 3641, 3642, 0, 0, 0, 0, 3647, 3648, 3649, 3650, 3651, 3652, 3653, 3654, 3655, 3656, 3657, 3658, 3659, 3660, 3661, 3662, 3663, 3664, 3665, 3666, 3667, 3668, 3669, 3670, 3671, 3672, 3673, 3674, 3675, 0, 0, 0, 0}},
                                                                      {{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 8221, 162, 163, 164, 8222, 166, 167, 216, 169, 342, 171, 172, 173, 174, 198, 176, 177, 178, 179, 8220, 181, 182, 183, 248, 185, 343, 187, 188, 189, 190, 230, 260, 302, 256, 262, 196, 197, 280, 274, 268, 201, 377, 278, 290, 310, 298, 315, 352, 323, 325, 211, 332, 213, 214, 215, 370, 321, 346, 362, 220, 379, 381, 223, 261, 303, 257, 263, 228, 229, 281, 275, 269, 233, 378, 279, 291, 311, 299, 316, 353, 324, 326, 243, 333, 245, 246, 247, 371, 322, 347, 363, 252, 380, 382, 8217}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 7682, 7683, 163, 266, 267, 7690, 167, 7808, 169, 7810, 7691, 7922, 173, 174, 376, 7710, 7711, 288, 289, 7744, 7745, 182, 7766, 7809, 7767, 7811, 7776, 7923, 7812, 7813, 7777, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 372, 209, 210, 211, 212, 213, 214, 7786, 216, 217, 218, 219, 220, 221, 374, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 373, 241, 242, 243, 244, 245, 246, 7787, 248, 249, 250, 251, 252, 253, 375, 255}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 8364, 165, 352, 167, 353, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 381, 181, 182, 183, 382, 185, 186, 187, 338, 339, 376, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255}},
                                                                      {{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 260, 261, 321, 8364, 8222, 352, 167, 353, 169, 536, 171, 377, 173, 378, 379, 176, 177, 268, 322, 381, 8221, 182, 183, 382, 269, 537, 187, 338, 339, 376, 380, 192, 193, 194, 258, 196, 262, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 272, 323, 210, 211, 212, 336, 214, 346, 368, 217, 218, 219, 220, 280, 538, 223, 224, 225, 226, 259, 228, 263, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 273, 324, 242, 243, 244, 337, 246, 347, 369, 249, 250, 251, 252, 281, 539, 255}}}};
    // NOLINTEND(readability-magic-numbers)
    auto result = codepage_data[codepage - 1][character];
    if (result == 0) {
        throw IfcParse::IfcException("Character not defined");
    }
    return result;
}

std::string IfcUtil::convert_utf8(const std::wstring& string) {
    return std::wstring_convert<std::codecvt_utf8<std::wstring::value_type>>().to_bytes(string);
}

std::wstring IfcUtil::convert_utf8(const std::string& string) {
    return std::wstring_convert<std::codecvt_utf8<std::wstring::value_type>>().from_bytes(string);
}

#ifdef _MSC_VER

// bug in msvc 2015 and 2017, unsure if fixed in later versions

std::u32string IfcUtil::convert_utf8_to_utf32(const std::string& s) {
    bool is_ascii = true;
    for (char c : s) {
        if (static_cast<unsigned char>(c) >= 128) {
            is_ascii = false;
            break;
        }
    }
    if (is_ascii) {
        return std::u32string(s.begin(), s.end());
     } else {
        auto converted = std::wstring_convert<std::codecvt_utf8<int32_t>, int32_t>().from_bytes(s);
        return std::u32string(reinterpret_cast<char32_t const*>(converted.data()));
    }
}

#else

std::u32string IfcUtil::convert_utf8_to_utf32(const std::string& s) {
    bool is_ascii = true;
    for (char c : s) {
        if (static_cast<unsigned char>(c) >= 128) {
            is_ascii = false;
            break;
        }
    }
    if (is_ascii) {
        return std::u32string(s.begin(), s.end());
    } 
        return std::wstring_convert<std::codecvt_utf8<std::u32string::value_type>, std::u32string::value_type>().from_bytes(s);
   
}

#endif
