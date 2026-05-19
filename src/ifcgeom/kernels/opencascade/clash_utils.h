#pragma once

#include <gp_Vec.hxx>
#include <array>

#include "../ifc_geomlibrary_api.h"

struct IFC_GEOMLIBRARY_API ray {
    float origin[3];
    float dir[3];
    float dir_inv[3];
};

struct IFC_GEOMLIBRARY_API box {
    float corners[2][3];
};

IFC_GEOMLIBRARY_API bool is_intersect_ray_box(const struct ray *ray, const struct box *box);

IFC_GEOMLIBRARY_API bool intersectRayTriangle(	const gp_Vec& orig, const gp_Vec& dir,
                                                const gp_Vec& vert0, const gp_Vec& vert1, const gp_Vec& vert2, 
                                                Standard_Real& at, Standard_Real& au, Standard_Real& av,
                                                bool cull, float enlarge=0.0f);

IFC_GEOMLIBRARY_API void edgeEdgeDist(gp_Vec& x, gp_Vec& y,				// closest points
                 const gp_Vec& p, const gp_Vec& a,	// seg 1 origin, vector
                 const gp_Vec& q, const gp_Vec& b);	// seg 2 origin, vector

IFC_GEOMLIBRARY_API float distanceTriangleTriangleSquared(gp_Vec& cp, gp_Vec& cq, const std::array<gp_Vec, 3> p, const std::array<gp_Vec, 3> q);

IFC_GEOMLIBRARY_API bool trianglesIntersect(const gp_Vec& a1, const gp_Vec& b1, const gp_Vec& c1, const gp_Vec& a2, const gp_Vec& b2, const gp_Vec& c2/*, Segment* intersection*/, gp_Vec& int1, gp_Vec& int2, bool ignoreCoplanar);
