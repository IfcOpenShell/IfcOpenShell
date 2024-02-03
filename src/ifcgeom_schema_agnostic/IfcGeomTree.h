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

#ifndef IFCGEOMTREE_H
#define IFCGEOMTREE_H

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom_schema_agnostic/IfcGeomElement.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"
#include "../ifcgeom_schema_agnostic/IfcGeomMaterial.h"
#include "../ifcgeom_schema_agnostic/Kernel.h"
#include "../ifcgeom_schema_agnostic/base_utils.h"

#include <NCollection_UBTree.hxx>
#include <BRepBndLib.hxx>
#include <Bnd_Box.hxx>
#include <BRep_Builder.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepExtrema_DistShapeShape.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <TopTools_DataMapOfShapeInteger.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepExtrema_ExtPF.hxx>

#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <BRepExtrema_TriangleSet.hxx>
#include <BRepLProp_SLProps.hxx>
#include <BVH_BinaryTree.hxx>
#include <BVH_Box.hxx>
#include <BVH_BoxSet.hxx>
#include <BVH_LinearBuilder.hxx>
#include <BVH_Tree.hxx>
#include <Bnd_OBB.hxx>
#include <GeomAPI_ProjectPointOnSurf.hxx>
#include <Geom_Plane.hxx>
#include <IntTools_FaceFace.hxx>
#include "triangleintersects.hpp"
#include <STEPConstruct_PointHasher.hxx>
#include <boost/stacktrace.hpp>


namespace IfcGeom {

	struct ray_intersection_result {
		double distance;
		int style_index;
		IfcUtil::IfcBaseEntity* instance;
		std::array<double, 3> position;
		std::array<double, 3> normal;
		double ray_distance;
		double dot_product;
	};

	namespace {

		// Approximates the distance `other` protrudes into `volume` by finding the
		// max face-vertex distance for every face, and taking the minimal value of
		// those. Note that this uses the internal `BRepExtrema_ExtPF` which only
		// returns solutions whose when the vertex projected onto the face is contained
		// within the face boundaries. In case of concave `volume` this is desirable.

		double max_distance_inside(const TopoDS_Shape& volume, const TopoDS_Shape& other) {
			TopExp_Explorer exp_v(volume.Reversed(), TopAbs_FACE);

			double min_face_vertex_distance = std::numeric_limits<double>::infinity();

			for (; exp_v.More(); exp_v.Next()) {
				const TopoDS_Face& f = TopoDS::Face(exp_v.Current());

				BRepExtrema_ExtPF epf;
				epf.Initialize(f, Extrema_ExtFlag_MIN);

				double face_vertex_distance = 0.;

				TopExp_Explorer exp_o(other, TopAbs_VERTEX);
				for (; exp_o.More(); exp_o.Next()) {
					const TopoDS_Vertex& v = TopoDS::Vertex(exp_o.Current());
					epf.Perform(v, f);
					if (epf.IsDone() && epf.NbExt() == 1) {
						double d = epf.SquareDistance(1);
						if (d > face_vertex_distance) {
							face_vertex_distance = d;
						}
					}
				}

				if (face_vertex_distance < min_face_vertex_distance) {
					min_face_vertex_distance = face_vertex_distance;
				}
			}

			if (min_face_vertex_distance == std::numeric_limits<double>::infinity()) {
				return -1.;
			} else {
				return std::sqrt(min_face_vertex_distance);
			}
		}
	}

	namespace impl {
		template <typename T>
		class tree {
            struct ray {
                float origin[3];
                float dir[3];
                float dir_inv[3];
            };

            struct box {
                float corners[2][3];
            };

            struct PointHasher {
                std::size_t operator()(const gp_Pnt& p) const {
                    // Assuming theUpperBound is somewhat arbitrary, but should be large enough
                    // and suitable for the size of the container.
                    // Note: std::unordered_set expects hash values starting from 0, but OpenCASCADE
                    // produces hash codes in the range [1, theUpperBound]. So, we adjust by subtracting 1.
                    return static_cast<std::size_t>(STEPConstruct_PointHasher::HashCode(p, std::numeric_limits<Standard_Integer>::max())) - 1;
                }
            };

            // Functor for comparing two gp_Pnt objects for equality
            struct PointEqual {
                bool operator()(const gp_Pnt& p1, const gp_Pnt& p2) const {
                    return STEPConstruct_PointHasher::IsEqual(p1, p2);
                }
            };


