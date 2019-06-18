
#ifndef IFC4X2RT_H
#define IFC4X2RT_H

#define IfcSchema Ifc4x2

#include "../ifcparse/ifc_parse_api.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcEntityDescriptor.h"

namespace Ifc4x2 {
namespace Type {
    IFC_PARSE_API int GetAttributeCount(Enum t);
    IFC_PARSE_API int GetAttributeIndex(Enum t, const std::string& a);
    IFC_PARSE_API IfcUtil::ArgumentType GetAttributeType(Enum t, unsigned char a);
    IFC_PARSE_API Enum GetAttributeEntity(Enum t, unsigned char a);
    IFC_PARSE_API const std::string& GetAttributeName(Enum t, unsigned char a);
    IFC_PARSE_API bool GetAttributeOptional(Enum t, unsigned char a);
    IFC_PARSE_API bool GetAttributeDerived(Enum t, unsigned char a);
    IFC_PARSE_API std::pair<const char*, int> GetEnumerationIndex(Enum t, const std::string& a);
    IFC_PARSE_API std::pair<Enum, unsigned> GetInverseAttribute(Enum t, const std::string& a);
    IFC_PARSE_API std::set<std::string> GetInverseAttributeNames(Enum t);
    IFC_PARSE_API void PopulateDerivedFields(IfcEntityInstanceData* e);
}}

#endif
