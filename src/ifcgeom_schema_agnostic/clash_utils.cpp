#include "clash_utils.h"
#include <cassert>

#define GU_CULLING_EPSILON_RAY_TRIANGLE FLT_EPSILON*FLT_EPSILON
#define PX_MAX_F32 3.4028234663852885981170418348452e+38F

// Why can't I use std::clamp?
template<typename TC>
const TC& ios_clamp(const TC& v, const TC& lo, const TC& hi) {
    assert(!(hi < lo));
    return (v < lo) ? lo : (hi < v) ? hi : v;
}

// Branchless slab method. Note that this can still be optimised further by batching boxes.
// From Tavian Barnes - MIT License
// https://tavianator.com/2022/ray_box_boundary.html
bool is_intersect_ray_box(const struct ray *ray, const struct box *box) {
    float tmin = 0.0, tmax = INFINITY;

    for (int d = 0; d < 3; ++d) {
        bool sign = std::signbit(ray->dir_inv[d]);
        float bmin = box->corners[sign][d];
        float bmax = box->corners[!sign][d];

        float dmin = (bmin - ray->origin[d]) * ray->dir_inv[d];
        float dmax = (bmax - ray->origin[d]) * ray->dir_inv[d];

        tmin = std::max(dmin, tmin);
        tmax = std::min(dmax, tmax);
    }

    return tmin < tmax;
}

// From NVIDIA-Omniverse PhysX - BSD 3-Clause "New" or "Revised" License
// https://github.com/NVIDIA-Omniverse/PhysX/blob/main/LICENSE.md
// https://github.com/NVIDIA-Omniverse/PhysX/blob/main/physx/source/geomutils/src/intersection/GuIntersectionRayTriangle.h
// With minor modifications to use gp_Vec type.
// More reading: https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
bool intersectRayTriangle(	const gp_Vec& orig, const gp_Vec& dir, 
                                                const gp_Vec& vert0, const gp_Vec& vert1, const gp_Vec& vert2, 
                                                Standard_Real& at, Standard_Real& au, Standard_Real& av,
                                                bool cull, float enlarge) {
    // Find vectors for two edges sharing vert0
    const gp_Vec edge1 = vert1 - vert0;
    const gp_Vec edge2 = vert2 - vert0;

    // Begin calculating determinant - also used to calculate U parameter
    const gp_Vec pvec = dir.Crossed(edge2); // error ~ |v2-v0|

    // If determinant is near zero, ray lies in plane of triangle
    const Standard_Real det = edge1.Dot(pvec); // error ~ |v2-v0|*|v1-v0|

    if(cull)
    {
        if(det<GU_CULLING_EPSILON_RAY_TRIANGLE)
            return false;

        // Calculate distance from vert0 to ray origin
        const gp_Vec tvec = orig - vert0;

        // Calculate U parameter and test bounds
        const Standard_Real u = tvec.Dot(pvec);

        const Standard_Real enlargeCoeff = enlarge*det;
        const Standard_Real uvlimit = -enlargeCoeff;
        const Standard_Real uvlimit2 = det + enlargeCoeff;

        if(u<uvlimit || u>uvlimit2)
            return false;

        // Prepare to test V parameter
        const gp_Vec qvec = tvec.Crossed(edge1);

        // Calculate V parameter and test bounds
        const Standard_Real v = dir.Dot(qvec);
        if(v<uvlimit || (u+v)>uvlimit2)
            return false;

        // Calculate t, scale parameters, ray intersects triangle
        const Standard_Real t = edge2.Dot(qvec);

        const Standard_Real inv_det = 1.0f / det;
        at = t*inv_det;
        au = u*inv_det;
        av = v*inv_det;
    }
    else
    {
        // the non-culling branch
        if(std::abs(det)<GU_CULLING_EPSILON_RAY_TRIANGLE)
            return false;

        const Standard_Real inv_det = 1.0f / det;

        // Calculate distance from vert0 to ray origin
        const gp_Vec tvec = orig - vert0; // error ~ |orig-v0|

        // Calculate U parameter and test bounds
        const Standard_Real u = tvec.Dot(pvec) * inv_det;
        if(u<-enlarge || u>1.0f+enlarge)
            return false;

        // prepare to test V parameter
        const gp_Vec qvec = tvec.Crossed(edge1);

        // Calculate V parameter and test bounds
        const Standard_Real v = dir.Dot(qvec) * inv_det;
        if(v<-enlarge || (u+v)>1.0f+enlarge)
            return false;

        // Calculate t, ray intersects triangle
        const Standard_Real t = edge2.Dot(qvec) * inv_det;

        at = t;
        au = u;
        av = v;
    }
    return true;
}