            // Branchless slab method. Note that this can still be optimised further by batching boxes.
            // https://tavianator.com/2022/ray_box_boundary.html
            bool is_intersect_ray_box(const struct ray *ray, const struct box *box) const {
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

            // Modified slightly to use gp_Vec and allow line-tri intersection
            // https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
            bool is_intersect_ray_tri(
                    const gp_Vec& ray_origin,
                    const gp_Vec& ray_vector,
                    const gp_Vec& ta,
                    const gp_Vec& tb,
                    const gp_Vec& tc,
                    gp_Vec& out_intersection_point,
                    const bool is_line = false
                    ) const {
                constexpr float epsilon = std::numeric_limits<float>::epsilon();

                gp_Vec edge1 = tb - ta;
                gp_Vec edge2 = tc - ta;
                gp_Vec ray_cross_e2 = ray_vector.Crossed(edge2);
                float det = edge1.Dot(ray_cross_e2);

                if (det > -epsilon && det < epsilon)
                    return false;    // This ray is parallel to this triangle.

                float inv_det = 1.0 / det;
                gp_Vec s = ray_origin - ta;
                float u = inv_det * s.Dot(ray_cross_e2);

                if (u < 0 || u > 1)
                    return false;

                gp_Vec s_cross_e1 = s.Crossed(edge1);
                float v = inv_det * ray_vector.Dot(s_cross_e1);

                if (v < 0 || u + v > 1)
                    return false;

                // At this stage we can compute t to find out where the intersection point is on the line.
                float t = inv_det * edge2.Dot(s_cross_e1);

                if (is_line) {
                    out_intersection_point = ray_origin + ray_vector * t;
                    return true;
                } else {
                    if (t > epsilon) // ray intersection
                    {
                        out_intersection_point = ray_origin + ray_vector * t;
                        return true;
                    }
                    else // This means that there is a line intersection but not a ray intersection.
                        return false;
                }
            }

            bool is_point_in_shape(
                    gp_Pnt v,
                    opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh,
                    BRepExtrema_TriangleSet triangle_set,
                    // In the case of "touching" rays, let's check again!
                    bool should_check_again = false
                    ) const {
                ray v_ray;
                v_ray.origin[0] = v.X();
                v_ray.origin[1] = v.Y();
                v_ray.origin[2] = v.Z();

                if (should_check_again) {
                    // The first check may be incorrect if it intersects
                    // exactly between triangles or on edges of triangles.
                    // A second check is used to "double check" the results.
                    // The second check is perpendicular because AEC objects
                    // are typically symmetrical along an axis, and goes down
                    // because there's typically less stuff down there.
                    v_ray.dir[0] = 0.0f;
                    v_ray.dir[1] = 0.0f;
                    v_ray.dir[2] = -1.0f;
                    v_ray.dir_inv[0] = INFINITY; // 1.0f/dir[0]
                    v_ray.dir_inv[1] = INFINITY; // 1.0f/dir[1]
                    v_ray.dir_inv[2] = -1.0f; // 1.0f/dir[2]
                } else {
                    v_ray.dir[0] = 1.0f;
                    v_ray.dir[1] = 0.0f;
                    v_ray.dir[2] = 0.0f;
                    v_ray.dir_inv[0] = 1.0f; // 1.0f/dir[0]
                    v_ray.dir_inv[1] = INFINITY; // 1.0f/dir[1]
                    v_ray.dir_inv[2] = INFINITY; // 1.0f/dir[2]
                }

                gp_Vec ray_origin(v.X(), v.Y(), v.Z());
                gp_Vec ray_vector(v_ray.dir[0], v_ray.dir[1], v_ray.dir[2]);

                int total_intersections = 0;

                std::stack<int> stack;
                stack.push(0);

                while ( ! stack.empty()) {
                    int i = stack.top();
                    stack.pop();

                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt min_point = bvh->MinPoint(i);
                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt max_point = bvh->MaxPoint(i);

                    box box;
                    // + 1e-5 for tolerance
                    box.corners[0][0] = min_point[0] - 1e-5;
                    box.corners[0][1] = min_point[1] - 1e-5;
                    box.corners[0][2] = min_point[2] - 1e-5;
                    box.corners[1][0] = max_point[0] + 1e-5;
                    box.corners[1][1] = max_point[1] + 1e-5;
                    box.corners[1][2] = max_point[2] + 1e-5;
                    /*
                    std::cout << "Ray " 
                        << v_ray.origin[0] << " "
                        << v_ray.origin[1] << " "
                        << v_ray.origin[2] << " "
                        << std::endl;
                    std::cout << "Box " 
                        << min_point[0] << " "
                        << min_point[1] << " "
                        << min_point[2] << " "
                        << max_point[0] << " "
                        << max_point[1] << " "
                        << max_point[2] << " "
                        << std::endl;
                    */

                    if ( ! is_intersect_ray_box(&v_ray, &box)) {
                        continue;
                    }
                    //std::cout << "Ray hits box" << std::endl;
                    if (bvh->IsOuter(i)) {
                        //std::cout << "Ray hits leaf" << std::endl;
                        // Do ray triangle check.
                        for (int j=bvh->BegPrimitive(i); j<=bvh->EndPrimitive(i); ++j) {
                            BVH_Vec3d v1, v2, v3;
                            triangle_set.GetVertices(j, v1, v2, v3);

                            gp_Vec ta(v1[0], v1[1], v1[2]);
                            gp_Vec tb(v2[0], v2[1], v2[2]);
                            gp_Vec tc(v3[0], v3[1], v3[2]);
                            gp_Vec intersection_point;

                            /*
                            std::cout << "ray origin " << ray_origin.X() << " " << ray_origin.Y() << " " << ray_origin.Z() << std::endl;
                            std::cout << "inside-tri " << ta.X() << " " << ta.Y() << " " << ta.Z() << std::endl;
                            std::cout << "inside-tri " << tb.X() << " " << tb.Y() << " " << tb.Z() << std::endl;
                            std::cout << "inside-tri " << tc.X() << " " << tc.Y() << " " << tc.Z() << std::endl;
                            */
                            if (is_intersect_ray_tri(ray_origin, ray_vector, ta, tb, tc, intersection_point)) {
                                // std::cout << " intersected " << intersection_point.X() << " " << intersection_point.Y() << " " << intersection_point.Z() << std::endl;
                                total_intersections++;
                            }
                        }
                    } else {
                        stack.push(bvh->Child<0>(i));
                        stack.push(bvh->Child<1>(i));
                    }
                }

                return total_intersections % 2 != 0;
            }

			bool test_intersection(const T& tA, const T& tB, const TopoDS_Shape& A, const TopoDS_Shape& B, double tolerance) const {
                // Attempt 3:
                //  1. For each vert of A that is inside shape B, find the shortest distance to the closest face
                //  2. Of those verts, find the innermost vert (i.e. the vert that has the longest distance)

                // OBB check
                auto obb_a = obbs_.find(tA)->second;
                auto obb_b = obbs_.find(tB)->second;
                obb_b.Enlarge(-tolerance);
                if (obb_a.IsOut(obb_b)) {
                    return false;
                }

                // No need to search beyond the distance of the max protrusion.
                double max_protrusion = max_protrusions_.find(tB)->second;

                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;
                std::unordered_map<int, std::vector<int>> bvh_clashes;

                for (int i=0; i<bvh_a->Length(); ++i) {
                    if ( ! bvh_a->IsOuter(i)) {
                        continue;
                    }

                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_a_min = bvh_a->MinPoint(i);
                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_a_max = bvh_a->MaxPoint(i);
                    bvh_a_min[0] -= 1e-3;
                    bvh_a_min[1] -= 1e-3;
                    bvh_a_min[2] -= 1e-3;
                    bvh_a_max[0] += 1e-3;
                    bvh_a_max[1] += 1e-3;
                    bvh_a_max[2] += 1e-3;

                    BVH_Box<Standard_Real, 3> box_a(bvh_a_min, bvh_a_max);
                    //BVH_Box<Standard_Real, 3> box_a(bvh_a->MinPoint(i), bvh_a->MaxPoint(i));

                    std::stack<int> stack;
                    stack.push(0);

                    while ( ! stack.empty()) {
                        int j = stack.top();
                        stack.pop();

                        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_b_min = bvh_b->MinPoint(j);
                        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_b_max = bvh_b->MaxPoint(j);
                        bvh_b_min[0] -= max_protrusion + 1e-3;
                        bvh_b_min[1] -= max_protrusion + 1e-3;
                        bvh_b_min[2] -= max_protrusion + 1e-3;
                        bvh_b_max[0] += max_protrusion + 1e-3;
                        bvh_b_max[1] += max_protrusion + 1e-3;
                        bvh_b_max[2] += max_protrusion + 1e-3;

                        //if (box_a.IsOut(bvh_b->MinPoint(j), bvh_b->MaxPoint(j))) {
                        if (box_a.IsOut(bvh_b_min, bvh_b_max)) {
                            continue;
                        }
                        if (bvh_b->IsOuter(j)) {
                            if (bvh_clashes.find(i) != bvh_clashes.end()) {
                                bvh_clashes[i].push_back(j);
                            } else {
                                bvh_clashes[i] = {j};
                            }
                        } else {
                            stack.push(bvh_b->Child<0>(j));
                            stack.push(bvh_b->Child<1>(j));
                        }
                    }
                }

                if (bvh_clashes.empty()) {
                    return false;
                }

                BRepExtrema_TriangleSet triangle_set_a = triangle_sets_.find(tA)->second;
                BRepExtrema_TriangleSet triangle_set_b = triangle_sets_.find(tB)->second;
                std::unordered_map<int, TopoDS_Face> faces_a = faces_.find(tA)->second;
                std::unordered_map<int, TopoDS_Face> faces_b = faces_.find(tB)->second;

                // ~10% faster?
                std::unordered_set<gp_Pnt, PointHasher, PointEqual> points_in_b_cache;
                std::unordered_set<gp_Pnt, PointHasher, PointEqual> points_not_in_b_cache;

                double protrusion = -std::numeric_limits<double>::infinity();
                std::array<double, 3> protrusion_point;
                std::array<double, 3> surface_point;

                for (const auto& pair : bvh_clashes) {
                    int bvh_a_i = pair.first;
                    std::vector<int> bvh_b_is = pair.second;

                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        std::vector<gp_Vec> ray_vectors;

                        BVH_Vec3d v1, v2, v3;

                        if (faces_a[triangle_set_a.GetFaceID(i)].Orientation() == TopAbs_REVERSED) {
                            triangle_set_a.GetVertices(i, v1, v3, v2);
                        } else {
                            triangle_set_a.GetVertices(i, v1, v2, v3);
                        }

                        gp_Pnt v1_a_pnt(v1[0], v1[1], v1[2]);
                        gp_Pnt v2_a_pnt(v2[0], v2[1], v2[2]);
                        gp_Pnt v3_a_pnt(v3[0], v3[1], v3[2]);

                        std::array<double, 3> t1a = {v1_a_pnt.X(), v1_a_pnt.Y(), v1_a_pnt.Z()};
                        std::array<double, 3> t1b = {v2_a_pnt.X(), v2_a_pnt.Y(), v2_a_pnt.Z()};
                        std::array<double, 3> t1c = {v3_a_pnt.X(), v3_a_pnt.Y(), v3_a_pnt.Z()};

                        gp_Vec normal_a;
                        try {
                            gp_Vec dir1_a(v1_a_pnt, v2_a_pnt);
                            gp_Vec dir2_a(v1_a_pnt, v3_a_pnt);
                            normal_a = dir1_a.Crossed(dir2_a).Normalized();
                        } catch (...) {
                            continue;
                        }

                        std::array<gp_Pnt, 3> points_a = {v1_a_pnt, v2_a_pnt, v3_a_pnt};
                        std::vector<gp_Pnt> points_in_b;

                        for (const auto& v : points_a) {
                            if (points_not_in_b_cache.find(v) != points_not_in_b_cache.end()) {
                                continue;
                            }

                            if (points_in_b_cache.find(v) != points_in_b_cache.end()) {
                                points_in_b.push_back(v);
                                continue;
                            }

                            if (obb_b.IsOut(v)) {
                                points_not_in_b_cache.insert(v);
                                continue;
                            }

                            if (is_point_in_shape(v, bvh_b, triangle_set_b)
                                    && is_point_in_shape(v, bvh_b, triangle_set_b, true)) {
                                points_in_b.push_back(v);
                                points_in_b_cache.insert(v);
                            } else {
                                points_not_in_b_cache.insert(v);
                            }
                        }

                        if (points_in_b.empty()) {
                            continue;
                        }

                        double v_protrusion = std::numeric_limits<double>::infinity();
                        std::array<double, 3> v_protrusion_point;
                        std::array<double, 3> v_surface_point;

                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                BVH_Vec3d v1_b, v2_b, v3_b;

                                if (faces_b[triangle_set_b.GetFaceID(j)].Orientation() == TopAbs_REVERSED) {
                                    triangle_set_b.GetVertices(j, v1_b, v3_b, v2_b);
                                } else {
                                    triangle_set_b.GetVertices(j, v1_b, v2_b, v3_b);
                                }

                                tri_count_++;

                                gp_Pnt v1_b_pnt(v1_b[0], v1_b[1], v1_b[2]);
                                gp_Pnt v2_b_pnt(v2_b[0], v2_b[1], v2_b[2]);
                                gp_Pnt v3_b_pnt(v3_b[0], v3_b[1], v3_b[2]);

                                /*
                                std::cout << "->cont " << v1_b[0] << " " << v1_b[1] << " " << v1_b[2] << std::endl;
                                std::cout << "->cont " << v2_b[0] << " " << v2_b[1] << " " << v2_b[2] << std::endl;
                                std::cout << "->cont " << v3_b[0] << " " << v3_b[1] << " " << v3_b[2] << std::endl;
                                */

                                gp_Vec normal_b;
                                try {
                                    gp_Vec dir1_b(v1_b_pnt, v2_b_pnt);
                                    gp_Vec dir2_b(v1_b_pnt, v3_b_pnt);
                                    normal_b = dir1_b.Crossed(dir2_b).Normalized();
                                    ray_vectors.push_back(normal_b);
                                } catch (...) {
                                    continue;
                                }

                                // We're penetrating _into_ a shape, so don't
                                // compare distances to faces with roughly the
                                // same normal as the penetration.
                                if (normal_a.Dot(normal_b) >= 0.9f) {
                                    continue;
                                }

                                for (const auto& v : points_in_b) {
                                    gp_Vec ray_origin(v.X(), v.Y(), v.Z());
                                    gp_Vec point_on_b;

                                    gp_Vec ta(v1_b[0], v1_b[1], v1_b[2]);
                                    gp_Vec tb(v2_b[0], v2_b[1], v2_b[2]);
                                    gp_Vec tc(v3_b[0], v3_b[1], v3_b[2]);

                                    /*
                                    std::cout << "POINT IN B " << v.X() << " " << v.Y() << " " << v.Z() << std::endl;
                                    std::cout << "dir-> " << normal_b.X() << " " << normal_b.Y() << " " << normal_b.Z() << std::endl;
                                    std::cout << "->tri " << v1_b[0] << " " << v1_b[1] << " " << v1_b[2] << std::endl;
                                    std::cout << "->tri " << v2_b[0] << " " << v2_b[1] << " " << v2_b[2] << std::endl;
                                    std::cout << "->tri " << v3_b[0] << " " << v3_b[1] << " " << v3_b[2] << std::endl;
                                    */

                                    // Do (cheaper) line check.
                                    if (is_intersect_ray_tri(ray_origin, normal_b, ta, tb, tc, point_on_b, true)) {
                                        gp_Pnt pnt_on_b(point_on_b.X(), point_on_b.Y(), point_on_b.Z());
                                        double current_v_protrusion = v.Distance(pnt_on_b);

                                        /*
                                        // What happens now?
                                        if (current_v_protrusion > max_protrusion) {
                                            continue;
                                        }
                                        */

                                        // std::cout << "We got a current protrusion " << current_v_protrusion << std::endl;
                                        if (current_v_protrusion < v_protrusion) {
                                            // std::cout << "New v_protrusion winner of " << current_v_protrusion << std::endl;
                                            v_protrusion = current_v_protrusion;
                                            v_protrusion_point = {v.X(), v.Y(), v.Z()};
                                            v_surface_point = {point_on_b.X(), point_on_b.Y(), point_on_b.Z()};
                                        }
                                    }
                                }
                            }
                        }

                        if (v_protrusion != std::numeric_limits<double>::infinity()) {
                            if (v_protrusion > protrusion) {
                                std::cout << "New actual protrusion winner of " << v_protrusion << std::endl;
                                protrusion = v_protrusion;
                                protrusion_point = v_protrusion_point;
                                surface_point = v_surface_point;
                            }
                        }
                    }
                }

