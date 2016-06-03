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

/********************************************************************************************
 *                                                                                          *
 * This file has been generated from                                                        *
 * http://www.buildingsmart-tech.org/downloads/ifc/ifc2x3tc/IFC2X3_TC1_EXPRESS_longform.zip *
 * Do not make modifications but instead modify the Python script that has been             *
 * used to generate this.                                                                   *
 *                                                                                          *
 ********************************************************************************************/

#ifndef IFC2X3RT_H
#define IFC2X3RT_H

#define IfcSchema Ifc2x3

#include "../ifcparse/IfcParse_Export.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcEntityDescriptor.h"
#include "../ifcparse/IfcWritableEntity.h"

namespace Ifc2x3 {
namespace Type {
    IfcParse_EXPORT int GetAttributeCount(Enum t);
    IfcParse_EXPORT int GetAttributeIndex(Enum t, const std::string& a);
    IfcParse_EXPORT IfcUtil::ArgumentType GetAttributeType(Enum t, unsigned char a);
    IfcParse_EXPORT Enum GetAttributeEntity(Enum t, unsigned char a);
    IfcParse_EXPORT const std::string& GetAttributeName(Enum t, unsigned char a);
    IfcParse_EXPORT bool GetAttributeOptional(Enum t, unsigned char a);
    IfcParse_EXPORT bool GetAttributeDerived(Enum t, unsigned char a);
    IfcParse_EXPORT std::pair<const char*, int> GetEnumerationIndex(Enum t, const std::string& a);
    IfcParse_EXPORT std::pair<Enum, unsigned> GetInverseAttribute(Enum t, const std::string& a);
    IfcParse_EXPORT std::set<std::string> GetInverseAttributeNames(Enum t);
    IfcParse_EXPORT void PopulateDerivedFields(IfcWrite::IfcWritableEntity* e);
}}

#endif
