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

#include "ifc_parse_api.h"

#include <string>

#ifndef IFCPARSE_UTILS_H
#define IFCPARSE_UTILS_H

namespace IfcUtil {

/// Replaces spaces and potentially other problem causing characters with underscores.
IFC_PARSE_API void sanitate_material_name(std::string& str);

IFC_PARSE_API void escape_xml(std::string& str);
IFC_PARSE_API void unescape_xml(std::string& str);

namespace path {

IFC_PARSE_API bool delete_file(const std::string& filename);
IFC_PARSE_API bool rename_file(const std::string& old_filename, const std::string& new_filename);

#if defined(_MSC_VER) && defined(_UNICODE)

/// Uses windows.h string conversion functions
IFC_PARSE_API std::string to_utf8(const std::wstring& str);

/// Uses windows.h string conversion functions
IFC_PARSE_API std::wstring from_utf8(const std::string& str);
#else
/// Identity operation
IFC_PARSE_API inline std::string to_utf8(const std::string& str) { return str; }

/// Identity operation
IFC_PARSE_API inline std::string from_utf8(const std::string& str) { return str; }
#endif

} // namespace path

} // namespace IfcUtil

#endif