                if (protrusion > tolerance) {
                    protrusion_distances_.push_back(protrusion);
                    protrusion_points_.push_back(protrusion_point);
                    surface_points_.push_back(surface_point);
                    return true;
                }
                return false;
            }

			bool test(const TopoDS_Shape& A, const TopoDS_Shape& B, bool completely_within, double extend) const {
				if (extend > 0.) {
					BRepExtrema_DistShapeShape dss(A, B);
					if (dss.Perform() && dss.NbSolution() >= 1) {
						if (dss.Value() <= extend) {
							distances_.push_back(dss.Value());
							protrusion_distances_.push_back(max_distance_inside(B, A));
						}						
						return dss.Value() <= extend;
					}
				} else {
					if (util::count(A, TopAbs_SHELL) == 0 ||
						util::count(B, TopAbs_SHELL) == 0)
					{
						return false;
					}

					if (completely_within) {
						BRepAlgoAPI_Cut cut(B, A);
						if (cut.IsDone()) {
							if (util::count(cut.Shape(), TopAbs_SHELL) == 0) {
								return true;
							}
						}
					} else {
						BRepAlgoAPI_Common common(A, B);
						if (common.IsDone()) {
							if (util::count(common.Shape(), TopAbs_SHELL) > 0) {
								return true;
							}
						}
					}
				}
				return false;
			}

