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

// SWAR (SIMD within a register) helpers the tokenizer uses to test eight
// bytes at a time for the characters that end or structure a token.

#ifndef IFCPARSE_SWAR_H
#define IFCPARSE_SWAR_H

#include <cstdint>

// These helpers sit on the tokenizer's innermost loop; left to the
// compiler's heuristics they end up as calls, one per eight bytes.
#if defined(_MSC_VER)
#define IFC_SWAR_INLINE __forceinline
#else
#define IFC_SWAR_INLINE inline __attribute__((always_inline))
#endif

namespace ifcopenshell {
namespace SWAR {
constexpr uint32_t ONES32 = 0x01010101u;
constexpr uint32_t HIGHS32 = 0x80808080u;
constexpr uint64_t ONES = 0x0101010101010101ull;
constexpr uint64_t HIGHS = 0x8080808080808080ull;

constexpr uint64_t splat(unsigned char c) {
    return ONES * c;
}

IFC_SWAR_INLINE uint32_t has_zero_byte(uint32_t x) {
    return (x - ONES32) & ~x & HIGHS32;
}

IFC_SWAR_INLINE uint64_t has_zero_byte(uint64_t x) {
    return (x - ONES) & ~x & HIGHS;
}

IFC_SWAR_INLINE uint32_t eq_mask(uint32_t x, uint32_t c) {
    return has_zero_byte(x ^ c);
}

IFC_SWAR_INLINE uint64_t eq_mask(uint64_t x, uint64_t c) {
    return has_zero_byte(x ^ c);
}

namespace chars {
constexpr uint64_t lpar = splat('(');
constexpr uint64_t rpar = splat(')');
constexpr uint64_t eq = splat('=');
constexpr uint64_t comma = splat(',');
constexpr uint64_t semi = splat(';');
constexpr uint64_t slash = splat('/');

constexpr uint64_t space = splat(' ');
constexpr uint64_t cr = splat('\r');
constexpr uint64_t lf = splat('\n');
constexpr uint64_t tab = splat('\t');

constexpr uint64_t quote = splat('"');
constexpr uint64_t dot = splat('.');
constexpr uint64_t apostrophe = splat('\'');
constexpr uint64_t hash = splat('#');
} // namespace chars

template <bool IncludeDot = true>
IFC_SWAR_INLINE uint64_t has_special_char(uint64_t x) {
    return eq_mask(x, chars::lpar) |
           eq_mask(x, chars::rpar) |
           eq_mask(x, chars::eq) |
           eq_mask(x, chars::comma) |
           eq_mask(x, chars::semi) |
           eq_mask(x, chars::slash) |
           eq_mask(x, chars::space) |
           eq_mask(x, chars::cr) |
           eq_mask(x, chars::lf) |
           eq_mask(x, chars::tab) |
           eq_mask(x, chars::quote) |
           (IncludeDot ? eq_mask(x, chars::dot) : uint64_t{0});
}

template <bool IncludeDot = true>
IFC_SWAR_INLINE uint32_t has_special_char(uint32_t x) {
    return eq_mask(x, static_cast<uint32_t>(chars::lpar)) |
           eq_mask(x, static_cast<uint32_t>(chars::rpar)) |
           eq_mask(x, static_cast<uint32_t>(chars::eq)) |
           eq_mask(x, static_cast<uint32_t>(chars::comma)) |
           eq_mask(x, static_cast<uint32_t>(chars::semi)) |
           eq_mask(x, static_cast<uint32_t>(chars::slash)) |
           eq_mask(x, static_cast<uint32_t>(chars::space)) |
           eq_mask(x, static_cast<uint32_t>(chars::cr)) |
           eq_mask(x, static_cast<uint32_t>(chars::lf)) |
           eq_mask(x, static_cast<uint32_t>(chars::tab)) |
           eq_mask(x, static_cast<uint32_t>(chars::quote)) |
           (IncludeDot ? eq_mask(x, static_cast<uint32_t>(chars::dot)) : uint32_t{0});
}

}

namespace SWAR {
// The characters the attribute scan of the lazy index has to look at: string
// delimiters, parentheses, the attribute separator, references, comments and
// the instance terminator. Everything else is passed over untouched.
IFC_SWAR_INLINE uint64_t has_scan_char(uint64_t x) {
    return eq_mask(x, chars::apostrophe) |
           eq_mask(x, chars::lpar) |
           eq_mask(x, chars::rpar) |
           eq_mask(x, chars::comma) |
           eq_mask(x, chars::hash) |
           eq_mask(x, chars::slash) |
           eq_mask(x, chars::semi);
}
} // namespace SWAR
} // namespace ifcopenshell

#endif