// From NVIDIA-Omniverse PhysX - BSD 3-Clause "New" or "Revised" License
// https://github.com/NVIDIA-Omniverse/PhysX/blob/main/LICENSE.md
// https://github.com/NVIDIA-Omniverse/PhysX/blob/main/physx/source/geomutils/src/sweep/GuSweepCapsuleCapsule.cpp
// With minor modifications to use gp_Vec type.
void edgeEdgeDist(gp_Vec& x, gp_Vec& y,				// closest points
                 const gp_Vec& p, const gp_Vec& a,	// seg 1 origin, vector
                 const gp_Vec& q, const gp_Vec& b)	// seg 2 origin, vector
{
    const gp_Vec Tx = q - p;
    const double ADotA = a.Dot(a);
    const double BDotB = b.Dot(b);
    const double ADotB = a.Dot(b);
    const double ADotT = a.Dot(Tx);
    const double BDotT = b.Dot(Tx);

    // t parameterizes ray (p, a)
    // u parameterizes ray (q, b)

    // Compute t for the closest point on ray (p, a) to ray (q, b)
    const Standard_Real Denom = ADotA*BDotB - ADotB*ADotB;

    Standard_Real t;	// We will clamp result so t is on the segment (p, a)
    if(Denom!=0.0f)	
        t = ios_clamp((ADotT*BDotB - BDotT*ADotB) / Denom, 0.0, 1.0);
    else
        t = 0.0f;

    // find u for point on ray (q, b) closest to point at t
    Standard_Real u;
    if(BDotB!=0.0f)
    {
        u = (t*ADotB - BDotT) / BDotB;

        // if u is on segment (q, b), t and u correspond to closest points, otherwise, clamp u, recompute and clamp t
        if(u<0.0f)
        {
            u = 0.0f;
            if(ADotA!=0.0f)
                t = ios_clamp(ADotT / ADotA, 0.0, 1.0);
            else
                t = 0.0f;
        }
        else if(u > 1.0f)
        {
            u = 1.0f;
            if(ADotA!=0.0f)
                t = ios_clamp((ADotB + ADotT) / ADotA, 0.0, 1.0);
            else
                t = 0.0f;
        }
    }
    else
    {
        u = 0.0f;
        if(ADotA!=0.0f)
            t = ios_clamp(ADotT / ADotA, 0.0, 1.0);
        else
            t = 0.0f;
    }

    x = p + a * t;
    y = q + b * u;
}