		protected:

			// @todo this is ugly, embed this in the return type
			mutable std::vector<double> distances_;
			mutable std::vector<double> protrusion_distances_;
			mutable std::vector<std::array<double, 3>> protrusion_points_;
			mutable std::vector<std::array<double, 3>> surface_points_;
            mutable long long tri_count_ = 0;

		public:

			void add(const T& t, const Bnd_Box& b) {
				tree_.Add(t, b);
			}

			void add(const T& t, const TopoDS_Shape& s) {
				Bnd_Box b;
				BRepBndLib::AddClose(s, b);
				add(t, b);
				shapes_[t] = s;
			}

			void add_triangulated(const T& t, const TopoDS_Shape& s) {
                // Note that the original add function is also used elsewhere (e.g. boolean_utils.cpp)
                // We don't want to randomly add triangulated voids in our
                // tree, so for now this is a separate function.
                BRepMesh_IncrementalMesh(s, 1.e-3, false, 0.5);

				Bnd_Box b;
				BRepBndLib::AddClose(s, b);
				tree_.Add(t, b);
				shapes_[t] = s;

                Bnd_OBB obb;
                BRepBndLib::AddOBB(s, obb, true, true, false);
                obbs_[t] = obb;

                max_protrusions_[t] = std::min(std::min(obb.XHSize(), obb.YHSize()), obb.ZHSize()) * 2;

                BVH_BoxSet<double, 3>* boxset = new BVH_BoxSet<double, 3>();
                BRepExtrema_ShapeList shape_list;

                std::unordered_map<int, TopoDS_Face> faces;

                TopExp_Explorer exp_f;
                int i = 0;
                for (exp_f.Init(s, TopAbs_FACE); exp_f.More(); exp_f.Next()) {
                    shape_list.Append(exp_f.Current());

                    Bnd_Box aabb;
                    BRepBndLib::Add(exp_f.Current(), aabb);
                    double x, y, z, X, Y, Z;
                    aabb.Get(x, y, z, X, Y, Z);
                    const BVH_Box<Standard_Real, 3>::BVH_VecNt min(x, y, z);
                    const BVH_Box<Standard_Real, 3>::BVH_VecNt max(X, Y, Z);
                    BVH_Box<Standard_Real, 3> bvhBox(min, max);
                    boxset->Add(i, bvhBox);

                    faces[i] = TopoDS::Face(exp_f.Current());
                    i++;
                }

                /* Option 1: Builder?
                BVH_Tree<double, 3, BVH_BinaryTree>* bvh = new BVH_Tree<double, 3, BVH_BinaryTree>();
                BVH_Box<Standard_Real, 3> bvhBox2; // What's the point of this?
                BVH_LinearBuilder<Standard_Real, 3> builder;
                builder.Build(boxset, bvh, bvhBox2);
                */

                /* Option 2: Box set works, but ends up still comparing over 17 billion tri pairs
                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh = boxset->BVH();
                */

                // Option 3: Triangle set - down to 96 million pairs
                BRepExtrema_TriangleSet triangle_set(shape_list);
                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh = triangle_set.BVH();

                // Debug
                /*
                std::cout << "DEBUGG:" << std::endl;
                for (int i=0; i<triangle_set.Size(); ++i) {
                    BVH_Vec3d v1, v2, v3;
                    triangle_set.GetVertices(i, v1, v2, v3);
                    int face_id = triangle_set.GetFaceID(i);
                    std::cout << "Triangle in triangle set:" << std::endl;
                    std::cout << v1[0] << " " << v1[1] << " " << v1[2] << std::endl;
                    if (faces[face_id].Orientation() == TopAbs_REVERSED) {
                        std::cout << v3[0] << " " << v3[1] << " " << v3[2] << std::endl;
                        std::cout << v2[0] << " " << v2[1] << " " << v2[2] << std::endl;
                    } else {
                        std::cout << v2[0] << " " << v2[1] << " " << v2[2] << std::endl;
                        std::cout << v3[0] << " " << v3[1] << " " << v3[2] << std::endl;
                    }
                }
                */

                triangle_sets_[t] = triangle_set;
                boxsets_[t] = boxset;
                bvhs_[t] = bvh;
                faces_[t] = faces;
			}

