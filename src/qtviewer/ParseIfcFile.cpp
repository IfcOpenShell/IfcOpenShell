#include "ParseIfcFile.h"

#include "../ifcparse/Ifc2x3.h"
#define IfcSchema Ifc2x3

#include "../ifcgeom/IfcGeom.h"

ParseIfcFile::ParseIfcFile() {}

ParseIfcFile::~ParseIfcFile() {}

void ParseIfcFile::Parse(const std::string& filePath)
{
    //IfcParse::IfcFile ifcFile(filePath);
}