// From NVIDIA-Omniverse PhysX - BSD 3-Clause "New" or "Revised" License
// https://github.com/NVIDIA-Omniverse/PhysX/blob/main/LICENSE.md
// https://github.com/NVIDIA-Omniverse/PhysX/blob/main/physx/source/geomutils/src/distance/GuDistanceTriangleTriangle.cpp
// With minor modifications to use gp_Vec type.
float distanceTriangleTriangleSquared(gp_Vec& cp, gp_Vec& cq, const std::array<gp_Vec, 3> p, const std::array<gp_Vec, 3> q)
{
    std::array<gp_Vec, 3> Sv;
    Sv[0] = p[1] - p[0];
    Sv[1] = p[2] - p[1];
    Sv[2] = p[0] - p[2];

    std::array<gp_Vec, 3> Tv;
    Tv[0] = q[1] - q[0];
    Tv[1] = q[2] - q[1];
    Tv[2] = q[0] - q[2];

    gp_Vec minP, minQ;
    bool shown_disjoint = false;

    float mindd = PX_MAX_F32;

    for(int i=0;i<3;i++)
    {
        for(int j=0;j<3;j++)
        {
            edgeEdgeDist(cp, cq, p[i], Sv[i], q[j], Tv[j]);
            const gp_Vec V = cq - cp;
            const float dd = V.Dot(V);

            if(dd<=mindd)
            {
                minP = cp;
                minQ = cq;
                mindd = dd;

                int id = i+2;
                if(id>=3)
                    id-=3;
                gp_Vec Z = p[id] - cp;
                float a = Z.Dot(V);
                id = j+2;
                if(id>=3)
                    id-=3;
                Z = q[id] - cq;
                float b = Z.Dot(V);

                if((a<=0.0f) && (b>=0.0f))
                    return V.Dot(V);

                        if(a<=0.0f)	a = 0.0f;
                else	if(b>0.0f)	b = 0.0f;

                if((mindd - a + b) > 0.0f)
                    shown_disjoint = true;
            }
        }
    }

    gp_Vec Sn = Sv[0].Crossed(Sv[1]);
    float Snl = Sn.Dot(Sn);

    if(Snl>1e-15f)
    {
        const std::array<double, 3> Tp = {(p[0] - q[0]).Dot(Sn),
                        (p[0] - q[1]).Dot(Sn),
                        (p[0] - q[2]).Dot(Sn)};

        int index = -1;
        if((Tp[0]>0.0f) && (Tp[1]>0.0f) && (Tp[2]>0.0f))
        {
            if(Tp[0]<Tp[1])		index = 0; else index = 1;
            if(Tp[2]<Tp[index])	index = 2;
        }
        else if((Tp[0]<0.0f) && (Tp[1]<0.0f) && (Tp[2]<0.0f))
        {
            if(Tp[0]>Tp[1])		index = 0; else index = 1;
            if(Tp[2]>Tp[index])	index = 2;
        }

        if(index >= 0) 
        {
            shown_disjoint = true;

            const gp_Vec& qIndex = q[index];

            gp_Vec V = qIndex - p[0];
            gp_Vec Z = Sn.Crossed(Sv[0]);
            if(V.Dot(Z)>0.0f)
            {
                V = qIndex - p[1];
                Z = Sn.Crossed(Sv[1]);
                if(V.Dot(Z)>0.0f)
                {
                    V = qIndex - p[2];
                    Z = Sn.Crossed(Sv[2]);
                    if(V.Dot(Z)>0.0f)
                    {
                        cp = qIndex + Sn * Tp[index]/Snl;
                        cq = qIndex;
                        return (cp - cq).SquareMagnitude();
                    }
                }
            }
        }
    }

    gp_Vec Tn = Tv[0].Crossed(Tv[1]);
    float Tnl = Tn.Dot(Tn);
  
    if(Tnl>1e-15f)
    {
        const std::array<double, 3> Sp = {(q[0] - p[0]).Dot(Tn),
                        (q[0] - p[1]).Dot(Tn),
                        (q[0] - p[2]).Dot(Tn)};

        int index = -1;
        if((Sp[0]>0.0f) && (Sp[1]>0.0f) && (Sp[2]>0.0f))
        {
            if(Sp[0]<Sp[1])		index = 0; else index = 1;
            if(Sp[2]<Sp[index])	index = 2;
        }
        else if((Sp[0]<0.0f) && (Sp[1]<0.0f) && (Sp[2]<0.0f))
        {
            if(Sp[0]>Sp[1])		index = 0; else index = 1;
            if(Sp[2]>Sp[index])	index = 2;
        }

        if(index >= 0)
        { 
            shown_disjoint = true;

            const gp_Vec& pIndex = p[index];

            gp_Vec V = pIndex - q[0];
            gp_Vec Z = Tn.Crossed(Tv[0]);
            if(V.Dot(Z)>0.0f)
            {
                V = pIndex - q[1];
                Z = Tn.Crossed(Tv[1]);
                if(V.Dot(Z)>0.0f)
                {
                    V = pIndex - q[2];
                    Z = Tn.Crossed(Tv[2]);
                    if(V.Dot(Z)>0.0f)
                    {
                        cp = pIndex;
                        cq = pIndex + Tn * Sp[index]/Tnl;
                        return (cp - cq).SquareMagnitude();
                    }
                }
            }
        }
    }

    if(shown_disjoint)
    {
        cp = minP;
        cq = minQ;
        return mindd;
    }
    else return 0.0f;
}