			std::vector<T> select_box(const T& t, bool completely_within = false, double extend=-1.e-5) const {
				typename map_t::const_iterator it = shapes_.find(t);
				if (it == shapes_.end()) {
					return std::vector<T>();
				}

				Bnd_Box b;
				BRepBndLib::AddClose(it->second, b);

				// Gap is assumed to be positive throughout the codebase,
				// but at least for IsOut() in the selector a negative
				// Gap should work as well.
				b.SetGap(b.GetGap() + extend); 
				
                // Should this filter itself? (i.e. t)
				return select_box(b, completely_within);
			}

			std::vector<T> select_box(const gp_Pnt& p, double extend=0.0) const {
				Bnd_Box b;
				b.Add(p);
				b.SetGap(b.GetGap() + extend);
				return select_box(b);
			}

			std::vector<T> select_box(const Bnd_Box& b, bool completely_within = false) const {
				selector s(b);
				tree_.Select(s);
				if (completely_within) {
					std::vector<T> ts = s.results();
					std::vector<T> ts_filtered;
					ts_filtered.reserve(ts.size());
					typename std::vector<T>::const_iterator it = ts.begin();
					for (; it != ts.end(); ++it) {
						const TopoDS_Shape& shp = shapes_.find(*it)->second;
						Bnd_Box B;
						BRepBndLib::AddClose(shp, B);

						// BndBox::CornerMin() /-Max() introduced in OCCT 6.8
						double x1, y1, z1, x2, y2, z2;
						b.Get(x1, y1, z1, x2, y2, z2);
						double gap = B.GetGap();
						gp_Pnt p1(x1 - gap, y1 - gap, z1 - gap);
						gp_Pnt p2(x2 + gap, y2 + gap, z2 + gap);
						
						if (!b.IsOut(p1) && !b.IsOut(p2)) {
							ts_filtered.push_back(*it);
						}
					}
					return ts_filtered;
				} else {
					return s.results();
				}
			}

