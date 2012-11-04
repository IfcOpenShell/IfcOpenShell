ADD_EXECUTABLE(IfcParseExamples IfcParseExamples.cpp)
TARGET_LINK_LIBRARIES (IfcParseExamples IfcParse)

ADD_EXECUTABLE(IfcOpenHouse IfcOpenHouse.cpp)
TARGET_LINK_LIBRARIES (IfcOpenHouse IfcParse IfcGeom TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet)
