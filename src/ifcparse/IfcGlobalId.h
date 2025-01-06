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

#ifndef IFCGLOBALID_H
#define IFCGLOBALID_H

#include "ifc_parse_api.h"

#include <boost/uuid/uuid.hpp>
#include <string>

namespace IfcParse {

/// A helper class for the creation of IFC GlobalIds.
class IFC_PARSE_API IfcGlobalId {
  private:
    std::string string_data_;
    std::string formatted_string_;
    boost::uuids::uuid uuid_data_;

  public:
    static const unsigned int length = 22;
    IfcGlobalId();
    IfcGlobalId(const std::string&);
    operator const std::string&() const;
    operator const boost::uuids::uuid&() const;
    const std::string& formatted() const;
};

} // namespace IfcParse

#endif