			std::vector<T> clash_intersection(const T& t, double tolerance = 0.002) const {
				protrusion_distances_.clear();
				protrusion_points_.clear();
				surface_points_.clear();

				std::vector<T> ts = select_box(t, true, 1e-5);
				if (ts.empty()) {
					return ts;
				}
                std::cout << "Passes box check" << std::endl;

				const TopoDS_Shape& A = shapes_.find(t)->second;

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());
                std::cout << "We have to check X box results " << ts.size() << std::endl;

                int i = 0;

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;
                    // Don't clash against itself.
                    if (t == *it) {
                        continue;
                    }
                    i++;
                    std::cout << "Currently doing" << i << std::endl;

					if (test_intersection(t, *it, A, B, tolerance)) {
						ts_filtered.push_back(*it);
					}
				}
                std::cout << "Tri count " << tri_count_ << std::endl;

				return ts_filtered;
			}

			std::vector<T> select(const T& t, bool completely_within = false, double extend = 0.0) const {
				distances_.clear();
				protrusion_distances_.clear();

				std::vector<T> ts = select_box(t, completely_within, extend);
				if (ts.empty()) {
					return ts;
				}

				const TopoDS_Shape& A = shapes_.find(t)->second;

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;

					if (test(A, B, completely_within, extend)) {
						ts_filtered.push_back(*it);
					}
				}

				return ts_filtered;
			}

			std::vector<T> select(const TopoDS_Shape& s, bool completely_within = false, double extend = -1.e-5) const {
				distances_.clear();
				protrusion_distances_.clear();

				Bnd_Box bb;
				BRepBndLib::AddClose(s, bb);
				bb.SetGap(bb.GetGap() + extend);

				std::vector<T> ts = select_box(bb, completely_within);

				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;

                    /*
					if (test(s, B, completely_within, extend)) {
						ts_filtered.push_back(*it);
					}
                    */
				}

				return ts_filtered;
			}

			std::vector<T> select(const IfcGeom::BRepElement* elem, bool completely_within = false, double extend = -1.e-5) const {
				auto compound = elem->geometry().as_compound();
				compound.Move(elem->transformation().data());
				return select(compound, completely_within, extend);
			}

			std::vector<T> select(const gp_Pnt& p, double extend=0.0) const {
				distances_.clear();
				protrusion_distances_.clear();

				std::vector<T> ts = select_box(p, extend);
				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				TopoDS_Vertex v;
				if (extend > 0.) {
					BRep_Builder B;
					B.MakeVertex(v, p, Precision::Confusion());
				}

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;
					if (extend > 0.0) {
						BRepExtrema_DistShapeShape dss(v, B);
						if (dss.Perform() && dss.NbSolution() >= 1 && dss.Value() <= extend) {
							distances_.push_back(dss.Value());							
							protrusion_distances_.push_back(max_distance_inside(B, v));

							ts_filtered.push_back(*it);
						}
					} else {
						TopExp_Explorer exp(B, TopAbs_SOLID);
						for (; exp.More(); exp.Next()) {
							BRepClass3d_SolidClassifier cls(exp.Current(), p, 1e-5);
							if (cls.State() != TopAbs_OUT) {
								ts_filtered.push_back(*it);
								break;
							}
						}
					}
				}

				return ts_filtered;
			}

		protected:
			typedef NCollection_UBTree<T, Bnd_Box> tree_t;
			typedef std::map<T, TopoDS_Shape> map_t;

			tree_t tree_;
			map_t shapes_;
            std::map<T, Bnd_OBB> obbs_; 
            std::map<T, double> max_protrusions_; 
            //std::map<T, BVH_Tree<double, 3, BVH_BinaryTree>*> bvhs_; 
            std::map<T, opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>> bvhs_; 
            std::map<T, BVH_BoxSet<double, 3>*> boxsets_; 
            std::map<T, BRepExtrema_TriangleSet> triangle_sets_; 
            std::unordered_map<T, std::unordered_map<int, TopoDS_Face>> faces_;
			
			bool enable_face_styles_ = false;

			class selector : public tree_t::Selector
			{
			public:
				selector(const Bnd_Box& b)
					: tree_t::Selector()
					, bounds_(b)
				{}

				Standard_Boolean Reject(const Bnd_Box& b) const {
					return bounds_.IsOut(b);
				}

				Standard_Boolean Accept(const T& o) {
					results_.push_back(o);
					return Standard_True;
				}

				const std::vector<T>& results() const {
					return results_;
				}

			private:
				std::vector<T> results_;
				const Bnd_Box& bounds_;
			};

		};
	}

	class tree : public impl::tree<IfcUtil::IfcBaseEntity*> {
	public:

		tree() {};

		tree(IfcParse::IfcFile& f) {
			add_file(f, IfcGeom::IteratorSettings());
		}

		tree(IfcParse::IfcFile& f, const IfcGeom::IteratorSettings& settings) {
			add_file(f, settings);
		}

		tree(IfcGeom::Iterator& it) {
			add_file(it);
		}		

		void add_file(IfcParse::IfcFile& f, const IfcGeom::IteratorSettings& settings) {
			IfcGeom::IteratorSettings settings_ = settings;
			settings_.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
			settings_.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
			settings_.set(IfcGeom::IteratorSettings::SEW_SHELLS, true);

			IfcGeom::Iterator it(settings_, &f);

			add_file(it);
		}

		void add_file(IfcGeom::Iterator& it) {
			if (it.initialize()) {
				do {
					add_element(dynamic_cast<IfcGeom::BRepElement*>(it.get()));
				} while (it.next());
			}
		}

		void add_element(IfcGeom::BRepElement* elem, bool should_triangulate=false) {
			if (!elem) {
				return;
			}
			auto compound = elem->geometry().as_compound();
			compound.Move(elem->transformation().data());
            if (should_triangulate) {
                add_triangulated(elem->product(), compound);
            } else {
                add(elem->product(), compound);
            }
			auto git = elem->geometry().begin();

			if (enable_face_styles_) {
				TopoDS_Iterator it(compound);
				for (; it.More(); it.Next(), ++git) {
					std::unique_ptr<IfcGeom::Material> adaptor;					
					if (git->hasStyle()) {
						adaptor.reset(new Material(git->StylePtr()));
					} else {
						adaptor.reset(new Material(IfcGeom::get_default_style(elem->type())));
					}
					
					// Assumption is that the number of styles is small, so the linear lookup time is not significant.
					auto sit = std::find(styles_.begin(), styles_.end(), *adaptor);
					size_t index;
					if (sit == styles_.end()) {
						index = styles_.size();
						styles_.push_back(*adaptor);
					} else {
						index = std::distance(styles_.begin(), sit);
					}

					TopExp_Explorer exp(it.Value(), TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						face_styles_.Bind(exp.Current(), (int) index);
					}
				}
			}
		}

		const std::vector<double>& distances() const {
			return distances_;
		}

		const std::vector<double>& protrusion_distances() const {
			return protrusion_distances_;
		}

		const std::vector<std::array<double, 3>>& protrusion_points() const {
			return protrusion_points_;
		}

		const std::vector<std::array<double, 3>>& surface_points() const {
			return surface_points_;
		}

		std::vector<IfcGeom::ray_intersection_result> select_ray(const gp_Pnt& p0, const gp_Dir& d, double length = 1000.) const {
			gp_Pnt p1 = p0.XYZ() + d.XYZ() * length;
			auto E = BRepBuilderAPI_MakeEdge(p0, p1).Edge();
			Bnd_Box bb;
			bb.Add(p0);
			bb.Add(p1);
			auto candidates = select_box(bb);

			std::multimap<double, ray_intersection_result> ordered;

			for (auto& c : candidates) {
				BRepExtrema_DistShapeShape dss(E, shapes_.find(c)->second);
				for (int i = 1; i <= dss.NbSolution(); ++i) {
					if (dss.SupportTypeShape1(i) != BRepExtrema_IsOnEdge) {
						// @todo set to 0, is it on the first verteX?
						continue;
					}
					if (dss.SupportTypeShape2(i) != BRepExtrema_IsInFace) {
						continue;
					}
					double u, v, w;
					dss.ParOnEdgeS1(i, u);
					auto face = TopoDS::Face(dss.SupportOnShape2(i));
					int sidx = -1;
					if (enable_face_styles_) {
						sidx = face_styles_.Find(face);
					}
					dss.ParOnFaceS2(i, v, w);
					BRepGProp_Face prop(face);
					gp_Pnt P;
					gp_Vec V;
					prop.Normal(v, w, P, V);
					ordered.insert({ u,	{ u, sidx, c,
						{P.X(), P.Y(), P.Z()},
						{V.X(), V.Y(), V.Z()},
						d.XYZ().Dot(p0.XYZ() - P.XYZ()),
						V.Dot(d)
					} });
				}
			}

			std::vector<ray_intersection_result> result;
			for (auto& p : ordered) {
				result.push_back(p.second);
			}

			return result;
		}

		bool enable_face_styles() const {
			return enable_face_styles_;
		}

		void enable_face_styles(bool b) {
			enable_face_styles_ = b;
		}

		const std::vector<IfcGeom::Material>& styles() const {
			return styles_;
		}

	protected:
		typedef TopTools_DataMapOfShapeInteger face_style_map_t;

		face_style_map_t face_styles_;
		std::vector<IfcGeom::Material> styles_;
	};

}

#endif
