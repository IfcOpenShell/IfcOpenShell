#ifndef PROFILE_HELPER_H
#define PROFILE_HELPER_H

#include <gp_Trsf2d.hxx>
#include <TopoDS_Shape.hxx>

namespace IfcGeom {
	namespace util {
		bool profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face);
	}
}

#endif